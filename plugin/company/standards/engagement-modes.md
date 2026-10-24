# Standard — Engagement Modes & Convention Precedence

**Applies to:** every role, on every task, without exception.
**Status:** this standard **governs every other standard**. Where another file in `company/standards/` conflicts with the precedence ladder below, this file wins.

The company works on two kinds of project, and they are not governed the same way:

| Mode | Meaning |
|---|---|
| **Greenfield** | A new project started from scratch. The company chooses the stack and its conventions become the project's conventions. |
| **Brownfield** | An existing codebase — Laravel of any version, plain PHP, WordPress, or anything else, with its own structure, conventions, and history. |

**The default assumption is brownfield.** A project is greenfield only when the sponsor says so and the directory is genuinely empty.

---

## 1. The precedence ladder

When two sources of guidance disagree, the higher one wins. This ladder is the single most important rule in the company.

1. **Explicit sponsor instruction** for this project or task.
2. **The project's own committed configuration** — `.editorconfig`, `pint.json`, `.php-cs-fixer.php`, `phpcs.xml`, `.eslintrc`, `.prettierrc`, `composer.json` platform constraints. These are the project's rules, written down and enforced by its own tooling.
3. **The conventions actually observed in the existing codebase**, as recorded in `.claude/project/conventions.md`. When the file you are editing disagrees with the project as a whole, **the file you are editing wins** — local consistency beats global consistency.
4. **`company/standards/`** — this directory. The company's defaults.
5. **Framework or community defaults** — PSR-12, Laravel conventions, WordPress Coding Standards.
6. **Agent preference.** Effectively never. If you are choosing on personal preference, you have skipped a rung.

**The one exception is the security floor (§6), which never yields to anything below rung 1.**

### What this means in practice

> In an existing project, the company's standards are the *fallback*, not the rule. Code that is consistent with the surrounding codebase and violates `coding-standards.md` is **correct**. Code that follows `coding-standards.md` and clashes with the surrounding codebase is **a defect**, and `code-reviewer` rejects it.

If the project uses tabs, you use tabs. If it uses `snake_case` methods, you use `snake_case`. If it puts queries in controllers, your controller matches — and the improvement gets raised as tech debt (§7), not smuggled into your task.

---

## 2. Greenfield mode

The company's standards apply in full, and this is the only mode in which they apply in full.

1. `solution-architect` selects the stack and records the decision in `.claude/project/decisions.md`. In the absence of a reason to differ, the company default is the Laravel profile in `stack-profiles.md`.
2. `devops-engineer` initializes the repository, the toolchain, and the config files that make the standards enforceable — formatter config, linter config, `.editorconfig`, CI.
3. `.claude/project/conventions.md` is still written, and states that the project adopts the company standards, naming any deliberate deviation.
4. Everything in `coding-standards.md`, `testing-standards.md`, `git-workflow.md`, and `code-ownership.md` applies as written.

---

## 3. Brownfield mode — the survey comes first

**No implementation task may be assigned in a brownfield project until the codebase survey is complete and `conventions.md` exists.** The PM enforces this at Definition of Ready; an agent handed a task without it rejects the task.

The survey is a task in its own right — a Spike, assigned to `solution-architect` (or the senior implementation role available), time-boxed, producing exactly one artifact: `.claude/project/conventions.md`.

### 3.1 Survey checklist

**Runtime and versions** — verify, never assume. Every one of these is a hard constraint on what you may write.

- [ ] PHP version — from `php -v` and the `composer.json` `platform`/`require` constraint. **They can differ; the lower one governs.**
- [ ] Database engine and version; whether it is MySQL, MariaDB, or something else
- [ ] Web server and how the app is served (Apache/Nginx/built-in, docroot, rewrite rules)
- [ ] Node version and whether a JS build step exists at all

**Project type**

- [ ] Framework and exact version (`composer.json`, `composer.lock`, `artisan --version`, WordPress `version.php`), or "plain PHP / no framework"
- [ ] Is the framework version still supported, and is upgrading in scope? (Usually not — do not assume it is.)
- [ ] Dependency management: Composer, npm, vendored libraries committed to the repo, or manual downloads

**Structure**

- [ ] Entry point(s) — `public/index.php`, a router, per-page scripts, or WordPress bootstrap
- [ ] Where business logic lives, where data access lives, where views live, where assets live
- [ ] Autoloading — PSR-4, classmap, manual `require`, or none
- [ ] Configuration and secrets — `.env`, `config.php`, `wp-config.php`, constants, hardcoded values
- [ ] **Directory structure written out as an actual tree.** Do not describe it from a framework's documentation; describe what is there.

**Conventions actually in use** — sample several files across different areas, and record the *dominant* pattern plus known exceptions.

- [ ] Indentation (tabs or spaces, width), line endings, max line length
- [ ] Brace style, quote style, array syntax (`array()` vs `[]`)
- [ ] Naming: classes, methods, functions, variables, DB tables and columns, files
- [ ] Type declarations — used, partially used, or absent; `strict_types` present or not
- [ ] Error handling — exceptions, error codes, silent failure, `die()`
- [ ] Comment and docblock style
- [ ] Whether the codebase is internally consistent, or has distinct legacy and modern zones (record where the boundary runs)

**Frontend**

- [ ] Templating — Blade, plain PHP includes, WP template hierarchy, a template engine
- [ ] CSS — SCSS, LESS, plain CSS, a framework (Bootstrap and version, Tailwind); compiled or hand-written
- [ ] JS — jQuery (which version), vanilla, modules, a framework; how it is included
- [ ] Asset locations — the folders where JS and CSS files live (source and public), and how a page links them. Record them in `conventions.md`.
- [ ] Build tooling — Vite, Laravel Mix, Gulp, Webpack, or none. **If there is no build step, do not introduce one** without architect and sponsor approval.

