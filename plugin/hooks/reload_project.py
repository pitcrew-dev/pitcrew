#!/usr/bin/env python3
"""SessionStart hook, run after /compact (manual or automatic).

Compacting squeezes the conversation into a summary, and the PM can lose
where the project stands and what the user has already corrected. This puts
the small files that hold exactly that back into the conversation:

  * .claude/project/plan.md     the plan; its "Now" section comes first
  * .claude/project/status.md   current progress (projects from before plan.md)
  * .claude/project/lessons.md  corrections that must not be repeated

Looks in the session's folder and its parents. Each file is capped, so a
file that has grown too big can't flood the context.

Silent when there is no project. Fails OPEN on any internal error.
"""
import json
import os
import sys

FILES = ("plan.md", "status.md", "lessons.md")
MAX_CHARS = 4000


def find_project(start):
    current = os.path.abspath(start)
    while True:
        folder = os.path.join(current, ".claude", "project")
        if any(os.path.isfile(os.path.join(folder, name)) for name in FILES):
            return folder
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    folder = find_project(payload.get("cwd") or os.getcwd())
    if not folder:
        return 0

    parts = []
    for name in FILES:
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                text = handle.read().strip()
        except OSError:
            continue
        if not text:
            continue
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + "\n[... cut here; read the full file if you need the rest]"
        parts.append("## .claude/project/%s\n\n%s" % (name, text))

    if parts:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows would otherwise choke on non-ASCII notes
        sys.stdout.write("The conversation was just compacted. Where the project stands, reloaded from its files:\n\n")
        sys.stdout.write("\n\n".join(parts) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
