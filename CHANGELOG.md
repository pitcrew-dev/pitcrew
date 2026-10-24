# Changelog

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
