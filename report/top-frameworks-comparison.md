# What the most-loved AI coding frameworks do better — and what's worth taking

**Date:** 2026-09-15 · **Method:** star counts pulled live from the GitHub API today; READMEs and key files read for the top software-development repos · **Status:** report only — nothing changed.

---

## 1. Short answer

- **Your design is already in the same league as the top frameworks.** Its core ideas show up in repos with 50k–290k stars: role agents (BMAD), two review gates (superpowers), right-sized process (BMAD), and "think first, simplest, surgical" (karpathy-skills, 213k stars, which is almost word for word your global `CLAUDE.md` §1).
- **Your brownfield rule ("the existing project wins") is rarer than it should be.** Most top frameworks assume a fresh project; only OpenSpec makes existing codebases a main focus.
- **They're ahead on 8 small, cheap mechanics** (§4). The best ones fix problems your news pilot actually hit: agents going in circles, rework paying full startup cost again, bloated plan files, and parallel agents colliding.
- **Don't install any of the big frameworks whole.** The largest ones ship 68 agents and 292 skills (ECC), which is the opposite of "minimum tokens". Take the ideas, not the packages.

---

## 2. The repos developers love most (software development only)

Filtered out: marketing, research, video, prompt-leak and desktop-app repos.

| Stars | Repo | What it is | Relevant to us? |
|---:|---|---|---|
| 286.7k | [obra/superpowers](https://github.com/obra/superpowers) | Skills chain: brainstorm → worktree → plan → subagent build → TDD → review → finish | ✅ **Very** — closest to our delivery loop |
| 258.4k | [affaan-m/ECC](https://github.com/affaan-m/ECC) | Huge harness: 68 agents, 292 skills, hooks, rules, memory, "instincts", config security scan | ⚠ Ideas only — far too big |
| 213.0k | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | One `CLAUDE.md`: think first, simplicity, surgical changes, goal-driven | ✅ You already have it |
| 176.3k | [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official skills | Assessed in the first report |
| 138.4k | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | "Laziest senior dev" — a 7-step ladder before writing any code | ✅ **Yes** — fills our "design approach" gap cheaply |
| 136.8k | [github/spec-kit](https://github.com/github/spec-kit) | Spec-driven: constitution → specify → plan → tasks → implement | ⚠ Ideas only — we already have the flow |
| 116.7k | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | Codebase → queryable knowledge graph | ⚠ Trial only (see codegraph) |
| 105.6k | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Makes the agent write terse text to cut tokens | ⚠ Only for agent-to-agent reports, never to you |
| 93.9k | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | Persistent memory across sessions | ❌ You already have memory + project files |
| 70.8k | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | Pre-built code index for agents, supports PHP and Laravel routes | ⚠ Trial on a **large** existing project |
| 68.3k | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | Lightweight specs: `specs/` (truth) · `changes/` (in progress) · `archive/` | ✅ The archive idea |
| 65.9k | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | Collected practices | ✅ Several cheap rules |
| 64.5k | [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) | Context engineering: fresh subagents, lean main session, `STATE.md` | ⚠ Archived June 2026, moved to [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core) (9.5k). Idea only. |
| 53.0k | [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | Agile AI team: PM, architect, UX, dev, test roles, scale-adaptive tracks | ✅ Confirms our design |
| 39.7k | [wshobson/agents](https://github.com/wshobson/agents) | Big plugin marketplace of agents | ❌ More agents = more tokens |
| 29.3k | [oraios/serena](https://github.com/oraios/serena) | Semantic code search and edit (MCP) | ⚠ Same verdict as codegraph |
| 23.9k | [SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) | Commands and personas | ❌ Overlaps what you have |

---

## 3. Where vibe_coding already matches or beats them

| Your feature | Their version | Verdict |
|---|---|---|
| Four principles in global `CLAUDE.md` | karpathy-skills (213k) — same four | **Equal.** |
| Developer → code review → QA | superpowers: two checks per task, "spec compliance" then "code quality" | **Equal** — same idea, different names. |
| Risk lanes (Direct / Light / Standard / Sensitive) | BMAD "scale-adaptive" tracks; small changes skip planning | **Equal**, and yours is stricter on risky work (your approval). |
| Role agents with ownership boundaries | BMAD role agents | **Equal.** Yours adds the backend/frontend data contract, which BMAD doesn't have. |
| "The existing project wins" + codebase survey | OpenSpec says "built for brownfield"; most others assume greenfield | **You're ahead** on how strictly it's enforced. |
| Safety hooks + security floor | ECC has more hooks plus a config scanner | ECC is ahead on coverage; yours has holes (first report §3.1). |
| Stop conditions | superpowers: fix loop capped at 5 rounds | Equal idea; theirs is sharper (see 4.2). |

---

## 4. Ideas worth taking — ranked by value for the cost

Each idea is small (instructions or a hook), not a package install.

### 4.1 Report status codes — a way for agents to "ask" *(superpowers)*
Your biggest structural weakness is "subagents cannot ask questions". Superpowers gives every developer report one of four statuses:

`DONE` · `DONE_WITH_CONCERNS` · `NEEDS_CONTEXT` · `BLOCKED`

`NEEDS_CONTEXT` lets the agent stop cheaply and say what's missing, instead of guessing or grinding. **Cost:** 4 lines in each developer brief. **Where:** agent briefs + `/next-story` Step 3.

### 4.2 Continue the same agent for rework — don't start a new one *(superpowers)*
Superpowers **resumes the same implementer** for fix rounds 1–3, and only rounds 4–5 go to a fresh agent on a stronger model. Your `/next-story` says "re-dispatch to the same agent", but a new Agent call starts **cold** and re-reads everything. Claude Code's `SendMessage` continues an agent with its memory intact. **Win:** each review fix skips a full cold start. In the pilot, 2 of 7 tasks had a review fix. **Where:** `/next-story` "On FAIL" step.

### 4.3 Give the reviewer "the diff since BASE", not the whole story *(superpowers)*
Record the commit hash (BASE) before dispatching the developer, and give review and QA `git diff BASE`. They read exactly what changed, and it also catches out-of-scope files for free. **Cost:** 2 lines. **Where:** `/next-story` Steps 2–3.

### 4.4 Never run two developers in parallel on one folder *(superpowers — and your pilot proved it)*
Superpowers: *"Never dispatch multiple implementation subagents in parallel."* Your news pilot hit exactly this (pilot problem P2). **Cost:** 1 rule. **Where:** `/next-story` Step 2 (replace "unless two are genuinely independent").

### 4.5 The "do we even need this code?" ladder *(ponytail, 138k)*
This is the cheapest fix for the "design approach" gap. Before writing anything, go down these seven steps:

1. Does this need to exist? → no: skip it
2. Already in this codebase? → reuse it
3. Standard library does it? → use it
4. Framework has it built in? → use it (Laravel: validation, policies, `Str`, `Collection`, `Pipeline`, …)
5. Installed dependency does it? → use it
6. One line? → one line
7. Only then: the minimum that works — and **only here** use the pattern table (first report §4.2)

Ponytail's own benchmark claims **54% fewer lines and 22% fewer tokens** with safety kept. (That's their measurement, not ours.) **Cost:** ~10 lines in developer briefs; the reviewer checks "was a lower step skipped?"

### 4.6 Show the failing test first *(superpowers TDD)*
Your rule says "tests ship with the code". Superpowers requires **watching the test fail before writing the fix**. That proves the test actually tests something, and the pilot showed agents sometimes claim checks they didn't run. Ask for the failing run's output in the developer report (a few lines). Keep superpowers' harsher rule ("code written before the test is deleted") out — it clashes with brownfield work. **Where:** developer briefs, report item 4.

### 4.7 Archive finished work *(OpenSpec)*
OpenSpec keeps `specs/` (current truth), `changes/` (in progress) and `archive/` (done). That's the fix for the pilot's ~10k-token `backlog.md`: finished stories move to `backlog-done.md`, and `/next-story` reads only the live part. **Cost:** 1 rule in `/next-story` Step 4.

### 4.8 Cheap rules from claude-code-best-practice (66k)
| Rule | Why it fits |
|---|---|
| Keep `CLAUDE.md` near **~60 lines** (hard ceiling 200) | Your repo `CLAUDE.md` is 164 lines and duplicates the global one. |
| **Auto-format hook:** run Pint on each PHP file right after it's edited | Formatting never fails a review cycle again. Zero tokens unless something breaks. |
| **A "Gotchas" section in every agent brief**, filled from real failures | A cheap learning loop instead of ECC's heavy "instincts" system. The pilot already gives the first entries (false check claims, probe files, blocked commands). |
| Put deterministic behavior in `settings.json`, not in prose | Settings are enforced; `CLAUDE.md` text is only advice. |
| Keep context usage under ~40%; new task, new session | Matches your "one story per session". |

---

## 5. Considered and rejected — against "minimum tokens"

| Idea | Why not |
|---|---|
| **Install ECC / SuperClaude / agent collections** (wshobson, VoltAgent) | Every agent's description loads into every session (Claude Code caps combined descriptions at 15k tokens). Many overlapping agents break your one-owner-per-path rule. |
| **Caveman for everything** | It adds ~1,000 tokens to every call, and terse "caveman talk" breaks your plain-language rule for you. **Take only the idea:** agent-to-agent reports should be short (the pilot's QA reports were 1.6k–4.3k tokens each). |
| **Full spec-kit or GSD** | They'd duplicate your PM flow (`/new-project` → backlog → `/next-story`). GSD was archived and moved in June 2026 — too unstable to depend on. |
| **claude-mem** | You already have auto memory plus `.claude/project/` files. |
| **Code index (codegraph / serena / graphify) on small projects** | codegraph claims 62% fewer tokens in its own benchmark, but it adds MCP tools to every session and keeps more context resident. Worth a **trial on one large existing codebase** only — not news. |

---

## 6. Where these go in the plan (first report §7)

| Phase | Add from this report |
|---|---|
| **1. Fix what's broken** | 4.1 status codes · 4.2 continue the agent for rework · 4.3 diff since BASE · 4.4 no parallel developers |
| **3. Machine checks** | 4.8 Pint auto-format hook · 4.6 failing-test-first evidence |
| **4. Knowledge** | 4.5 the ladder, placed before the pattern table · 4.8 Gotchas sections, seeded from the pilot |
| **5. Trim tokens** | 4.7 archive finished stories · repo `CLAUDE.md` down to ~60 lines · short agent reports |
| **Later trial** | codegraph on one large brownfield project, measured with `/cost` before and after |

**Expected effect:** fewer rework cycles (4.1, 4.2, 4.6), cheaper reviews (4.3), smaller code (4.5), and plan files that stop growing (4.7). All of it is instructions and one hook — no new dependencies.

---

## 7. Limits

- Star counts are live from the GitHub API (2026-09-15). Numbers like "54% fewer lines" or "62% fewer tokens" are **each repo's own claims**; I haven't reproduced them.
- I read READMEs and superpowers' `subagent-driven-development` skill in full, not every file of every repo.
- GitHub's search limit cut off 2 of my 6 searches. The known top repos were checked directly, but a smaller gem could be missing.

## Sources

[superpowers](https://github.com/obra/superpowers) · [superpowers subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md) · [ECC](https://github.com/affaan-m/ECC) · [karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) · [ponytail](https://github.com/DietrichGebert/ponytail) · [spec-kit](https://github.com/github/spec-kit) · [caveman](https://github.com/JuliusBrussee/caveman) · [codegraph](https://github.com/colbymchenry/codegraph) · [OpenSpec](https://github.com/Fission-AI/OpenSpec) · [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) · [get-shit-done (archived)](https://github.com/gsd-build/get-shit-done) · [gsd-core](https://github.com/open-gsd/gsd-core) · [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) · [Spec Kit vs BMAD comparison](https://pradeepbatchu.medium.com/choosing-your-ai-coding-framework-spec-kit-vs-bmad-vs-claude-code-1a8fa261a751) · [Claude Code framework wars](https://shmck.substack.com/p/claude-code-framework-wars)
