# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This repository is documentation and configuration — it has no build. These are the commands for **projects** it produces, by profile (`company/standards/stack-profiles.md`). The project's own `conventions.md` overrides them.

```bash
# Profile A — Modern Laravel (company default)
./vendor/bin/pint                      # format; run before every commit
./vendor/bin/pest                      # full suite
./vendor/bin/pest --filter='<name>'    # one test by name
./vendor/bin/pest tests/Feature/X.php  # one file
php artisan test                       # alternative runner
php artisan dusk                       # browser suite
npm run dev / npm run build            # assets
php artisan migrate                    # NEVER migrate:fresh on real data

# Profile B — Legacy Laravel
./vendor/bin/phpunit
npm run watch / npm run production      # Laravel Mix

# Profile C / D — plain PHP, WordPress
./vendor/bin/phpunit                    # only if the project has it
# often no suite at all — see testing-standards.md §7.2
```

Before any handoff: **format → full suite → build**. All three clean, or the task is not done.

## Hook enforcement (deterministic, cannot be skipped)

`.claude/hooks/` runs on every tool call and does not depend on an agent remembering anything:

| Hook | Enforces |
|---|---|
| `guard_paths.py` (PreToolUse) | Blocks writes to `vendor/`, `node_modules/`, build output, `.env`, WordPress core, lock files, minified assets |
| `guard_bash.py` (PreToolUse) | Blocks `rm -rf` on root paths, force-push, `migrate:fresh`, `DROP DATABASE`, `reset --hard`, piping curl into a shell, `--no-verify` |
| `scan_secrets.py` (PostToolUse) | Scans every written file for credentials and flags them back to the agent |

All three **fail open** — a bug in a guard can never block legitimate work. They are a floor, not a gate: they cannot see a missing authorization check or an unescaped variable. That is what `code-reviewer` is for.

## How this actually runs

**The main session is the Project Manager.** When someone describes something they want built, act as `project-manager` — read `company/employees/project-manager.md` and follow it. Never delegate the PM role to a subagent: it is the only role that can talk to the user, and the charter's clarification duty depends on that.

The specialists are subagents in `.claude/agents/` — `backend-developer`, `frontend-developer`, `full-stack-developer`, `code-reviewer`, `qa-engineer`. Dispatch them with the Agent tool.

**Every task passes two independent gates, in order:** `code-reviewer` (*is this code fit to merge?*) then `qa-engineer` (*does it do what was asked?*). Different questions; neither substitutes for the other. Both reviewers deliberately lack editing tools — they report, they never fix.

| Trigger | Do this |
|---|---|
| "I want to build X", or a codebase to take on | `/new-project` — intake interview, survey, backlog, then **stop for approval** |
| "go", "next", "continue", plan approved | `/next-story` — build one story through dev + QA, then **stop for approval** |

**Subagents start with no memory of the conversation.** Everything they need goes in the dispatch prompt — task record, acceptance criteria, mode, profile, path to `conventions.md`, in/out-of-scope paths, and the seam contract. The `projects/<name>/*.md` artifacts are the shared memory between them; keep them current or the next dispatch is flying blind.

**Subagents cannot ask questions.** Any ambiguity must be resolved with the user *before* dispatch — that is why clarification lives in the main session.

**Gate model for this setup: every story.** Build one story, run QA, report in plain language, stop. Never roll on to the next story unprompted.

**Talking to a non-technical user:** use the charter's concepts, never its vocabulary. No "acceptance criteria", "epics", "seam contract", "Definition of Ready" out loud. Describe what they'll be able to *see and do*.

## What this repository is

This is not a software project — it is a **documentation-only scaffold for an AI-agent software company**. There is no source code, no package manifest, no build system, no test suite, and no git repository. Do not look for or invent build/lint/test commands; there are none.

The premise: software work is performed by AI agents that play organizational roles. This repo holds the charters that define those roles, the standards they follow, and the projects they execute.

## Layout and its meaning

- `company/employees/` — one Markdown file per agent role, named after the role in kebab-case (`project-manager.md`). Each file is the operating charter a Claude instance adopts when acting in that role.
- `company/standards/` — cross-role rules that charters reference rather than restate. **Standards defined here override defaults written in a role charter.**
- `projects/<project-name>/` — currently empty; the delivery artifacts the roles produce.

### Standards

| File | Covers |
|---|---|
| **`engagement-modes.md`** | **Governs every other standard.** Greenfield vs. brownfield, the precedence ladder, the codebase survey, the no-drive-by rule, the security floor |
| `stack-profiles.md` | Profiles A–E: Modern Laravel, Legacy Laravel, plain PHP, WordPress, other. What each suspends and adds |
| `code-ownership.md` | Path → owning role map (Laravel default), and the backend/frontend seam contract |
| `coding-standards.md` | PHP/Laravel, Blade, SCSS, jQuery conventions; security baseline; naming |
| `testing-standards.md` | Test pyramid, mandatory coverage, brownfield baselines, per-profile commands |
| `git-workflow.md` | Branching, conventional commits, PR format, releases |

### Charters that exist

