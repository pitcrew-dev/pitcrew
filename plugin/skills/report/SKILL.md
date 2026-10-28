---
name: report
description: Write a progress report the user can send to a client or manager — what was done, what it cost, risks, and what's next — and save it under .claude/project/reports/. Use when the user asks for a report, an update, a weekly summary, or something to send.
---

# Report — Something to Send

You are the **Project Manager**. Start no agent and change no file except the report.

## Step 1 — Gather

1. Find `.claude/project/`. If there is none, say so and offer `/company:start`. Stop.
2. **The period:** what the user asked for, else since the last `reports/report-*.md`, else the whole project. Say which.
3. Run the cost summary with the period's first day (leave `--since` out for the whole project). Use its numbers exactly; never add up costs yourself:

   ```bash
   sh "${CLAUDE_PLUGIN_ROOT}/hooks/run" cost_summary --since <YYYY-MM-DD>
   ```

   If it can't run, quote each story's latest `Story total $` from `activity.md` instead, and say the period's total couldn't be worked out.
4. Read `plan.md` (goals, `## Done` for the stories finished in the period, live pieces) and `decisions.md` (entries in the period, and `## Risks`). An old project has no `plan.md`: read whichever of `goals.md`, `backlog-done.md`, `status.md`, `backlog.md` and `raid.md` exist instead. Don't open code or gate reports.

## Step 2 — Write it

The reader is a client or manager who has never seen the project files: **plain words**, no task IDs, no file names, no jargon. About one page.

```markdown
# <Project name>: progress report, <period>

## In short
Two or three sentences: where it stands against the goals.

## Done
- What someone can now see or do, one line each, grouped by goal

## Goals
| Goal | Progress |
|---|---|

## Cost
Spent this period and in total, against the budget, in API-equivalent dollars:
what the same AI work would cost at Anthropic's API prices.

## Risks and open questions
- Each with what's being done about it, or what's needed from whom

## Next
- The next pieces, in order, and roughly how much is left
```

Leave out a section with nothing in it. Report a slipping goal or an overspend plainly; no spin.

## Step 3 — Save and show

1. Save it as `.claude/project/reports/report-<YYYY-MM-DD>.md`, adding `-2`, `-3`, … if one already exists for that day.
2. Show the report, then one line: where it's saved, and that it's ready to send. **Never send it anywhere yourself.**
