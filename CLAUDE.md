# CLAUDE.md

This repository is **agent-company**, a Claude Code framework that runs a project like a small software company: a Project Manager (the main session) plus developer, code-review and QA agents, for PHP work (Laravel, plain PHP, WordPress). It is installed into `~/.claude/` and then used from any project.

## How to answer the user

Always explain in **simple, short, clear words**, without being asked.

- Plain language, no jargon. If a technical term is unavoidable, explain it in one line.
- Short: lead with the answer, then only the details that matter.
- Use small tables or bullets instead of long paragraphs.

## Layout

| Path | Installed to | What it is |
|---|---|---|
| `home/company/working-agreement.md` | `~/.claude/company/` | Always-loaded rules, imported by one line in `~/.claude/CLAUDE.md` |
| `home/company/pm-brief.md` | `~/.claude/company/` | The main session's operating brief |
| `home/company/employees/` | `~/.claude/company/` | Full role charters, read on demand |
| `home/company/standards/` | `~/.claude/company/` | Standards; `engagement-modes.md` governs the rest |
| `home/agents/`, `home/skills/` | `~/.claude/agents/`, `~/.claude/skills/` | 5 subagents; `/new-project`, `/next-story` |
| `home/hooks/` | `~/.claude/hooks/agent-company/` | Safety and formatting hooks (Python) |
| `home/settings.fragment.json` | merged into `~/.claude/settings.json` | Hook wiring and permission rules |
| `install.py` (+ `install.sh`) | — | Installer: `--dry-run`, `--uninstall`, `--target` |
| `tests/` | — | Tests for the hooks and the installer |
| `report/` | — | Research and reviews behind design decisions; not installed |

## Commands

```bash
python -m unittest discover -s tests -v   # run before every commit
python install.py --dry-run               # what an install would change
python install.py                         # install or update ~/.claude
python install.py --uninstall             # remove everything it added
```

## Rules for changing this repo

- **Edit under `home/`, never `~/.claude/` directly.** Reinstall to try a change.
- **Every hook change comes with a test** in `tests/test_hooks.py`. Hooks fail open, exit 2 to block, and stay silent when all is well.
- **Tokens are a design constraint:**
  - the working agreement stays under ~90 lines
  - agent briefs stay short and point to standards instead of restating them
  - standards are read on demand
- **The precedence ladder governs every rule you add** (`engagement-modes.md`): the existing project wins, and security never yields.
- **Role charters keep their shape:** header, a decides / does-not-decide table, mission, numbered duties with exit criteria, anti-patterns, success criteria. Prescriptive prose and tables, no code.
- **Bump `VERSION` and add a `CHANGELOG.md` entry** for anything a user would notice.
- **Commits:** Conventional Commits, one concern per commit.

## Status

Six roles are written: PM, backend, frontend, full-stack, code-reviewer, QA. The rest (security, architect, devops, UX, BA, product owner) are not; the PM covers them or escalates to the user. The first real pilot, a Laravel news site, is reviewed in `report/`.
