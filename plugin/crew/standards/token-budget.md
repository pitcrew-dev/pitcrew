# Standard — Token Budget

**Applies to:** every role, every dispatch.
**Why:** multi-agent workflows cost **4–7× a single session**, because each subagent runs a fresh context and re-reads what it needs. **Careful** mode spawns three agents per task; **Quick** (the default) spawns one per task plus one QA per piece. Unchecked, that is how a budget disappears in an afternoon.

The goal is not to spend less on everything. It is to **spend where verification actually prevents a defect, and nowhere else.**

---

## 1. Right-size the ceremony — the biggest lever

The PM picks a lane per task and records it. Running the full gate on a copy change is waste; skipping it on a payment flow is negligence.

| Lane | When | Agents spawned | Cost |
|---|---|---|---|
| **Direct** | Copy text, a colour, a typo, a config value, a one-line content fix. No logic, no data, no permissions. | **0** — the main session does it and verifies | ~1× |
| **Light** | A small, low-risk change with real logic but no security surface: a validation message, a display format, a simple filter, **a small bug fix** (≤ 2 files, cause known) with a regression test shown failing first. | **1** — developer only; the main session reviews the diff and runs the new test and the suite | ~2× |
| **Standard** | Default for anything with logic, data, or user-visible behavior. | **Quick:** a developer per task (the PM checks `git diff BASE`, runs the check command and the new test), then **one** `qa-engineer` run after the piece's last task. No `code-reviewer`. **Careful:** developer → `code-reviewer` → `qa-engineer` per task | Quick ~2–3×; Careful ~4–7× |
| **Sensitive** | Auth, permissions, payment, personal data, file upload, migrations, deploy or going live, anything irreversible. | **Always the full flow, in both modes:** developer → `code-reviewer` → `qa-engineer` per task, `/security-review` and **the user** | ~4–7× plus a human gate |

**Rules:**

