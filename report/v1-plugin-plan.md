# v1 plan: Agent Company as a Claude Code plugin

**Status:** approved 2026-10-09 · M0–M6 done · **Date:** 2026-10-09 · **Current version:** 0.2.5 → **target 1.0.0**

## 1. The goal in one line

A software company inside Claude Code. **You're the board, Claude runs the company, and you always know what it's doing and what it costs.**

## 2. Decisions already made

| Decision | Choice | Decided by |
|---|---|---|
| Who it's for at launch | PHP developers: Laravel, WordPress, plain PHP | User |
| How it's installed | Claude Code plugin, through a marketplace | User |
| How much it does on its own | Stops for approval after every story. Autopilot comes in v3 | User |
| Which AI | Claude only | User |
| Ideas taken from Paperclip | Goals, budgets, activity log, live status. Its server, dashboard and database are left out on purpose | PM recommendation, user agreed |

## 3. What a user experiences in v1

| Moment | What they do | What they see |
|---|---|---|
| Install | `/plugin marketplace add <repo>`, then `/plugin install agent-company` | One prompt for budget defaults, then "ready" |
| Start | `/company:start` | The friendly interview, then a plan with **goals**, stories and a budget, and it stops for approval |
| Build | `/company:next` | One story built, reviewed and tested. The agent line shows who is working. It ends with "what you can now see and do", plus cost against budget |
| Check in | `/company:status` | One page: progress per goal, money spent and left, what's next, anything waiting on them |
| Weekly | `/company:report` | A report they can send to a client or manager: done, cost, risks, next |
| Upgrade | Run once if they're on 0.2.x | The plugin notices the old install, explains it in plain words, and offers to remove it with a backup |

## 4. Scope

**In v1**

1. Plugin packaging, a marketplace, and moving users off the old install
2. Goals: every story links to a goal, and progress is reported per goal
3. Budgets: per project and per story, warning at 80%, pause at 100% until the user approves more
4. Activity log: one line per agent run (when, story, agent, result, cost)
5. Status: `/company:status`, the agent status line, and `/company:report`
6. A polished first run: install to first approved plan in under 10 minutes
7. Professional release: README, docs, examples, validation in CI, evals, a clean changelog

**Not in v1, moved to later**

| Item | Release |
|---|---|
| Hiring new roles (security, architect, DevOps, designer) | v2 |
| Company memory beyond `lessons.md` | v2 |
| Autopilot / scheduled work | v3 |
| Multi-project overview | v3 |
| Languages other than PHP | Later, as stack packs |
| A web dashboard or server | Not planned. Files plus Claude Code is the product |

## 5. Facts from the Claude Code plugin docs that shape the design

Checked against the official plugin and hooks reference on 2026-10-09.

| Fact | What it means for us |
|---|---|
| A plugin **can't** ship permission rules. Only `agent` and `subagentStatusLine` settings apply | Today's deny/ask rules in `settings.fragment.json` move into the guard hooks. `guard_paths.py` must also block **reading** `.env` (today a permission rule does that) |
| A plugin **can't** load a `CLAUDE.md` | The working agreement is injected by a `SessionStart` hook (`additionalContext`) instead of one line in `~/.claude/CLAUDE.md` |
| Plugins can set the **subagent** status line, not the main one | The live line shows while agents work. The main status line is an optional extra the user turns on with one command. *This corrects what I said earlier.* |
| Everything is namespaced by plugin name | Commands become `/<name>:start`, agents `<name>:qa-engineer`. The short name matters, see §10 |
| Paths in skills and agents use `${CLAUDE_PLUGIN_ROOT}` | 10 files that point at `~/.claude/company/...` get rewritten |
| Hook input carries **no token counts** | Cost has to come from the agent's transcript or the result summary. Spike first (M0) |
| Hooks need an interpreter on PATH | The installer used to fill in the exact Python path. A plugin can't, so we need a safe way to find Python on Windows, macOS and Linux (M0) |
| Names starting `claude-` or `anthropic-` are refused | Pick a product name of our own |
| `claude plugin validate --strict` and `claude plugin eval` exist | Use both in CI and before every release |

## 6. Plugin layout

```text
agent-company/                    (repo root = the marketplace)
├── .claude-plugin/marketplace.json
└── plugin/
    ├── .claude-plugin/plugin.json      name, version 1.0.0, userConfig (budget defaults)
    ├── settings.json                   subagentStatusLine
    ├── skills/  start/ next/ status/ report/ (+ migrate/)
    ├── agents/  backend-, frontend-, full-stack-developer, code-reviewer, qa-engineer
    ├── company/ working-agreement, pm-brief, employees/, standards/   (read on demand, as now)
    ├── hooks/hooks.json + *.py         guards, secrets, formatting, reload, context, activity log
    └── evals/                          scripted checks of the main flows
```

