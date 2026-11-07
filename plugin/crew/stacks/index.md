# Stack guides: index

Short guides for stacks beyond PHP. **Read on demand:** the PM names the guide in each task, and an agent reads only the guide for its own task. A guide never outranks `.claude/project/conventions.md`, and never weakens the security floor (`standards/coding-standards.md` §7).

Guides point to the framework's **own, version-matched guidance** and add only the crew's rules: who owns which files, tests, security and dangerous commands. When the official docs and a guide disagree, the official docs for the installed version win (rung 5 of the precedence ladder in `standards/engagement-modes.md`).

## 1. Detecting the stack (the survey)

Read manifests; never guess. Never open `.env`, only `.env.example`.

| Signal | Stack | Guide |
|---|---|---|
| `next` in `package.json` dependencies | Next.js (React) | `nextjs.md` (it covers React too) |
| `react` without `next` (usually with Vite) | React | `react.md` |
| `prisma` or `@prisma/client` in `package.json`, or `prisma/schema.prisma` | Prisma | `prisma.md`, plus the database guide below |
| `provider = "postgresql"` in the schema, a `postgres://` URL in `.env.example`, `DB_CONNECTION=pgsql`, or `@supabase/*` | PostgreSQL | `postgres.md` |
| `provider = "mysql"`, a `mysql://` URL, or `DB_CONNECTION=mysql` / `mariadb` | MySQL or MariaDB | `mysql.md` |
| `laravel/framework`, WordPress, or plain PHP | PHP | `standards/stack-profiles.md`; Blade, SCSS and jQuery in `coding-standards.md` §4–6 |
| `drizzle-orm`, Vue, Nuxt, Svelte, Angular, or another stack | No guide yet | Follow its official docs (Profile E rules), and log "no crew guide for this stack" in `decisions.md` under `## Risks` |

- **Versions** come from the lock file (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`); `package.json` only gives ranges. The lock file also tells you the **package manager**. Use only that one.
- A project can have several stacks, for example a Laravel API with a Next.js frontend. List each one.

## 2. The Stack block in `conventions.md`

```markdown
## Stack
- Frontend: Next.js 16.3 (App Router), React 19 · guide: stacks/nextjs.md · docs: node_modules/next/dist/docs/
- Database: PostgreSQL 16 via Prisma 7.9 · guides: stacks/prisma.md, stacks/postgres.md
- Package manager: pnpm
- Formatter: Prettier (the format_js hook runs it) · Linter: ESLint
- Check command: pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build
```

Each line names the version, the guide, and where the official docs live, when the project has them.

## 3. Using a guide in a task

- The PM writes the guide path, and the official docs path, into the task record and the dispatch prompt (`pm-brief.md`, Definition of Ready).
- A task touches one side, so one guide. A Prisma task with PostgreSQL reads both `prisma.md` and `postgres.md`, which count as one database side.
- The code reviewer and QA check the guide's section 6 checklist, along with their usual checks.
