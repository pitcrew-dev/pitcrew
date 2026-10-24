# agent-company

A Claude Code framework that runs your project like a small, disciplined software company.

You talk to a **Project Manager** in plain language. It plans the work, hands each piece to a specialist agent, and puts every result through **two independent checks** (code review, then QA) before showing it to you. Built for PHP work: modern and legacy Laravel, plain PHP, and WordPress.

## Why use it

- **Your existing code wins.** On an existing codebase it surveys first, then matches the project's own conventions, versions and structure. No "modernizing" your code as a side effect.
- **Two gates on every change.** A reviewer asks *is this fit to merge?*; QA asks *does it do what was asked?* Neither can edit code, so neither can quietly paper over a problem.
- **Ceremony matched to risk.** A typo costs nothing extra. Logins, payments, personal data and migrations get a security review and **your approval**.
- **Safety that doesn't depend on the AI remembering.** Hooks keep agents out of `.env`, stop destructive commands, and scan every written file for secrets.
- **Built to spend tokens carefully.** Short agent briefs, standards read only when needed, reviews of the diff instead of the whole story, and fix rounds that continue the same agent instead of starting over.

## Requirements

- [Claude Code](https://code.claude.com)
- Python 3.8+ (for the hooks; nothing else to install)
- git

## Install

In Claude Code:

```
/plugin marketplace add <path-or-repository>
/plugin install company@agent-company
```

Then restart Claude Code. To try it without installing, from a clone: `claude --plugin-dir ./plugin`.

The plugin adds 5 agents (`company:backend-developer`, `company:frontend-developer`, `company:full-stack-developer`, `company:code-reviewer`, `company:qa-engineer`), the `/company:start` and `/company:next` commands, and the safety hooks. It does not touch your `~/.claude/settings.json` or `CLAUDE.md`.

### Safety rules it adds (they apply in every project)

A plugin cannot ship permission rules, so these are enforced by hooks.

| Kind | Rules |
|---|---|
| **Denied** | Reading or writing `.env` files (not `.env.example`); `migrate:fresh`, `migrate:reset`, `db:wipe`; force-push |
| **Asks you first** | Every `git push`, `git reset --hard`, `git branch -D`, `migrate --force`, PowerShell `Remove-Item` |
| **Hooks** | Block writes to `vendor/`, `node_modules/`, build output, lock files, WordPress core, `wp-config.php` and private keys; stop irreversible Bash and PowerShell commands; flag secrets in written files; format PHP with the project's own Pint when that can't reformat old code |

A search over a whole folder can still match lines inside `.env`; only a path that points straight at a `.env` file is blocked.

## Use

From any project directory, in Claude Code:

| You say | What happens |
|---|---|
| "I want to build a booking site for my salon" or "take over this codebase" | `/company:start`: a short plain-language interview, a survey of any existing code, then a plan in pieces you can see working. **It stops for your approval.** |
| "go" / "next" | `/company:next`: builds one piece through developer → review → QA, then shows you the result and **stops**. |

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
