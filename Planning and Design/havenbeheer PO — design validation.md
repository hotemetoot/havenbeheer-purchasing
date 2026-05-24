# Havenbeheer Purchasing — PO Design Validation

**Purpose:** This document captures every assumption and decision made about the Purchase Order (PO) data model and execution workflow. Use it to validate with the team before building begins.

**How to use:** Walk through each section with the team. For each item, ask: *is this how we actually do it, or want to do it?* Push back wherever reality differs from what's written here.

**Status:** Design phase. Nothing has been built. Anything here can still change.

---

## 1. Scope

### What a PO represents
- Vendor commitment
- Receiving reality
- Operational truth

### Relationship to Purchase Requests
- A PO can only be created against an **approved** PR
- **One PR → one PO** (enforced). If a need changes after approval, a new PR must be submitted.
- A PR expires for new POs 30 days after `approved_at` (hardcoded in workflow)
- Procurement can also manually close a PR for new POs at any time via `closed_for_new_pos` flag
- The supplier on the PO is pre-filled from the PR (locked at PR approval) and is not editable

### Explicitly NOT in scope (v1)
- Goods returns and defective item handling (handled via comments and attachments on the PO)
- Formal receiving events log (receiving tracked as a single quantity field; Record History plugin provides audit trail if needed)
- Per-line delivery dates
- Inventory management (`products` collection is a v1 stub only)
- Financial accounting (payment tracking is operational visibility only, not bookkeeping)

---

## 2. Process overview

### Normal happy path

```
PR approved (supplier already confirmed at PR level)
  → Procurement creates draft PO (supplier pre-filled from PR)
  → Validates internally
  → Sends to supplier (via system or PDF export + email)
  → Supplier confirms (optional step)
  → Finance pays (before or after delivery — both are valid)
  → Supplier delivers (single or multiple deliveries)
  → Procurement logs received quantities per line
  → All lines received → notification fires to procurement
  → Procurement clicks Complete → PO completed and locked
```

### Variants

| Scenario | Path |
|---|---|
| Supplier skips confirmation | `sent` → `partially_received` or `received` directly |
| Payment before delivery | Finance updates `payment_status` at any point |
| Multiple deliveries per line | `received_quantity` updated incrementally |
| Imperfect outcome | Procurement closes PO with `close_reason` |

---

## 3. Status lifecycle

| Status | Meaning |
|---|---|
| `draft` | Created internally, not yet sent to supplier |
| `sent` | Sent to supplier |
| `confirmed` | Supplier confirmed fulfillment — voluntary, not required |
| `partially_received` | At least one line has received_quantity > 0; not all complete |
| `received` | All lines fully received — derived from lines, reversible |
| `completed` | Procurement finalized — all good, PO and lines locked |
| `closed` | Closed with reason — imperfect outcome, PO and lines locked |
| `cancelled` | Pulled before sending |

### Transitions

| From | To | Trigger |
|---|---|---|
| `draft` | `sent` | Procurement action |
| `sent` | `confirmed` | Procurement logs supplier confirmation |
| `sent` | `partially_received` | First line receiving logged |
| `sent` | `received` | All lines received in a single update |
| `confirmed` | `partially_received` | First line receiving logged |
| `confirmed` | `received` | All lines received in a single update |
| `partially_received` | `received` | All lines reach `received` (workflow-derived) |
| `received` | `partially_received` | A line's `received_quantity` corrected downward |
| `received` | `completed` | Procurement clicks "Complete" — manual action |
| `sent`, `confirmed`, `partially_received` | `closed` | Procurement clicks "Close" + fills `close_reason` |
| `draft` | `cancelled` | Procurement pulls it back |

### Terminal states
`completed`, `closed`, `cancelled` — PO and all lines are locked after reaching any of these.

---

## 4. Roles and visibility

| Role | PO permissions |
|---|---|
| Procurement | Create, edit (while not terminal), manage status transitions |
| Finance | Update `payment_status` and `payment_date` only |
| Director | View all POs |
| Submitter | View only — POs linked to their own PRs |
| Submitter's department | View only — POs linked to their department's PRs |

---

## 5. Budget overrun logic

Evaluated at `draft → sent` transition. Compares the PO total in USD against the PR's `quoted_total_usd` (which was locked at PR approval).

### Three zones

| Zone | Condition | Action |
|---|---|---|
| 1 | PO `total_usd` ≤ PR `quoted_total_usd` | Proceed normally |
| 2 | PR amount < PO total ≤ PR amount × 110% | Warn procurement + require `budget_override_comment` |
| 3 | PO total > PR amount × 110% | Block. A new PR is required. |

- **Tolerance percentage:** 110% — hardcoded in workflow, not user-editable
- Since one PR → one PO, there is no cumulative total to compute. The check is simply PO `total_usd` vs `PR.quoted_total_usd`.
- **Zone 2/3 notifications:** Director + head of Finance department

### PR expiry for new POs

