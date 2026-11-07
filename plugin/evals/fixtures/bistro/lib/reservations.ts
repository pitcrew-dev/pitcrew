import "server-only";
import { db } from "./db";

export async function freeTables(startsAt: Date, partySize: number) {
  return db.diningTable.findMany({
    where: {
      seats: { gte: partySize },
      reservations: { none: { startsAt } },
    },
    select: { id: true, seats: true },
  });
}
