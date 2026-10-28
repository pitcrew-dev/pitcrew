# Plan: the free version (Quick mode)

**Status:** Steps 1–6 done, 7 in progress · **Date:** 2026-10-28 · **From:** 0.9.0 → **1.0.0**

## 1. The goal in one line

Keep the safety and the "plan, then build one piece, then stop" flow, but cut the AI work so one piece costs **about $5–8 instead of about $17**.

## 2. Why

- The most-used plugins are small: Superpowers has a cheap mode with one review at the end; claude-code-safety-net is one hook; Anthropic's feature-dev is one command.
- Today every task runs 3 agents (developer, reviewer, QA), and the PM reads up to 11 project files per piece. That is where the money goes.
- Claude Code already has `/rewind` (undo), so we don't build one.

## 3. What changes, in short

| Area | Today | Free version |
|---|---|---|
| Mode | One way of working | **Quick** (default) or **Careful** (today's full flow), one setting |
| Normal piece of work (Quick) | Developer → reviewer → QA, **per task** | Developer per task, the PM checks each change, then **one QA at the end of the piece** |
| Risky work (logins, payments, personal data, database changes, going live) | Full flow + security review + user OK | **Unchanged.** Always the full flow, in both modes |
| Project files | 11 | **6:** `plan.md`, `conventions.md`, `decisions.md`, plus the small ones hooks use (`lessons.md`, `budget.md`, `activity.md`) |
| Start interview | 6–10 questions | **3–5**, each with a default |
| Three design options | Always for a new site | **Only when asked** |
| Developer chosen | Backend / frontend / full-stack | **Full-stack by default**; split only for big pieces |
| Bug fixes | Need a plan first | **`/company:fix`**: one command, no plan |
| Empty folder | Breaks without git | **Sets up git** and a safe `.gitignore` first |
| Undo | Not mentioned | Reports mention `/rewind`, and every task is its own commit |

**Not in this version:** JavaScript and other stacks, browser testing, more agents or roles, an undo command.

## 4. The steps

Each step ends with the tests passing. One step at a time; I stop after each for your OK.

### Step 1 — The Quick / Careful setting

- Add a setting `careful_mode` (on/off, **off** by default) to `plugin.json`.
- A project can override it with one line in `budget.md`: `Mode: careful`.
- The session-start hook tells the PM which mode is on.
- Tests for both.

**Done when:** a new session says "Quick mode" by default, and "Careful mode" when the setting or the project line says so.

### Step 2 — Fewer project files

- New `plan.md` holds what 8 files held before. At the top: **Now** (where we are). Then the request in the user's words, the goals, the pieces with their tasks and checks, and done pieces as one line each.
- `decisions.md` also holds risks.
- Update `/company:start`, `/company:next`, `/company:status`, `/company:report`, the PM brief and the PM charter to use them.
- The after-compact hook reloads `plan.md` (its top part) and `lessons.md` instead of `status.md`. Test updated.
- **Old projects** (the 11-file layout): on the first `/company:next`, the PM offers to merge them into `plan.md`, and does it only after a yes. Old files are left in place, never deleted.
- Update the salon example project and the eval setups.

**Done when:** `/company:status` and `/company:report` work on the updated salon example, and an old-layout project gets the offer.

### Step 3 — The Quick flow in `/company:next`

- Quick: developer per task → the PM checks `git diff`, runs the check command and the new test → after the last task, **one QA** checks the whole piece against what was asked.
- Careful, and **all risky work in either mode**: today's flow, unchanged.
- The rework rules stay (same agent, three strikes and stop).
- Update the working agreement (stays under 90 lines), the PM brief and `token-budget.md`. A typical piece becomes about $7, and the default piece budget goes from $25 to **$12**.

**Done when:** a Quick piece on the salon example runs 1 developer + 1 QA, and a login piece still runs the full flow.

### Step 4 — A lighter `/company:start`

- 3–5 questions, each with a default.
- Design options only when the user asks for them.
- In a folder without git: write a `.gitignore` that keeps out `.env`, `vendor/` and `node_modules/`, run `git init`, and make a first commit. If code already exists, ask first.

**Done when:** start on an empty folder asks 5 questions or fewer and leaves a git repo with no `.env` in it.

### Step 5 — `/company:fix`

- One command: "the booking form gives an error" → the PM finds the cause → one developer writes a test that fails, fixes it, and the test passes → the PM checks the change → one commit.
- Works without a plan or project files.
- If the fix touches logins, payments, personal data or the database, it stops and switches to the full flow.
- Logged and budgeted like any task (IDs `FIX-001`, `FIX-002`, …).

**Done when:** a planted bug in the salon example is fixed with one developer run, a test, and a commit.

### Step 6 — Words and version

- README: Quick vs Careful, `/company:fix`, `/rewind`, new cost figures.
- `CHANGELOG.md` entry, `VERSION` and `plugin.json` to 1.0.0.

### Step 7 — Test and measure

- All unit tests pass, and `claude plugin validate ./plugin --strict` is clean.
- Run the evals once (start, next in Quick, fix, status, report) in CI on Linux.
- **Measure one Quick piece on the salon example** and compare it with today's ~$17.

**Done when:** a Quick piece costs **$8 or less**. If it doesn't, I report the real number and why before anything is released.

### Step 8 — Release (needs your OK, it's public)

- Push to GitHub and get CI green on Windows, macOS and Linux.
- A short demo GIF for the README.
- Tag `v1.0.0` and check the install command works.

## 5. Decisions for you (defaults in bold)

| Question | Default |
|---|---|
| Default mode for new users | **Quick** |
| Default budget per piece | **$12** (was $25) |
| Old projects | **Offer to merge, only on a yes, nothing deleted** |
| Version for the free release | **1.0.0** |
| Rename the repo (`vide_coding` looks like a typo) | **Rename to `agent-company`.** Changes the install address, so it's done in Step 8 |

## 6. Cost of building this

Mostly text changes to skills and briefs, plus two small hook changes with tests. Rough guess: **$30–50 of AI work in total**, plus about $10–15 for one eval run and the measurement in Step 7.

## 7. Risks

| Risk | What we do |
|---|---|
| Fewer checks let more bugs through | Risky work keeps the full flow; QA still checks every piece; Careful mode is one setting away |
| Savings are smaller than hoped | Step 7 measures before release, and we report the real number |
| Old projects break | Merge only on a yes; old files kept |
