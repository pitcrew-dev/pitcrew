# agent-company

A Claude Code framework that runs your project like a small, disciplined software company.

You talk to a **Project Manager** in plain language. It plans the work, hands each piece to a specialist agent, and checks every result before showing it to you: one QA run per piece in **Quick** mode (the default), or code review and QA on every task in **Careful** mode. Built for PHP work: modern and legacy Laravel, plain PHP, and WordPress.

## Why use it

- **Your existing code wins.** On an existing codebase it surveys first, then matches the project's own conventions, versions and structure. No "modernizing" your code as a side effect.
- **Independent checks.** A reviewer asks *is this fit to merge?*; QA asks *does it do what was asked?* Neither can edit code, so neither can quietly paper over a problem. Quick mode runs QA once per piece; Careful mode runs both on every task.
- **Ceremony matched to risk.** A typo costs nothing extra. Logins, payments, personal data and migrations get a security review and **your approval**.
- **Safety that doesn't depend on the AI remembering.** Hooks keep agents out of `.env`, stop destructive commands, and scan every written file for secrets.
- **You always know what it costs.** Every agent run is logged with its measured cost. Each piece of work has a budget: a warning at 80%, and at 100% it stops and asks you.
- **Built to spend tokens carefully.** Short agent briefs, standards read only when needed, reviews of the diff instead of the whole story, and fix rounds that continue the same agent instead of starting over.

## Requirements

- [Claude Code](https://code.claude.com)
- Python 3.8+ (for the hooks; nothing else to install)
- git

## Install

In Claude Code:

```
/plugin marketplace add kasshif01/vide_coding
/plugin install company@agent-company
```

Then restart Claude Code. To try it without installing, from a clone: `claude --plugin-dir ./plugin`.

The plugin adds 5 agents (`company:backend-developer`, `company:frontend-developer`, `company:full-stack-developer`, `company:code-reviewer`, `company:qa-engineer`), the `/company:start`, `/company:next`, `/company:fix`, `/company:status` and `/company:report` commands, the safety hooks, and an activity log with costs and budgets. It does not touch your `~/.claude/settings.json` or `CLAUDE.md`.

### Your first ten minutes

1. **Install** (above). Claude Code asks for two budgets: per piece of work ($12 is a good start) and per project (0 for no limit). You can change both later in `/config`.
2. **Open your project folder** in Claude Code, empty or with existing code.
3. **Say what you want**, e.g. `/company:start I want a website for my salon where customers can book online`.
4. **Answer one round of 3 to 5 questions.** Every question has a default; skip what you don't know. For existing code, it reads the code first and asks less.
5. **Read the plan:** your goals, the pieces in order, what it assumed, what it left out, the budget, and what it needs from you. Ask for design options if you want to pick a look.
6. **Say "go"** and it builds the first piece.

In our test (a new salon booking site), steps 3 to 5 took about 4½ minutes of AI time and cost about $1.65.

If you had version 0.2.x installed, the first session tells you, and shows the one command that removes it.

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
| "go" / "next" | `/company:next`: builds one piece (checks depend on the mode, below), then shows you the result and what it cost, and **stops**. |
| "it's broken" / "fix this error" | `/company:fix`: one problem, one developer. It writes a test that fails, fixes it, shows it passing, and **stops**. |
| "where are we?" | `/company:status`: one screen with progress per goal, money spent and left, what's next, and anything waiting on you. |
| "write me an update" | `/company:report`: a one-page report you can send to a client or manager, saved in `.claude/project/reports/`. |

Its working files go in `<your-project>/.claude/project/`. Commit them. They are the team's shared memory between sessions.

| File | What it holds |
|---|---|
| `plan.md` | Where we are, your request, goals, the pieces with their tasks, and what's done |
| `decisions.md` | Choices and who made them, plus the risks |
| `conventions.md` | The project's own rules and how to check it |
| `lessons.md` | Mistakes not to repeat |
| `budget.md` | Budgets (default $12 a piece) and the mode |
| `activity.md` | One line per agent run, with its cost |

**Undo:** every task is its own commit, so you can say "undo that" or use Claude Code's `/rewind`.

### Quick or Careful

| | Quick (default) | Careful |
|---|---|---|
| Each task | One developer; the PM checks the diff and tests | Developer, then code review, then QA |
| End of a piece | One QA run for the whole piece | Already done per task |
| Logins, payments, personal data, database changes, going live | Always the careful checks, plus your approval | Same |
| Rough cost per piece | About $7 (an estimate, not yet measured) | About $17 (pilot average) |

Turn Careful on in the plugin settings, or per project with a `Mode:` line in `budget.md`.

## How a piece of work flows

This is the Careful flow. In Quick, steps 3 and 4 become one QA run after the piece's last task.

1. The PM checks the task is fully specified, picks the lane, and records the starting commit.
2. One developer agent builds it, with tests it has **seen fail first**. It can stop and ask the PM for missing context instead of guessing.
3. The code reviewer reviews the diff against the project's conventions and the security floor.
4. QA verifies every acceptance criterion and tries to break it.
5. Sensitive work always gets the full flow, `/security-review` and your approval.
6. The PM commits, updates the project files, reports in plain language, and stops.

A failed check goes back to the **same** developer, with its context intact. Three failures on one task is a hard stop, and the PM brings it to you with a recommendation.

## Try it on the example project

`plugin/evals/fixtures/salon/` is a half-built salon booking site with its project files filled in. Copy it somewhere, open the copy in Claude Code with the plugin loaded, and try `/company:status` or `/company:report`.

## Develop

```bash
python -m unittest discover -s tests -v   # the hooks, manifests and uninstaller
claude plugin validate ./plugin --strict  # the plugin files
cd plugin && claude plugin eval . --scaffold --trust-plugin --runs 1 --ablation none   # the evals (paid)
```

The evals in `plugin/evals/` cover starting a project, a story stopped by its budget, status, the report, the fix command, and the notice about an old install. They are real model calls. On Windows, status and report can't run their cost script (shell commands need a sandbox Windows doesn't have), so run the full suite on Linux or macOS, or in CI.

CI (`.github/workflows/ci.yml`) runs the tests on Windows, macOS and Linux and checks the plugin on every push. The evals run when started by hand, with an `ANTHROPIC_API_KEY` secret.

See `CLAUDE.md` for the layout and the rules for changing the framework, and `CHANGELOG.md` for what changed.

## Status and limits

- **Version 1.0.0**. Piloted on one real Laravel project; the findings are in `report/`.
- Six of eleven roles are written. There is no dedicated security, architecture or devops agent yet: the PM covers them, or asks you.
- Permission rules and hooks are a **floor, not a gate**. A Bash permission rule isn't a hard security boundary (`git -C . push` is spelled differently from `git push`), which is why the hooks back them up.
- Tested by hand on Windows (Git Bash and PowerShell). CI runs the tests on macOS and Linux too.
- Costs are **API-equivalent**: what the work would cost at Anthropic's pay-per-use prices. On a subscription you don't pay this per token; it shows where the effort went.
- **License:** MIT.
