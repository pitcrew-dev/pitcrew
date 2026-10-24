# Standard — Git Workflow

**Model:** trunk-based development — a protected `main`, short-lived task branches, one task per pull request.
**Applies to:** every role that changes files.

> ### ⚠ This describes greenfield. An existing repository keeps its own workflow.
>
> Per [`engagement-modes.md`](engagement-modes.md), a project's established VCS conventions outrank this file. During the survey, read `git log` and the branch list and record in `conventions.md`:
>
> - The **branching model** actually in use — `develop`/`release` branches, long-lived environment branches, or trunk
> - The **commit message style** in the history. **Do not impose Conventional Commits on a project that has never used them** — match what is there
> - Whether **merge or squash** is the norm, and whether history is linear or has merge commits
> - Whether PRs are used at all, and what review is expected
> - What is committed that this file would exclude — `vendor/`, build output, and committed dependencies are common and are **not** to be "fixed" unasked
>
> **If the project is not under version control**, that is a project risk logged in `raid.md` and escalated to the sponsor before implementation begins. Initializing a repository over someone's live codebase is a sponsor decision, not an agent's.

---

## 1. Branches

- **`main` is always deployable.** It is protected: no direct pushes, no force-pushes, merges only via reviewed PR.
- **One task, one branch, one PR.** Branches are short-lived — hours to a day or two. A branch open longer than a few days means the task was sliced too large; tell the PM.
- Name branches after the task ID from the PM's assignment record, so any branch traces to the requirement that justified it:

  ```
  <type>/<TASK-ID>-<short-kebab-summary>

  feat/PROJ-E02-S05-T03-user-search-endpoint
  fix/PROJ-D014-order-total-rounding
  chore/PROJ-E01-S02-T01-pint-config
  ```

  Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`, `spike`.
- Branch from current `main`. **Rebase onto `main`, do not merge `main` into your branch** — keep history linear and the diff honest.

## 2. Commits

**One line only. Conventional Commits**, imperative mood, subject <= 72 characters, no trailing period, **no body**:

```
<type>(<scope>): <what changed>
```

```
feat(users): add paginated search endpoint
fix(orders): round order totals to two decimals
chore(ci): cache composer downloads
```

Rules:

- **One line.** No body, no bullet lists, no explanation paragraphs. A change that needs paragraphs to explain is too big: split it.
- **No trailers.** No `Co-Authored-By`, no session or tool links, no sign-off lines.
- Where the project uses task IDs, put the ID in the scope: `feat(PROJ-E02-S05-T03): add user search endpoint`.
- **Atomic commits.** One logical change each. The suite passes at every commit, not merely at the tip.
- **Never mix concerns.** Formatting, refactoring and behavior change go in separate commits. A reformatting diff bundled with a logic change is unreviewable and will be sent back.
- Never commit: `.env`, secrets, keys, `vendor/`, `node_modules/`, `public/build/`, IDE state, `.orig`/`.rej`, or commented-out code.
- No `wip`, `fix`, `asdf` or `stuff` as messages. Squash them before opening the PR.
- **Never rewrite published history** on a shared branch. Rebase your own task branch freely before review; never after others have pulled it.

The reasoning that used to go in a commit body belongs in the PR body (section 3) and in `decisions.md`.

## 3. Pull requests

A PR is opened only when the task's Definition of Done is otherwise satisfied — tests written and green, Pint clean, build passing.

**PR title:** `<type>(<scope>): <summary>  [TASK-ID]`

**PR body:**

```markdown
## Task
PROJ-E02-S05-T03 — <task title>

## What changed
<Two or three sentences. What behavior is different now.>

## Why
<The requirement or defect this serves.>

## Acceptance criteria
- [ ] Given … When … Then …
- [ ] Given … When … Then …

## Seam changes
<View-data keys, route names, or JSON shapes added, renamed, or removed.
 "None" if none. A rename here requires the paired frontend task to be linked.>

## Testing
<What was added. How a reviewer verifies it locally.>

## Risk
<Migrations, data backfill, config or env changes, anything needing a deploy step
 or a rollback plan. "None" if none.>
```

Rules:

- **Keep PRs small.** Under ~400 changed lines is the target; a PR over ~800 gets returned to the PM as a slicing failure, not reviewed.
- **The author never merges their own PR unreviewed.** `code-reviewer` approval is required; `security-engineer` approval is additionally required when the change touches auth, payment, PII, or file upload.
- **Draft PRs are for feedback, not for merging.** Mark ready only when every box above is real.
- **Address every review comment** — with a change, or with a reply explaining why not. Silently resolving a thread is prohibited.
- **A failed review returns the task to development on the same branch and the same task record** (PM charter, Duty 8.2). Do not open a fresh PR for a rework cycle; push follow-up commits to the existing one so the review history stays intact.
- **Squash-merge** into `main`, with the final message following §2 and referencing the task ID. Delete the branch on merge.

## 4. Conflicts

- Rebase early and often; a long-lived branch is a conflict generator.
- **Resolve conflicts in your own code only.** A conflict in a path your role does not own (`code-ownership.md`) means two tasks collided — stop, and raise it to the PM rather than resolving someone else's work.
- After resolving, re-run the full suite. A conflict resolution that compiles is not a conflict resolution that works.

## 5. Releases

- `main` is tagged for release using semantic versioning: `v<major>.<minor>.<patch>`.
- Every release carries a changelog entry generated from conventional-commit types.
- Migrations ship with the release that needs them and are verified reversible in staging before production.
- `devops-engineer` owns the tag, the deploy, and the rollback plan; the developer owns making the change safe to roll back.
