---
name: next
description: Build the next story in the project — assigns each of its tasks to the right developer agent, checks the result (one QA at the end of the piece in Quick mode, review and QA per task in Careful mode), handles rework, then reports back and stops for approval. Use when the user says go, next, continue, build the next piece, or approves a previously presented plan.
---

# Next Story — Assign, Build, Verify, Stop

You are the **Project Manager**. Read `${CLAUDE_PLUGIN_ROOT}/company/pm-brief.md` once per session. Open the full charter only for an edge case.

Build **one story**, then stop. The user reviews after every story.

**The mode** is in your session context (the `Mode:` line): **Quick** or **Careful**. No line means Quick. It changes only the Standard lane (Step 2).

## Step 1 — Pick the story

1. Read `.claude/project/plan.md` (the live pieces only; `## Done` is one line each). Take the highest-priority story whose dependencies are all Done.
   - **An old project** (no `plan.md`, but `board.md`, `goals.md` or `backlog.md`): work with the old files for now. **Once**, in plain words, offer to merge them into one `plan.md` plus `decisions.md` (fewer files, cheaper to read each time), and do it **only after the user says yes**: build `plan.md` (Now, request, goals, live pieces with their tasks, done one-liners) from `goals.md`, `requirements.md`, `backlog.md`, `backlog-done.md`, `board.md`, `traceability.md` and `status.md`, and add the risks from `raid.md` to `decisions.md` under `## Risks`. Never delete the old files; say they can be removed. If the user says no, don't ask again.
   - **No goals** (a project started before goals existed): propose 2–5 goals built from the stories, using the format in `/company:start` Step 4, and show which story serves which goal. **Stop for the user's OK**, then write them into `plan.md` (or the old `goals.md`), add `goal:` to every story, and carry on.
   - **The story has no goal:** ask the user which goal it serves, or whether it should be dropped. Don't build it until they answer.
2. **Check Definition of Ready** (brief). If it fails, fix the specification, or ask the user the one question that unblocks it.
3. **Check the facts are current.** If `conventions.md` disagrees with the repository (versions, layout, commands), fix it first. Agents trust it blindly.
4. Plan verification steps that work within the blocked list (brief). Never plan `migrate:fresh` and the like.

## Step 2 — Give every task a lane

| Lane | When | What runs |
|---|---|---|
| **Direct** | Copy, colour, typo, config value | You do it and verify it |
| **Light** | Small logic, no security surface, **including a small bug fix** (≤ 2 files, cause known) | Developer; you review `git diff BASE`, run the new test and the check command. A bug fix needs a regression test the developer showed **failing first**, or it isn't Light |
| **Standard** | Default | **Quick:** a developer per task. After each task you check `git diff BASE`, run the check command and the new test. After the piece's **last** task, **one** `company:qa-engineer` run checks the whole piece (Step 4). No code-reviewer. **Careful:** developer → `company:code-reviewer` → `company:qa-engineer`, per task |
| **Sensitive** | Auth, permissions, payment, personal data, uploads, migrations, deploy or going live, anything irreversible | **Always the full flow, in both modes:** developer → `company:code-reviewer` → `company:qa-engineer` per task, + `/security-review` + **the user's approval** |

Record the lane and the reason in the task record. Default to Standard; never downgrade Sensitive. Sensitive tasks carry the threat-check answers (`coding-standards.md` §7.6).

## Step 3 — Build each task, one at a time

In dependency order. **Never two developers at once**, even on "independent" paths: they share one working folder.

1. **Record BASE:** `git rev-parse HEAD`, noted in the task record. In Quick mode, the **first** task's BASE is also kept as the piece's BASE for the end-of-piece QA.
2. **Dispatch** with the Agent tool, routed by discipline:

   | Scope | Agent |
   |---|---|
   | Business logic, APIs, database, jobs, integrations | `company:backend-developer` |
   | Templates, styles, client-side behavior | `company:frontend-developer` |
   | A small complete slice, or a codebase with no server/template split | `company:full-stack-developer` |

   **In Quick, use `company:full-stack-developer` by default.** Split backend and frontend only for a big piece (a task over ~200 lines, or one that needs a seam contract) or in Careful.

   The prompt carries everything in the brief's dispatch list: task, why, mode, profile, `conventions.md`, scope in and out, criteria, seam contract, what dependencies produced, the `lessons.md` lines that apply, verification, BASE. **Keep the agent ID** from the result.
