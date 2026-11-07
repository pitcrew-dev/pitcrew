# Stack guide: MySQL and MariaDB

For projects on MySQL or MariaDB, whatever the ORM. With Prisma, also read `prisma.md`. In Laravel, the PHP rules in `coding-standards.md` §3 still apply.

## 1. Official guidance first

- Check the server version and whether it's **MySQL or MariaDB**. They differ: for example, MariaDB stores `JSON` as `LONGTEXT`, and some functions and defaults differ.
- The project's migration tool decides how schema changes are made. Never change the schema by hand in a SQL client.

## 2. Who owns what

**`backend-developer`** owns the schema, migrations and indexes.

## 3. Schema and queries

- Use **`utf8mb4`** (with the project's collation), so emoji and every language are stored correctly. Plain `utf8` in MySQL is only 3 bytes.
- Use InnoDB tables, with foreign keys and constraints in the database, not only in code.
- **Index length:** InnoDB indexes allow 3072 bytes, which is `VARCHAR(768)` in `utf8mb4`. An index on a longer column needs a prefix length or a different design.
- Use `DECIMAL` for money (never `FLOAT`), and store times in UTC.
- Multi-step writes that must all succeed together run in a transaction.
- **SQLite in tests accepts what MySQL rejects:** string length, strict mode, `JSON` and some `ALTER TABLE` forms. If the suite runs on SQLite, check limits against the real MySQL schema.

## 4. Security floor for MySQL

- Every query is parameterized, through the ORM or with placeholders. Never build SQL from strings with user input.
- Don't turn off strict mode to make a failing insert pass. Fix the data or the schema.
- Don't change database users or grants inside a feature task: raise it with the PM.

## 5. Dangerous commands (blocked or asked by the hooks)

| Command | Rule |
|---|---|
| `DROP DATABASE`, `DROP SCHEMA`, `mysqladmin drop` | Blocked |
| `DROP TABLE`, `TRUNCATE`, `DELETE` without `WHERE` | Asks the user first. Schema changes belong in a migration. |

## 6. Review and QA checklist

- [ ] New tables and columns use `utf8mb4`, and indexed strings fit the index length
- [ ] Money is `DECIMAL`, and new rules are also database constraints
- [ ] Every query is parameterized
- [ ] Tests on SQLite were checked against MySQL limits
