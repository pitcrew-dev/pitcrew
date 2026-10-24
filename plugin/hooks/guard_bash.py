#!/usr/bin/env python3
"""PreToolUse guard for the Bash and PowerShell tools.

Catches irreversible commands before they run. Two outcomes:

  deny  never allowed; the reason goes back to the agent (exit 2)
  ask   runs only if the user approves (permissionDecision "ask")

Quoted text is treated as data, so a commit message that mentions
`git reset --hard` is not a reset. The exception is a payload that really
runs: `bash -c "..."`, `mysql -e "..."`, `pwsh -Command "..."`, `eval "..."`.
Delete commands are also checked with quotes removed, so `rm -rf "/"` is
still caught.

This is the only net for these rules: a plugin cannot ship permission rules,
so every deny and ask rule from the old settings.json lives here.

Fails OPEN on any internal error: a bug here must never block real work.
"""
import json
import re
import subprocess
import sys

DENY, ASK = "deny", "ask"

SEPARATOR = re.compile(r"&&|\|\||[;|&\n]")
HEREDOC = re.compile(r"<<-?[ \t]*(['\"]?)(\w+)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", re.S)
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
EXECUTED_PAYLOAD = re.compile(r"(?:^|\s)(?:-c|-e|--execute|-command|-query|/c|eval)[ \t]*=?[ \t]*$", re.I)
LEADING_ASSIGNMENT = re.compile(r"^\w+=")

WRAPPERS = {"sudo", "command", "exec", "nohup", "time", "env"}
DELETE_COMMANDS = {"rm", "remove-item", "ri", "rd", "rmdir", "del", "erase"}
ROOT_TARGET = re.compile(
    r"^(/|/\*|~|~/|~/\*|\$home[\\/]?|\$env:userprofile[\\/]?|[a-z]:[\\/]?\*?|\\|\*"
    r"|\.|\.[\\/]|\.[\\/]\*|\.\.|\.\.[\\/]\*?)$",
    re.I,
)
SOURCE_TARGET = re.compile(
    r"^(\.[\\/])?(app|src|lib|database|resources|config|routes|tests|public|wp-content|\.git)[\\/]?$",
    re.I,
)
PROTECTED_BRANCHES = {"main", "master"}

TEXT_RULES = [
    (DENY, re.compile(r"\bdrop\s+(database|schema)\b", re.I),
     "Dropping a database destroys every table in it. Destructive database operations need the "
     "user's explicit decision: stop and ask them."),
    (ASK, re.compile(r"\bdrop\s+table\b", re.I),
     "Dropping a table deletes its data. Schema changes belong in a migration."),
    (ASK, re.compile(r"\btruncate\s+table\b|\bdelete\s+from\s+[\w.`\"\[\]]+\s*(;|$)", re.I | re.M),
     "Unfiltered data deletion (no WHERE clause)."),
    (DENY, re.compile(r"\b(curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^\n]*"
                      r"\|\s*(sudo\s+)?((ba|z|da)?sh|iex|invoke-expression|python3?|php)\b", re.I),
     "Piping downloaded code straight into an interpreter runs unreviewed remote code. "
     "Download it, read it, then run it."),
    (DENY, re.compile(r"\bchmod\s+(-[a-z]+\s+)*0?777\b", re.I),
     "chmod 777 makes files world-writable. Use the narrowest permission that works."),
    (DENY, re.compile(r"\b(format-volume|clear-disk|initialize-disk|mkfs(\.\w+)?)\b"
                      r"|\bformat\s+[a-z]:|\bdd\b[^\n]*\bof=/dev/", re.I),
     "Disk-level destruction. Never run by an agent."),
]


def strip_data(command):
    """Blank out quoted text and heredoc bodies, except payloads that execute."""
    command = HEREDOC.sub(" ", command)
    out, last = [], 0
    for match in QUOTED.finditer(command):
        out.append(command[last:match.start()])
        if EXECUTED_PAYLOAD.search(command[:match.start()]):
            # A payload that runs is its own command line: newlines make it separate segments.
            out.append("\n" + match.group(0)[1:-1] + "\n")
        else:
            out.append(" ")
        last = match.end()
    out.append(command[last:])
    return "".join(out)


def segments(text):
    """Split a command line into simple commands, each a list of tokens."""
    for raw in SEPARATOR.split(text):
        tokens = raw.split()
        while tokens and (tokens[0].lower() in WRAPPERS or LEADING_ASSIGNMENT.match(tokens[0])):
            tokens = tokens[1:]
        if tokens:
            yield tokens


def check_delete(tokens):
    name = tokens[0].lower().replace("\\", "/").rsplit("/", 1)[-1]
    if name not in DELETE_COMMANDS:
        return None
    recursive = False
    for arg in tokens[1:]:
        low = arg.lower()
        if low in ("--recursive", "/s", "-r") or low.startswith("-rec"):
            recursive = True
        elif name == "rm" and low.startswith("-") and not low.startswith("--") and "r" in low[1:]:
            recursive = True
    if not recursive:
        return None
    targets = [t for t in tokens[1:] if not t.startswith("-") and t.lower() not in ("/s", "/q")]
    if any(ROOT_TARGET.match(t) for t in targets):
        return DENY, ("Recursive delete of a root, home, current-directory or wildcard path. "
                      "If a deletion is really needed, name the exact directory and ask the user.")
    if any(SOURCE_TARGET.match(t) for t in targets):
        return ASK, "Recursive delete of a project source directory."
    return None


