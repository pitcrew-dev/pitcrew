#!/usr/bin/env python3
"""SubagentStop hook: one line in .claude/project/activity.md per agent run.

Written by a hook, not left to the AI, so the log is complete and the
numbers are measured. Each line has:

  * when the agent finished
  * the task ID, read from the PM's latest instruction (e.g. PVN-E01-S02-T01)
  * the agent type
  * its result line (STATUS: ... or VERDICT: ...)
  * the agent's cost, and the PM's cost since the previous line
  * the story's running total, so the PM can report it without adding up

Costs are API-equivalent dollars (costs.py). A follow-up message to the
same agent is a new line with only the new cost: .activity-state.json in
the project folder remembers what has been counted.

Silent when there is no project. Fails OPEN on any internal error.
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import costs  # noqa: E402

LOG = "activity.md"
STATE = ".activity-state.json"
HEADER = ("# Activity log\n\n"
          "One line per agent run, written by a hook. Append only: never edit it.\n"
          "Costs are API-equivalent dollars: what the same work would cost at Anthropic's API prices.\n\n"
          "| Time | Task | Agent | Result | Agent $ | PM $ | Story total $ |\n"
          "|---|---|---|---|---|---|---|\n")
TASK_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:-E\d+)?-(?:S\d+(?:-T\d+)?|D\d+)\b")
RESULT = re.compile(r"\b(?:VERDICT|STATUS):\s*([A-Z_]+)")


def find_project(start):
    current = os.path.abspath(start)
    while True:
        folder = os.path.join(current, ".claude", "project")
        if os.path.isdir(folder):
            return folder
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def text_of(content):
    """Plain text of a message, plus the report an agent hands back."""
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif block.get("type") == "tool_use" and block.get("name") == "SubagentHandback":
            parts.append(str((block.get("input") or {}).get("message", "")))
    return "\n".join(parts)


def read_agent(path):
    """(task ID, result) of the agent's latest run.

    One agent can be sent several tasks in a row, so the task is the one in
    the latest instruction that names a task, and the result is the latest
    result line.
    """
    task, result = "-", "-"
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            text = text_of((entry.get("message") or {}).get("content"))
            if entry.get("type") == "user":
                found = TASK_ID.search(text)
                task = found.group(0) if found else task
            elif entry.get("type") == "assistant":
                found = RESULT.findall(text)
                result = found[-1] if found else result
    return task, result


def agent_type(payload, path):
    if payload.get("agent_type"):
        return payload["agent_type"]
    try:
        with open(path[:-len(".jsonl")] + ".meta.json", encoding="utf-8") as handle:
            return json.load(handle).get("agentType") or "agent"
    except (OSError, ValueError):
        return "agent"


def story_of(task):
    return re.sub(r"-T\d+$", "", task)


def story_total(log_path, story):
    """Sum of agent and PM costs already logged for this story."""
    total = 0.0
    try:
        with open(log_path, encoding="utf-8") as handle:
            for line in handle:
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if len(cells) == 7 and cells[1] != "Task" and story_of(cells[1]) == story:
                    try:
                        total += float(cells[4]) + float(cells[5])
                    except ValueError:
                        pass
    except OSError:
        pass
    return total


def load_state(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    folder = find_project(payload.get("cwd") or os.getcwd())
    agent_path = payload.get("agent_transcript_path")
    if not folder or not agent_path or not os.path.isfile(agent_path):
        return 0

    state_path = os.path.join(folder, STATE)
    state = load_state(state_path)

    agent_key = "agent:" + (payload.get("agent_id") or agent_path)
    agent_cost, state[agent_key] = costs.transcript_cost(agent_path, state.get(agent_key, ""))

    pm_cost = 0.0
    main_path = payload.get("transcript_path")
    if main_path and os.path.isfile(main_path):
        pm_key = "pm:" + (payload.get("session_id") or main_path)
        pm_cost, state[pm_key] = costs.transcript_cost(main_path, state.get(pm_key, ""), main=True)

    task, result = read_agent(agent_path)
    log_path = os.path.join(folder, LOG)
    total = (story_total(log_path, story_of(task)) if task != "-" else 0.0) + agent_cost + pm_cost

    when = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    row = "| %s | %s | %s | %s | %.2f | %.2f | %s |\n" % (
        when, task, agent_type(payload, agent_path), result,
        agent_cost, pm_cost, "%.2f" % total if task != "-" else "-")

    new = not os.path.isfile(log_path)
    with open(log_path, "a", encoding="utf-8", newline="\n") as handle:
        if new:
            handle.write(HEADER)
        handle.write(row)
    with open(state_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(state, handle, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