**Tests**

- [ ] Test framework and location, if any
- [ ] **Does the suite currently pass?** Run it. Record the baseline — which tests fail on arrival, before anyone touches anything.
- [ ] Coverage of the area your work will touch

**Version control**

- [ ] Is it a git repository? Something else? Nothing?
- [ ] Branching model inferred from branch names and history
- [ ] Commit message style inferred from `git log` — do not impose Conventional Commits on a project that has never used them
- [ ] Whether `vendor/`, `node_modules/`, or build output are committed (they often are; do not "fix" this unasked)

**Danger zones** — the most valuable section of the survey.

- [ ] Generated files that must never be hand-edited
- [ ] Third-party code that has been modified in place
- [ ] Areas with no tests, high coupling, or known fragility
- [ ] Files or directories the sponsor has declared off-limits
- [ ] Anything whose purpose cannot be determined — record it as unknown rather than guessing

### 3.2 The output

`.claude/project/conventions.md` records the findings above, and from that moment **it is rung 3 of the precedence ladder for that project**. It is a living document: any agent discovering a convention it does not capture, or contradicting what it says, updates it in the same PR and tells the PM.

---

## 4. Working in an existing codebase

1. **Read before writing.** Read the module you are changing and at least two comparable modules elsewhere in the project. Match what you find.
2. **Match the local pattern even when a better one exists.** A file's internal consistency outranks the project's; the project's outranks the company's.
3. **Use the project's own tools.** If it has a formatter config, run it. If it has none, match the surrounding formatting by hand — and do not introduce a formatter as a side effect of a feature task.
4. **Reuse the project's existing helpers, base classes, and utilities** rather than introducing an equivalent from the company's preferred stack.
5. **Do not introduce a dependency** — Composer package, npm package, framework, build tool — without architect approval and security sign-off. Existing projects often have deployment constraints that make a new dependency expensive or impossible.
6. **Follow the project's structure, not the framework's textbook.** If services live in `app/Lib/`, yours goes in `app/Lib/`.

---

## 5. The no-drive-by rule

**Change only what the task requires.**

Prohibited as part of a feature or fix task:

- Reformatting, re-indenting, or re-styling code you did not otherwise need to change
- Renaming existing variables, methods, or files for clarity
- Refactoring surrounding code, extracting methods, or "tidying while I'm here"
- Upgrading a dependency, a language feature, or a framework idiom
- Deleting code that appears unused
- Adding type declarations or `strict_types` to an untyped file
- Fixing unrelated bugs you noticed

Every one of these is legitimate work. **None of it belongs in a task that did not ask for it.** Reasons: it inflates the diff so review cannot see the real change, it makes `git blame` useless, it risks breaking behavior with no test to catch it, and it silently expands scope the PM never approved (PM charter, Duty 9).

**What to do instead:** record it, and tell the PM. It becomes a `tech-debt` item, sized and prioritized like any other work. If the PM agrees it is urgent, it becomes its own task with its own PR.

The one permitted exception is a change that is genuinely unavoidable to make the task work — and it is called out explicitly in the PR body, with the reason.

---

## 6. The security floor

**Security standards never yield to local convention.** They sit above every rung except an explicit sponsor decision, and even then the decision is recorded in `decisions.md` with the risk stated.

You may never write, in any project, in any mode, however much the surrounding code does it:

- User input interpolated into SQL. Use prepared statements, the query builder, or `$wpdb->prepare()` — always.
- Unescaped user data rendered into HTML.
- A write endpoint with no authorization check, or no CSRF protection.
- A secret, key, password, or token committed to the repository.
- User input passed to `eval()`, `exec()`, `unserialize()`, or an include path.
- A password stored with anything but a modern hash.

**But: matching the security floor is not licence to fix the rest of the codebase.** When you find pre-existing violations outside your task's scope:

1. Your own new code meets the floor. Always.
2. Existing violations are **reported to the PM immediately**, who routes them to `security-engineer` (PM charter, Duty 11 — security findings escalate).
3. You do **not** fix them inside your task. They are sized, prioritized, and assigned like any other work.
4. If a violation is severe and live — active injection, exposed credentials, unauthenticated admin access — say so at once and mark it urgent. The PM escalates to the sponsor the same cycle.

---

## 7. Improving a brownfield codebase

Improvement is welcome. It is just never a side effect.

- Log the observation as `tech-debt` in the backlog with a concrete description and the cost of leaving it.
- The PM prioritizes it against feature work like anything else.
- Approved improvements get their own task, own branch, own PR, own tests, and are reviewed on their own merits.
- **Refactors ship separately from behavior changes**, always — `git-workflow.md` §2.
- Prefer the boy-scout rule at *task* granularity, not line granularity: leave the module you were assigned better, in a way the PM approved, not every file you happened to open.

**Characterization tests come first.** Before refactoring untested legacy code, write tests that capture what it does *now* — including behavior that looks wrong. You cannot safely change what you cannot verify, and in legacy code today's bug is sometimes tomorrow's depended-upon feature.

---

## 8. The PM's obligations

At intake (PM charter, Duty 1), the PM records:

- [ ] **Engagement mode** — greenfield or brownfield
- [ ] **Stack profile** — which profile in `stack-profiles.md` applies
- [ ] **Whether `conventions.md` exists.** If not, in brownfield, the first task assigned is the survey. Nothing else may be assigned before it.

Every assignment record then names the applicable profile and points to `conventions.md`, so an implementation agent knows which rulebook governs before it opens a file.
