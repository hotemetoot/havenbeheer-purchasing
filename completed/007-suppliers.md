# 007 — Suppliers (descoped)

**Built:** 2026-05-24. **Design change:** D26 — `supplier_issues` and `supplier_evaluations` postponed; only `suppliers` built. Verification of S1, S2, S5 (those that don't require issues/evaluations): confirm with user.

## Goal (as built)
Track suppliers with enough fields to use them as a "Suggested supplier" on a PR. Defer the supplier-issue logging and evaluation scoring features.

## What was built
- `suppliers` collection (collection key `a4ogom91smz`) with these fields:
  - `name` (input, title field)
  - `display_name`, `tax_id`, `email`, `phone`
  - `address` (textarea)
  - `country` (select)
  - `default_currency` (select USD/SRD/EUR)
  - `payment_terms` (select Net30/Net60/Net90/COD/Prepayment) per D17
  - `status` (select active/inactive/blocked, default active)
  - `current_rating` (number 1–5) — manual per D6
  - `notes` (textarea)
- Optional `supplier` (m2o → suppliers, "Suggested supplier" label) on `purchase_requests`.
- Approval workflow updated to a new revision (the version active during the MVP7 build was `366232953880576`; since superseded by `366234405109760`) so all three approval forms display the supplier field.
- ACL: procurement-only create/edit on `suppliers` (Guard #9 per D8); all roles view.

## What was NOT built (D26 — postponed)
- `supplier_issues` collection
- `supplier_evaluations` collection
- "Anyone can log a supplier issue / procurement resolves" workflow
- Evaluation scoring (1–5) UI
- Original verification scenarios S3, S4 (issue logging + procurement resolution)

A future MVP can revisit. See [chunks/deferred-supplier-issues-evaluations.md](../chunks/deferred-supplier-issues-evaluations.md).

## Live IDs
See [project_current_state.md](../project_current_state.md) for current workflow + collection IDs.

## Scenarios applicable to what was built
- S1: procurement adds a supplier → succeeds (confirm with user)
- S2: alice (member) tries to add a supplier → blocked (confirm with user)
- S5: PR submits with `supplier` populated; PR submits with `supplier` empty (confirm with user)
- S3, S4: not applicable — issue logging not built.
