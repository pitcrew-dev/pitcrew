# News project (`C:\laragon\www\news`) — `.claude` review

**Date:** 2026-09-15 · **Project:** Pakistan Verified News (Laravel 12, greenfield, Profile A) · **Status:** report only — nothing changed.

**What I read:** `CLAUDE.md`, all of `.claude/project/` (conventions, backlog, board, status, decisions, RAID, traceability, requirements, 7 QA reports, feed spike), `.claude/memory/`, `composer.json`, git history (14 commits).

---

## 1. Short answer

This is the **first real run** of the vibe_coding system, and it **mostly works**. The gates caught real problems, the safety hook stopped a dangerous command, and the records are clear enough that a new session can pick up the project cold.

The weak spots are: **files going stale** (some describe the project as it was before any code existed), **parallel tasks tripping over each other**, **QA can't see the page** (no browser), **no automatic code checkers**, and **the planning files are getting expensive** to read on every story.

---

## 2. What's good — with evidence

| # | Good | Evidence |
|---|---|---|
| G1 | **Review catches real problems** | Review failed twice for real reasons: a drive-by change to a shared style (`.page-title`, E01-S02-T02) and a first-pass defect (E01-S02-T01). It also spotted that a `javascript:` link could be saved as a source URL (R14) — a real security hole, logged before it could ship. |
| G2 | **"Verify, don't trust" works** | A developer claimed a manual check ("13 articles / OGRA") that wasn't true. The PM checked the database and caught it; review and QA re-checked on their own (`status.md`). |
| G3 | **The safety hook did its job** | Blocked `migrate:fresh` on MySQL; the developer didn't try to get around it (board, E02-S02-T01). `.env` writes are blocked, so you set real secrets yourself (ISS02). |
| G4 | **Risky work waits for you** | Every migration (Sensitive lane) was merged only after your approval (E01-S01-T02, E02-S02-T01). |
| G5 | **Biggest unknown checked first** | The feed check (spike) ran before any code and found OGRA/SBP/PSX have no RSS. You chose the fix (D14) before stories were built on a wrong assumption. |
| G6 | **Clear decision trail** | `decisions.md` records every choice with the reason and **who decided** (you vs PM). `raid.md` tracks risks with owners. Every commit names its task ID. |
| G7 | **Real versions, not guesses** | `conventions.md` records that the CLI runs PHP 8.2 but the Laragon web server runs 8.3, and fixes the ceiling at 8.2. That's exactly what the survey is for. |
| G8 | **SQLite-vs-MySQL risk caught a real bug** | Tests run on SQLite, but QA also checks MySQL (R08). It found MySQL rejects URLs over 500 characters while SQLite doesn't (E02-S02-T01). |
| G9 | **Existing problems reported, not fixed on the side** | Laravel's default "Test User" with password `password` in `DatabaseSeeder` was logged as a risk (R15), not quietly edited. Correct by the rules. |
| G10 | **Product rules written as hard rules** | `CLAUDE.md` "Invariants code must never violate" (one source never publishes, no confidence %, etc.) — clear, testable, and used as pass/fail checks. |
| G11 | **Lanes used sensibly** | Direct for a colour-contrast fix (D03), Light for scaffold and spike, Sensitive for migrations and auth. A story took 7 dispatches — under the 10 limit. |
| G12 | **QA is thorough and honest** | Each report lists what was **not** tested and why. QA tries edge cases beyond the checklist. |

---

## 3. What's bad — with evidence

### Files that are out of date (the most urgent)

| # | Problem | Evidence | Why it matters |
|---|---|---|---|
| B1 | **`CLAUDE.md` describes the project before any code existed** | Says "Pre-code. Laravel is not scaffolded yet and the folder is not a git repository" and "Commands (once scaffolded)". There have been 14 commits since. | This file loads in **every** session. Every session starts with wrong facts. |
| B2 | **`conventions.md` is also out of date** | Says "Laravel not installed yet" and "The tree doesn't exist yet". Laravel 12.69.2 and Pest 3.8.7 are installed (board, T01). | This is the file that **outranks the company rules**. Agents read it first. |
| B3 | **`status.md` is behind the board** | Says 7 tasks done and 63 tests; the board shows 10 done and 78 tests. It still lists "Waiting on sponsor: The News feed, `.idea` folder" — both already decided (D15a, D18). | Your summary view is wrong. |
| B4 | **Board rows contradict themselves** | E02-S02-T01 says both "Sponsor approved merge" and "Merge needs the sponsor's approval". E01-S02-T02 is "Done" but ends with "Waiting on QA". | Old text is left in when a row is updated. |

**Root cause (system-level):** nothing in `/next-story` says "refresh `CLAUDE.md` and `conventions.md` when the facts change" (e.g. after the scaffold task). Only the board and status get updated, and even those keep old text.

### How tasks run

| # | Problem | Evidence | Fix |
|---|---|---|---|
| B5 | **Parallel tasks share one working folder** | E02-S02-T01 and T02 ran "alongside". Each QA run found the other's temporary test file in `tests/Feature/` (`QaProbeRawItemTest.php`, `QaProbeSourceSeederT02Test.php`). One made `pint --test` fail during the other's QA. | Don't run QA in parallel on the same folder, or give each agent its own copy (`isolation: worktree` in the agent settings). |
| B6 | **QA writes temporary tests into the real test folder** | Every QA report creates `tests/Feature/QaProbe*.php`, then deletes it. | One missed delete and a junk test gets committed. Put probes in an ignored folder, e.g. `tests/QaProbe/` in `.gitignore`. |
| B7 | **QA can't see the page** | "No browser available to me" in the QA reports. The 375px check is done by the PM in Chrome, using 375px iframes (`status.md`). | The "check it at phone size" criterion is passed on reading the code, not on seeing it. Give QA a browser tool, or make the PM's browser check an official, recorded step. |
| B8 | **The plan asked for a command the safety hook blocks** | Backlog E01-S01-T02 verification: "`php artisan migrate:fresh --seed` works on local MySQL". The hook blocks `migrate:fresh`. | The PM writes plans without knowing the blocked list. Wastes a turn and tempts a workaround. The PM brief should include the blocked commands. |

