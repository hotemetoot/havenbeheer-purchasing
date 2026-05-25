# 009d — PO completion / closing / cancellation + immutability

## Goal
Procurement can complete a received PO, close a stuck one with a reason, or cancel a draft. Terminal POs are immutable (same pattern as PR Guard A).

## Scope (in)
- **Complete action:** status `received → completed` (manual procurement action).
- **Close action:** status `sent / confirmed / partially_received → closed`. Requires `close_reason` (single-select) and `close_comment` (textarea).
- **Cancel action:** status `draft → cancelled`.
- **PO immutability guard** when status ∈ {completed, closed, cancelled} — same pattern as PR Guard A (D24 limitation noted for bulk-update).
- Audit timestamps: `sent_at`, `confirmed_at`, `completed_at`, `closed_at`, `cancelled_at`.

## Scope (out)
- Template printing (9e).
- Reopening closed/completed POs.

## Dependencies
- Requires 9a, 9b, 9c.

## Acceptance
- C1: complete from `received` → `completed`, timestamp set.
- C2: close from `sent` → `closed` requires reason + comment, timestamp set.
- C3: cancel from `draft` → `cancelled`, timestamp set.
- C4: any edit on terminal PO → blocked.
- C5: D24-style bulk-update limitation acknowledged; document and defer matching fix if needed.
- Manual verification by user.

## Phases
- **9d.1** Add status transition actions (complete / close / cancel).
- **9d.2** Build PO immutability guard.
- **9d.3** Verify C1–C5.
