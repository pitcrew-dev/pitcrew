"use client";

export function ReservationForm() {
  // TODO (BIS-E01-S02): post to a server action that saves the reservation.
  return (
    <form>
      <label>
        Name <input name="name" required />
      </label>
      <label>
        Phone <input name="phone" type="tel" required />
      </label>
      <label>
        Date and time <input name="startsAt" type="datetime-local" required />
      </label>
      <label>
        Guests <input name="partySize" type="number" min={1} max={12} required />
      </label>
      <button type="submit">Reserve</button>
    </form>
  );
}