- **Default to Standard.** The mode (the `Mode:` line in the session context; none means Quick) only changes Standard. A typical piece costs about $7 in Quick (an estimate, still to be measured) and about $17 in Careful (the pilot's average). Choosing a cheaper lane is a decision the PM records with a reason, not a shortcut taken quietly.
- **Never downgrade a Sensitive task.** The lane is set by what the code touches, not by how small the diff looks.
- **Never batch lanes.** Three Direct changes are still Direct; one Standard task in the group makes that task Standard, not all of them.
- **A failed gate does not downgrade.** Rework re-runs the same lane.

## 2. Model routing

| Agent | Model | Why |
|---|---|---|
| Main session (PM) | Opus | Planning, decomposition, and talking to the user — where judgment compounds |
| Developers | Sonnet | Near-identical output to Opus on 80–90% of coding tasks |
| `code-reviewer`, `qa-engineer` | Sonnet | Their verdicts gate delivery; a wrong pass costs more than the model saves |

Do not downgrade a gate to Haiku to save money. Do use Haiku for genuinely mechanical work — extraction, formatting, classification, a boolean check — if such an agent is ever added.

**Audit warning:** the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable silently overrides every agent's frontmatter with no signal in the transcript. If cost numbers look wrong, check it before trusting anything here.

## 3. Scope the context

Reading only the relevant files uses **60–80% fewer tokens at equal output quality.**

- **Grep before you read.** Locate the symbol, then read that file — never a whole directory to "get oriented".
- **Read a range, not a file**, when the file is large and you know where you are going.
- **Never read `vendor/`, `node_modules/`, lock files, or build output.** The hooks block writing them; do not waste context reading them either.
- **Do not re-read what is already in context.** If you read it this session, it is still there.
- **Subagents read the tiered list in their brief**, not the whole standards set. That is 58 lines instead of 967.

## 4. Dispatch once, completely

A subagent cannot ask a question. An incomplete dispatch produces a wrong result, and re-dispatching pays the full cold-start cost again.

> The quality of the dispatch prompt is the single largest driver of subagent reliability. **One complete dispatch is cheaper than two cheap ones.**

Include everything the brief asks for: task record, criteria, mode, profile, `conventions.md` path, in/out-of-scope paths, seam contract, what upstream tasks produced, and the BASE commit.

**Rework continues the same agent.** A fix round goes back to the developer that did the work (`SendMessage` with its agent ID). It still holds the files and its reasoning, so it doesn't pay a cold start. Only the third attempt is a fresh agent, given a written summary.

**Reviewers read the diff, not the story.** Review and QA get `git diff BASE` and the file list, and read around it only as far as they need.

**Gates test; they don't investigate.** Measured on 52 gate runs across four projects: QA took twice the steps of review (median 51 vs 26), and a one-file bug fix took QA 98 calls. The time went on reading `vendor/`, hunting for the PHP path and server config, and re-running the full suite. So:

- every gate prompt carries the **setup facts** (PHP path, check command, test database, how to run a quick script)
- QA gets a **depth**: *Focused* for small changes (≤ 3 adversarial cases, ~20 calls), *Full* otherwise
- the reviewer runs only the new and changed tests; QA runs the full suite **once**, at the end

## 5. Stop conditions

Grinding is the expensive failure mode. Stop and ask rather than retry:

- **Three failed gate cycles on one task** — hard stop, escalate. Never a fourth.
- **A task exceeding roughly twice its estimate** — stop, report, re-slice.
- **The same error twice in a row** — stop. A third attempt at the same approach will not work.
- **A story spawning more than ~10 agent dispatches** — stop and report. The decomposition is wrong.
- **Any loop with no new information between iterations** — stop immediately.
- **An agent hitting its `maxTurns`** (developers 100, QA 80, review 50) — stop. The caps are a runaway guard, not a budget; an agent that hits one returns partial work, and the task is re-sliced.
- **A story or the project reaching its budget** — the `check_budget` hook blocks the next agent. Stop and ask the user: a top-up (suggest an amount, and say why it ran over) or stop the story. Record an approved top-up in `budget.md`; never add one the user didn't approve. At 80% the hook warns: tell the user in the next report. A running agent is never cut off.

### Budgets

Costs are API-equivalent dollars, measured per agent run in `activity.md`. The defaults are **$12 per story** and **no project cap**, set in the plugin settings. A project can override them in `.claude/project/budget.md`:

| Line | Example |
|---|---|
| `Story budget: $<n>` | `Story budget: $12` |
| `Project budget: $<n>` or `none` | `Project budget: $250` |
| `Mode: quick` or `careful` (optional; overrides the plugin setting for this project) | `Mode: careful` |
| A **Top-ups** table, one row per approval | `\| 2026-10-24 \| SHOP-E01-S02 \| $10 \| user \|` (use `project` instead of a story ID for the project cap) |

A typical piece is about $7 in Quick mode (an estimate) and about $17 in Careful mode (the pilot's average, the PM included). At `/pit:start`, suggest a project cap of stories × $7 (Quick) or × $17 (Careful), rounded up.

## 6. Session hygiene

- **One story per session where practical.** `/clear` between stories: long sessions accumulate history that is re-sent on every turn, and attention degrades as the window fills ("context rot").
- **`/compact` at a natural boundary**, not mid-task.
- **Keep the project files lean**, because `/pit:next` reads them every time. Finished stories collapse to one line in `plan.md`; task notes are one line; its **Now** section is rewritten, not appended; agent reports stay under ~40 lines. On the first pilot, the backlog alone had grown to ~10k tokens.
- **`/cost` to measure.** Take a baseline before optimizing anything — without one you cannot tell whether a change helped.
- **Keep `CLAUDE.md` stable.** It sits in the cached prefix; editing it mid-session invalidates the cache and every subsequent turn pays full price.

## 7. Connected tools

Every connected MCP server loads its tool definitions into context. Twenty tools is 10,000 tokens gone before a single instruction is read; heavy servers cost far more.

- **Disconnect servers you are not using for this project.** This is the largest single saving available outside model choice.
- Claude Code defers tool schemas past a threshold and loads them on demand — do not defeat that by pulling in tools speculatively.
