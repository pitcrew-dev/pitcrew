CREATE TABLE "DiningTable" (
    "id" SERIAL NOT NULL,
    "seats" INTEGER NOT NULL,
    CONSTRAINT "DiningTable_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Reservation" (
    "id" SERIAL NOT NULL,
    "tableId" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "startsAt" TIMESTAMPTZ NOT NULL,
    "partySize" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Reservation_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "Reservation_tableId_idx" ON "Reservation"("tableId");

ALTER TABLE "Reservation" ADD CONSTRAINT "Reservation_tableId_fkey" FOREIGN KEY ("tableId") REFERENCES "DiningTable"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
