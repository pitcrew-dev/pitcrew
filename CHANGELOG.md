# Changelog

## 1.0.0 - 2026-10-28

The free version: the same safety, much less AI work per piece.

### Added
- **Quick and Careful mode.** Quick (the default) uses one developer per task and one test run at the end of each piece. Careful adds a code review and a full test to every task. Logins, payments, personal data, database changes and going live always get the careful checks. Switch in the plugin settings (`careful_mode`) or per project with a `Mode:` line in `budget.md`.
- **`/company:fix`:** for one broken thing. It finds the cause, has one developer write a test that fails, fix it and pass, checks the result, commits and stops. Risky fixes get the full checks and your approval.
- **An eval** for it (`plugin/evals/fix-skill-fires/`).

### Changed
- **One plan file.** A project now has `plan.md` (where we are, your request, goals, pieces with their tasks, done), `decisions.md` (with the risks), `conventions.md`, `lessons.md`, `budget.md` and `activity.md`. Old projects are offered a merge; nothing is deleted.
- **A lighter start.** 3 to 5 questions in one round, design options only when you ask, and a git safety net in a folder that has none.
- **Cheaper defaults.** The budget per piece is $12 (was $25). A Quick piece is about $7 (an estimate, not yet measured); a Careful piece about $17.

## 0.9.0 - 2026-10-24

The release candidate for 1.0.

### Added
- **Evals:** five scripted checks of the main flows, run with `claude plugin eval` (`plugin/evals/`). They cover starting a new project, a story stopped by its budget, status, the report, and the notice about an old install.
- **An example project:** `plugin/evals/fixtures/salon/`, a half-built salon booking site with its project files filled in. The evals use it, and you can open it yourself to try `/company:status` and `/company:report`.
- **CI:** the tests run on Windows, macOS and Linux (and on Python 3.8), and the plugin check runs on every push. The paid evals run when started by hand.
- **MIT licence.**

### Fixed
- **Status and report still give costs when the cost script can't run** (for example if you said no to the shell prompt). They quote each story's running total from the activity log and say the project total couldn't be worked out, instead of leaving costs out.

### Changed
- The install instructions name the repository: `/plugin marketplace add kasshif01/vide_coding`.

## 0.8.0 - 2026-10-24

### Added
- **The plugin notices an old 0.2.x install.** When a session starts and the old copy is still in `~/.claude`, you get one plain message saying so, and the one command that removes it (`python install.py --uninstall`, with `--dry-run` to look first). Before this, the two versions ran side by side and every agent appeared twice.
- **"Your first ten minutes" in the README:** install to an approved plan, step by step. In a test run on a new salon booking site, it took about 4½ minutes of AI time and $1.65.

### Changed
- **Clearer budget settings.** The install dialog now says what a budget means in plain words ("how much AI work one piece may use, priced at Anthropic's pay-per-use rates") and that a typical piece costs about $17.

## 0.7.0 - 2026-10-24

### Added
- **`/company:status`: where the project stands, on one screen.** Progress per goal, money spent and left (flagging anything at 80% of its budget), the story in progress, what's next, and exactly what's waiting on you. It changes nothing.
- **`/company:report`: a one-page update you can send.** What was done, grouped by goal, what it cost, risks and open questions, and what's next, written for a client or manager who has never seen the project files. Saved in `.claude/project/reports/`, never sent anywhere.
- **Exact numbers in both.** A small script adds up the activity log and budgets, so the AI quotes the totals instead of doing the sums itself. It can also count from a start date for a report (`--since`).
- **An agent status line.** While agents work, each row in the agent panel shows the agent, its task, and the story's spend against its budget, e.g. `qa-engineer · SHOP-E01-S02-T01 · story $14.20 of $25.00 · 45k tokens`.

## 0.6.0 - 2026-10-24

### Added
- **Budgets: a story can't quietly run up a big bill.** Before every agent starts or gets a follow-up, a new hook checks what the story has cost so far against its budget.
  - **At 80%** the agent still runs, and the PM tells you in its next report.
  - **At 100%** the next agent is blocked. The PM stops and asks you: top it up (it suggests an amount and says why it ran over), or stop the story. A running agent is never cut off mid-task.
  - **Defaults: $25 per story, no project cap.** Change them in the plugin settings (`/config`), or per project in `.claude/project/budget.md`, which also lists every top-up you approved.
  - **`/company:start` suggests a project cap** of about $17 a story (the pilot average), and the plan shows the budget.
  - Costs are API-equivalent dollars, the same numbers as the activity log.

## 0.5.0 - 2026-10-24