### Quality and security

| # | Problem | Evidence | Fix |
|---|---|---|---|
| B9 | **No automatic code checkers** | `composer.json` dev tools: Pint + Pest only. No Larastan/PHPStan, no architecture tests, no `composer audit`. | New projects are the **cheapest** time to add them — there's no old code to create a baseline for. |
| B10 | **Server-side URL fetching risk not logged** (SSRF, OWASP 2025 A01) | `news:fetch` downloads whatever `feed_url` says, and the admin sources screen (E03-S03) will let someone edit it. Nothing stops `http://localhost/...` or internal addresses. | Add to RAID: only public `http`/`https` hosts, block private IP ranges. Attach to E02-S02-T03 and E03-S03-T01 (the same way R14 was handled). |
| B11 | **AI prompt injection not logged** | Feed text goes straight into the Anthropic prompt (E02-S05). An item could contain "ignore your rules and…". R03 covers copying, not this. Official items auto-publish (Tier A) with no human check. | Add a risk: feed text is data, never instructions. The structured output check and the "one source never publishes" gate should hold whatever the model says. Add a test with an injection-style feed item. |
| B12 | **Malformed-XML handling is tested, hostile XML isn't** | AC5 covers malformed XML only. | Confirm the feed parser doesn't load external entities (XXE). PHP 8 + libxml 2.9 is safe by default — one test proves it stays that way. |
| B13 | **Default Test User still in the seeder** (R15) | Reported correctly, still open. | Must be removed before the auth story (E03-S01) — it's a login with a known password. |

### Token cost

Estimated as characters ÷ 4.

| File | Size | When it's read | Problem |
|---|---|---|---|
| `backlog.md` | **~10k tokens** (459 lines) | Every `/next-story` | Done stories stay in full detail. Grows every story. |
| `board.md` | ~1.8k | Every story | "Reason" cells are whole paragraphs; the detail already lives in the QA reports. |
| QA reports | 1.6k–4.3k **each** | Written every task | Long narrative. Good for trust, heavy on output tokens. |
| `CLAUDE.md` + `conventions.md` | ~1.1k + ~1.2k | Every session / every agent | Commands and rules repeated in both, and the copies have already drifted (B1, B2). |

**Cheap fixes:** move finished stories to `backlog-done.md`; keep board reasons to one line pointing to the report; cap QA reports (one line per criterion plus defects only); keep commands in `conventions.md` only, and have `CLAUDE.md` point to it.

### Small things

- `decisions.md` IDs are out of order (D14 before D13, D21 before D20). Append in order.
- The project has **no `.claude/settings.json`**. A project hook would suit one rule perfectly: *"never point tests at the `pvn` database — `RefreshDatabase` wipes it"* (conventions §1). Right now that's only a sentence. A hook makes it impossible.
- Memory lives in `.claude/memory/` through a Windows junction. It works, but breaks if the project is moved or re-cloned. The memory note explains how to rebuild it.

---

## 4. Where each fix belongs

| Fix | In the news project | In vibe_coding (the system) |
|---|---|---|
| Refresh `CLAUDE.md`, `conventions.md`, `status.md`; clean board rows (B1–B4) | ✅ now, Direct lane | ✅ add "refresh facts when they change" to `/next-story` Step 4 |
| Parallel QA / probe files (B5, B6) | — | ✅ agent `isolation: worktree` or "no parallel QA"; probe folder rule in the QA brief |
| QA browser (B7) | — | ✅ browser tool for QA, or a formal PM browser-check step |
| Blocked commands in plans (B8) | ✅ fix backlog line 62 | ✅ PM brief lists the blocked commands |
| Larastan + arch tests + audit (B9) | ✅ one Light task | ✅ part of the greenfield scaffold task by default |
| SSRF, prompt injection, XXE risks (B10–B12) | ✅ add to RAID + acceptance of upcoming tasks | ✅ add to the security checklist (maturity report §4.3) |
| Remove Test User (B13) | ✅ before E03-S01 | — |
| Token trims | ✅ archive backlog, shorten board | ✅ put the size rules in the PM brief |
| `pvn` DB guard hook | ✅ project `.claude/settings.json` | — |

---

## 5. Recommended next step

1. **Before the next story:** refresh the four stale files (B1–B4), fix backlog line 62, and add the SSRF + prompt-injection risks to RAID. All Direct lane (the PM does it, no agents), ~1 session.
2. **In vibe_coding:** fold B5–B8 into Phase 1 of the maturity report — they're proven by this pilot, not guesses.
3. **Next Light task in news:** add Larastan + architecture tests while the code is still small.

---

## 6. Limits of this review

- I read QA reports and plans; I didn't re-run the test suite or open the site.
- Token sizes are estimates, not measured with `/cost`.
- E02-S02-T03 (`news:fetch`) is in progress (untracked files in `app/Services`, `app/Console`, `tests/`), so I didn't judge that code.
