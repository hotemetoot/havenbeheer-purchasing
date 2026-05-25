# 009a — PO collection + po_lines + Generate-PO button

## Goal
Procurement can click "Generate PO" on an approved PR to spin up a draft `purchase_orders` record with one default `po_line` pre-filled from the PR. Lines are editable in NocoBase; PO total is auto-maintained by a small workflow.

## Scope (in)
- New collections:
  - `delivery_addresses` (name, address, is_default boolean, status)
  - `units_of_measure` (name, abbreviation, status)
  - `products` (name, description, default_uom, status) — v1 stub
  - `purchase_orders` — per PO design validation §9: `po_number` sequence, `purchase_request` m2o, `supplier` m2o, `delivery_address` m2o, `status`, `currency`, `fx_rate_to_usd`, `total`, `total_usd`, `payment_status`, `payment_date`, `expected_delivery_date`, `quotations` attachment-multi, `attachments` attachment-multi, `supplier_note`, `internal_notes`, `budget_override_comment`, `close_reason`, `close_comment`, audit timestamps
  - `po_lines` — per PO design §9: `purchase_order` m2o, `product` m2o optional, `description`, `unit_of_measure` m2o, `quantity_ordered`, `unit_price`, `line_total` formula, `line_total_usd` formula, `received_quantity`, `line_status`
- Add `address` (textarea) to `suppliers`.
- **Generate-PO action** on `purchase_requests` table/detail. Visibility: only when `status = approved` AND no PO yet (D9: one PR → one PO).
- Generate-PO behavior: creates draft PO pre-filled —
  - `supplier` ← `pr.supplier`
  - `currency` ← `pr.quoted_currency`
  - `fx_rate_to_usd` ← `pr.fx_rate_to_usd`
  - one default `po_line`: description from `pr.description` (or `pr.title`), `unit_price` = `pr.quoted_total`, `quantity_ordered` = 1
  - `quotations` copied from `pr.quotation_attachment`
- Procurement can edit `po_lines` post-generate: split into structured lines, add/remove.
- Small workflow keeps `purchase_orders.total` = SUM(`po_lines.line_total`). NocoBase formula fields cannot aggregate child records (PO design decision 12).
- **Guard:** API-side block on creating a PO against a PR with status ≠ approved.

## Scope (out)
- Sending the PO (status `draft → sent`) — MVP9b.
- Budget zones / overrun guard — MVP9b.
- Receiving — MVP9c.
- Completion / closing / cancellation — MVP9d.
- Template printing — MVP9e.
- Multi-PO per PR — explicitly out under D9.

## Dependencies
- Requires MVP7 (suppliers) and MVP8 (PR has the attachment + supplier surfaces).

## Acceptance
- PO1: Generate PO from an approved PR → succeeds, one default line, all pre-fill rules match.
- PO2: Generate PO from a non-approved PR → button hidden in UI, API call blocked.
- PO3: PR with an existing PO → Generate-PO button hidden.
- PO4: Add/edit/remove `po_lines` → `purchase_orders.total` updates correctly.
- PO5: ACL — only procurement can edit `po_lines`.
- Manual verification by user before marking complete.

## Phases
- **9a.1** Create the 4 lookup/header collections + `po_lines`.
- **9a.2** Add `address` to `suppliers`.
- **9a.3** Build PO list + detail page.
- **9a.4** Build Generate-PO action (workflow that creates PO + 1 default line; visibility linkage on the button).
- **9a.5** Build the small total-maintenance workflow.
- **9a.6** Build the create-PO guard (request-interception checking PR status).
- **9a.7** Verify the acceptance scenarios.
