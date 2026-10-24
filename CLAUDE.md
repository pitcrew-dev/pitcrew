# CLAUDE.md

This repository is **agent-company**, a Claude Code framework that runs a project like a small software company: a Project Manager (the main session) plus developer, code-review and QA agents, for PHP work (Laravel, plain PHP, WordPress). It ships as a Claude Code plugin named `company` (marketplace `agent-company`) and is then used from any project.

## How to answer the user

Always explain in **simple, short, clear words**, without being asked.

- Plain language, no jargon. If a technical term is unavoidable, explain it in one line.
- Short: lead with the answer, then only the details that matter.
- Use small tables or bullets instead of long paragraphs.

## Layout

| Path | What it is |
|---|---|
| `plugin/.claude-plugin/plugin.json` | Plugin manifest; `version` must equal `VERSION` |
| `.claude-plugin/marketplace.json` | Marketplace manifest; install id `company@agent-company` |
| `plugin/company/working-agreement.md` | Always-loaded rules, injected at session start by the `load_agreement` hook |
| `plugin/company/pm-brief.md` | The main session's operating brief |
| `plugin/company/employees/` | Full role charters, read on demand |
| `plugin/company/standards/` | Standards; `engagement-modes.md` governs the rest |
| `plugin/agents/`, `plugin/skills/` | 5 subagents (`company:*`); `/company:start`, `/company:next`, `/company:status`, `/company:report` |
| `plugin/hooks/` | `hooks.json`, the `run` launcher (finds Python), the safety, formatting, activity-log and budget hooks (Python), `costs.py` (shared cost and budget reading), `cost_summary.py` (run by `/company:status` and `/company:report`) and `agent_status.py` (the agent status line) |
| `plugin/settings.json` | Turns on the agent status line |
| `plugin/evals/` | Plugin evals (`claude plugin eval`), and `fixtures/salon/`, the sample project they and the README use |
| `.github/workflows/ci.yml` | Tests on Windows, macOS and Linux and the plugin check on every push; the paid evals on demand |
| `install.py` (+ `install.sh`) | Removes an old 0.2.x install (`--uninstall`); kept for one release, not part of the plugin |
| `tests/` | Tests for the hooks, the manifests and the uninstaller |
| `report/` | Research and reviews behind design decisions; not shipped |

## Commands

```bash
python -m unittest discover -s tests -v   # run before every commit
claude --plugin-dir ./plugin              # try the plugin in a session
claude plugin validate ./plugin           # check the manifests (also: claude plugin validate .)
```

## Rules for changing this repo

- **Edit under `plugin/`.** Try a change with `claude --plugin-dir ./plugin`.
- **A plugin cannot ship permission rules**, so every deny and ask rule lives in a hook (`guard_paths.py`, `guard_bash.py`) with a test.
- **Hook commands go through `plugin/hooks/run`** (it must keep LF line endings; see `.gitattributes`).
- **Every hook change comes with a test** in `tests/test_hooks.py`. Hooks fail open, exit 2 to block, and stay silent when all is well.
- **Tokens are a design constraint:**
  - the working agreement stays under ~90 lines
  - agent briefs stay short and point to standards instead of restating them
  - standards are read on demand
- **The precedence ladder governs every rule you add** (`engagement-modes.md`): the existing project wins, and security never yields.
- **Role charters keep their shape:** header, a decides / does-not-decide table, mission, numbered duties with exit criteria, anti-patterns, success criteria. Prescriptive prose and tables, no code.
- **Bump `VERSION` and add a `CHANGELOG.md` entry** for anything a user would notice.
- **Commits:** Conventional Commits, **one line only, no trailers**, one concern per commit.

## Status

Six roles are written: PM, backend, frontend, full-stack, code-reviewer, QA. The rest (security, architect, devops, UX, BA, product owner) are not; the PM covers them or escalates to the user. The first real pilot, a Laravel news site, is reviewed in `report/`.
