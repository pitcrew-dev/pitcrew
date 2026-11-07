# Stack guide: Prisma

For projects using the Prisma ORM. Also read the database guide for its provider: `postgres.md` or `mysql.md`.

## 1. Official guidance first

- **Check the major version** in the lock file before writing anything. Version 7 moved configuration into `prisma.config.ts` and connects through a driver adapter. Version 8 has no reset command at all. Follow what the project already uses.
- If the project has Prisma's official skills installed (`prisma/skills`), follow them.
- The Prisma docs for the installed version win over this guide.

## 2. Who owns which files

**`backend-developer`** owns `prisma/schema.prisma`, `prisma/migrations/**`, `prisma.config.ts`, seed scripts, and the module that creates the Prisma client. Other code gets data through backend-owned data-access functions, never by importing the client into UI code.

## 3. Tests and migrations

- **A schema change is a migration:** `prisma migrate dev --name <what_changed>` creates the SQL in `prisma/migrations/`. Commit the schema and the migration together.
- **Never edit or delete a migration that has been applied or committed.** Fix forward with a new migration.
- `prisma db push` is only for projects that have **no** `prisma/migrations/` folder. Never use it in a project that has migrations.
- Read the generated SQL before committing. A rename can show up as a drop and an add, which loses data. Fix that by hand in the new migration.
- Tests use a **separate test database** (the project's test `DATABASE_URL`), never the development one.

## 4. Security floor for Prisma

- **Raw SQL only as a tagged template:** `` prisma.$queryRaw`... ${value}` `` sends values as parameters. **Never** `$queryRawUnsafe` or `$executeRawUnsafe` with any user input, because that's SQL injection.
- Select only the fields you need (`select`), and never send a whole record with password hashes or tokens to the client.
- Every query that reads or writes a user's data filters by the owner or checks permission. Prisma doesn't do this for you.
- Multi-step writes that must all succeed together use `prisma.$transaction`.

## 5. Dangerous commands (blocked by the hooks)

| Command | Rule |
|---|---|
| `prisma migrate reset`, `prisma db push --force-reset`, `prisma db push --accept-data-loss` | Blocked. They delete data. The user runs them, if ever. |
| Setting `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION` | Blocked. Only the user gives Prisma that consent. Never set it, and never repeat an old approval. |
| `prisma migrate deploy` | Asks the user first, because it changes a real database |

If you think a reset is needed, stop and explain why to the PM.

## 6. Review and QA checklist

- [ ] Every schema change has a new migration, committed with the schema, and no old migration was edited
- [ ] The generated SQL has no accidental drop (for example a rename shown as drop and add)
- [ ] No `$queryRawUnsafe` or `$executeRawUnsafe` with user input
- [ ] Queries filter by the owner or check permission, and select only the fields needed
- [ ] Tests ran against the test database
