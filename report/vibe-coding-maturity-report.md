# vibe_coding — Maturity & Gap Report

**Date:** 2026-09-15 · **Scope:** the whole repo (`home/`, `install.sh`, `CLAUDE.md`, `README.md`) plus what is installed in `~/.claude/` · **Status:** report only — nothing has been changed.
**Updated:** 2026-09-15 with evidence from the first real project, the news pilot (see [news-project-claude-review.md](news-project-claude-review.md)). Changed sections: §1, §2, **new §3.4**, §4.1, §4.3, §5, §6, §7, §8.
**Updated again:** 2026-09-15 with ideas from the most-starred AI coding frameworks on GitHub (see [top-frameworks-comparison.md](top-frameworks-comparison.md)). Changed sections: §1, §4.1, §4.2, **new §4.5**, §5, §6, §7, §8, Sources.
**Final review:** 2026-09-15 — read top to bottom, main claims re-checked against the official Claude Code docs. Verdict and changes in **§0**.

---

## 0. Final verdict (after a deep re-check)

**The report is good and ready to act on.** I re-read it top to bottom and re-checked its main claims against the official Claude Code docs. Nothing in it turned out wrong. The re-check made the plan **better and simpler** in 3 places, found **1 new gap**, and fixed 3 small inconsistencies:

| Type | What | Section |
|---|---|---|
| ✅ Better | **Built-in permission rules** (`deny` / `ask` in `settings.json`) do most of what the regex hooks try to do, and do it correctly: they understand `&&` / `;` chains, PowerShell and its aliases, don't false-alarm on quoted text, and check `> file` redirects. Hooks can't override them. Use rules first, hooks only for what rules can't do. | §3.1 |
| ✅ Better | **`claude plugin eval`** is Claude Code's official way to test the framework itself: it runs test prompts with and without it and scores the difference. That fills the "no tests for the system" gap. | §4.4 |
| ✅ Better | **Packaging as a plugin** makes hooks merge instead of overwrite and enables the evals. Plugins can't ship `CLAUDE.md` or permission rules, so a small installer stays. A later phase, not phase 1. | §3.2, §7 |
| ⚠ New gap | **Agents can read `.env`.** Secrets then land in the conversation. The hooks only guard *writing* it. | §3.1 |
| ✅ Confirmed | `SendMessage` resumes a finished agent with its memory (A2); the auto-format hook is an official documented pattern (A8); `maxTurns`, `isolation` and per-agent `mcpServers` all exist. | §4.5 |
| ⚠ Caution | The "don't let a developer finish on red" hook must guard against a loop: Claude Code overrides a stop hook after 8 blocks in a row. | §4.1 |
| 🔧 Fixed | Inconsistencies: `CLAUDE.md` target ~40 vs ~60 lines; "worktree" vs "one at a time"; `design-patterns` vs `design-approach` file name. | §3.4, §5, §6 |

**Start with Phase 1a (safety)**, then 1b (the delivery loop). Both are small, and each can be approved on its own (§7).

---

## 1. Short answer

The **idea and structure are strong** (roles, two review gates, risk-based lanes, "the existing project wins", a security floor). But it is **not mature yet**, for four reasons:

1. **It has only one real run so far** — the news project (3 stories, 10 tasks done). The pilot showed the design works (the checks caught real bugs, the safety hook held), and it also exposed **5 process problems nobody predicted** (§3.4). One project is not yet enough to call the rules proven.
2. **It relies on AI reviewers to catch bugs, not on machines.** There is no static analysis, no architecture test, no dependency audit. Machines catch whole classes of bugs for almost zero tokens.
3. **The safety hooks have real holes** — I tested them live and 9 of 16 dangerous cases got through (details in §3).
4. **Some guidance is missing:** how to choose a design approach (e.g. factory/strategy), several 2025 security areas, error handling, and a few files contradict each other.

**Compared with the most-loved frameworks** (superpowers 287k stars, BMAD 53k, spec-kit 137k, ponytail 138k and others), the **design is already at their level**, and it's stricter than most on existing codebases. What they have that we don't is **10 small mechanics** that make agents cheaper and more reliable (§4.5). All are instructions or one hook; none needs a package install.

---

## 2. What is already good — keep it

| Strength | Why it matters |
|---|---|
| Existing project's conventions outrank company rules | The #1 way AI damages legacy code is "modernizing" it. This prevents it. |
| Risk lanes (Direct / Light / Standard / Sensitive) | Right idea for cost: a typo does not cost what a payment flow does. |
| Two separate gates (review, then QA) with no edit tools | Reviewers can't quietly "fix" and hide problems. |
| Security floor that never yields | Correct, and matches OWASP's #1 risk (access control). |
| Short agent briefs, full charters only "when needed" | Good token design already (~1.0–1.5k tokens per brief). |
| Stop conditions (3 failed cycles, same error twice…) | Prevents runaway spend. |
| Slopsquatting check (verify a package exists) | Ahead of most setups. |