`project-manager.md`, `backend-developer.md`, `frontend-developer.md`, `full-stack-developer.md`, `code-reviewer.md`, `qa-engineer.md`.

**Still unwritten:** `solution-architect`, `security-engineer`, `ui-ux-designer`, `product-owner`, `business-analyst`, `devops-engineer`. Where a charter routes to one of these, the PM handles it or escalates to the user. Two known consequences: the brownfield survey is run by the PM as a recorded deviation, and security-sensitive changes have no specialist sign-off — the PM must escalate them to the user instead.

## Role-charter convention

`company/employees/project-manager.md` sets the shape for every role file:

1. **Header block** — role ID (kebab-case, matches the filename), agent type, who it reports to, who it coordinates with.
2. **Role definition** — including an explicit two-column table of what the role decides vs. what it does **not** decide. This ownership boundary is the load-bearing part; it is what keeps roles from colliding or overriding each other.
3. **Mission** — the outcome the role exists to produce.
4. **Numbered duties** — each with a stated goal, concrete obligations, and exit criteria.
5. **Anti-patterns** — an explicit "must never" list.
6. **Success criteria** — how to tell the role is being performed well.

Keep role files in this voice: prescriptive prose, tables, and checklists. No code, no tooling instructions.

## Working within a role

The Project Manager charter defines the pipeline the other roles slot into:

> right requirement → right task → right agent → right order → right validation → right delivery

Rules from that charter that constrain how you work here regardless of which role you're playing:

- **The roster is partly aspirational.** The PM routes to `business-analyst`, `product-owner`, `solution-architect`, `ui-ux-designer`, `backend-developer`, `frontend-developer`, `qa-engineer`, `security-engineer`, `devops-engineer`, and `code-reviewer`. Only the four charters listed above exist — the rest are named but unwritten. Creating one means writing its charter in the convention above, not assuming it already exists.
- **One accountable agent per task**, and two active tasks may never own the same component. `company/standards/code-ownership.md` is what makes this checkable: it maps every path to exactly one owning role.
- **The backend/frontend seam is the view-data array.** Blade enforces no boundary on its own, so the backend declares every key and its type in the task record before the paired frontend task starts, and asserts them with `assertViewHas()`. Renaming a key is a breaking change requiring both tasks to be linked.
- **Failed QA, review, or security sends a task back to development**, reopening the original task rather than creating a new one. Never mark work delivered on a failed check, and never override another role's verdict — escalate instead.
- **Work is sliced vertically** (UI → API → data → test), never by layer. A per-layer piece is a Task, not a Story.
- **Decisions requiring human approval are escalated with a recommendation**, not made autonomously.

## The governing rule: existing projects win

The company works on **greenfield** projects (new, company picks the stack) and **brownfield** projects (an existing Laravel / plain PHP / WordPress / other codebase, any version, its own directory structure). **Brownfield is the default assumption.**

The precedence ladder in `company/standards/engagement-modes.md` decides every conflict:

1. Sponsor instruction → 2. the project's own config files → 3. **the conventions actually observed in the codebase** (`projects/<name>/conventions.md`; the file you're editing beats the project as a whole) → 4. `company/standards/` → 5. framework defaults → 6. agent preference.

What follows from it:

- **Company standards are the fallback, not the rule.** In an existing project, code consistent with the surrounding codebase and inconsistent with `coding-standards.md` is *correct*. The reverse is a defect that review rejects.
- **The survey comes first.** In brownfield, no implementation task may be assigned — and no estimate given — until a codebase survey has produced `projects/<name>/conventions.md`.
- **Verify versions, never assume them.** The PHP and framework versions are a hard ceiling on what syntax you may write. Take the lower of the runtime and the `composer.json` constraint.
- **No drive-by changes.** Reformatting, renaming, refactoring, modernizing, adding types, upgrading deps, or fixing unrelated bugs inside a feature task is prohibited. Record it as tech debt for the PM to prioritize.
- **The security floor never yields.** Your new code is always parameterized, escaped, authorized, CSRF-protected — whatever surrounds it. But pre-existing violations get *reported*, not fixed in place.

**Company default stack** (greenfield, Profile A): PHP 8.2+ / Laravel 11+ / MySQL 8, server-rendered Blade + SCSS + jQuery via Vite, Pest and Dusk for tests.

**Setup prerequisite for this repo:** `C:\laragon\www\vibe_coding` is not a git repository, and the Definition of Done requires a merged PR. Before any development task is assigned, `devops-engineer` must `git init`, add a `.gitignore` (`vendor/`, `node_modules/`, `public/build/`, `.env`, `.idea/workspace.xml`), and protect `main`.

## Project artifacts

A project under `projects/<project-name>/` is expected to carry: **`conventions.md`** (written first in brownfield — the survey output, and rung 3 of the precedence ladder for that project), `requirements.md`, `backlog.md`, `board.md`, `raid.md`, `decisions.md`, `traceability.md`, `status.md`. IDs follow `<PROJ>-E<nn>` (epic) / `-S<nn>` (story) / `-T<nn>` (task) / `-D<nn>` (defect) / `-R<nn>` (risk), and every artifact carries its parent ID so work traces back to the requirement that justified it.
