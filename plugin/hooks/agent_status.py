#!/usr/bin/env python3
"""Subagent status line: who is working, on which task, and the story's budget.

Claude Code runs this on every refresh of the agent panel, with all visible
agent rows on stdin. For each row whose description names a task ID, it
writes one line back:

    qa-engineer · SHOP-E01-S02-T01 · story $14.20 of $25.00 · 45k tokens

Rows without a task ID, and anything outside a project, keep Claude Code's
default rendering. Reads only small files, so it stays fast.

Fails OPEN: on any error it prints nothing and the default rows show.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import costs  # noqa: E402


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    folder = costs.find_project(payload.get("cwd") or os.getcwd())
    if not folder:
        return 0
    stories, _ = costs.logged(os.path.join(folder, "activity.md"))
    story_budget, _, topups = costs.budgets(folder)

    out = []
    for task in payload.get("tasks") or []:
        found = costs.TASK_ID.search(task.get("description") or "")
        if not task.get("id") or not found:
            continue
        story = costs.story_of(found.group(0))
        agent = (task.get("agentType") or "agent").split(":")[-1]
        tokens = task.get("tokenCount") or 0
        content = "%s · %s · story $%.2f of $%.2f · %dk tokens" % (
            agent, found.group(0), stories.get(story, 0.0), story_budget + topups.get(story, 0.0), tokens // 1000)
        out.append(json.dumps({"id": task["id"], "content": content}, ensure_ascii=False))
    if out:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
