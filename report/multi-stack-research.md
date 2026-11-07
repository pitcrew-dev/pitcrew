# Supporting more stacks: research

**Date:** 2026-11-07
**Question:** How should PitCrew support React, Next.js and other frontend frameworks, and databases beyond MySQL, without adding cost or losing quality?

## The short answer

1. **Keep the five roles.** Teach them stacks through small guides that are loaded only when needed. Don't add a "React developer".
2. **Use the official, version-matched guidance that framework makers now ship.** Don't rewrite it. Our guides add only what is ours: who owns which files, tests, the security floor, and dangerous commands.
3. **The PM names the exact guide in each dispatch.** Agents don't reliably load optional guidance on their own.
4. **Dangerous database commands go in hooks**, not in prose.
5. **Every stack ships with an eval** that proves the crew follows it.

## What we found

### 1. Role-based teams stay stack-generic

| Source | Finding |
|---|---|
| BMAD Method | Roles (PM, architect, dev, QA) are stack-generic by design. The stack is recorded in a project document, and stack specifics come as add-on "expansion packs" (for example Django+React, MEAN). |
| PitCrew today | Already does the same thing: the survey writes `conventions.md`, which every agent reads first. Profile E ("other framework") already says to follow the framework's official standards. |

**Meaning:** the structure is right. What's missing is stack knowledge, not new roles.

### 2. Official, version-matched docs beat hand-written rules

| Source | Finding |
|---|---|
| Next.js 16.2 and 16.3 | Next.js ships its docs inside the package (`node_modules/next/dist/docs/`) and writes a managed `AGENTS.md`/`CLAUDE.md` block pointing at them. In Vercel's evals, bundled docs reached a **100%** pass rate against **79%** at best for skills. Next.js 16.3 **retired its knowledge skills** for this reason, and kept skills only for multi-step workflows. |
| Vercel's evals | With skills available but not mentioned, the pass rate matched having nothing (53%): the agent didn't invoke them. Telling it explicitly raised the rate to 79%. |
| Laravel Boost | Detects installed packages from `composer.json` and assembles **version-aware** guidelines (for example Livewire 2, 3 or 4; Tailwind 3 or 4). Package authors ship their own guidelines. |
| Vendor skills | Vercel (`react-best-practices`), Supabase (`postgres-best-practices`) and Prisma (`prisma/skills`) all publish official agent guidance, under open licences. |
| Context7 | An MCP server that serves version-specific library docs. Useful, but its benefit is unmeasured (vendor claims only). |

**Meaning:** our guides must not try to be React or Postgres manuals. They go stale and lose to the official docs. Instead they **point to the official guidance for the detected version** and add only PitCrew's rules.

### 3. More always-loaded context costs money and doesn't add correctness

| Source | Finding |
|---|---|
| ETH Zurich, "Evaluating AGENTS.md" (arXiv 2602.11988) | Context files gave **no improvement** in task success, and **over 20% higher** cost. |
| Lulla et al. (arXiv 2601.20404) | Curated, focused files cut runtime by 28.6% and output tokens by 16.6%. |
| Two-agent ablation (arXiv 2607.27250) | Neither full nor on-demand context measurably moved correctness. Failures were about implementation skill, not missing knowledge. |
| Factorial study (arXiv 2605.10039) | File length (25 to 500 lines) and instruction position didn't change compliance. Compliance **fell about 5.6% with each extra function** written in one session. |

**Meaning:**
- Load a stack guide **only for the task that needs it**, and keep it short and focused. This matches the "tokens are a design constraint" rule in `CLAUDE.md`.
- Correctness comes from **small tasks and independent checks**, which PitCrew already has, more than from more text. The reviewer and QA must check the stack rules too.

### 4. Agents don't reliably load optional guidance

- Vercel saw skills go unused unless the agent was told about them (above).
- Claude Code subagents can preload skills through a `skills:` frontmatter field, but that list is fixed per agent, not per project.
- PitCrew already writes a full brief for every dispatch.

**Meaning:** the **PM puts the guide's path in the task record and the dispatch prompt** ("Stack guide: `crew/stacks/nextjs.md`; official docs: `node_modules/next/dist/docs/`"). That's deterministic, per project, and costs nothing when unused.

### 5. Database safety belongs in hooks

| Source | Finding |
|---|---|
| Prisma 7 | Detects AI agents and **blocks** `migrate reset`, `db push --force-reset` and `db push --accept-data-loss` until the user's exact consent is passed in `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION`. Agents must not fake or reuse that consent. Prisma 8 removes reset entirely. |
| destructive_command_guard (dcg) | A Claude Code hook with per-database packs (SQLite, MySQL, PostgreSQL) that flags `DROP` and `TRUNCATE` and suggests a backup first. |
| Hook guides | PreToolUse hooks that exit 2 are the reliable layer, because the model can't forget them after compaction. Pattern matching is a heuristic, so restricted database users and backups stay the real safety net. |

**Meaning:** extend `guard_bash.py` with tests, for each ORM and database CLI. **Never set Prisma's consent variable ourselves**, and block agents from setting it.

## Recommended design

### Detection, in the survey (`/pit:start`)