`home/` becomes `plugin/`. `install.py` stays for one release, but only to **uninstall** the 0.2.x version.

## 7. New project files (in the user's project, `.claude/project/`)

| File | Holds | Rule |
|---|---|---|
| `goals.md` | 2–5 goals, each with an ID, a plain-words outcome, and "done when" | Written at `/company:start`. Changed only with the user's OK |
| `budget.md` | Project budget, per-story default, spent so far, approved top-ups | Updated after each story |
| `activity.md` | One line per agent run: time, story, agent, result, cost | Append only, never edited |
| `backlog.md` | Gets one new field per story: `goal: G1` | A story with no goal gets questioned |

Existing projects keep working. On their first `/company:next`, the PM proposes `goals.md` built from the existing backlog and asks for approval.

## 8. Milestones

Each milestone ends with tests passing and a working plugin. Effort is a rough guess.

| # | Milestone | Done when | Effort |
|---|---|---|---|
| **M0** ✅ | **Spikes: answer the unknowns** (results in §12) | (a) We can read real token cost per agent run, or there's a documented fallback. (b) Hooks run on Windows, macOS and Linux without a hard-coded Python path. (c) The plugin loads alongside the old install, with the clash shown | 1 day |
| **M1** ✅ | **Repackage, same behaviour** | `claude plugin validate --strict` passes. All 0.2.5 behaviour works from the plugin: the same tests pass, `.env` reads are blocked by a hook, the working agreement is injected at session start | 2 days |
| **M2** ✅ | **Moving off 0.2.x** | The plugin detects the old install and offers a one-step removal with a backup. Tested on a copy of a real 0.2.5 setup. Project files are untouched | 1 day |
| **M3** ✅ | **Goals** | `/company:start` writes `goals.md`. Every story has a goal. Status and report group by goal. Old projects are offered goals on first run | 1 day |
| **M4** ✅ | **Activity log and cost** | Every agent run adds one line to `activity.md`, written by a hook rather than left to the AI. Cost per story is shown at the end of `/company:next` | 1–2 days |
| **M5** ✅ | **Budgets** | Warning at 80%. At 100% the PM stops and asks before the next dispatch, never mid-task. Defaults come from `userConfig` and can be changed per project. These are added to the stop rules in `token-budget.md` | 1 day |
| **M6** ✅ | **Status and report** | `/company:status` (one screen) and `/company:report` (shareable) both work on an empty, a half-done and a finished project. The subagent status line shows the agent, story and budget used | 1–2 days |
| **M7** | **First-run polish** | A new user goes from install to an approved plan in under 10 minutes on a sample project. Every message passes the plain-words check | 1 day |
| **M8** | **Release** | README with a demo GIF, docs, an example project, CI (tests + validate + evals), `CHANGELOG` 1.0.0, a tagged release, and the marketplace live | 1–2 days |

**Total: about 10–13 working days.** Order: M0 → M1 → M2 must come first. M3–M6 can then go one story at a time, then M7 and M8.

## 9. Quality bar for release

- [ ] All existing tests pass, plus new tests for every new or changed hook
- [ ] `claude plugin validate --strict` is clean
- [ ] Evals cover start, next, status, report and migrate on a sample Laravel project
- [ ] Tested on Windows (Laragon), macOS and Linux
- [ ] Moving from 0.2.5 tested on a real setup: project files untouched, backup created
- [ ] Security floor unchanged: `.env`, secrets, destructive commands and core files are still blocked
- [ ] The working agreement stays under ~90 lines, and no new always-loaded text beyond what the hook injects
- [ ] Every user-facing message reviewed for plain words

## 10. Decisions on naming, licence and budget (user, 2026-10-09)

| Question | Decision |
|---|---|
| Product name and command prefix | Plugin name `company` (short commands such as `/company:next`), display name "Agent Company" |
| Public or private repo for the marketplace | Public on GitHub, MIT licence |
| Default budget | Measured on real stories in M0, then the default is set from that |

## 11. Risks

