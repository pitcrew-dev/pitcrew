# Multi-stack, phase 1: build plan

**Date:** 2026-11-07 · **Target version:** 2.1.0 · **Research:** `multi-stack-research.md`
**Scope:** React and Next.js for the frontend; PostgreSQL and MySQL through Prisma for the database.
**Status:** approved by the user on 2026-11-07, with all three decisions answered yes.

## What "done" means

| # | Check | How we prove it |
|---|---|---|
| 1 | On an existing Next.js + Prisma + PostgreSQL project, `/pit:start` writes a **Stack** block into `conventions.md` with versions, the stack guides and where the official docs live | Eval `start-existing-next` |
| 2 | Every task on that project names its stack guide, and goes to the right developer | Eval `next-dispatch-names-guide` |
| 3 | An agent can't reset or wipe the database through Prisma, Drizzle, `dropdb`, or an npm script that hides them, and can't fake Prisma's consent | Hook tests in `tests/test_hooks.py` |
| 4 | A file an agent writes is formatted with the project's **own** Prettier, only when the project already uses it | Hook tests |
| 5 | A new project can choose "a web app with React (Next.js)" in `/pit:start`, and pick **Recommended setup** or **Let me choose** | Eval `start-new-next-site` checks both paths |
| 6 | **PHP projects behave exactly as before** | All 71 current tests and the 6 current evals still pass |
| 7 | Token limits hold: the working agreement stays under 90 lines, each agent brief grows by 3 lines at most, and guides are read only on demand | Line counts checked in the final review |

## The work, in build order

One concern per commit. The safety pieces come first, because they're independent and protect everything after them.

### 1. Database safety hook (`guard_bash.py`, with tests)

| Command | Rule | Why |
|---|---|---|
| `prisma migrate reset`, `prisma db push --force-reset`, `prisma db push --accept-data-loss` | **Deny** | Deletes data. Same list Prisma itself protects. |
| Setting `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION` (`VAR=…`, `export`, `$env:`) | **Deny** | Only the user may give that consent. Prisma forbids agents from faking it. |
| `prisma migrate deploy` | **Ask** | Applies migrations to a real database |
| `drizzle-kit drop` | **Deny** | Deletes migrations |
| `drizzle-kit push` | **Ask** | Can drop columns without a migration |
| `dropdb`, `mysqladmin drop` | **Deny** | Deletes a whole database |
| `npm`/`pnpm`/`yarn`/`bun run <script>` where the script name has `reset`, `drop`, `wipe`, `fresh` or `nuke` | **Ask** | Scripts hide the real command |
| `DROP` / `TRUNCATE` through `psql -c` or `mysql -e` | Already covered by today's text rules | Gets a test for the `psql` case |

Each rule gets a block test and a "similar but safe" test, for example `prisma migrate dev` and a commit message that mentions `migrate reset`.

### 2. Protected paths (`guard_paths.py`, with tests)

Block writes to Next.js and tool build output: `.next/`, `.turbo/`, `.vercel/output/`. (`dist/` is left alone, because some projects keep source there.)

### 3. Formatter for JavaScript and TypeScript (new hook `format_js.py`, with tests)

Works the same way as `format_php.py` does for Pint:
- runs only when the project has a Prettier config **and** a local `node_modules/.bin/prettier`
- formats only the file just written, and only if it's new or its committed version was already Prettier-clean, so it never reformats old code
- covers `.js .jsx .ts .tsx .mjs .cjs .css .scss .json`
- silent on success, fails open, and never installs Prettier

Biome support waits for phase 2.

### 4. Stack guides (`plugin/crew/stacks/`, new)

| File | Purpose | Lines |
|---|---|---|
| `index.md` | **Detection table:** which file or signal means which stack and which guide, plus the **Stack block** format for `conventions.md` | ~40 |
| `nextjs.md` | Next.js (App and Pages Router) | ~90 |
| `react.md` | React without Next.js (Vite and similar) | ~70 |
| `prisma.md` | Prisma ORM, versions 6 to 8 | ~70 |
| `postgres.md` | PostgreSQL rules, including Supabase | ~60 |
| `mysql.md` | MySQL and MariaDB rules (the MySQL tips now in agent briefs move here) | ~50 |

