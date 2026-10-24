#!/usr/bin/env python3
"""PreToolUse hook on Agent and SendMessage: keeps each story inside its budget.

Before an agent is started or sent a follow-up, it adds up what the story has
cost so far (activity.md, plus the PM's work not logged yet) and compares it
with the story's budget:

  * under 80%: silent
  * 80% or more: lets the agent run and tells the PM to warn the user
  * 100% or more: blocks it (exit 2). The PM stops, asks the user, and
    records an approved top-up in budget.md before trying again

The project total is checked the same way when a project budget is set.
An agent that is already running is never interrupted.

Budgets come from .claude/project/budget.md, else the plugin settings
(story_budget, project_budget), else $25 per story and no project cap.

Silent when there is no project. Fails OPEN on any internal error.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import costs  # noqa: E402

WARN_AT = 0.8


def unlogged_pm_cost(folder, payload):
    """The PM's work since the last activity line, not in activity.md yet."""
    path = payload.get("transcript_path")
    if not path or not os.path.isfile(path):
        return 0.0
    try:
        with open(os.path.join(folder, ".activity-state.json"), encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        state = {}
    mark = state.get("pm:" + (payload.get("session_id") or path), "")
    return costs.transcript_cost(path, mark, main=True)[0]


def check(label, spent, limit):
    """('block' | 'warn' | None, plain-words message)."""
    if spent >= limit:
        return "block", (
            "Budget reached for %s: $%.2f of $%.2f (API-equivalent). Don't start or continue an agent. "
            "Stop and ask the user, in plain words: carry on with a top-up (suggest an amount and why), "
            "or stop here. If they approve, add a row to .claude/project/budget.md under Top-ups "
            "(date | %s | amount | approved by the user), then try again." % (label, spent, limit, label))
    if spent >= limit * WARN_AT:
        return "warn", (
            "%s has used $%.2f of its $%.2f budget (%d%%, API-equivalent). Tell the user in your next "
            "report, before it runs out." % (label, spent, limit, spent * 100 / limit))
    return None, ""


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    if payload.get("tool_name") not in ("Agent", "Task", "SendMessage"):
        return 0
    folder = costs.find_project(payload.get("cwd") or os.getcwd())
    if not folder:
        return 0

    tool_input = payload.get("tool_input") or {}
    found = costs.TASK_ID.search(str(tool_input.get("prompt") or tool_input.get("message") or ""))
    story_budget, project_budget, topups = costs.budgets(folder)
    stories, total = costs.logged(os.path.join(folder, "activity.md"))
    pm = unlogged_pm_cost(folder, payload)

    results = []
    if found:
        story = costs.story_of(found.group(0))
        results.append(check("story " + story, stories.get(story, 0.0) + pm, story_budget + topups.get(story, 0.0)))
    if project_budget:
        results.append(check("the project", total + pm, project_budget + topups.get("project", 0.0)))

    blocks = [message for verdict, message in results if verdict == "block"]
    if blocks:
        sys.stderr.write("\n".join(blocks) + "\n")
        return 2
    warnings = [message for verdict, message in results if verdict == "warn"]
    if warnings:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "additionalContext": " ".join(warnings)}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