- 30 days after `approved_at`, the PR's `closed_for_new_pos` flag is automatically set to `true`
- Procurement can also set this flag manually at any time
- If a PR expires before a PO is created, a new PR must be submitted and approved — no extension mechanism

---

## 6. Payment

Payment is tracked for **operational visibility only** — not for accounting.

- Finance has NocoBase access and updates payment fields directly
- Single payment transaction per PO assumed — no child collection
- Payment is orthogonal to PO status — Finance can update it at any lifecycle stage

**`payment_status` values:** `unpaid` / `prepayment_made` / `fully_paid`

---

## 7. Document generation

PO documents are generated using NocoBase's **Template Printing plugin** (Word `.docx` template → PDF). The PO document pulls from:
- PO header fields (po_number, date, expected_delivery_date, supplier_note)
- Supplier record (name, address, payment_terms_days)
- Delivery address
- PO lines (description, UoM, quantity, unit_price, line_total)

The `supplier_note` field appears on the printed document. `internal_notes` does not.

**Note:** LibreOffice must be installed on the server for PDF output.

---

## 8. Hard business rules (guards)

| # | Guard | Rule |
|---|---|---|
| 1 | **PR must be approved** | Cannot create PO against a PR with status ≠ `approved` |
| 2 | **PR must not be expired** | Cannot create PO if `PR.closed_for_new_pos = true` |
| 3 | **One PO per PR** | Cannot create a PO if a non-cancelled PO already exists against the same PR |
| 4 | **Budget zone check** | At `draft → sent`: evaluate PO `total_usd` vs `PR.quoted_total_usd` (see Section 5) |
| 5 | **Override comment required** | Zone 2: cannot send without `budget_override_comment` |
| 6 | **Close requires reason** | `close_reason` and `close_comment` required when transitioning to `closed` |
| 7 | **Immutability** | PO and lines locked when status ∈ (`completed`, `closed`, `cancelled`) |
| 8 | **Cancel from draft only** | Cannot cancel a PO that has been sent |
| 9 | **Complete from received only** | Cannot complete a PO unless status = `received` |

---

## 9. Data model — collections

### New collections

#### `delivery_addresses`

| Field | Type | Notes |
|---|---|---|
| `name` | text | e.g. "Main Warehouse", "Harbour Gate 3" |
| `address` | textarea | |
| `is_default` | boolean | Pre-selected on new POs |
| `status` | single select | active / inactive |

#### `units_of_measure`

| Field | Type | Notes |
|---|---|---|
| `name` | text | e.g. "Kilogram" |
| `abbreviation` | text | e.g. "kg" |
| `status` | single select | active / inactive |

#### `products` (v1 stub — full inventory deferred to v2)

| Field | Type | Notes |
|---|---|---|
| `name` | text | |
| `description` | textarea | |
| `default_uom` | belongsTo (units_of_measure) | |
| `status` | single select | active / inactive |

#### `purchase_orders`

| Field | Type | Notes |
|---|---|---|
| `po_number` | sequence | Format: PO-YYYY-0001. Auto-generated, not editable. Resets annually. |
| `purchase_request` | belongsTo (purchase_requests) | Required. PR must be approved, not expired, and have no existing non-cancelled PO. |
| `supplier` | belongsTo (suppliers) | Pre-filled from `PR.supplier` at PO creation. **Not editable.** |
| `delivery_address` | belongsTo (delivery_addresses) | Pre-filled from `is_default` |
| `status` | single select | See Section 3 |
| `currency` | single select | 3 supported currencies |
| `fx_rate_to_usd` | decimal | Snapshotted at PO creation |
| `total` | decimal | Workflow-maintained — sum of `po_lines.line_total`. Formula fields cannot aggregate child records in NocoBase. |
| `total_usd` | formula | `total × fx_rate_to_usd` |
| `payment_status` | single select | unpaid / prepayment_made / fully_paid |
| `payment_date` | date | Set by Finance |
| `expected_delivery_date` | date | |
| `quotations` | attachment (multi) | Supplier quotation documents (copies from PR for reference) |
| `attachments` | attachment (multi) | Confirmations, delivery notes, other supporting docs |
| `supplier_note` | textarea | Printed on PO document |
| `internal_notes` | textarea | Not printed — procurement use only |
| `budget_override_comment` | textarea | Required in zone 2 — explains the overrun |
| `close_reason` | single select | Required when status = `closed` |
| `close_comment` | textarea | Required when status = `closed` |
| `created_by` | belongsTo (users) | Auto-set |
| `sent_at` | datetime | Audit |
| `confirmed_at` | datetime | Audit — nullable (`confirmed` is voluntary) |
| `completed_at` | datetime | Audit |
| `closed_at` | datetime | Audit |
| `cancelled_at` | datetime | Audit |

**`close_reason` values:** `supplier_unable_to_fulfill` / `partial_fulfillment_accepted` / `duplicate` / `replaced_by_new_po` / `other`

