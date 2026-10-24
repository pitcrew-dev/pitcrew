#!/usr/bin/env python3
"""SessionStart hook: puts the working agreement into every session.

A plugin cannot load a CLAUDE.md, so this prints company/working-agreement.md
as SessionStart context, with one line first that says where the company
folder is. The agreement and the PM brief refer to the other files by short
paths ("standards/token-budget.md"); that line is how they resolve.

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
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": intro + "\n\n" + agreement,
    }}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
