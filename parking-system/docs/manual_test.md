# Manual test checklist

Tick each one off after a fresh `python setup_db.py` + `python run.py`.

## Auth
- [ ] Register a new account. Validation errors appear for short password,
      mismatched confirm, bad email.
- [ ] Log in as `admin@smartpark.in` / `Password@123` → lands on `/admin/`.
- [ ] Log in as `aarthi@example.com` → lands on `/`.
- [ ] Sign out, then open `/admin/` directly → redirected to login.
- [ ] Try to POST a form without a CSRF token (edit HTML in devtools) →
      400 error page appears.

## Live map
- [ ] `/availability` shows both levels. Click the Basement 1 tab — slots move.
- [ ] Slot states match the legend (mint = available, rose = occupied,
      periwinkle = reserved, butter = EV, orchid = women).
- [ ] Leave the page open 10 seconds — the map polls and one or two slots
      change state when an admin marks an entry.

## Booking
- [ ] Log in as `aarthi`. Go to `/book`. Click a green slot on the map.
- [ ] Set start = now + 15 min, end = +2 hours. Fee updates live.
- [ ] Select an EV bay → charger options appear and the vehicle type switches
      to EV Car. Fee includes the ₹12/hr add-on.
- [ ] Submit. Payment page appears with the correct amount.
- [ ] Choose UPI → Confirm. Ticket page appears with a QR code.
- [ ] Open the same slot in a second tab and try to book the *same* window →
      "Someone just took that slot" message.

## My bookings & cancel
- [ ] `/bookings` shows the new booking under "Upcoming".
- [ ] Cancel it. Slot turns green again on the map within 5 seconds.

## Admin
- [ ] Admin → Overview. Revenue card updates after a payment.
- [ ] Slot manager: add a slot `G-30` at position `980, 130`. It appears on the
      map on the next poll.
- [ ] Disable `G-30`. It shows as disabled and cannot be booked.
- [ ] Entry/exit desk: log entry for `KA-01-AB-1234` at `G-30` (a fresh bay).
      Slot turns pink on the map.
- [ ] Mark exit → fee is computed, session disappears from "Currently inside",
      slot turns green.
- [ ] Users page: toggle disable on `karthik@example.com`. Sign in as Karthik
      in another tab → kicked out on next request.
- [ ] Women's Safety monitor: as `meera@example.com`, press SOS on an active
      ticket. Within 5 seconds the admin nav badge shows "1 open". Click into
      the page, resolve it. Badge disappears.

## Reports
- [ ] Pick a 7-day range → chart, table and peak hours populate.
- [ ] CSV download opens in Excel with correct totals.
- [ ] Print view (Ctrl+P) looks clean — no glass blur, no background blobs.

## Accessibility & polish
- [ ] Tab through the booking page. Focus ring is visible on every input,
      button and slot tile.
- [ ] Slots are reachable with Tab and selectable with Enter / Space.
- [ ] Turn on "Reduce motion" in the OS. Blobs stop drifting.
- [ ] Resize to a phone width (e.g. 375px). Layout is single-column, blobs
      are softer, no horizontal scroll.
- [ ] Print a ticket (Ctrl+P). Background blobs and toasts are hidden.

## Notes
- Blob drift, blur and glass effects are disabled automatically under
  `prefers-reduced-motion: reduce` and inside `@media print`.
- If a browser does not support `backdrop-filter`, the app falls back to a
  solid white glass surface with the same border and shadow.