| Risk | Effect | Plan |
|---|---|---|
| ~~Token cost can't be read reliably~~ | — | Closed in M0: exact usage is in the transcripts (§12a) |
| Python missing or under a different name | Hooks silently don't run, and the safety floor is gone | M0. Hooks fail open today, so in v1 the plugin checks at session start and warns plainly if Python is missing |
| Old install and plugin both active | Duplicate agents, hooks run twice | M2 detection and a one-step removal |
| Moving rules from permissions into hooks misses a case | Weaker safety floor | Port every current deny/ask rule into a hook test before deleting `settings.fragment.json` |
| Plugin features change (status line, monitors are marked experimental) | Breakage after a Claude Code update | Use only stable features in v1. Validate in CI against the latest Claude Code |

## 12. M0 results (2026-10-09)

Tested on Windows 11, Claude Code 2.1.294, with a throwaway plugin. macOS and Linux are **not tested yet**; that moves to the M8 release checklist.

### (a) Cost can be measured exactly

- The `SubagentStop` hook receives `agent_transcript_path`. That file has a `usage` block on every model call (fresh input, cache writes, cache reads, output, model name). Count each message `id` once, because one message can appear on several lines.
- The `.meta.json` next to each agent transcript gives the agent type. The main session's own transcript (`transcript_path`) gives the PM's cost the same way.
- **Raw token totals are misleading.** In the pilot, 96% of tokens were cache reads, which cost 1/10 of fresh input. Budgets are therefore kept in **API-equivalent dollars**, priced per model from a small table shipped with the plugin (Sonnet 5/5.5 $2 / $10 / $0.20 read, Opus 5.5 $4 / $20 / $0.20 read, cache write = 1.25× input). Subscription users pay no per-token bill, so the UI says "API-equivalent", not "spent".

**Measured on the news pilot** (13 stories, 27 tasks, 75 agent runs, all sessions):

| | Cost |
|---|---|
| Whole pilot | ≈ $223 (PM ≈ $88, agents ≈ $135) |
| Per story (average) | ≈ $17 |
| Per run, median: reviewer / QA / backend / frontend | $0.39 / $1.02 / $1.55 / $0.89 |
| Worst single run | $18 (a backend run inside the story that took 3 failed gate cycles) |

**The PM is about 40% of the cost**, so a story's cost must include the main session, not just the agents.

**Default budget, from these numbers:** **$25 per story** (warning at $20). That covers a normal story and catches a runaway. **No default project cap.** At `/company:start` the PM suggests one: number of stories × $17, rounded up.

### (b) Hooks find Python without a hard-coded path

- On this machine `python` and `py` exist, but `python3` doesn't. On macOS and Linux it's usually the other way round, so no single name works everywhere.
- **Working design:** each hook runs as `sh "${CLAUDE_PLUGIN_ROOT}/hooks/run" <name>`. The small `run` script tries `python3`, `python`, then `py`, keeps the first one that really runs Python 3.8+ (this skips the Windows Store fake `python3`), and saves the choice to `${CLAUDE_PLUGIN_DATA}/python-path`. If none works, it exits 0, so the hook fails open.
- Verified: the hook ran, it found `C:\...\Python314\python.exe`, and `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` were both set.
- **Cost:** about 90 ms more per hook call than calling Python directly (170 ms vs 80 ms on Windows). Acceptable. Revisit if it ever feels slow.
- **Still needed:** if Python can't be found, a session-start check must say so plainly, because silently running without safety hooks is not acceptable (§11).
- **Assumption:** `sh` exists. That is true with Git for Windows, which Laragon users normally have. Test on a Windows machine without Git Bash in M8.

### (c) The plugin and the old install clash. Confirmed

- A `SessionStart` hook can inject context: the injected line reached the model. **This is how the working agreement will be loaded.**
- With both installed, the model saw **two QA agents**, `company:qa-engineer` and the old `qa-engineer`, and the old `next-story` skill was still listed. **M2 (moving off 0.2.x) is required**, not optional.
- The plugin passes `claude plugin validate`. Its only warning was a missing `author`.

### What changes in the plan

| Area | Change |
|---|---|
| §5 "no token counts" | Solved: transcripts via `SubagentStop` and the main `transcript_path` |
| §5 "interpreter on PATH" | Solved: the `hooks/run` launcher, with a session-start warning if Python is missing |
| M4 | Write the cost reader once and use it for both the activity log and budgets. Include the PM's cost |
| M5 | Defaults: $25 per story, warning at 80%, no project cap unless the user sets one |
| §11 risk 1 | Closed. The estimate fallback isn't needed |

## 13. After v1

- **v2, grow the team:** a hiring flow with approval, security and architect roles, company memory
- **v3, autopilot:** scheduled Light-lane work that queues for approval, and a multi-project overview
