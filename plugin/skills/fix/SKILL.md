---
name: fix
description: Fix one broken thing. Finds the cause, has one developer write a test that reproduces it and then fix it, checks the result, and stops. Use when the user says it's broken, "fix this error", "this page shows an error", "there's a bug", or pastes an error message. For one problem only, not new features.
---

# Fix — One Problem, One Developer, Stop

You are the **Project Manager**. Read `${CLAUDE_PLUGIN_ROOT}/company/pm-brief.md` once per session. Respect "Never plan what the framework blocks".

## Step 1 — Write it down, check the size

Write the user's words down **verbatim**. If it is really a **new feature**, or **several problems**, say so in one line and offer `/company:start` or adding it to the plan. Then stop.

## Step 2 — Safety net

No git repo: follow `/company:start` Step 4b (don't restate it here). Then record **BASE** with `git rev-parse HEAD`.

## Step 3 — Give it an ID

Hooks log cost by this ID. Put it in every dispatch and in the agent's description.

| Situation | ID |
|---|---|
| A project exists (`.claude/project/plan.md`) | `<PREFIX>-D<n>`: prefix from `plan.md`, next free number |
| No project | `FIX-D<n>`: look at `git log` for the last one used |

## Step 4 — Find the cause, cheaply

Reproduce it or read the error. **Grep before reading**; open only the files involved. Take the setup facts (check command, how to run a test) from `conventions.md`; with no project, find them once yourself.

## Step 5 — Lane check

| Touches | Lane |
|---|---|
| Login or permissions, payment, personal data, uploads, database schema or migrations, deploy | **Sensitive.** Tell the user in one line, then run the full flow from `/company:next` Steps 3–4 for this one task: review, QA, `/security-review` and **their approval** |
| Anything else | **Light** |

## Step 6 — Light: one developer

Dispatch **one** agent, `company:full-stack-developer` by default, with:

- the problem, verbatim
- the cause you found, and the scope (files in, files out)
- the setup facts, the ID and BASE
- the rule: **write a test that reproduces the bug, show it failing, fix it, show it passing, run the check command**

Then you check `git diff BASE`, run the new test and the check command. If anything is wrong, send it back to the **same** developer with `SendMessage`. Three strikes: stop and ask the user. When it's right, commit in the project's style (`conventions.md`), with the ID in the message.

## Step 7 — Record (only if a project exists)

- One line under `## Done` in `plan.md`: ID, what was fixed, date.
- One line in `lessons.md` if the same cause could happen again.

## Step 8 — Report and STOP

In plain words:

- **What was broken**, and **why**
- **What changed**
- **How they can check it themselves:** the exact page or command
- **What it cost:** the last line for this ID in `activity.md`
- "To undo this, just say so, or use `/rewind`."

Then stop. Don't start on anything else.
