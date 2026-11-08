# Plan

## Now

- Where we are: piece S02 (booking form saves a booking) is in QA; its email task is blocked.
- Next: S02-T02 once the owner gives the email sender address, then E02-S01 (today's bookings page).
- Waiting on the owner: the email address that confirmation emails are sent from.

## The request

A salon owner wants customers to book appointments online, and staff to see today's bookings at a glance.

## Goals

| ID | Outcome | Done when | Progress |
|---|---|---|---|
| G1 | Customers can book an appointment online without calling | I book on my phone and it shows in the admin list | 1 of 2 stories |
| G2 | Staff see today's bookings at a glance | I open the admin page and see today's list | 0 of 1 stories |

## Pieces

### SHOP-E01-S02 Booking form saves a booking
goal: G1 · So that customers can book without calling · size: 2 tasks · lane: Standard

| Task | What | Role | Lane | State | Date | Note |
|---|---|---|---|---|---|---|
| SHOP-E01-S02-T01 | Save booking | backend-developer | Standard | In QA | 2026-10-23 | Review PASS; QA next |
| SHOP-E01-S02-T02 | Confirmation email | backend-developer | Standard | Blocked | 2026-10-23 | Needs the owner's email sender address |

### SHOP-E02-S01 Today's bookings page
goal: G2 · So that staff see the day at a glance · size: 1 task · lane: Standard

| Task | What | Role | Lane | State | Date | Note |
|---|---|---|---|---|---|---|
| SHOP-E02-S01-T01 | Bookings list for today | full-stack-developer | Standard | Ready | 2026-10-23 | |

## Done

- SHOP-E01-S01 Booking page shows free times (G1), 2026-10-20. Review PASS, QA PASS.
