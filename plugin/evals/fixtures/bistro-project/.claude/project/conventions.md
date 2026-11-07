# Conventions

- Mode: greenfield, started by PitCrew. Profile: Next.js app (`stacks/index.md`).

## Stack
- Frontend: Next.js 16.3 (App Router), React 19 · guide: stacks/nextjs.md · docs: node_modules/next/dist/docs/
- Database: PostgreSQL 16 via Prisma 7.9 · guides: stacks/prisma.md, stacks/postgres.md
- Package manager: pnpm
- Formatter: Prettier (the format_js hook runs it) · Linter: ESLint
- Check command: pnpm lint && pnpm exec tsc --noEmit && pnpm test && pnpm build

## Setup facts
- Test database: `bistro_test` (the test DATABASE_URL). Tests never touch the development database.
- Data access lives in `lib/` (server-only); components in `components/`; pages in `app/`.
