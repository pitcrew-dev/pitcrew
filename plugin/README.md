# PitCrew

An AI dev team inside Claude Code. Your main Claude session becomes a **project manager** that talks to you in plain words, plans the work in small pieces, and hands each piece to specialist agents: developers build it, a code reviewer and a QA engineer check it, a security engineer guards risky work, and a devops engineer prepares hosting without ever deploying. It stops for your approval after every piece, and it tells you what each piece cost.

Works with PHP (Laravel, plain PHP, WordPress), and with React and Next.js on PostgreSQL or MySQL through Prisma.

Full documentation, diagrams and examples: https://github.com/pitcrew-dev/pitcrew

## Install

```
/plugin marketplace add pitcrew-dev/pitcrew
/plugin install pit@pitcrew
```

## Use

| Command | What it does |
|---|---|
| `/pit:start` | Start a new project or take on an existing one: a few questions, then a plan for your OK |
| `/pit:next` | Build the next piece through the checks, then stop for your OK |
| `/pit:fix` | Fix one broken thing |
| `/pit:status` | Where the project stands, and what it has cost |
| `/pit:report` | A progress report you can send to a client or manager |

Agents: `pit:backend-developer`, `pit:frontend-developer`, `pit:full-stack-developer`, `pit:devops-engineer`, `pit:code-reviewer`, `pit:qa-engineer`, `pit:security-engineer`.

## What it runs on your machine

Everything runs locally. **PitCrew makes no network calls and sends no data anywhere** beyond your normal Claude Code session.

Its hooks are small, readable Python scripts in `hooks/`, started by `hooks/run`, a shell launcher that finds Python on your machine. They:

- **load the working agreement** (`crew/working-agreement.md`) at session start, and reload the project's plan after a compaction
- **guard files:** block reading or writing `.env` files, and writing dependencies, build output, lock files, private keys and WordPress core
- **guard commands:** block irreversible commands (database wipes, force-push, recursive deletes of root folders, `terraform destroy`), and **ask you first** before pushes, deploys, connections to servers, cloud CLIs and other risky commands. They answer Claude Code's permission check with "deny" or "ask"; they never change your permission settings
- **scan every written file for secrets** and warn the agent
- **format code with your project's own tools:** Pint for PHP and Prettier for JavaScript and TypeScript, only when your project already uses them, and never on old unformatted files. For this they run `git` and your project's own `vendor/bin/pint` or Prettier
- **track cost:** read your session's transcript file to price each agent run, write one line per run to `.claude/project/activity.md` in your project, and stop before a budget you set is passed
- **show a status line** for running agents

PitCrew writes its project files only to `.claude/project/` in your project.

## Data

PitCrew does not collect, store or send personal data. The cost log and project files stay in your project folder.

## License

MIT
