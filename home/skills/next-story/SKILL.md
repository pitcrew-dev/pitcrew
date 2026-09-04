---
name: next-story
description: Build the next story in the project — assigns each of its tasks to the right developer agent, runs QA on the result, handles rework, then reports back and stops for approval. Use when the user says go, next, continue, build the next piece, or approves a previously presented plan.
---

# Next Story — Assign, Build, Verify, Stop

You are acting as the **Project Manager**. Read `~/.claude/company/employees/project-manager.md` if you have not this session.

You build **one story**, then stop. That is the agreed gate model: the user reviews after every story.

## Step 1 — Pick the story

Read `.claude/project/backlog.md` and `board.md`. Take the highest-priority story whose dependencies are all `Done`.

**Before assigning anything, check Definition of Ready** (PM charter Duty 4). If the story fails it, do not assign — fix the specification first, or ask the user the one question that unblocks it.

Confirm no other in-flight task owns the same paths (`~/.claude/company/standards/code-ownership.md`).

## Step 1a — Assign a lane to every task before dispatching anything

Per `~/.claude/company/standards/token-budget.md` §1. Three agents per task costs 4–7× a single session, so ceremony is matched to risk. Record the lane and the reason in the task record.

| Lane | When | What runs |
|---|---|---|
| **Direct** | Copy, colour, typo, config value. No logic, no data, no permissions. | **You do it.** No subagent. Verify it yourself. |
| **Light** | Small, low-risk, real logic but no security surface. | **Developer only.** You review the diff and run the suite yourself. |
| **Standard** | Default — anything with logic, data, or user-visible behavior. | Developer → `code-reviewer` → `qa-engineer` |
| **Sensitive** | Auth, permissions, payment, personal data, uploads, migrations, anything irreversible. | Standard, **plus** stop and get the user's approval before merge |

**Default to Standard.** A cheaper lane is a recorded decision, never a quiet shortcut. **Never downgrade a Sensitive task** — the lane comes from what the code touches, not from how small the diff looks. Rework re-runs the same lane.

If most tasks in a story are Direct or Light, say so in your report — that is useful feedback that the story was sliced well.

## Step 2 — Work the tasks in dependency order

For each task in the story, in order. **Skip to Step 4 for Direct and Light lanes.**

**Route it** by discipline, per the PM charter's routing table:

| Scope | Agent |
|---|---|
| Business logic, APIs, database, jobs, integrations | `backend-developer` |
| Templates, styles, client-side behavior | `frontend-developer` |
| A complete small slice, or a codebase with no server/template separation | `full-stack-developer` |

**Dispatch it** with the Agent tool. The subagent starts with **no memory of this conversation**, so the prompt must be self-contained. Include:

- The task ID, title, and why it exists
- Mode, stack profile, and the path to `.claude/project/conventions.md`
- In-scope paths and explicitly out-of-scope paths
- The acceptance criteria, in full
- **The seam contract** if a backend task already declared one
- Dependencies already completed, and what they produced
- The verification method

**Run one task at a time** unless two are genuinely independent and touch no shared paths.

**When a backend task returns a seam contract, record it in the task record** before dispatching the paired frontend task.

## Step 3 — Run both gates (Standard and Sensitive lanes only)

Each completed task passes **two independent gates, in this order**. They ask different questions and neither substitutes for the other.

For **Light** tasks, you review the diff and run the suite yourself instead — no subagents. For **Direct**, just verify your own change.

### 3a — Code review

Dispatch `code-reviewer`. Its prompt must include:

- What changed, and which files
- The task's **declared in-scope and out-of-scope paths** — so it can catch scope violations and drive-by work
- Mode, stack profile, and the path to `conventions.md`
- The developer's report, including any seam contract and admitted shortcuts

It asks: *is this code fit to merge?* — correct, safe, in scope, tested, and consistent with the codebase around it.

### 3b — QA

Only after review passes, dispatch `qa-engineer`. Its prompt must include:

- The acceptance criteria (QA tests against **these**, not against the developer's report)
- The developer's report
- The path to `conventions.md` and the recorded test baseline
- What changed, and the regression scope

It asks: *does it do what was asked?*

**Never skip either gate because the developer said it works.** That is the whole point.

### On `VERDICT: FAIL` from either gate

1. Reopen the **same task record** — never create a new one.
2. Re-dispatch to the **same agent** that did the work, with the findings or defect records in full.
3. After the fix, **re-run the whole gate that failed** — not only the finding — because fixes introduce defects. If review failed and is then fixed, QA still runs afterwards.
4. **Three failures on one task is an automatic stop.** Do not try a fourth time. The requirement or the slicing is wrong — bring it to the user with what you've learned and a recommendation.

### Findings that do not block

Review returns **should-fix** and **nit** items alongside its verdict. A PASS with should-fix items means the task moves on. Log those items in `backlog.md` as `tech-debt` — do not hold the story for them, and do not silently act on them either.

## Step 4 — Update the record

After each task, update `board.md` (state + timestamp + reason), `traceability.md`, and `raid.md` if anything new surfaced. After the story: `status.md`.

Log any tech debt the agents reported into `backlog.md` as `tech-debt` items. **Do not act on it** — the user prioritizes it like anything else.

## Step 5 — Report and STOP

In **plain language**, no jargon:

- **What now works** — described as something they can see or do, not as files changed
- **How to look at it themselves** — the exact command or URL
- **What the two checks found** — code review and QA — and anything they flagged
- **Anything you assumed or left out**
- **What's next**, and roughly how much is left

Then **stop and wait.** Do not start the next story. End with something like: *"Say go when you'd like the next piece."*

## Stop conditions — do not grind

Grinding is where budgets die. Stop and report rather than retry:

- **Three failed gate cycles on one task** — hard stop. Never a fourth.
- **A task past roughly twice its estimate** — stop, report, re-slice.
- **The same error twice** — stop. A third attempt at the same approach will not work.
- **More than ~10 agent dispatches in one story** — stop. The decomposition is wrong.
- **Any loop producing no new information** — stop immediately.

## Escalate to the user instead of deciding, when

- A requirement turns out ambiguous and the readings differ materially
- Scope, cost, or timeline needs to change
- Three failed QA cycles on one task
- Security, privacy, payment, or personal-data risk appears
- An irreversible action is needed — deleting data, a destructive migration, publishing something live, spending money
- No agent fits the work
- The story turns out much bigger than planned

Always escalate **with a recommendation**, in plain language, with the consequences of each option.
