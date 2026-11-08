# Plan

## Now

- Where we are: piece S01 (the home and reservation pages) is done.
- Next: BIS-E01-S02-T01, the reservation form saves a reservation.
- Waiting on the owner: nothing.

## The request

A restaurant owner wants guests to reserve a table online, and staff to see tonight's reservations.

## Goals

| ID | Outcome | Done when | Progress |
|---|---|---|---|
| G1 | Guests reserve a table online without calling | I reserve on my phone and it shows in the staff list | 1 of 2 stories |

## Pieces

### BIS-E01-S02 Reservation form saves a reservation
goal: G1 · So that guests can reserve without calling · size: 1 task · lane: Standard

Checks:
- Given a free table for 4 at 19:00, when a guest submits the form for 4 people at 19:00, then the reservation is saved and they see a confirmation.
- Given no table seats 13, when a guest asks for 13 people, then they see "No table is big enough" and nothing is saved.

| Task | What | Role | Lane | State | Date | Note |
|---|---|---|---|---|---|---|
| BIS-E01-S02-T01 | Server action that validates and saves a reservation, wired to the form | full-stack-developer | Standard | Ready | 2026-10-24 | Stack guides: stacks/nextjs.md, stacks/prisma.md |

## Done

- BIS-E01-S01 Home and reservation pages (G1), 2026-10-22. QA PASS.