#### `po_lines`

| Field | Type | Notes |
|---|---|---|
| `purchase_order` | belongsTo (purchase_orders) | Required |
| `product` | belongsTo (products) | Optional — pre-fills `description` and `unit_of_measure` if set |
| `description` | text | Required. Editable regardless of product link. |
| `unit_of_measure` | belongsTo (units_of_measure) | Pre-filled from product if linked |
| `quantity_ordered` | decimal | Supports fractional units (kg, m³, etc.) |
| `unit_price` | decimal | In PO currency |
| `line_total` | formula | `quantity_ordered × unit_price` |
| `line_total_usd` | formula | `line_total × purchase_order.fx_rate_to_usd` |
| `received_quantity` | decimal | Updated on delivery. Enable Record History on this field. |
| `line_status` | single select | pending / partially_received / received — workflow-maintained |

### Modified collections

#### `suppliers`
Add: `address` (textarea) — used on printed PO document

#### `purchase_requests`
- Add: `closed_for_new_pos` (boolean, default `false`). Exempt from PR immutability guard — operational flag. Set by procurement manually or by the 30-day expiry workflow.

---

## 10. Workflows summary

| # | Trigger | Action |
|---|---|---|
| 1 | PO `draft → sent` | Evaluate budget zone. Zone 2: require `budget_override_comment`, notify Director and Finance department head. Zone 3: block transition, notify Director and Finance department head. |
| 2 | `po_lines.received_quantity` updated | Recalculate `line_status`. Recalculate PO `total`. Derive PO status (`partially_received` / `received`). |
| 3 | All PO lines reach `line_status = received` | Notify procurement: "PO [po_number] is ready to complete." |
| 4 | PO status → `completed`, `closed`, or `cancelled` | Lock PO and all child lines (Before Action guard). Set audit timestamp. |
| 5 | PR `approved_at` + 30 days | Set `PR.closed_for_new_pos = true`. |

---

## 11. Open questions for the team

1. **Supplier payment terms on document** — is `suppliers.payment_terms_days` (a number) sufficient for the PO document, or does the client need more structured payment terms (e.g. "Net 30", "COD")?
2. **Products catalogue v2 scope** — what fields and workflows will the future inventory feature require? (Deferred to v2)

---

## 12. Decisions log

1. One PR → one PO enforced by guard #3 on PO collection
2. PO line items are created fresh by procurement; not derived from PR quotation lines
3. PO has its own currency and FX rate snapshotted at creation; amounts also stored in USD
4. `purchase_orders.supplier` is pre-filled from `PR.supplier` at PO creation and is not editable — supplier is locked at PR approval, not at PO creation
5. `received` status is derived from line items and reversible; not a terminal state
6. `completed` is the terminal happy path state — manual procurement action after all lines received
7. `completed` and `closed` are separate terminal states — not collapsed
8. `close_reason` single select with mandatory `close_comment` on all closed POs
9. Payment tracked as `payment_status` + `payment_date` on PO header only — no child collection
10. Payment is orthogonal to PO status — Finance updates independently at any stage
11. Receiving tracked as `received_quantity` on line only — no receiving_events collection; Record History plugin provides audit trail
12. PO total is workflow-maintained (not a native formula) because NocoBase formula fields cannot aggregate child records
13. Budget overrun: soft cap with three zones; Zone 3 blocks and requires new PR. Since one PR → one PO, check is PO total vs PR `quoted_total_usd` directly — no cumulative calculation needed.
14. Budget overrun tolerance hardcoded in workflow at 110% — not user-editable
15. PR expires for new POs 30 days after `approved_at` — hardcoded in workflow
16. `closed_for_new_pos` flag on PR is exempt from immutability guard — operational flag
17. Procurement can also manually set `closed_for_new_pos = true` at any time
18. Director notification on Zone 2/3 overrun targets the single Director role
19. `units_of_measure` is a client-managed lookup collection — not a single select
20. `products` collection added as v1 stub; full inventory management deferred to v2
21. `delivery_addresses` is a client-managed lookup collection with a default value
22. PO number format: PO-YYYY-0001 via NocoBase sequence field, resets annually
23. PO document generated via Template Printing plugin (Word → PDF); LibreOffice required on server
24. Submitter and submitter's department have view-only access to POs linked to their PRs
25. Comments on POs via built-in Comment Collection plugin (same pattern as PRs)
26. No attachments on PO lines — PO-level attachment fields are sufficient
27. `confirmed` status is voluntary — POs can transition directly from `sent` to receiving states
28. Two attachment fields on PO: `quotations` (reference copies) + `attachments` (everything else)
29. No PR expiry extension mechanism — expired PRs require a new PR submission and approval
30. If a PO is cancelled, a new PO can be created against the same PR (provided it hasn't expired) — the one-PO-per-PR guard checks for non-cancelled POs only

---

*End of PO validation document.*
