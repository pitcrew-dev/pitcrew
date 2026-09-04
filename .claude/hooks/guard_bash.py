#!/usr/bin/env python
"""PreToolUse guard for Bash.

Blocks irreversible operations that the PM charter reserves for human approval
(Duty 11: "a production-affecting or irreversible action"). An agent cannot
un-drop a database or un-force-push.

Contract: exit 2 blocks the call and returns stderr to the model.
Fails OPEN on any internal error.
"""
import json
import re
import sys

DENY = [
    (r"\brm\s+(-[a-z]*[rf][a-z]*\s+)+(/|~|\$HOME|[a-z]:[\\/]|\*|\.\.)(\s|$)",
     "Recursive delete of a root, home, or wildcard path. If a deletion is genuinely needed, name the exact directory and get the user's approval first."),
    (r"\bgit\s+push\b.*(--force|(^|\s)-f(\s|$))(?!-with-lease)",
     "Force-push rewrites published history. Use --force-with-lease, and only on your own task branch — never on main (git-workflow.md, section 2)."),
    (r"\bgit\s+(clean\s+-[a-z]*[fd]|checkout\s+--\s+\.|restore\s+--\s*(staged\s+)?\.)",
     "This discards uncommitted work irreversibly. Confirm with the user before throwing away changes you did not make."),
    (r"\bgit\s+reset\s+--hard\b",
     "git reset --hard destroys uncommitted work. Confirm with the user first, or use git stash."),
    (r"\bdrop\s+(database|table|schema)\b",
     "Destructive schema change. Migrations are append-only once merged (coding-standards.md, section 3), and destructive database operations require the user's explicit approval (PM charter, Duty 11)."),
    (r"\btruncate\s+table\b|\bdelete\s+from\s+\w+\s*;",
     "Unfiltered data deletion. This requires the user's explicit approval."),
    (r"\bmigrate:(fresh|reset)\b|\bdb:wipe\b",
     "This drops every table and destroys the data. Use a normal forward migration; if a rebuild is genuinely needed, the user must approve it."),
    (r"\bcurl\b[^|]*\|\s*(sudo\s+)?(ba)?sh\b|\bwget\b[^|]*\|\s*(sudo\s+)?(ba)?sh\b",
     "Piping a downloaded script straight into a shell executes unreviewed remote code. Download it, read it, then run it."),
    (r"\bchmod\s+(-[a-z]+\s+)*777\b",
     "chmod 777 makes files world-writable. Set the narrowest permission that works."),
    (r"\bgit\s+commit\b.*(--no-verify|(^|\s)-n(\s|$))",
     "Skipping hooks bypasses the checks that make the gate real. Fix what the hook is complaining about."),
]


def main() -> int:
    payload = json.loads(sys.stdin.read())

    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or ""
    if not command:
        return 0

    haystack = command.lower()

    for pattern, reason in DENY:
        if re.search(pattern, haystack):
            sys.stderr.write("BLOCKED by irreversible-action guard.\n\n%s\n\nCommand: %s\n" % (reason, command))
            return 2

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
