#!/usr/bin/env python3
"""Cost summary for /company:status and /company:report.

Not a hook: the PM runs it through the launcher, so the numbers it reports
are added up by code, not by the model:

    sh "${CLAUDE_PLUGIN_ROOT}/hooks/run" cost_summary [--since YYYY-MM-DD]

Reads .claude/project/activity.md and budget.md from the current folder or
a parent, and prints spent against budget per story and for the project.
With --since it also prints what was spent from that date on, for a report.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import costs  # noqa: E402


def percent(spent, limit):
    return " (%d%%)" % (spent * 100 / limit) if limit else ""


def summary(folder, since=""):
    log_path = os.path.join(folder, "activity.md")
    stories, total = costs.logged(log_path)
    story_budget, project_budget, topups = costs.budgets(folder)
    runs, last = 0, "-"
    try:
        with open(log_path, encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("| 20"):
                    runs, last = runs + 1, line.split("|")[1].strip()
    except OSError:
        pass

    lines = ["Costs are API-equivalent dollars.", "Budget per story: $%.2f" % story_budget]
    if project_budget:
        limit = project_budget + topups.get("project", 0.0)
        lines.append("Project: $%.2f spent of $%.2f%s, $%.2f left"
                     % (total, limit, percent(total, limit), max(limit - total, 0.0)))
    else:
        lines.append("Project: $%.2f spent, no project cap" % total)
    if not runs:
        lines.append("No agent runs logged yet.")
        return "\n".join(lines)
    lines.append("Agent runs: %d, last at %s" % (runs, last))
    lines.append("Per story:")
    for story in sorted(stories):
        limit = story_budget + topups.get(story, 0.0)
        extra = ", top-ups $%.2f" % topups[story] if story in topups else ""
        lines.append("  %s  $%.2f of $%.2f%s%s" % (story, stories[story], limit, percent(stories[story], limit), extra))
    untied = total - sum(stories.values())
    if untied >= 0.005:
        lines.append("Not tied to a story: $%.2f" % untied)
    if since:
        period, period_total = costs.logged(log_path, since)
        lines.append("Since %s: $%.2f in total" % (since, period_total))
        for story in sorted(period):
            lines.append("  %s  $%.2f" % (story, period[story]))
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    since = args[1] if len(args) == 2 and args[0] == "--since" else ""
    folder = costs.find_project(os.getcwd())
    if not folder:
        print("No .claude/project folder here or in a parent folder.")
        return 0
    sys.stdout.reconfigure(encoding="utf-8")
    print(summary(folder, since))
    return 0


if __name__ == "__main__":
    sys.exit(main())
