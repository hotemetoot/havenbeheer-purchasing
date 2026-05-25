# 007 — Suppliers + supplier_issues + supplier_evaluations

**Built:** 2026-05-24. **Verification status:** confirm with user (S1–S5 scenarios — execution status not recorded in the migrated memory).

## Goal
Track suppliers, log supplier issues from any user, and capture procurement's structured evaluations. Link a "Suggested supplier" on each PR.

## What was built
- `suppliers` collection: name, display_name, tax_id, country, default_currency, `payment_terms` single-select (Net30/Net60/Net90/COD/Prepayment per D17), status, notes, `current_rating` (manual 1–5 per D6).
- `supplier_issues` collection (full schema per PR design §11).
- `supplier_evaluations` collection (full schema; `score` 1–5 per D7).
- Optional `supplier` (m2o → suppliers, "Suggested supplier" label) on `purchase_requests`.
- ACL: procurement-only create/edit on `suppliers` (Guard #9 per D8); all roles view. All roles create supplier issues and evaluations; procurement edits/resolves.
- Approval workflow updated to a new revision (active version `366232953880576`) so all three approval forms display the supplier field. Director's view is readPretty.

## Live IDs
See [project_current_state.md](../project_current_state.md) for current approval surface IDs (`7xwj8l0sjqp`, `knwxauc0yoz`, `lav2su037qi`) and disabled old surfaces under "Stale IDs".

## Scenarios (verification pending confirmation)
- S1: procurement adds a supplier → succeeds
- S2: alice (member) tries to add a supplier → blocked
- S3: anyone logs a supplier_issue → succeeds
- S4: procurement resolves an issue → succeeds
- S5: PR submits with `supplier` populated; PR submits with `supplier` empty (both valid)