Every guide has the same six sections:
1. **Official guidance first:** where the version-matched docs live, and which official vendor skill to follow if the project has it installed.
2. **Who owns which folders**
3. **Tests**
4. **Security floor for this stack**
5. **Dangerous commands** (enforced by piece 1)
6. **Review and QA checklist:** 5 to 10 lines

Key content, so you can check the direction:

| Guide | Highlights |
|---|---|
| `nextjs.md` | Use the docs in `node_modules/next/dist/docs/` (Next.js 16.2+), and never edit Next's managed block in `AGENTS.md`. Follow the router the project already uses. **The full-stack developer is the default**, because server and UI code mix. Every server action is a public endpoint, so validate its input and check permission inside it. Middleware is never the only auth check. Only `NEXT_PUBLIC_` variables reach the browser, so secrets never get that prefix. No `dangerouslySetInnerHTML` with user data. |
| `react.md` | Follow react.dev and the rules of hooks. Use the project's own data layer and state library. Vite's `VITE_` variables are public. Same XSS rule. |
| `prisma.md` | `schema.prisma` and migrations belong to the backend developer. Never edit an applied migration. `$queryRaw` only as a tagged template, never `$queryRawUnsafe` with user input. The consent rule. Check the major version, because Prisma 8 removes reset. |
| `postgres.md` | Index foreign keys, use transactions for multi-step writes, put constraints in the database. Turn on row-level security for Supabase tables. Follow Supabase's `postgres-best-practices` if installed. |
| `mysql.md` | utf8mb4, strict mode, index length limits, and the SQLite-in-tests warning |

The existing Blade, SCSS and jQuery rules stay where they are (`coding-standards.md` §4–6). `index.md` points to them. No PHP file moves in this phase.

### 5. Detection in the survey (`/pit:start` Step 2 and `engagement-modes.md` §3)

The survey also reads `package.json` and its lock file (versions and package manager), `prisma/schema.prisma` (the database provider), `drizzle.config.*`, and the database scheme in `.env.example` (never `.env`). It writes the Stack block, for example:

```markdown
## Stack
- Frontend: Next.js 16.3 (App Router), React 19 · guide: stacks/nextjs.md · docs: node_modules/next/dist/docs/
- Database: PostgreSQL 16 via Prisma 7.9 · guides: stacks/prisma.md, stacks/postgres.md
- Package manager: pnpm
- Check command: pnpm lint && pnpm tsc --noEmit && pnpm test && pnpm build
```

For Next.js 16.1 or older, which have no bundled docs, the PM **offers** to run Next's official codemod, which adds `AGENTS.md`. It never runs it unasked, because the existing project wins.

### 6. The PM names the guide (`pm-brief.md`, `/pit:next`, `/pit:fix`)

- The task record gets a **Stack guide** line, and Definition of Ready fails without one when the Stack block lists a guide.
- Every dispatch prompt includes the guide's path and the official docs path.
- Routing: Next.js tasks go to `pit:full-stack-developer` by default. Backend and frontend split only by the guide's folder map, and only for big tasks or in Careful mode.

### 7. Agent briefs (5 files, at most 3 lines each)

- **Developers:** "Read the stack guide named in your dispatch. Without one, for Blade, SCSS or jQuery, use `coding-standards.md` §4–6." This replaces the current Blade-only pointer. The frontend description gains "or the project's components folder".
- **Code reviewer and QA:** "Also check the stack guide's checklist."

### 8. New projects (`/pit:start` Step 3c)

**Recommended or custom.** The stack questions become two paths:

| Screen | Who sees it | Questions |
|---|---|---|
| 1 | Everyone, as one `AskUserQuestion` screen | **What kind of site is it?** and **How should we choose the tools?**, with "Recommended setup (we pick for you)" first and "Let me choose" second |
| 2 | Only users who chose "Let me choose" | Up to 4 questions on one screen: frontend and interactivity, styles, database, and one more only when it's relevant (for example testing or hosting). Each has the recommended option first and one honest trade-off. |