Read manifests, never guess: `package.json` and its lock file, `composer.json`, `prisma/schema.prisma`, `drizzle.config.*`, `docker-compose.*`, and the database scheme in `.env.example` (never `.env`). Write a **Stack** block into `conventions.md` with names **and versions**, and the guides that apply.

### Stack guides: `plugin/crew/stacks/` (read on demand, about 60 to 100 lines each)

Each guide has the same shape:

| Section | Content |
|---|---|
| **Official guidance first** | Where the version-matched docs live (for example Next.js bundled docs, Laravel Boost if installed) and which vendor guidance to follow |
| **Folder ownership** | Which paths are backend, frontend or shared. Where a framework blurs the line (Next.js server components and server actions), the full-stack developer is the default. |
| **Tests** | The test tools the project uses, and what "a test that failed first" means here |
| **Security floor for this stack** | For example no `dangerouslySetInnerHTML` with user data, no secrets in client bundles, parameterized queries through the ORM, row-level security for Supabase |
| **Dangerous commands** | Listed, and enforced by hooks |
| **Review and QA checklist** | Five to ten lines the reviewer and QA check against |

The current Blade, SCSS and jQuery rules move into a `blade` guide, so PHP becomes one stack among several and not the hidden default.

### Changes to existing parts

| Part | Change |
|---|---|
| Agent briefs | "Read the stack guide named in your dispatch" replaces the hard-coded Blade, SCSS and jQuery pointers |
| `code-ownership.md` | Becomes the general rule. The path maps move into each stack guide. |
| `stack-profiles.md` | Profiles A to E stay for PHP, with a pointer to `stacks/` for everything else |
| `/pit:start` (new projects) | Offers a stack choice with a recommended default |
| `guard_bash.py` | Adds Prisma, Drizzle, TypeORM, Sequelize, Knex and Mongo commands, `DROP`/`TRUNCATE` through `psql`, `mysql` or `sqlite3`, and setting the Prisma consent variable. Each gets a test. |
| Formatting hook | Runs the project's own Prettier or Biome on the written file, only when the project has a config, the same way we use Pint |
| Evals | One sample project per stack (for example Next.js + Prisma + PostgreSQL) that checks the crew uses the right guide and the right owner |

### Phases

| Phase | Stacks | Why |
|---|---|---|
| 1 | React, Next.js; PostgreSQL, MySQL; Prisma | The most common new-project stack, and the vendors publish strong official guidance |
| 2 | Vue and Nuxt; SQLite; Drizzle | Next most common |
| 3 | MongoDB; others on demand | Less common for our users |

## Risks

- **Vendor guidance changes fast.** Next.js retired its skills within months. Our guides point to the vendor's guidance and don't copy it, so a change costs a line, not a rewrite.
- **Mixed stacks** (Laravel API with a Next.js frontend). The Stack block lists both, and each task names the guide for its side.
- **Hooks are pattern matches.** They're a floor, not a gate, as with today's PHP rules.
- **Token cost.** One guide per task at most, about 1 to 2k tokens, read only by the agent doing that task.

## Sources

- [Anthropic: skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code features overview (subagents can preload skills)](https://code.claude.com/docs/en/features-overview)
- [Next.js: set up your project for AI coding agents](https://nextjs.org/docs/app/guides/ai-agents)
- [Next.js 16.2: AI improvements](https://nextjs.org/blog/next-16-2-ai)
- [Next.js 16.3: AI improvements (skills retired)](https://nextjs.org/blog/next-16-3-ai-improvements)
- [Vercel: AGENTS.md outperforms skills in our agent evals](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)
- [Vercel agent skills docs](https://vercel.com/docs/agent-resources/skills)
- [Laravel AI docs (Boost guidelines)](https://laravel.com/docs/ai)
- [Supabase agent skills](https://github.com/supabase/agent-skills)
- [Supabase: Postgres best practices for AI agents](https://supabase.com/blog/postgres-best-practices-for-ai-agents.md)
- [Prisma: stop your AI agent dropping your database](https://www.prisma.io/blog/stop-your-ai-agent-dropping-your-database)
- [Prisma agent safety reference](https://raw.githubusercontent.com/prisma/skills/main/prisma-cli/references/agent-safety.md)
- [Prisma migrate reset docs](https://www.prisma.io/docs/cli/migrate/reset)
- [destructive_command_guard](https://awesome.ecosyste.ms/projects/github.com%2FDicklesworthstone%2Fdestructive_command_guard)
- [ETH Zurich: Evaluating AGENTS.md (arXiv 2602.11988)](https://arxiv.org/abs/2602.11988)
- [On the impact of AGENTS.md files on efficiency (arXiv 2601.20404)](https://arxiv.org/abs/2601.20404)
- [Do context files help coding agents? (arXiv 2607.27250)](https://arxiv.org/html/2607.27250v1)
- [Instruction adherence factorial study (arXiv 2605.10039)](https://arxiv.org/abs/2605.10039)
- [Probe-and-refine tuning of repository guidance (arXiv 2606.20512)](https://arxiv.org/pdf/2606.20512)
- [BMAD Method core architecture](https://cdn.jsdelivr.net/npm/@ptnglobal/bmad-method@4.43.1/docs/core-architecture.md)
- [Context7 overview](https://context7.com/docs/overview)