def check_remove_item(tokens):
    if tokens[0].lower() == "remove-item":
        return ASK, "Remove-Item deletes files. The user approves it first."
    return None


def current_branch(cwd):
    # symbolic-ref also works on a branch with no commits yet; rev-parse doesn't.
    try:
        proc = subprocess.run(["git", "symbolic-ref", "--short", "HEAD"], cwd=cwd or None,
                              capture_output=True, text=True, timeout=3)
        return proc.stdout.strip() if proc.returncode == 0 else None
    except Exception:
        return None


def check_git(tokens, cwd):
    if tokens[0].lower().replace("\\", "/").rsplit("/", 1)[-1] not in ("git", "git.exe"):
        return None
    i = 1
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
    if i >= len(tokens):
        return None
    sub, rest = tokens[i].lower(), tokens[i + 1:]
    flags = [t for t in rest if t.startswith("-")]
    args = [t for t in rest if not t.startswith("-")]
    short = "".join(f[1:] for f in flags if not f.startswith("--"))

    if sub == "push":
        if "--force" in flags or "f" in short or any(a.startswith("+") for a in args):
            return DENY, ("Force-push rewrites published history. Use --force-with-lease, and only on "
                          "your own task branch, never on main.")
        if "--no-verify" in flags:
            return DENY, "Skipping hooks bypasses the checks that make the gate real."
        refs = args[1:]
        targets = [r.split(":")[-1].replace("refs/heads/", "") for r in refs]
        if not refs:
            branch = current_branch(cwd)
            targets = [branch] if branch else []
        if (set(targets) & PROTECTED_BRANCHES or "--all" in flags or "--mirror" in flags
                or "--delete" in flags or "d" in short):
            return ASK, "Pushing to a protected branch (or deleting a remote branch) is the user's call."
        return ASK, "Every push publishes work. The user approves it first."
    if sub == "commit" and ("--no-verify" in flags or "n" in short):
        return DENY, "Skipping hooks bypasses the checks that make the gate real. Fix what the hook reports."
    if sub == "reset" and "--hard" in flags:
        return ASK, "git reset --hard destroys uncommitted work. Consider git stash instead."
    if sub == "clean" and ("f" in short or "--force" in flags):
        return ASK, "git clean deletes untracked files for good."
    if sub == "checkout" and any(a in (".", "*", ":/") for a in args):
        return ASK, "This discards every uncommitted change in the working tree."
    if sub == "restore" and "--staged" not in flags and "S" not in short \
            and any(a in (".", "*", ":/") for a in args):
        return ASK, "This discards every uncommitted change in the working tree."
    if sub == "branch" and ("D" in short or ("--delete" in flags and ("--force" in flags or "f" in short))):
        return ASK, "Force-deleting a branch can lose unmerged work."
    if sub == "stash" and args and args[0].lower() in ("drop", "clear"):
        return ASK, "Dropping a stash loses that work for good."
    return None


def check_artisan(tokens):
    lowered = [t.lower() for t in tokens]
    idx = next((i for i, t in enumerate(lowered) if t.endswith("artisan")), None)
    if idx is None or idx + 1 >= len(lowered):
        return None
    cmd, rest = lowered[idx + 1], lowered[idx + 2:]
    if cmd in ("migrate:fresh", "migrate:reset", "migrate:refresh", "db:wipe"):
        return DENY, ("This drops every table and destroys the data. Use a forward migration; if a "
                      "rebuild is really needed, the user runs it themselves.")
    production = "--force" in rest or any(r.startswith("--env=prod") for r in rest)
    if production and (cmd.startswith("migrate") or cmd.startswith("db:seed")):
        return ASK, "Running migrations or seeders with --force (production mode) is the user's call."
    return None


def check_wp(tokens):
    lowered = [t.lower() for t in tokens]
    if lowered[0] == "wp" and lowered[1:3] in (["db", "drop"], ["db", "reset"], ["site", "empty"]):
        return DENY, "This wipes the WordPress database. Never run by an agent."
    return None


def evaluate(command, cwd=None):
    found = []
    stripped = strip_data(command)
    for tokens in segments(stripped):
        for check in (check_delete, check_remove_item, check_artisan, check_wp):
            verdict = check(tokens)
            if verdict:
                found.append(verdict)
        verdict = check_git(tokens, cwd)
        if verdict:
            found.append(verdict)
    # Delete targets are often quoted ("C:\", "/"), so check them with quotes removed too.
    unquoted = HEREDOC.sub(" ", command).replace('"', " ").replace("'", " ")
    for tokens in segments(unquoted):
        verdict = check_delete(tokens)
        if verdict:
            found.append(verdict)
    for kind, pattern, reason in TEXT_RULES:
        if pattern.search(stripped):
            found.append((kind, reason))
    for wanted in (DENY, ASK):
        for kind, reason in found:
            if kind == wanted:
                return kind, reason
    return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    command = (payload.get("tool_input") or {}).get("command") or ""
    if not command.strip():
        return 0
    verdict = evaluate(command, payload.get("cwd"))
    if not verdict:
        return 0
    kind, reason = verdict
    if kind == DENY:
        sys.stderr.write("BLOCKED by the irreversible-action guard.\n\n%s\n" % reason)
        return 2
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "Irreversible-action guard: " + reason,
    }}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