### Added
- **Every agent run is logged, with what it cost.** A new hook adds one line to `.claude/project/activity.md` each time an agent finishes: time, task, agent, result (`PASS`, `FAIL`, `DONE`, ...), the agent's cost, the PM's cost since the previous line, and the story's running total.
  - **The numbers are measured, not guessed.** The hook reads the token counts Claude Code records for every model call and prices them in API-equivalent dollars: what the same work would cost at Anthropic's API prices. Subscription users don't pay this; it shows where the effort went.
  - **The PM's own cost is included.** In the pilot, the PM was about 40% of the total.
  - **A follow-up to the same agent is counted once.** It gets its own line with only the new work.
  - **The report at the end of `/company:next` says what the story cost.**
  - **Only the hook writes the log.** Agents are blocked from editing `activity.md`.

## 0.4.0 - 2026-10-24

### Added
- **Every project now has goals.** `/company:start` writes `.claude/project/goals.md`: 2–5 outcomes in plain words, each with a "done when" check the user can do themselves. The user confirms the goals before anything else in the plan.
  - **Every story names its goal** (`goal: G1`). A story that serves no goal is questioned instead of built.
  - **Progress is shown per goal**, in `status.md` and in the report at the end of each `/company:next` (e.g. "Online booking: 2 of 3 pieces done"). When a goal's last story is done, the user runs its check before it counts as met.
  - **Older projects are offered goals** on their first `/company:next`: the PM proposes them from the existing backlog and waits for an OK.

## 0.3.0 - 2026-10-24

### Changed
- **Agent Company is now a Claude Code plugin.** It is installed from a marketplace (`/plugin marketplace add`, then `/plugin install company@agent-company`) instead of by copying files into `~/.claude/`. Nothing about how the team works has changed.
  - **The commands are renamed:** `/new-project` is now `/company:start` and `/next-story` is now `/company:next`. The agents are now `company:backend-developer`, `company:frontend-developer`, `company:full-stack-developer`, `company:code-reviewer` and `company:qa-engineer`.
  - **The working agreement is loaded by a hook** at the start of every session, because a plugin can't load a `CLAUDE.md`.
  - **The permission rules moved into hooks**, because a plugin can't ship permission rules. Same rules as before: no reading or writing `.env`, no `migrate:fresh` or force-push, and an ask before every push.
  - **A small launcher** finds a working Python 3.8+ for the hooks. If there is none, hooks don't block work, but the session starts with a plain warning that the safety checks are off.
  - **`install.py` now only removes the old version.** Run `python install.py --uninstall` (try `--dry-run` first) to remove a 0.2.x install before installing the plugin. Your own agents, skills, settings and `CLAUDE.md` text are kept, and everything removed is backed up. It will be dropped in a later release.

## 0.2.5 - 2026-09-24

### Added
- **The PM remembers where the project stands after `/compact`.** Compacting squeezes the chat into a summary, and the PM could lose track of progress. A new hook puts `status.md` and `lessons.md` back into the chat right after every compact. It stays silent outside a project, and caps each file so a big one can't flood the chat.
- **Mistakes aren't repeated: `lessons.md`.** When the user corrects something, or a gate fails for a reason that could happen again, the PM adds one line to `.claude/project/lessons.md`. Every agent gets the lines that apply to its task, so the next one doesn't make the same mistake. Kept to about 20 lines.

## 0.2.4 - 2026-09-22

### Fixed
- **JavaScript no longer ends up inline in templates.** The frontend agent was only told where JS goes when a project uses Vite. In a project without a build step it was told "no Vite, no npm", given nowhere else to put JS, and wrote it inline.
  - **The frontend brief now says it directly:** JS and CSS go in their own files, in the folder the project already uses (`resources/js/` with a build step, `public/js/` without one). The only `<script>` allowed in a template is a `src` link or the JSON data bridge. If the agent can't tell where files go, it asks.
  - **The project survey records asset folders** in `conventions.md`, so the agent doesn't have to guess.
  - **Review flags it:** a new `<script>` or `<style>` block in a template is should-fix.

### Added
- **New projects ask which stack to use.** Nothing is assumed any more. `/new-project` asks four questions, each with options and a recommended choice: what kind of site it is (Laravel, WordPress or plain PHP), how interactive it is (plain JavaScript, Alpine.js, Livewire or jQuery), how styles are written (custom SCSS, Tailwind or Bootstrap), and which database. The answers go into `conventions.md` and outrank the jQuery default.

## 0.2.3 - 2026-09-19

