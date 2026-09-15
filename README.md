# agent-company

A Claude Code framework that runs your project like a small, disciplined software company.

You talk to a **Project Manager** in plain language. It plans the work, hands each piece to a specialist agent, and puts every result through **two independent checks** (code review, then QA) before showing it to you. Built for PHP work: modern and legacy Laravel, plain PHP, and WordPress.

## Why use it

- **Your existing code wins.** On an existing codebase it surveys first, then matches the project's own conventions, versions and structure. No "modernizing" your code as a side effect.
- **Two gates on every change.** A reviewer asks *is this fit to merge?*; QA asks *does it do what was asked?* Neither can edit code, so neither can quietly paper over a problem.
- **Ceremony matched to risk.** A typo costs nothing extra. Logins, payments, personal data and migrations get a security review and **your approval**.
- **Safety that doesn't depend on the AI remembering.** Permission rules and hooks keep agents out of `.env`, stop destructive commands, and scan every written file for secrets.
- **Built to spend tokens carefully.** Short agent briefs, standards read only when needed, reviews of the diff instead of the whole story, and fix rounds that continue the same agent instead of starting over.

## Requirements

- [Claude Code](https://code.claude.com)
- Python 3.8+ (for the installer and the hooks; nothing else to install)
- git

## Install

```bash
git clone <repository-url> agent-company
cd agent-company
python install.py --dry-run   # shows exactly what would change
python install.py
```

Then restart Claude Code. To update: `git pull && python install.py`. To remove: `python install.py --uninstall`.

### What the installer changes

| Where | What | Your own things |
|---|---|---|
| `~/.claude/CLAUDE.md` | Adds **one import line** for the working agreement | Kept |
| `~/.claude/company/` | Working agreement, PM brief, role charters, standards | — |
| `~/.claude/agents/` | 5 agents (`backend-developer`, `frontend-developer`, `full-stack-developer`, `code-reviewer`, `qa-engineer`) | Kept. Same-named ones are replaced and backed up |
| `~/.claude/skills/` | `new-project`, `next-story` | Kept |
| `~/.claude/hooks/agent-company/` | 4 hooks | — |
| `~/.claude/settings.json` | Adds the hooks and permission rules below | Everything else kept |

Everything replaced is backed up to `~/.claude/.backup/<time>/`. A manifest records what was added, so updates and uninstall touch only that. If your `settings.json` isn't valid JSON, the installer changes nothing.

### Safety rules it adds (they apply in every project)

| Kind | Rules |
|---|---|
| **Denied** | Reading or writing `.env`, `.env.local`, `.env.production`, `.env.staging`; `migrate:fresh`, `migrate:reset`, `db:wipe`; force-push |
| **Asks you first** | `git push`, `git reset --hard`, `git branch -D`, `migrate --force`, PowerShell `Remove-Item` |
| **Hooks** | Block writes to `vendor/`, `node_modules/`, build output, lock files, WordPress core, `wp-config.php` and private keys; stop irreversible Bash and PowerShell commands; flag secrets in written files; format PHP with the project's own Pint when that can't reformat old code |

You can change any rule in your `settings.json`. Uninstall removes only the rules the installer added.

## Use

From any project directory, in Claude Code:

| You say | What happens |
|---|---|
| "I want to build a booking site for my salon" or "take over this codebase" | `/new-project`: a short plain-language interview, a survey of any existing code, then a plan in pieces you can see working. **It stops for your approval.** |
| "go" / "next" | `/next-story`: builds one piece through developer → review → QA, then shows you the result and **stops**. |

Its working files go in `<your-project>/.claude/project/`: conventions, backlog, board, decisions, risks and status. Commit them. They are the team's shared memory between sessions.

## How a piece of work flows

1. The PM checks the task is fully specified, picks the lane, and records the starting commit.
2. One developer agent builds it, with tests it has **seen fail first**. It can stop and ask the PM for missing context instead of guessing.
3. The code reviewer reviews the diff against the project's conventions and the security floor.
4. QA verifies every acceptance criterion and tries to break it.
5. Sensitive work gets `/security-review` and your approval.
6. The PM commits, updates the project files, reports in plain language, and stops.

A failed check goes back to the **same** developer, with its context intact. Three failures on one task is a hard stop, and the PM brings it to you with a recommendation.

## Develop

```bash
python -m unittest discover -s tests -v
```

See `CLAUDE.md` for the layout and the rules for changing the framework, and `CHANGELOG.md` for what changed.

## Status and limits

- **Version 0.2.0.** Piloted on one real Laravel project; the findings are in `report/`.
- Six of eleven roles are written. There is no dedicated security, architecture or devops agent yet: the PM covers them, or asks you.
- Permission rules and hooks are a **floor, not a gate**. A Bash permission rule isn't a hard security boundary (`git -C . push` is spelled differently from `git push`), which is why the hooks back them up.
- Tested on Windows (Git Bash and PowerShell). The hooks and installer are plain Python and are written to run on macOS and Linux too.
- **License:** not chosen yet.
