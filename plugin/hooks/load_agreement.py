#!/usr/bin/env python3
"""SessionStart hook: puts the working agreement into every session.

A plugin cannot load a CLAUDE.md, so this prints company/working-agreement.md
as SessionStart context, with one line first that says where the company
folder is. The agreement and the PM brief refer to the other files by short
paths ("standards/token-budget.md"); that line is how they resolve.

When a session starts and the old 0.2.x copy-in install is still in the
Claude config folder, it also tells the user, once, how to remove it.

Silent when the file is missing. Fails OPEN on any internal error.
"""
import json
import os
import sys


def plugin_root():
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if root:
        return root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def old_install():
    """The config folder still holding a 0.2.x copy-in install, or None."""
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    markers = (".agent-company.json", os.path.join("company", "working-agreement.md"),
               os.path.join("hooks", "agent-company"))
    return base if any(os.path.exists(os.path.join(base, marker)) for marker in markers) else None


OLD_INSTALL = (
    "Agent Company: an older copy (0.2.x) is still installed in %s, so every agent and command "
    "is there twice. To remove it, run `python install.py --uninstall` in the agent-company folder "
    "you installed it from (add --dry-run first to see what it would remove). Your own files are "
    "kept, and everything it removes is backed up first.")


def main():
    folder = os.path.abspath(os.path.join(plugin_root(), "company"))
    path = os.path.join(folder, "working-agreement.md")
    if not os.path.isfile(path):
        return 0
    with open(path, encoding="utf-8") as handle:
        agreement = handle.read().strip()
    if not agreement:
        return 0
    intro = "Company files are in: %s/ -- paths below are relative to it." % folder.replace("\\", "/")
    output = {"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": intro + "\n\n" + agreement,
    }}
    payload = json.loads(sys.stdin.read() or "{}")
    old = old_install() if payload.get("source", "startup") == "startup" else None
    if old:
        message = OLD_INSTALL % old.replace("\\", "/")
        output["systemMessage"] = message
        output["hookSpecificOutput"]["additionalContext"] += (
            "\n\n" + message + " Mention this to the user once, in plain words, and offer to show them the command.")
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
