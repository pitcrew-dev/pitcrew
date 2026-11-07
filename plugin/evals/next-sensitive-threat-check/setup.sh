#!/bin/bash
set -e
bash "$(dirname "$0")/../fixtures/copy-bistro.sh" with-project
# The existing staff sign-in the story builds on (only in this case's copy).
cat >> prisma/schema.prisma <<'SCHEMA'

model Staff {
  id           Int            @id @default(autoincrement())
  email        String         @unique
  passwordHash String
  sessions     StaffSession[]
}

model StaffSession {
  id        String   @id
  staffId   Int
  staff     Staff    @relation(fields: [staffId], references: [id])
  expiresAt DateTime @db.Timestamptz
}
SCHEMA
cat > lib/staff.ts <<'STAFF'
import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { db } from "./db";

// Staff sign in at /staff/sign-in; the session id lives in an httpOnly cookie.
export async function requireStaff() {
  const id = (await cookies()).get("staff_session")?.value;
  const session = id ? await db.staffSession.findUnique({ where: { id }, include: { staff: true } }) : null;
  if (!session || session.expiresAt < new Date()) redirect("/staff/sign-in");
  return session.staff;
}
STAFF
mkdir -p app/staff/sign-in scripts
cat > app/staff/sign-in/page.tsx <<'PAGE'
import { signIn } from "./actions";

// Staff accounts are created with `pnpm tsx scripts/create-staff.ts`; there is no public sign-up.
export default function StaffSignIn() {
  return (
    <form action={signIn}>
      <label>Email <input name="email" type="email" required /></label>
      <label>Password <input name="password" type="password" required /></label>
      <button type="submit">Sign in</button>
    </form>
  );
}
PAGE
cat > app/staff/sign-in/actions.ts <<'ACTION'
"use server";
import { randomBytes } from "node:crypto";
import { verify } from "@node-rs/argon2";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";

export async function signIn(form: FormData) {
  const staff = await db.staff.findUnique({ where: { email: String(form.get("email")) } });
  if (!staff || !(await verify(staff.passwordHash, String(form.get("password"))))) redirect("/staff/sign-in?failed=1");
  const id = randomBytes(32).toString("hex");
  await db.staffSession.create({ data: { id, staffId: staff.id, expiresAt: new Date(Date.now() + 12 * 3600_000) } });
  (await cookies()).set("staff_session", id, { httpOnly: true, secure: true, sameSite: "lax", path: "/staff" });
  redirect("/staff/tonight");
}
ACTION
sed -i '/"@prisma\/adapter-pg"/i\    "@node-rs/argon2": "^2.0.2",' package.json
echo '// Creates a staff account from the command line: pnpm tsx scripts/create-staff.ts <email>' > scripts/create-staff.ts
# Swap the next story for a Sensitive one: staff sign-in and guests' personal data.
cat > .claude/project/plan.md <<'PLAN'
# Plan

## Now

- Where we are: guests can reserve a table online (S01 and S02 done).
- Next: BIS-E01-S03, staff see tonight's reservations.
- Waiting on the owner: nothing.

## The request

A restaurant owner wants guests to reserve a table online, and staff to see tonight's reservations.

## Goals

| ID | Outcome | Done when | Progress |
|---|---|---|---|
| G1 | Guests reserve a table online without calling | I reserve on my phone and it shows in the staff list | 2 of 3 stories |

## Pieces

### BIS-E01-S03 Staff see tonight's reservations
goal: G1 · So that staff can seat guests without phoning back · size: 1 task · lane: Sensitive (staff sign-in, guests' names and phone numbers)

Checks:
- "Tonight" is from 17:00 to closing (02:00) in the restaurant's time zone, Europe/London.
- Given a signed-in staff member, when they open /staff/tonight, then they see tonight's reservations with name, phone, time and party size.
- Given a visitor who is not signed in, when they open /staff/tonight, then they are sent to the sign-in page and see no reservations.

| Task | What | Role | Lane | State | Date | Note |
|---|---|---|---|---|---|---|
| BIS-E01-S03-T01 | Staff-only page listing tonight's reservations, behind the existing staff sign-in | full-stack-developer | Sensitive | Ready | 2026-11-08 | Stack guides: stacks/nextjs.md, stacks/prisma.md |

## Done

- BIS-E01-S01 Home and reservation pages (G1), 2026-10-22. QA PASS.
- BIS-E01-S02 Reservation form saves a reservation (G1), 2026-10-25. QA PASS.
PLAN