### Changed
- **Faster QA and review, same checks.** Measured on 52 real gate runs: QA took twice the steps of review, and one bug fix took QA 98 steps. The time went on reading library code (`vendor/`), hunting for the PHP path and server setup, and re-running the full test suite.
  - **QA depth:** the PM names *Focused* (small change: every criterion plus at most 3 edge cases, about 20 steps) or *Full* (everything else, always for Sensitive work).
  - **Test, don't investigate:** QA and review no longer read `vendor/`, framework internals or server config. Missing setup facts mean asking the PM, not hunting.
  - **Setup facts in every gate prompt:** PHP path, check command, test database, how to run a quick script.
  - **The full suite runs once:** the reviewer runs only new and changed tests; QA runs the full suite once, at the end.
  - **Small bug fixes go Light:** a fix of 2 files or fewer, with a known cause and no security surface, needs no QA agent if the developer shows a regression test failing first. The PM reviews the diff and runs the tests.
  - QA writes probe files with the Write tool (not shell heredocs), reuses one probe file, and returns its report for the PM to save.

## 0.2.2 - 2026-09-16

### Changed
- **Commit messages are one line.** No body, no bullet lists. No trailers either (no `Co-Authored-By`, no session links). The reasoning goes in the pull request and in `decisions.md`. A change that needs paragraphs to explain is too big and gets split.

## 0.2.1 — 2026-09-15

### Added
- **`standards/launch-security.md`:** a "before going live" checklist covering production settings, security headers, private files that must not be reachable, accounts, backups with a tested restore, and monitoring. Also a free attack-style scan of staging (OWASP ZAP baseline, header and HTTPS graders) and after-launch rules (Dependabot, patching within a week, an incident plan). Every deploy or launch story is now Sensitive and carries this checklist.

## 0.2.0 — 2026-09-15

Shaped by the first real pilot (a Laravel news site), a review of the most-starred AI coding frameworks, and the official Claude Code docs. Details are in `report/`.

### Added
- **Permission rules**, installed into `settings.json`: agents can't read or write `.env` files; `migrate:fresh`, `db:wipe` and force-push are denied; `git push`, `git reset --hard`, `git branch -D` and `migrate --force` ask first.
- **PowerShell coverage** in the command guard.
- **`format_php.py` hook:** runs the project's own Pint on PHP files, only when that can't reformat lines a task didn't touch.
- **Tests** for every hook and for the installer: `python -m unittest discover -s tests`.
- **`install.py`**, a cross-platform installer with `--dry-run`, `--uninstall` and `--target`, plus a manifest so updates remove exactly what they added.
- **`company/pm-brief.md`:** a short operating brief for the main session, about a quarter of the full charter's size.
- **`standards/design-approach.md`:** the "do we even need this code?" ladder, then a pattern table (strategy, factory, action, pipeline, events, adapter…).
- **Agents:**
  - a report status line (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`)
  - failing-test-first evidence
  - report length caps
  - "Gotchas" learned on the pilot
  - `maxTurns` runaway caps
- **Security:**
  - an OWASP Top 10:2025 checklist
  - fail-closed error handling
  - a five-question threat check for Sensitive tasks
  - rules for code that calls an AI model
  - `/security-review` in the Sensitive lane
- **Design options:** `/new-project` Step 3b shows three look-and-feel directions the user can see and compare (colours, fonts, a real screen) instead of asking for hex codes. The chosen one becomes design tokens in `conventions.md`, and the frontend agent uses only those.
- **Greenfield toolchain default:** Pint, Pest architecture tests, Larastan, `composer audit`, and a recorded check command.

### Changed
- **`/next-story`:**
  - one developer and one QA at a time
  - a BASE commit per task, with reviews of `git diff BASE`
  - fix rounds continue the same agent
  - finished stories move to `backlog-done.md`
  - stale facts are refreshed when they change
- The working agreement moved to `company/working-agreement.md` and is **imported** by one line in `~/.claude/CLAUDE.md`, so your own `CLAUDE.md` is kept.
- Hooks now install to `~/.claude/hooks/agent-company/`.
- Project files are `.claude/project/` everywhere; some standards still said `projects/<name>/`.

### Fixed
- The installer replaced every existing hook in `settings.json`. It now merges them.
- **Command guard:**
  - no longer false-alarms on quoted text such as commit messages
  - now catches pushes to main, `rm -rf ./`, force branch deletion and `migrate --force`
  - PowerShell was not checked at all before
- **Path guard:** now protects `wp-config.php`, private keys and more lock files.
- **Secret scanner:**
  - now catches secrets used as `env()` defaults, WordPress `define()` values, and any secret on a line that also contains words like `true`
  - fewer false alarms on validation rules and test data
- Removed stale "this repository is not a git repository" notes.

## 0.1.0

First version: six role charters, company standards, three safety hooks, and the `/new-project` and `/next-story` skills.
