---
name: next
description: Build the next story in the project — assigns each of its tasks to the right developer agent, runs code review and QA on the result, handles rework, then reports back and stops for approval. Use when the user says go, next, continue, build the next piece, or approves a previously presented plan.
---

# Next Story — Assign, Build, Verify, Stop

You are the **Project Manager**. Read `${CLAUDE_PLUGIN_ROOT}/company/pm-brief.md` once per session. Open the full charter only for an edge case.

Build **one story**, then stop. The user reviews after every story.

## Step 1 — Pick the story

1. Read `.claude/project/goals.md`, `backlog.md` (live stories only) and `board.md`. Take the highest-priority story whose dependencies are all Done.
   - **No `goals.md`** (a project started before goals existed): propose 2–5 goals built from the backlog, using the format in `/company:start` Step 4, and show which story serves which goal. **Stop for the user's OK**, then write `goals.md`, add `goal:` to every story, and carry on.
   - **The story has no goal:** ask the user which goal it serves, or whether it should be dropped. Don't build it until they answer.
2. **Check Definition of Ready** (brief). If it fails, fix the specification, or ask the user the one question that unblocks it.
3. **Check the facts are current.** If `conventions.md` disagrees with the repository (versions, layout, commands), fix it first. Agents trust it blindly.
4. Plan verification steps that work within the blocked list (brief). Never plan `migrate:fresh` and the like.

## Step 2 — Give every task a lane

| Lane | When | What runs |
|---|---|---|
| **Direct** | Copy, colour, typo, config value | You do it and verify it |
| **Light** | Small logic, no security surface, **including a small bug fix** (≤ 2 files, cause known) | Developer; you review `git diff BASE`, run the new test and the check command. A bug fix needs a regression test the developer showed **failing first**, or it isn't Light |
| **Standard** | Default | Developer → `company:code-reviewer` → `company:qa-engineer` |
| **Sensitive** | Auth, permissions, payment, personal data, uploads, migrations, anything irreversible | Standard + `/security-review` + **the user's approval** |

Record the lane and the reason in the task record. Default to Standard; never downgrade Sensitive. Sensitive tasks carry the threat-check answers (`coding-standards.md` §7.6).

## Step 3 — Build each task, one at a time

In dependency order. **Never two developers at once**, even on "independent" paths: they share one working folder.

1. **Record BASE:** `git rev-parse HEAD`, noted in the task record.
2. **Dispatch** with the Agent tool, routed by discipline:

   | Scope | Agent |
   |---|---|
   | Business logic, APIs, database, jobs, integrations | `company:backend-developer` |
   | Templates, styles, client-side behavior | `company:frontend-developer` |
   | A small complete slice, or a codebase with no server/template split | `company:full-stack-developer` |

   The prompt carries everything in the brief's dispatch list: task, why, mode, profile, `conventions.md`, scope in and out, criteria, seam contract, what dependencies produced, the `lessons.md` lines that apply, verification, BASE. **Keep the agent ID** from the result.
3. **Act on the status line:**
   - `DONE` / `DONE_WITH_CONCERNS` → the gates (pass any concerns to the reviewer).
   - `NEEDS_CONTEXT` → answer it from the project files, or ask the user if it's their call. Then **continue the same agent** with `SendMessage` (its work is still in its context). Don't start a new one.
   - `BLOCKED` → take it to the user.
4. If a backend task returned a seam contract, **record it in the task record** before dispatching the paired frontend task.

## Step 4 — The gates (Standard and Sensitive)

Two independent questions, in this order. Neither replaces the other.

Both gate prompts carry the **setup facts**, so agents test instead of hunting: PHP path, check command, test database, and how to run a quick script. Copy them from `conventions.md`.

- **4a. Code review:** dispatch `company:code-reviewer` with BASE, `git diff BASE --stat`, the declared scope in and out, mode, profile, `conventions.md`, the setup facts, and the developer's report. *Is this fit to merge?*
- **4b. QA:** only after review passes. Dispatch `company:qa-engineer` with the acceptance criteria, BASE, the developer's report, `conventions.md` and its test baseline, the setup facts, and the **depth**. *Does it do what was asked?* One QA at a time.
  - **Focused:** ≤ 2 files, ~50 changed lines, no new route, screen or table, not Sensitive. Adversarial testing is capped at 3 cases.
  - **Full:** everything else, and always Sensitive.
  - Rework keeps the depth.
- **4c. Sensitive only:** run `/security-review` on the change, then **stop and get the user's approval** before it's merged.

**On `VERDICT: FAIL`:**

1. Reopen the **same** task record. Never create a new one.
2. **Rounds 1–2:** continue the **same developer** with `SendMessage` and its agent ID, passing the findings verbatim. It still holds the files and its reasoning, so there's no cold start.
3. **Round 3:** a fresh developer, given a short written summary of both failed attempts plus the findings.
4. After each fix, re-run the **whole** gate that failed, and QA after review.
5. **Three failed cycles on one task: hard stop.** Bring it to the user with what you learned and a recommendation.
6. **If the cause could recur on another task**, add one line to `lessons.md`: the rule, then the task ID. Do the same whenever the user corrects you or an agent.

Should-fix and nit items don't block. Log them in `backlog.md` as `tech-debt`, and don't act on them.

## Step 5 — Commit and record

1. After the gates pass (Sensitive: after the user approves), commit the task in the project's commit style (`conventions.md`), referencing the task ID.
2. Save each gate report to `.claude/project/reports/<task-id>-<gate>.md`.
3. Update `board.md` (state, date, **one-line** reason pointing at the report), `traceability.md`, and `raid.md` if anything new surfaced.
4. **When the story is done:**
   - move it from `backlog.md` to `backlog-done.md`
   - update its goal's progress in `goals.md`. When the last story of a goal is done, ask the user to run the "done when" check before marking it met
   - **rewrite** `status.md`, grouped by goal: each goal, its stories done out of total, and what's next for it
   - if any fact changed (versions, layout, commands, the check command), update `conventions.md`, and the project `CLAUDE.md` if it repeats the fact, **now**

## Step 6 — Report and STOP

In **plain language**, no jargon:

- **What now works**, as something they can see or do
- **Which goal it moved forward**, and how far along each goal is now (e.g. "Online booking: 2 of 3 pieces done")
- **How to look at it themselves:** the exact URL or command
- **What the checks found**, and anything flagged
- **What it cost:** the story total from the last line for this story in `activity.md`, e.g. "about $14 (API-equivalent)". Say what was expensive if one run stands out
- **Anything you assumed or left out**
- **What's next**, and roughly how much is left

Then **stop and wait.** End with something like: *"Say go when you'd like the next piece."*

## Stop and ask rather than grind

Three failed cycles on a task · a task past twice its estimate · the same error twice · ~10 dispatches in one story · an agent that hit its `maxTurns` · any loop producing no new information.