**Confirmed by the news pilot:**
- Code review failed changes for real reasons (a drive-by style change) and found a real security hole (a `javascript:` link could be saved as a source URL).
- The PM, review and QA each caught a developer's false "I checked it" claim.
- The safety hook blocked `migrate:fresh`, and the agent didn't try to get around it.
- Every migration waited for your approval.
- A story took 7 agent dispatches, under the limit of 10.

---

## 3. Problems found — verified, not guessed

### 3.1 Hook holes (live test against the installed hooks)

I fed test inputs straight into `~/.claude/hooks/*.py`. Result:

| Test | Expected | Actual |
|---|---|---|
| `git reset --hard` | block | ✅ blocked |
| `.env` / `.env.production` write | block | ✅ blocked |
| Stripe live key in code | flag | ✅ flagged |
| **Any command through the PowerShell tool** | block dangerous ones | ❌ **not checked at all** — hook matcher is `Bash` only. On your Windows machine Claude has a PowerShell tool, so `Remove-Item -Recurse -Force C:\` passes. Fix: matcher `Bash|PowerShell` + PowerShell patterns. |
| `git push origin main` | block (your standard says main is protected) | ❌ allowed |
| `git branch -D main` | block | ❌ allowed |
| `rm -rf ./` or `rm -rf src/` | block | ❌ allowed (only root/home paths are caught) |
| `php artisan migrate --force` (production) | ask the user | ❌ allowed |
| A commit message that merely *mentions* `reset --hard` | allow | ❌ **blocked (false alarm)** — the guard scans quoted text too. It blocked my own test run today. |
| Writing `wp-config.php` (holds DB password) | block | ❌ allowed |
| Writing `storage/oauth-private.key` | block | ❌ allowed |
| Secret as a default: `env('STRIPE_SECRET', 'sk_live_…')` | flag | ❌ **missed** — any line containing `env(` is skipped as a "placeholder". This is a very common real leak. |
| Password on a line that also contains `true`/`null` | flag | ❌ missed — whole line skipped |
| WordPress `define('DB_PASSWORD', '…')` | flag | ❌ missed |

Also by design: a file written through a shell command (`echo … > .env`) bypasses both the path guard and the secret scanner, because those only watch Write/Edit.

**New gap (final review): agents can *read* `.env`.** Nothing stops the Read tool from opening it, so real secrets land in the conversation and its saved transcript.

**Better fix than patching the regex (final review):** Claude Code has built-in **permission rules** in `settings.json`, checked before any hook and impossible for a hook to override. Per the official docs, they:
- split `a && b`, `;`, pipes and subshells, and check **each** command, so there's no false alarm on text inside quotes
- cover **PowerShell** by parsing it properly, including aliases (`rm`, `del` → `Remove-Item`)
- check `> file` redirects against `Edit` deny rules, which closes the `echo … > .env` bypass
- block **reading** a file with `Read(...)` deny rules

Sketch of what goes into the installed `settings.json`:

```json
"permissions": {
  "deny": ["Read(**/.env)", "Read(**/.env.production)", "Edit(**/.env)", "Edit(**/wp-config.php)",
           "Bash(php artisan migrate:fresh *)", "Bash(php artisan db:wipe *)", "Bash(git push --force *)"],
  "ask":  ["Bash(git push *)", "Bash(git branch -D *)", "Bash(rm -rf *)", "Bash(php artisan migrate --force *)",
           "PowerShell(Remove-Item *)"]
}
```

Two limits to respect:
- **A deny rule can't have exceptions**, so list each secret file by name. `.env.*` would also block `.env.example`, which agents must be able to edit.
- **The docs say Bash rules are not a hard security boundary**: `git -C . push` isn't matched by `Bash(git push *)`. Keep the hook as a second net for the few patterns that matter most, and keep the secret scanner, which rules can't replace.

The installer must **merge** `permissions` the same way it should merge hooks (§3.2).

### 3.2 Installer bug

`install.sh` line 105: `settings["hooks"] = …` **replaces** every hook you already have in `~/.claude/settings.json`. The README promises it *merges*. Harmless today (you have no other hooks), but it would silently delete any hook you add later.

**Phase 1 fix:** merge instead of replace, for both `hooks` and the new `permissions` (§3.1). **Later option (final review):** package `agents/`, `skills/` and `hooks/` as a Claude Code **plugin**. It can load straight from `~/.claude/skills/<name>/` with no marketplace, plugin hooks run alongside yours instead of replacing them, and files are referenced with `${CLAUDE_PLUGIN_ROOT}`. Trade-offs:
- A plugin **can't** ship `CLAUDE.md` or permission rules, so a small installer stays for those two.
- Skills show up namespaced (`/<plugin>:next-story`), though "go" still triggers them through their description.
- Old copies in `~/.claude/agents/` must be removed, because they override same-named plugin agents.

### 3.3 Files that contradict each other

| Conflict | Where | Risk |
|---|---|---|
| Project files live in **`projects/<name>/`** vs **`.claude/project/`** | Standards and charters use one, agents/skills/README the other (21 mentions across 14 files) | An agent told "read `projects/x/conventions.md`" finds nothing and either blocks or guesses. |
| `git-workflow.md` says "vibe_coding is not a git repository, devops must `git init`" | Installed globally, so it is read in **every** project | Wrong (it is a repo) and irrelevant elsewhere — noise that can confuse an agent. |
| Repo `CLAUDE.md` says "no git repository", "only four charters exist" (then lists six), paths `company/…` and `.claude/hooks/` | Repo root | Out of date since the move to `home/`. |
| Standards say "`security-engineer` / `solution-architect` must approve" | Many places | These roles don't exist, so every such rule silently falls back to "escalate to user". Works, but it's a detour baked into the rules. |

### 3.4 Problems proven by the news pilot *(new)*

These are not guesses: each one happened. Details and file references are in [news-project-claude-review.md](news-project-claude-review.md).

| # | Problem | What happened | Fix in the system |
|---|---|---|---|
| P1 | **Facts go stale — nothing refreshes them** | `CLAUDE.md` still says "no code yet, not a git repository" after 14 commits. `conventions.md` still says "Laravel not installed". `status.md` shows 7 tasks done while the board shows 10. Old text is left inside board rows ("Done … Waiting on QA"). | `/next-story` Step 4: *"when a fact changes (versions, layout, commands), update `CLAUDE.md` and `conventions.md` in the same step; replace board text, don't append."* Keep commands in `conventions.md` only; `CLAUDE.md` points to it. |
| P2 | **Parallel tasks share one working folder** | Two tasks ran side by side; each QA run found the other's temporary test file, and one broke the other's format check. | **One developer and one QA at a time** (same as A4, §4.5). `isolation: worktree` only if parallel work is ever needed again. |
| P3 | **QA writes temporary tests into the real test folder** | Every QA report creates `tests/Feature/QaProbe*.php` and deletes it afterwards. One missed delete and a junk test gets committed. | QA brief: probes go in `tests/QaProbe/`, which is git-ignored. |
| P4 | **QA can't see the page** | QA has no browser, so "check it at phone size" is passed by reading code. The PM did the real check by hand in Chrome. | Give **only** `qa-engineer` a browser tool (the `mcpServers` field in its agent settings, so other agents don't pay the token cost), or make the PM's browser check a formal, recorded step. |
| P5 | **The PM planned a command the hook blocks** | The backlog told an agent to verify with `migrate:fresh`, which the safety hook blocks. | The PM brief lists the blocked commands so plans never ask for them. |

---

## 4. What is missing

### 4.1 Automatic checkers — the biggest lever for "bug free" (and the cheapest)

Today the only thing between AI-written code and your project is *another AI reading it*. Machines should go first; AI reviewers should only judge what machines can't.

| Check | What it catches | Token cost |
|---|---|---|
| **Larastan / PHPStan** (static analysis) | Wrong types, undefined methods, null bugs, wrong argument counts — before any test runs | ~0; only error lines come back |
| **Pest architecture tests** (`arch()`) | "Controllers must not use DB", "no `dd()`", "models only in `app/Models`" — your rules, enforced by code instead of a reviewer's memory | ~0 |
| **`composer audit` / `npm audit`** | Known-vulnerable packages (OWASP 2025 #3, new category) | ~0 |
| **One `check` command per project** (format → analyse → tests), recorded in `conventions.md` | Gives every agent one command that answers "is it OK?" | ~0 |
| **`SubagentStop` hook on developer agents** that runs that `check` command and refuses to let the agent finish while it fails | A developer can't report "done" on red — a failed review cycle (two cold-start agents) is avoided. ⚠ Must read the `stop_hook_active` field and let go after one retry: Claude Code overrides a stop hook that blocks 8 times in a row. | Only failure output |

**Brownfield rule still applies:** in an existing project these tools are added only with approval, as their own task, using a **baseline** (PHPStan baseline = "don't fail on old errors, only on new ones"). This matches your existing "no worse than baseline" test rule.

**Pilot evidence:** the news project's dev tools are only Pint and Pest, with no static analysis, architecture tests or audit. A new project is the cheapest moment to add them because there is no old code to baseline. **Make Larastan + architecture tests part of the greenfield scaffold task by default.**

**Two more cheap checks from the top frameworks** (§4.5): an **auto-format hook** that runs the project's formatter on each PHP file right after it's edited, so formatting never fails a review (A8); and **"show the failing test first"** as evidence in the developer report (A6).

Pest 5 (released July 2026) adds **Test Impact Analysis** (runs only tests your change touched — Laravel Cloud went from 3 min to 5 s) and an **Agent plugin** for AI verification. It needs PHP 8.4+, so it fits greenfield, not most legacy projects.

### 4.2 Design approach guide — "which pattern for which problem"

Nothing today tells a developer agent *how to shape* a solution. The result is either copy-paste code or over-engineered abstractions (both common AI failures). What's needed is **one short guide (~50 lines)**, not a design-patterns textbook.

**Step 1 — the "do we even need this code?" ladder** *(from ponytail, 138k stars; it claims 54% fewer lines and 22% fewer tokens in its own benchmark)*. Go down in order and stop at the first "yes":

1. Does this need to exist? → no: skip it
2. Already in this codebase? → reuse it
3. Standard library does it? → use it
4. Framework has it built in? → use it (Laravel: validation, policies, `Str`, `Collection`, `Pipeline`, …)
5. Installed dependency does it? → use it
6. One line? → one line
7. Only then: the minimum that works, using the table below

**Step 2 — only if you reach rung 7, pick the shape from this table:**

| Problem you actually have | Use | Laravel-native form | Don't |
|---|---|---|---|
| Several interchangeable ways to do one thing (payment gateways, shipping rates, export formats) | **Strategy** | Interface + container binding, or a `Manager` class | Long `if/else` or `switch` on type |
| Creating objects that vary by type/config | **Factory** | Static named constructor, or `Manager::driver()` | `new` scattered across controllers |
| One business operation used from several places (controller, job, command) | **Action** | `app/Actions/X::handle()` | Logic duplicated in controllers |
| Multi-step processing where steps can be added/removed | **Pipeline** | `Pipeline::send()->through([...])` | One 200-line method |
| "When X happens, also do Y, Z" | **Observer / Events** | Events + queued listeners | Stuffing side effects into the controller |
| Talking to an external API | **Adapter** | Own interface + one class per provider, `Http::fake()` in tests | Calling the SDK directly everywhere |
| Complex or reused queries | **Query scope / query object** | `scopeActive()`, dedicated query class | Repository wrapper over Eloquent *(only if the project already has repositories)* |
| Money, email, status with rules | **Value object / Enum** | Backed enum (PHP 8.1+), small readonly class | Raw strings and floats |

**Two rules that go with it:**
- **Rule of three:** no interface or pattern until there is a *second* real case. One implementation = plain class. (Matches your "simplicity first" principle.)
- **The project's existing pattern wins.** If they use repositories, you use repositories.

The reviewer then gets one extra check: *"Is there an abstraction with only one use? → should-fix."*

### 4.3 Security — mapped to OWASP Top 10:2025 (final list, January 2026)

| # | Risk | Covered today? | Missing |
|---|---|---|---|
| A01 | Broken access control (now includes SSRF) | Partly — write routes authorized | **Read** routes (seeing someone else's record by changing the ID); **SSRF** (server fetching a user-supplied URL) |
| A02 | Security misconfiguration (moved up to #2) | ❌ | `APP_DEBUG=false` in production, security headers (CSP, HSTS, X-Frame-Options), cookie flags (Secure, HttpOnly, SameSite), CORS, no directory listing |
| A03 | **Software supply chain** (new) | Partly — "package exists" check | `composer audit` / `npm audit`, lock files committed, abandoned packages |
| A04 | Cryptographic failures | Partly — password hashing | Encrypt personal data at rest (Laravel `encrypted` cast), HTTPS only, random tokens via `Str::random` / `random_bytes`, never home-made crypto |
| A05 | Injection | ✅ good | — |
| A06 | Insecure design | ❌ | A **5-question threat check** for Sensitive-lane tasks: who can reach this, what can they change, what if they lie about the input, what is logged, what fails open |
| A07 | Authentication failures | ❌ | Rate limiting on login / password reset / OTP, session ID regenerated on login, `Password::defaults()`, no "user not found" vs "wrong password" difference, 2FA for admins |
| A08 | Data integrity failures | Partly — no `unserialize()` on input | Verify webhook signatures, signed URLs for sensitive links |
| A09 | Logging & alerting | Partly — says what *not* to log | What **must** be logged: failed logins, permission denials, admin actions |
| A10 | **Mishandling exceptional conditions** (new) | ❌ | Error-handling rule: fail **closed** (on error, deny — never allow), catch specific exceptions, never swallow errors silently |

**Found in the pilot, missing from the checklist *(new)*:**

| Risk | Pilot example | Rule to add |
|---|---|---|
| **SSRF** (part of A01) | `news:fetch` downloads whatever `feed_url` says, and an admin screen will let someone edit it, so internal addresses like `http://localhost/…` could be fetched. | Any URL the server fetches: `http`/`https` only, public hosts only, private IP ranges blocked. |
| **Prompt injection** (the #1 risk in OWASP's Top 10 for LLM Applications) | Feed text goes straight into the Anthropic prompt, and official items auto-publish with no human check. | Text sent to an AI is **data, never instructions**. The code-side checks (structured output, the publishing rules) must hold whatever the model returns. Test with a hostile input. |
| **XXE** (hostile XML) | Feeds are XML; only *malformed* XML is tested. | One test proving external entities are not loaded. |

These apply to any project that fetches URLs, calls an AI, or parses XML, not just news.

**Missing security role — cheapest fix:** don't write a `security-engineer` charter yet. Claude Code already ships **`/security-review`**. Make it part of the Sensitive lane (after code review, before your approval). Zero maintenance, zero new files to load.

### 4.4 Smaller gaps

| Gap | Note |
|---|---|
| No error-handling standard | Ties to A10 above. Currently only "log exceptions with context". |
| Accessibility is only in the frontend agent brief | Not in `coding-standards.md`, so the reviewer has no rule to cite. |
| No JSON/API response standard | AJAX seam exists, but no standard error shape or status-code table. |
| No safe-migration rule for big tables | e.g. add column nullable first, backfill in a job, then constrain. |
| No `maxTurns` on any agent | Your stop conditions are written down but not enforced — an agent can grind. `maxTurns` in the agent frontmatter caps it automatically. |
| No tests for the system itself | No sample scenarios to check the skills and agents actually behave as written (Anthropic's guide: build at least 3 evaluations per skill *before* adding more instructions). **Built-in answer (final review): `claude plugin eval`.**<br>• Each test case is a folder with a realistic prompt ("go", "I want a booking site") plus checks, e.g. "did `/next-story` fire?", "was `conventions.md` read first?", "did it stop after one story?"<br>• The checks `regex`, `tool_used` and `file_exists` cost nothing; AI-judged checks cost extra.<br>• It reports the score **with vs without** the framework.<br>• It counts against your plan's usage, so use `--runs 1 --ablation none` while writing cases.<br>• It needs the framework packaged as a plugin (§3.2). |

### 4.5 Compared with the most-loved frameworks — what to add *(new)*

Full research: [top-frameworks-comparison.md](top-frameworks-comparison.md).

**Scorecard — our framework vs the best of theirs:**

| Area | vibe_coding today | Best in class (stars) | Result |
|---|---|---|---|
| Working principles | Four principles in global `CLAUDE.md` | karpathy-skills (213k) — the same four | ✅ Equal |
| Two review checks | Code review → QA | superpowers (287k): "spec compliance" → "code quality" | ✅ Equal |
| Right-sized process | 4 risk lanes, you approve risky work | BMAD (53k) scale-adaptive tracks | ✅ Equal; ours is stricter |
| Role team | 5 agents with path ownership + data contract | BMAD role agents | ✅ Equal; our data contract is extra |
| Existing codebases | Precedence ladder + survey first | OpenSpec (68k) "built for brownfield" | ✅ **Ours is ahead** |
| Safety hooks | 3 hooks, with holes (§3.1) | ECC (258k): many hooks + a config scanner | ⚠ Behind — fix in phase 1 |
| Agent can't ask a question | "Reject and report back" | superpowers: 4 report statuses | ❌ → **A1** |
| Cost of a fix round | New cold agent every time | superpowers: continue the same agent | ❌ → **A2** |
| What reviewers read | The whole task and its files | superpowers: only the diff since the task began | ❌ → **A3** |
| Developers in parallel | Allowed "if independent" | superpowers: never (pilot P2 proved why) | ❌ → **A4** |
| Writing less code | Pattern table (proposed) | ponytail (138k): the "need this code?" ladder | ❌ → **A5** |
| Tests prove something | Tests ship with the code | superpowers: watch it fail first | ⚠ → **A6** |
| Plan files | Grow forever (~10k tokens in the pilot) | OpenSpec: archive finished work | ❌ → **A7** |
| Formatting | Reviewer catches it | best-practice (66k): auto-format hook | ❌ → **A8** |
| Learning from failures | Nothing | ECC "instincts" (heavy) / "Gotchas" lists (light) | ❌ → **A9** (light version) |
| Agent report size | Long (QA 1.6k–4.3k tokens each) | caveman (106k): terse agent output | ❌ → **A10** (idea only) |

**What to add — and exactly where in `home/`:**

| ID | Add | Where | Size |
|---|---|---|---|
| **A1** | Every developer report ends with one status: `DONE` · `DONE_WITH_CONCERNS` · `NEEDS_CONTEXT` (say exactly what's missing) · `BLOCKED`. The PM answers `NEEDS_CONTEXT` and continues the same agent; `BLOCKED` goes to you. This gives agents a cheap way to "ask" instead of guessing. | `agents/*-developer.md` "Your report back"; `skills/next-story` Step 3 | ~6 lines |
| **A2** | **Fix rounds continue the same agent** (with `SendMessage`, so it keeps its memory) instead of starting a new cold one. Rounds 1–2 continue; round 3 is a fresh agent given a written summary of both failures. The hard stop after 3 failures stays. *Confirmed in the final review: `SendMessage` resumes a finished agent from its own transcript. Use the agent ID from the spawn result.* | `skills/next-story` "On VERDICT: FAIL" | ~5 lines |
| **A3** | Record the commit hash (**BASE**) before each developer starts. Review and QA get `git diff BASE` and the changed-file list, not the whole story. Out-of-scope files show up for free. | `skills/next-story` Steps 2–3; `agents/code-reviewer.md` | ~3 lines |
| **A4** | **One developer at a time; one QA at a time.** Replaces "unless two are genuinely independent". | `skills/next-story` Step 2 | 1 line |
| **A5** | The 7-rung ladder (§4.2) before writing code; the pattern table only at rung 7. The reviewer adds one check: *"Was a lower rung skipped? Is there an abstraction with only one use?"* → should-fix. | `agents/*-developer.md`; `agents/code-reviewer.md`; new `company/standards/design-approach.md` (~50 lines, read only at rung 7) | ~10 lines in briefs |
| **A6** | For new behavior and every bug fix: paste the **failing** test run (≤10 lines), then the passing one. Superpowers' "delete code written before the test" is **not** adopted — it clashes with brownfield work. | `agents/*-developer.md` report item 4; `company/standards/testing-standards.md` §2 | ~3 lines |
| **A7** | When a story is Done, move it from `backlog.md` to `backlog-done.md`; `/next-story` reads only the live file. Board "Reason" = one line pointing to the report. | `skills/next-story` Step 4 | ~3 lines |
| **A8** | **Auto-format hook:** after an Edit/Write of a `*.php` file, run the project's formatter on that one file — **only if the project already uses one** (e.g. `vendor/bin/pint` plus `pint.json`), so it never introduces a formatter into an existing codebase. Fails open and stays silent unless something breaks. *Final review: the official hooks guide shows this exact pattern (with Prettier). Watch during testing whether the agent has to re-read a file the formatter changed.* | new `hooks/format_php.py`; `settings.hooks.json` (using the `if` field so it only starts for PHP files) | ~40-line script |
| **A9** | A **"Gotchas"** list (≤10 lines) at the end of each agent brief, fed from real failures. Seeded from the pilot: *"never claim a manual check you didn't run"*, *"probe tests go in `tests/QaProbe/`"*, *"SQLite passes things MySQL rejects — check string lengths"*, *"don't plan commands the hooks block"*. | every `agents/*.md` | ≤10 lines each |
| **A10** | Report length caps: developer report ≤ ~40 lines; QA one line per criterion, then only defects and "not tested". Plain words stay for anything the PM passes to **you**. | `agents/*.md` report formats | ~2 lines each |

**Deliberately not added:** installing ECC, SuperClaude or agent collections (every extra agent costs tokens in every session and breaks one-owner-per-path); caveman as an install (it adds ~1,000 tokens per call and breaks your plain-language rule); full spec-kit or GSD (they duplicate `/new-project` → `/next-story`, and GSD was archived in June 2026); claude-mem (you already have memory). A code index (codegraph) is a **later trial on one large existing project** only.

---

## 5. Token optimization — where the tokens actually go

Estimated as characters ÷ 4.

| Loaded when | Size | Finding |
|---|---|---|
| Every session, every project: global `CLAUDE.md` | ~1.4k | Fine. |
| Every session **in this repo**: repo `CLAUDE.md` | ~3.3k | Mostly repeats the global file → you pay twice on every turn here. Cut to repo-only facts (~60 lines, see item 8 below). |
| Every `/new-project` or `/next-story`: skill + full PM charter | ~1.3–1.9k + **~5.8k** | **Biggest single cost.** The agents got short briefs; the PM didn't. A ~1.5k PM brief (charter for edge cases only) saves ~4k tokens per story session. |
| Each Standard task: 3 agents × brief | ~1.0–1.5k each | Good already. |
| Stop conditions | repeated in 3 files | Global CLAUDE.md, `token-budget.md`, `next-story` — keep once. |
| **Pilot:** `backlog.md` | **~10k** | Read on every `/next-story`, and it grows every story because finished stories stay in full detail. Move finished stories to `backlog-done.md`. |
| **Pilot:** `board.md` | ~1.8k | "Reason" cells are paragraphs that repeat the QA reports. One line each, pointing to the report. |
| **Pilot:** QA reports | 1.6k–4.3k **each** | Long narrative. Cap them: one line per criterion, then defects and "not tested" only. |

**Other savings, cheapest first:**
1. **Machine checks before AI checks** (§4.1). The biggest token saving is a review cycle that never has to happen.
2. **`maxTurns` per agent** — hard cap on grinding.
3. **Hook `if` field** — e.g. only start the secret scanner for code/config files, not every write.
4. **Path-scoped rules instead of "skills" for coding conventions.** A rule file with `paths: ["**/*.blade.php"]` loads *only* when Claude touches a Blade file, automatically. That's how Blade/SCSS/jQuery rules should be delivered — not a "Frontend skill". ⚠ Must be tested first: the docs clearly support this in a project's `.claude/rules/`; that path matching works the same from `~/.claude/rules/` (global) isn't spelled out.
5. **Scripts over instructions** for repeatable jobs (e.g. the codebase survey): the script runs, only its output enters context — Anthropic's own guidance.
6. **Size rules for project files** *(from the pilot)*: archive finished stories, one-line board reasons, and capped QA reports. Write these rules into the PM brief so every project stays lean.
7. **Continue the agent for fixes; send reviewers only the diff** *(from superpowers, §4.5 A2–A3)*: in the pilot, 2 of 7 tasks needed a review fix, and each started a new agent from zero.
8. **Repo `CLAUDE.md` to ~60 lines** *(claude-code-best-practice: ~60 lines is safer for adherence, 200 is the ceiling)*. It's 164 lines today and repeats the global file.

---

## 6. Skills — which ones are worth it

Rule used: *add it only if Claude doesn't already know it, and it's cheaper than a failure it prevents.*

| Candidate | Verdict | Why |
|---|---|---|
| **Laravel Boost** (official, by the Laravel team) | ✅ **Yes, for Laravel projects** — default in greenfield; ask first in brownfield (it's a dev dependency) | Gives the agent guidelines **matched to the installed version** (Livewire 3 vs 4, etc.) and a docs search — directly fixes your "don't use APIs the version doesn't have" risk. Boost 2.0 moved content into on-demand skills (~40% leaner). Watch the MCP tool count. |
| **`/security-review`** (built into Claude Code) | ✅ **Yes** — use in the Sensitive lane | Free, maintained by Anthropic, replaces a charter you'd otherwise have to write. |
| **Own `survey-codebase` skill + script** | ✅ **Yes — worth building** | The brownfield survey is the most important step. A script that collects PHP/framework versions, directory tree, and test baseline is faster, cheaper and more accurate than an agent reading around. |
| **Own `design-approach.md` reference** (~50 lines, §4.2, A5) | ✅ **Yes — small** | Loaded by developers only when shaping a new piece of logic. |
| **Browser tool for `qa-engineer` only** *(from the pilot)* | ✅ **Yes** | The pilot's QA couldn't see pages (P4). Attach it through the QA agent's own `mcpServers` setting so no other agent loads its tools. |
| **Pest 5 Agent plugin / Test Impact Analysis** | ✅ Where PHP ≥ 8.4 | Faster, cheaper verification loops. Not for legacy projects. |
| **Anthropic `frontend-design` skill** | ⚠ **Only for greenfield visual design** | It pushes bold, distinctive new styling — the opposite of "match the existing site" in brownfield. Low cost when idle (~100 tokens), but don't let it fire on brownfield work. |
| **A generic "PHP skill" or "Frontend skill"** | ❌ **No** | Claude already knows PHP and CSS; your stack rules already exist. Deliver them as path-scoped rules (§5, item 4) instead. |
| **Writing the 6 missing role charters** | ❌ **Not now** | Each costs tokens and upkeep. Security → `/security-review`; architect → the design-pattern guide + `decisions.md`; devops → wait until there is real deployment work. |
| **Installing a whole framework** (ECC, SuperClaude, superpowers, agent collections) | ❌ **No** — take their ideas (§4.5) | ECC alone ships 68 agents and 292 skills. Every agent description loads into every session, and overlapping agents break one-owner-per-path. |
| **caveman** (terse-output skill) | ❌ Install · ✅ idea | Adds ~1,000 tokens per call, and terse talk breaks your plain-language rule. Only the idea is used: short agent-to-agent reports (A10). |
| **codegraph / serena** (code index) | ⚠ **Later trial**, one large existing project | Claims 62% fewer tokens in its own benchmark and supports PHP and Laravel routes, but adds MCP tools to every session. Not worth it on small projects like news. |

---

## 7. Recommended order

Each phase is small and can be approved separately.

| Phase | What | Effort | Why this order |
|---|---|---|---|
| **1a. Safety** | **Permission rules first** (§3.1): `deny` / `ask` for destructive commands in Bash **and** PowerShell, `Read` / `Edit` deny for `.env` files. Then patch the hooks only for what rules can't do (the secret scanner's misses, protected files, the false alarm). Installer merges `hooks` + `permissions` instead of replacing (§3.2). Contradictions and stale text (§3.3). `maxTurns` on agents. | 1 session · Light | Safety first; cheapest. Every item was tested or read in the docs. |
| **1b. Delivery loop** | Pilot problems P1–P3 and P5 (§3.4): the "refresh facts" step, the probe folder, blocked commands in the PM brief. **A1–A4** (§4.5): report statuses, continue the same agent for fixes, diff since BASE for reviewers, one developer and one QA at a time. | 1 session · Light | The pilot proved these happen. Try them on the next news story. |
| **2. Keep the pilot going** *(already running, news)* | Continue news story by story; note every process failure after each story; measure one story with `/cost` | ongoing | It already found P1–P5. The next stories (AI drafting, admin login) will test the Sensitive lane and security rules. |
| **3. Machine checks** | `check` command per project, `SubagentStop` hook, Larastan/arch tests/audit in the finish checklist (baseline in brownfield). **Try it on news first**, since it's new code with no baseline needed. **Plus** the auto-format hook (A8) and failing-test-first evidence (A6). | 1 session | Biggest bug and token win. |
| **4. Knowledge** | OWASP 2025 additions, **SSRF / prompt injection / XXE rules** (§4.3), 5-question threat check, error-handling rule, design-pattern guide, `/security-review` in Sensitive lane, **browser for QA** (P4), **the "need this code?" ladder before the pattern guide (A5)**, **Gotchas lists seeded from the pilot (A9)** | 1 session | Fill the gaps the pilot confirmed. |
| **5. Trim tokens** | PM brief, shorter repo `CLAUDE.md`, remove repeats, path-scoped rules (after testing), **project file size rules** (§5), **archive finished stories (A7)**, **short agent reports (A10)**, repo `CLAUDE.md` to ~60 lines | 1 session | Measure before/after with `/cost`. |
| **6. Skills** | Laravel Boost (per project), `survey-codebase` skill + script | 1 session | Last, because they build on phases 3–4. |
| **Later trial** | codegraph on one large existing project, measured with `/cost` before and after | 1 session | Only worth it on big codebases (§6). |
| **Later: plugin + tests** | Package agents / skills / hooks as a plugin (§3.2); write ~5 `claude plugin eval` cases for `/new-project` and `/next-story` (§4.4) | 1–2 sessions | Makes every later change measurable, so you can tell whether a change helped. |

---

## 8. Honest limits of this report

- **Hook results are real** (tested today). **Token numbers are estimates** (characters ÷ 4), not measured with `/cost`.
- I read every file in `home/` except the full charters of the non-PM roles, which I checked by structure (headings) only.
- Global path-scoped rules (`~/.claude/rules/` with `paths:`) need a quick test before relying on them.
- Pilot evidence comes from reading the news project's plans, QA reports and git history. I didn't re-run its tests or open the site.
- Savings figures from other frameworks (ponytail's 54% fewer lines, codegraph's 62% fewer tokens, etc.) are **their own benchmarks**; I haven't reproduced them.
- Permission rules, plugin packaging and `claude plugin eval` were checked **in the official docs**, not yet tried on this machine. Phase 1a includes testing the rules the same way the hooks were tested.
- Nothing was changed. Test script used for the hook check: in the session scratchpad, not the repo.

---

## Sources

- [OWASP Top 10:2025 — Introduction](https://owasp.org/Top10/2025/0x00_2025-Introduction/) · [Fastly: what changed in 2025](https://www.fastly.com/blog/new-2025-owasp-top-10-list-what-changed-what-you-need-to-know)
- [OWASP Laravel Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Laravel_Cheat_Sheet.html) · [OWASP ASVS index](https://cheatsheetseries.owasp.org/IndexASVS.html)
- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks) (PowerShell matcher, `if` field, Stop/SubagentStop blocking) · [hooks guide](https://code.claude.com/docs/en/hooks-guide) (auto-format example, stop-hook loop cap)
- [Claude Code permissions](https://code.claude.com/docs/en/permissions) (deny/ask rules, compound commands, PowerShell, `Read` deny, limits)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins) · [plugins reference](https://code.claude.com/docs/en/plugins-reference) · [plugin evals](https://code.claude.com/docs/en/plugin-evals)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) (`maxTurns`, `skills`, `hooks`, `effort` frontmatter)
- [Claude Code memory & path-scoped rules](https://code.claude.com/docs/en/memory)
- [Anthropic — Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Laravel Boost docs](https://laravel.com/docs/13.x/boost) · [Laravel AI-assisted development](https://laravel.com/docs/13.x/ai)
- [Pest 5 release (Laravel News)](https://laravel-news.com/pest-5)
- [Larastan](https://github.com/larastan/larastan) · [PHPStan baseline for legacy Laravel](https://richdynamix.com/articles/phpstan-baseline-burn-down-legacy-laravel)
- [Design patterns in Laravel — practical guide](https://hafiz.dev/blog/mastering-design-patterns-in-laravel)
- [anthropics/skills — frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
- Frameworks compared (§4.5): [superpowers](https://github.com/obra/superpowers) · [its subagent-driven-development skill](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md) · [ECC](https://github.com/affaan-m/ECC) · [karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) · [ponytail](https://github.com/DietrichGebert/ponytail) · [spec-kit](https://github.com/github/spec-kit) · [OpenSpec](https://github.com/Fission-AI/OpenSpec) · [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) · [caveman](https://github.com/JuliusBrussee/caveman) · [codegraph](https://github.com/colbymchenry/codegraph) · [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) · [gsd-core](https://github.com/open-gsd/gsd-core)