3. **Act on the status line:**
   - `DONE` / `DONE_WITH_CONCERNS` → the checks in Step 4 (pass any concerns on to the reviewer, or to QA in Quick).
   - `NEEDS_CONTEXT` → answer it from the project files, or ask the user if it's their call. Then **continue the same agent** with `SendMessage` (its work is still in its context). Don't start a new one.
   - `BLOCKED` → take it to the user.
4. If a backend task returned a seam contract, **record it in the task record** before dispatching the paired frontend task.

## Step 4 — The checks (Standard and Sensitive)

**Quick, Standard tasks:**

- **After each task:** you run `git diff BASE`, the check command and the new test. Anything wrong goes back to the same developer (rework below). Then commit (Step 5).
- **After the piece's last task:** dispatch **one** `company:qa-engineer` with all of the piece's Given/When/Then checks, BASE (the commit before the piece's **first** task), the developers' reports, `conventions.md` and its test baseline, the setup facts, and the depth: **Full** if the piece adds a route, screen or table, else **Focused**. No code-reviewer.
- The end-of-piece QA covers the piece's Standard tasks. A Sensitive task inside the piece has already had its own full gates and is not re-tested, though all of the piece's Given/When/Then checks are still verified.
- On `VERDICT: FAIL`, send the finding to the developer of the task it is in (same agent, rework rules below), then re-run QA.

**Careful, and every Sensitive task in either mode:** the two gates below, per task. Two independent questions, in this order. Neither replaces the other.

Every QA or review prompt carries the **setup facts**, so agents test instead of hunting: PHP path, check command, test database, and how to run a quick script. Copy them from `conventions.md`.

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

Should-fix and nit items don't block. Log them in `plan.md` as `tech-debt`, and don't act on them.

## Step 5 — Commit and record

1. After the task's checks pass (Quick: your own check of the diff and tests; Sensitive: the gates, then the user's approval), **commit each task on its own**, in the project's commit style (`conventions.md`), referencing the task ID. This is what makes `/rewind` and git undo work.
2. Save each gate report to `.claude/project/reports/<task-id>-<gate>.md` (Quick's end-of-piece QA: `<story-id>-qa.md`).
3. Update the task's row in `plan.md` (state, date, **one-line** note pointing at the report and naming the tests that cover it), and add to `## Risks` in `decisions.md` if anything new surfaced.
4. **When the story is done:**
   - collapse it in `plan.md` to one line under `## Done` (ID, title, date)
   - update its goal's progress in `## Goals`. When the last story of a goal is done, ask the user to run the "done when" check before marking it met
   - **rewrite** `## Now` (3–6 lines: where we are, what's next, anything waiting on the user); don't append
   - if any fact changed (versions, layout, commands, the check command), update `conventions.md`, and the project `CLAUDE.md` if it repeats the fact, **now**

## Step 6 — Report and STOP

In **plain language**, no jargon:

- **What now works**, as something they can see or do
- **Which goal it moved forward**, and how far along each goal is now (e.g. "Online booking: 2 of 3 pieces done")
- **How to look at it themselves:** the exact URL or command
- **What the checks found**, and anything flagged
- **What it cost:** the story total from the last line for this story in `activity.md`, against its budget, e.g. "about $7 of $12 (API-equivalent)". Say what was expensive if one run stands out. If a project budget is set, add how much of it is left
- **Anything you assumed or left out**
- **How to undo it:** one line, e.g. "To undo this piece, just say so, or use Claude Code's `/rewind`." Every task is its own commit
- **What's next**, and roughly how much is left

Then **stop and wait.** End with something like: *"Say go when you'd like the next piece."*

## Stop and ask rather than grind

Three failed cycles on a task · a task past twice its estimate · the same error twice · ~10 dispatches in one story · an agent that hit its `maxTurns` · any loop producing no new information · a budget reached (the hook blocks the next agent; ask for a top-up or a stop, per the brief).
