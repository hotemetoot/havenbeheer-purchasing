# 009a — PO collection + po_lines + Generate-PO button (built ✓)

## Goal
Procurement can click "Generate PO" on an approved PR to spin up a draft `purchase_orders` record with one default `po_line` pre-filled from the PR. Line items track quantity + receiving only (D27 — pricing descoped); PO `total` is manually entered from the supplier invoice.

## Scope (in) — as built
- New collections:
  - `delivery_addresses` (name, address, is_default boolean, status)
  - `units_of_measure` (name [unique], abbreviation, status)
  - `products` (name [unique], description, default_uom, status) — v1 stub
  - `purchase_orders` — `po_number` sequence (`PO-YYYY-NNNN`), `purchase_request` m2o (FK `purchaseRequestId` on PO side), `supplier` m2o, `delivery_address` m2o, `status`, `currency`, `fx_rate_to_usd`, `total` (manually entered), `total_usd` formula `{{total}} / {{fx_rate_to_usd}}` (division — `fx_rate_to_usd` is local-per-USD), `payment_status`, `payment_date`, `expected_delivery_date`, `invoice` attachment, `attachments` attachment-multi, `supplier_note`, `internal_notes`, `budget_override_comment`, `close_reason`, `close_comment`, audit timestamps (`sent_at`, `confirmed_at`, `completed_at`, `closed_at`, `cancelled_at` — populated by later MVPs).
  - `po_lines` — `purchase_order` m2o, `product` m2o optional, `description` textarea required, `unit_of_measure` m2o, `quantity_ordered`, `received_quantity`, `line_status` (default `pending`). **Pricing fields (`unit_price`, `line_total`, `line_total_usd`) were descoped per D27.**
- Inverse relation `purchase_requests.purchase_order` — `oho` / hasOne (virtual, no FK column on PR side).
- **Generate-PO action** on `purchase_requests` table/detail. Visibility: only when `status = approved` AND no PO yet AND user has role `Procurement`.
- Generate-PO behavior: creates draft PO pre-filled —
  - `purchase_request` ← `pr.id`
  - `supplier` ← `pr.supplier`
  - `currency` ← `pr.quoted_currency`
  - `fx_rate_to_usd` ← `pr.fx_rate_to_usd`
  - `total` ← `pr.quoted_total` (editable post-invoice)
  - `delivery_address` ← default row from `delivery_addresses`
  - `status` ← `draft`
  - `createdById` ← triggering user
  - one default `po_line`: `description` from `pr.description`, `quantity_ordered = 1`
- Procurement can edit `po_lines` post-generate: split into structured lines, add/remove.
- **Guards (two layers, both required):**
  - Inline condition node in Generate-PO workflow (catches button re-trigger / linkage-rule bypass — request-interception does NOT cover workflow-internal creates).
  - Global request-interception guard on `purchase_orders.create` (catches direct API POST that bypasses the button).

## Scope (out)
- Sending the PO (status `draft → sent`) — MVP9b.
- Budget zones / overrun guard — MVP9b.
- Receiving — MVP9c.
- Completion / closing / cancellation — MVP9d.
- Template printing — MVP9e.
- Multi-PO per PR — explicitly out under D9.
- Line-level pricing / line-level USD — descoped under D27.
- Workflow-maintained PO total from line sums — cancelled under D27 (total is manual).

## Dependencies
- Requires MVP7 (suppliers) and MVP8 (PR has the attachment + supplier surfaces).

## Acceptance — verified
- PO1: Generate PO from an approved PR → succeeds, one default line, all pre-fill rules match ✓
- PO2: Generate PO from a non-approved PR → button hidden in UI, direct API call blocked by request-interception guard ✓
- PO3: PR with an existing PO → Generate-PO button hidden ✓
- PO4: Inline guard blocks duplicate generation even if linkage rules are bypassed ✓
- PO5: ACL — only procurement can edit `po_lines` ✓

## Phases — as executed
- **9a.1** Lookup + header collections created.
- **9a.2** PO list + detail page built.
- **9a.3** Generate-PO action wired (custom-action workflow + button on PR table block + PR detail popup).
- **9a.4** Total-maintenance workflow — **cancelled (D27)**. PO `total` is manually entered.
- **9a.5** Create-PO request-interception guard built (key `vgv8hcrtjvx`).
- **9a.6** ACL applied (procurement-only mutations on PO/po_lines/lookups).
- **9a.7** Verified — see Acceptance.

## Final state
Authoritative reference: see `project_current_state.md` for collection schemas, workflow IDs, node keys, and stale IDs. Decisions affecting this chunk: D27.
