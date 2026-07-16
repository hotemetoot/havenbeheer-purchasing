# 009c — PO receiving

## Goal
Receiver records `received_quantity` per line. PO line status and PO header status auto-derive. Procurement gets an in-app notification when a PO is fully received.

## Scope (in)
- `po_lines.received_quantity` (decimal, fractional supported — PO design §9).
- `po_lines.line_status` single-select (pending / partially_received / received) — workflow-maintained.
- PO header status auto-derivation: all lines `received` → PO becomes `received`. Reversible when corrected downward.
- In-app notification when all lines received: "PO X ready to complete" → procurement.
- Record History enabled on `po_lines.received_quantity` (PO design §9 note).

## Scope (out)
- Completion (9d) — receipt is not the same as completion.
- Printing (9e).

## Dependencies
- Requires 9a (po_lines must exist) and 9b (PO must be `sent`-able).

## Acceptance
- R1: partial receive → line status partially_received, header stays `sent` (or whatever the prior status was).
- R2: full receive on all lines → header becomes `received`, notification fires.
- R3: corrected-down (received → partially_received) → header reverts from `received`.
- R4: receive against a non-`sent` PO → blocked.
- Manual verification by user.

## Phases
- **9c.1** Add receiving fields to po_lines (may already exist from 9a — verify).
- **9c.2** Receiving workflow (recompute line_status + PO header status).
- **9c.3** In-app notification on full-receive.
- **9c.4** Verify R1–R4.
