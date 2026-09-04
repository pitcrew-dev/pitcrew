# Agent Company

A project-manager-led AI development company for Claude Code. Installs globally
so any project on this machine can use it.

## Install

```bash
bash install.sh --dry   # preview; touches nothing
bash install.sh         # install or update
```

Copies `home/` into `~/.claude/`, merging `agents/` and `skills/` per item so
anything you already have is kept, and merging hooks into `settings.json` so
your existing settings survive. Everything replaced is backed up under
`~/.claude/.backup/<timestamp>/`.

Restart Claude Code afterwards.

## Use, from any project directory

| Say | What happens |
|---|---|
| "I want to build a website for my business" | Interview in plain language, survey any existing code, produce a plan, **stop for approval** |
| "go" / "next" | Build one story through developer -> code review -> QA, **stop for approval** |

## Structure

`home/` mirrors `~/.claude/` exactly — edit here, run `install.sh`, done.

```
home/
├── CLAUDE.md              # working agreement, loaded in every session (73 lines)
├── agents/                # 5 dispatchable subagents
├── skills/                # /new-project, /next-story
├── hooks/                 # deterministic guards (paths, commands, secrets)
├── company/
│   ├── employees/         # 6 role charters
│   └── standards/         # 8 standards; engagement-modes.md governs the rest
└── settings.hooks.json    # hook config, merged into your settings.json
```

Project artifacts are written into the target project at `.claude/project/`.

## How it is meant to work

The **main session is the Project Manager** — it talks to you, clarifies, plans,
dispatches, and reports. It never writes production code. Specialists run as
subagents; every completed task passes two independent gates (code review, then
QA), both of which deliberately lack editing tools.

Ceremony is matched to risk so a typo does not cost what a payment flow does:
Direct (0 agents), Light (1), Standard (3), Sensitive (3 + your approval).

In an existing codebase, **the project's conventions outrank these standards.**
Security is the one thing that never yields.

## Status

Six of eleven roles are written: project-manager, backend/frontend/full-stack
developer, code-reviewer, qa-engineer. Still unwritten: solution-architect,
security-engineer, ui-ux-designer, product-owner, business-analyst,
devops-engineer — where a charter routes to one of those, the PM handles it or
escalates to you.

**This has not yet been run on a real project.** Everything here is reasoned,
none of it is validated by use.
