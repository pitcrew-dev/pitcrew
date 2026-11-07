# Stack guide: PostgreSQL

For projects on PostgreSQL, including Supabase, whatever the ORM. With Prisma, also read `prisma.md`. In Laravel, the PHP rules in `coding-standards.md` §3 still apply.

## 1. Official guidance first

- Check the PostgreSQL version (from `docker-compose.*`, the hosting docs, or by asking the user) before using newer features.
- If the project has Supabase's official skill installed (`postgres-best-practices`), follow it.
- The project's migration tool decides how schema changes are made. Never change the schema by hand in a SQL client.

## 2. Who owns what

**`backend-developer`** owns the schema, migrations, indexes, database functions, triggers and row-level security policies.

## 3. Schema and queries

- **Index every foreign key.** PostgreSQL doesn't do it automatically, and joins and deletes get slow without one.
- Put the rules in the database too: `NOT NULL`, `UNIQUE`, `CHECK` and foreign keys, not only in application code.
- Use `timestamptz` for points in time, and `numeric` for money (never `float`).
- Multi-step writes that must all succeed together run in a transaction.
- On a big table, adding an index can lock writes. Raise it with the PM, so the user can choose a quiet time or `CREATE INDEX CONCURRENTLY`. Note that this can't run inside a transaction, and some migration tools wrap migrations in one.
- Fetch only the rows and columns you need. Paginate lists.

## 4. Security floor for PostgreSQL

- Every query is parameterized, through the ORM or with placeholders. Never build SQL from strings with user input.
- **Supabase:** turn on **row-level security on every table** in an exposed schema, with a policy for each action the app needs. The `service_role` key is server-only, and never in client code or a public variable.
- The app connects as a user with only the rights it needs. Don't change database users or grants inside a feature task: raise it with the PM.

## 5. Dangerous commands (blocked or asked by the hooks)

| Command | Rule |
|---|---|
| `DROP DATABASE`, `DROP SCHEMA`, `dropdb` | Blocked |
| `DROP TABLE`, `TRUNCATE`, `DELETE` without `WHERE` | Asks the user first. Schema changes belong in a migration. |

## 6. Review and QA checklist

- [ ] New foreign keys have indexes, and new rules are also database constraints
- [ ] Money is `numeric`, and times are `timestamptz`
- [ ] Every query is parameterized
- [ ] Supabase: every new table has row-level security with policies, and no `service_role` key is in client code
- [ ] Index changes on big tables were raised with the PM
