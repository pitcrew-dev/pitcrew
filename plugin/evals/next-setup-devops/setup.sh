#!/bin/bash
set -e
bash "$(dirname "$0")/../fixtures/copy-bistro.sh" with-project
# Put a setup story first: automatic checks on every push, before more building.
cat > .claude/project/plan.md <<'PLAN'
# Plan

## Now

- Where we are: the home and reservation pages are done (S01).
- Next: BIS-E00-S01, automatic checks on every push. The owner asked for it before more building.
- Waiting on the owner: nothing. They have a Vercel account and will connect the repository and set the secrets themselves.

## The request

A restaurant owner wants guests to reserve a table online, and staff to see tonight's reservations.

## Goals

| ID | Outcome | Done when | Progress |
|---|---|---|---|
| G1 | Guests reserve a table online without calling | I reserve on my phone and get a confirmation | 1 of 2 stories |
| G2 | Nothing broken reaches guests | A change that breaks the tests can't be merged | 0 of 1 stories |

## Pieces

### BIS-E00-S01 Automatic checks on every push
goal: G2 · So that a broken change is caught before anyone sees it · size: 1 task · lane: Standard (setup; nothing is deployed)

Checks:
- Given a push or pull request to main, when GitHub Actions runs, then lint, type check, tests and build run on Node 22 with pnpm from the lock file.
- Given a failing test, when the workflow runs, then it fails and shows which step broke.
- Given the Vercel project, when the owner connects it, then `vercel.json` and `.env.example` tell them every variable to set, with no values in the repository.

| Task | What | Role | Lane | State | Date | Note |
|---|---|---|---|---|---|---|
| BIS-E00-S01-T01 | GitHub Actions workflow, `vercel.json` for preview deploys, `.env.example` | devops-engineer | Standard | Ready | 2026-11-08 | Stack guides: stacks/nextjs.md, stacks/prisma.md |

### BIS-E01-S02 Reservation form saves a reservation
goal: G1 · depends on: BIS-E00-S01 · lane: Standard · state: Ready

## Done

- BIS-E01-S01 Home and reservation pages (G1), 2026-10-22. QA PASS.
PLAN
# The finished first story is already committed, as /pit:next would have done.
git init -q 2>/dev/null || true
git -c core.autocrlf=false add -A
git -c user.name="PitCrew eval" -c user.email="eval@example.invalid" commit -qm "feat: home and reservation pages (BIS-E01-S01)"