- **Recommended:** no more stack questions. The plan lists every default ("I used Tailwind and PostgreSQL, the recommended setup for a Next.js app. Say if you want something else.").
- **Let me choose:** the extra screen is the user's choice, so it doesn't count against the 3 to 5 question limit.
- Every answer, and every default used, is recorded in `decisions.md` (who decided) and in the Stack block of `conventions.md`.
- **Existing projects are unchanged:** no stack questions, because the survey decides.

Other changes:

- "What kind of site is it?" gets a fourth option: **"A web app with React (Next.js): rich, app-like pages"**, with an honest trade-off: more moving parts, and Node hosting instead of plain PHP hosting.
- The database question also applies to Next.js. PostgreSQL is recommended there, with MySQL as an option.
- The scaffolding task: `create-next-app` at a verified version, Vitest with React Testing Library, Playwright, ESLint and Prettier, `prisma init`, then the check command recorded. Package versions are checked before installing (`coding-standards.md` §7.1).
- The "this team works best with server-rendered pages" risk line stays for **other** frameworks (Vue and so on) until phase 2.

### 9. Evals and a sample project

- A new fixture `plugin/evals/fixtures/bistro/`: a half-built restaurant-booking app in **Next.js + Prisma + PostgreSQL**, with only the files the evals need (no `node_modules`), plus a second version with `.claude/project/` filled in.
- Three new evals:
  - `start-existing-next`: the Stack block is correct, with versions and guides
  - `next-dispatch-names-guide`: the task names `stacks/nextjs.md` and goes to the full-stack developer
  - `start-new-next-site`: the Next.js option is offered and recorded
- The evals are paid model calls. Run them in CI on Linux.

### 10. Docs and release

- README: a **"Stacks"** section with what's supported and what's planned. Status line: "PHP, plus React/Next.js and PostgreSQL/MySQL through Prisma".
- CLAUDE.md layout table: add `plugin/crew/stacks/`
- The working agreement's reference table: one new row (stack guides → `stacks/index.md`)
- The plugin description and keywords: add react, nextjs, postgres, prisma
- CHANGELOG, and VERSION 2.1.0 (additive, nothing breaks)

## Order and checks

| Step | Pieces | Gate before moving on |
|---|---|---|
| A | 1, 2, 3 (hooks) | New tests pass, all 71 old tests pass |
| B | 4 (guides) | Line counts, and every guide has the six sections |
| C | 5, 6, 7, 8 (wiring) | `claude plugin validate --strict`, and a manual run on the fixture with `--plugin-dir` |
| D | 9 (evals) | The three new evals pass, and the six old ones still pass |
| E | 10 (docs, version) | Final review against the "done" table |

## Not in phase 1

Vue and Nuxt, SQLite as its own guide, Drizzle guide (only its dangerous commands are blocked now), MongoDB, Biome, Python or other backend languages, and moving the PHP rules into `stacks/`.

## Roadmap after phase 1

Agreed with the user on 2026-11-07. Each new agent runs only when the work is risky enough, so Quick mode stays cheap.

| Order | Piece | What it does | When it runs |
|---|---|---|---|
| 1 | **Security agent** (read-only) | The threat check before coding, then a security pass after. Works with `/security-review`. | Only in the Sensitive lane (logins, payments, personal data, uploads, migrations) and before going live |
| 2 | **DevOps agent** | Prepares CI, Docker, hosting config (PHP hosting and Node or Vercel), backups and server settings, against `launch-security.md`. Never deploys or handles credentials without the user's approval. | Only for setup and go-live stories |
| 3 | Multi-stack phase 2 | Vue and Nuxt, SQLite guide, Drizzle guide, Biome | After the two agents |
| Later | Architect agent | Survey and design for very large codebases | Only if real projects show the PM struggling |

## Decisions for the user

1. **Offer Next.js for new projects in `/pit:start`?** Recommended: yes.
   **Decided (2026-11-07):** new projects ask "Recommended setup or let me choose?", with the custom questions only for those who want them.
2. **For older Next.js projects, offer Next's codemod that adds `AGENTS.md`?** Recommended: yes, always asking first.
3. **Release as 2.1.0?** Recommended: yes, since nothing breaks for existing users.
