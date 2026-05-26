# Plan — MVP9a: PO collection + Generate-PO button

## Context

MVPs 1–8 delivered the full PR side of the workflow (submit → dept → procurement → optional director → approved). MVP9 turns approved PRs into Purchase Orders. Per D9, each PR yields exactly one PO; per D10 generation is a manual button click by procurement.

MVP9a is the **data + creation** slice: build all PO-side collections, add a "Generate PO" action to the PR surface that creates a draft PO + one default line pre-filled from the PR, and stand up the small workflow that keeps `purchase_orders.total` in sync with its lines (NocoBase formula fields can't aggregate child rows — design decision 12). Sending, budget zones, receiving, completion, and printing are intentionally deferred to 9b–9e.

Chunk source: [chunks/009a-po-collection-and-generate-button.md](../chunks/009a-po-collection-and-generate-button.md).

## Phases

### 9a.1 — Lookup + header collections (no UI yet)

Skill: `nocobase-data-modeling`.

Create five collections:

**`delivery_addresses`** — `name` (input, title), `address` (textarea), `is_default` (boolean), `status` (select: active/inactive).

**`units_of_measure`** — `name` (input, title), `abbreviation` (input), `status` (select).

**`products`** (v1 stub) — `name` (input, title), `description` (textarea), `default_uom` (m2o → `units_of_measure`), `status` (select).

**`purchase_orders`** — per PO design §9:
- `po_number` (sequence, `PO-YYYY-NNNN`, auto, not editable, title)
- `purchase_request` (m2o → `purchase_requests`, required)
- `supplier` (m2o → `suppliers`, pre-filled, not editable post-create)
- `delivery_address` (m2o → `delivery_addresses`)
- `status` (select: draft / sent / confirmed / partially_received / received / completed / closed / cancelled; default `draft`)
- `currency` (select USD/SRD/EUR), `fx_rate_to_usd` (number) — snapshotted at create
- `total` (number, workflow-maintained; no formula)
- `total_usd` (formula.js: `{{total}} * {{fx_rate_to_usd}}`)
- `payment_status` (select: unpaid / prepayment_made / fully_paid; default unpaid), `payment_date` (date)
- `expected_delivery_date` (date)
- `invoice` (attachment single — supplier invoice once received)
- `attachments` (attachment multi — misc supporting docs)
- (no `quotations` field — PO detail page surfaces `purchase_request.quotation_attachment` via the relation instead of duplicating)
- `supplier_note` (textarea, printed on PDF later), `internal_notes` (textarea)
- `budget_override_comment` (textarea), `close_reason` (select; values deferred to 9d), `close_comment` (textarea)
- Audit timestamps (datetime, system-set later): `sent_at`, `confirmed_at`, `completed_at`, `closed_at`, `cancelled_at`. Build the fields now; population is 9b–9d.

**`po_lines`** — per PO design §9:
- `purchase_order` (m2o → `purchase_orders`, required)
- `product` (m2o → `products`, optional)
- `description` (textarea, required)
- `unit_of_measure` (m2o → `units_of_measure`)
- `quantity_ordered` (number), `unit_price` (number)
- `line_total` (formula.js: `{{quantity_ordered}} * {{unit_price}}`)
- `line_total_usd` (formula.js: `{{line_total}} * {{purchase_order.fx_rate_to_usd}}`)
- `received_quantity` (number, fractional allowed; Record History enabled)
- `line_status` (select: pending / partially_received / received; default `pending`, workflow-maintained later)

Add reverse o2m `purchase_orders.lines` on `purchase_orders` against `po_lines.purchase_order`.

Also add `purchase_requests.purchase_order` (o2o or o2m → `purchase_orders`) — used by the Generate-PO button visibility check.

### 9a.2 — PO list + detail pages

Skill: `nocobase-ui-builder`. Build:
- **Purchase Orders** list page with a table block showing: `po_number`, `purchase_request`, `supplier`, `status`, `total`, `currency`, `expected_delivery_date`, `payment_status`.
- PO detail popup (DetailsBlockModel) showing header fields, a child `po_lines` table block bound via `purchase_orders.lines` (lines editable inline — add/edit/delete row actions), and a read-only sub-block exposing `purchase_request.quotation_attachment` so procurement can see the PR's quotations without duplicating them on the PO.

Capture the new page UID + table block UID into `project_current_state.md` at session end.

### 9a.3 — Generate-PO action

Skill: `nocobase-ui-builder` + `nocobase-workflow-manage`.

a. **Workflow** (`custom-action`, sync, collection `purchase_requests`):
   - Trigger appends: `supplier`, `purchase_order` (to check existence).
   - Embedded guard (condition node): `status == "approved" AND purchase_order == null`. If false → end with response message.
   - Query node → fetch the default `delivery_addresses` row (filter `is_default == true AND status == "active"`, limit 1).
   - Create node → `purchase_orders` record with:
     - `purchase_request` ← `{{$context.data.id}}`
     - `supplier` ← `{{$context.data.supplier.id}}`
     - `delivery_address` ← `{{$jobsMapByNodeKey.<queryNode>.id}}` (the default row, if any)
     - `currency` ← `{{$context.data.quoted_currency}}`
     - `fx_rate_to_usd` ← `{{$context.data.fx_rate_to_usd}}`
     - `total` ← `{{$context.data.quoted_total}}`
     - `status` ← `draft`
   - Create node → one `po_lines` row:
     - `purchase_order` ← the just-created PO id
     - `description` ← `{{$context.data.description}}` (fallback `title` if empty)
     - `quantity_ordered` ← `1`
     - `unit_price` ← `{{$context.data.quoted_total}}`

b. **Button** on PR table block (`l1e2iwdwau9`) and PR detail popup (`2b367dbd157`). Use a `triggerWorkflow` action via `nb api flow-surfaces add-action`. Linkage rules on visibility:
   - Show when `status == "approved" AND purchase_order == null`.
   - Use `$ne` combined with `$and` if needed (per CLAUDE.md — `$notIn` not supported).

c. **Bind workflowKey:** Per CLAUDE.md gotcha — set via `nb api resource update --resource flowModels --pk <buttonUID> --body '{"workflowKey":"<key>"}'`. Do NOT try `flow-surfaces configure`.

### 9a.4 — Total-maintenance workflow

Skill: `nocobase-workflow-manage`. Workflow on `po_lines` (trigger: create / update / delete), sync:
- Query node aggregating `po_lines.line_total` where `purchase_order.id == $context.data.purchase_order.id` (use `nb api` aggregate or a JSON-query node summing the result set).
- Update node on `purchase_orders` (filterByTk = `$context.data.purchase_order.id`) → `total = <sum>`.

Verify `purchase_orders.total_usd` (formula) recomputes off the new total automatically.

### 9a.5 — Create-PO guard (request-interception)

Skill: `nocobase-workflow-manage`. Same shape as Guard A / Cancel Guard:
- Type `request-interception`, sync, global, on `purchase_orders` action=`create`.
- Query the referenced `purchase_request` (by `$context.params.values.purchase_request`).
- Condition: `pr.status != "approved" OR pr.purchase_order != null`.
- If true: response-message + end(endStatus:-1).

This catches API callers that bypass the UI button.

### 9a.6 — ACL

Skill: `nocobase-acl-manage`. Only procurement role gets create/update/delete on `purchase_orders`, `po_lines`, `delivery_addresses`, `units_of_measure`, `products`. Member role: read-only on PO (for visibility from PR detail). Per `member is base role`, do not double-grant view.

### 9a.7 — Verify

Pause and ask user to manually run acceptance scenarios PO1–PO5 from the chunk:
- PO1: Generate from approved PR → succeeds, one default line, all pre-fill correct.
- PO2: Try generating from non-approved PR → button hidden; API call blocked by 9a.5 guard.
- PO3: PR with existing PO → button hidden.
- PO4: Add/edit/delete `po_lines` → `purchase_orders.total` updates correctly (9a.4 workflow).
- PO5: ACL — non-procurement user cannot edit `po_lines`.

## Critical files / IDs to reuse

- PR table block: `l1e2iwdwau9` (attach Generate-PO button).
- PR detail popup: `2b367dbd157` (attach Generate-PO button).
- Active PR Approval workflow: `cv237r8h7k9` v `366549533655040` — read-only reference, not modified.
- Cancel workflow `59ezifdoqvj` + Cancel Guard `8yngslauuj4` — pattern template for the Generate-PO button workflow + create guard.
- Guard A `496ookqmg01` — pattern template for the request-interception guard shape.

## Live-change preview before execution

Before each phase that mutates live state, list intended changes + skill + expected UI result (per CLAUDE.md). No irreversible actions in 9a (all collections/workflows additive).

## Session-end housekeeping

- Update [project_current_state.md](../project_current_state.md): new collections, PO page UID, button UIDs, workflow keys (Generate-PO custom-action, Total-maintenance, Create-PO Guard).
- Commit after each verified phase per CLAUDE.md ("series of this-worked milestones").
- No D-entries expected unless plan changes during build.

## Resolved choices (pre-build)

- **`po_number`** — sequence `PO-YYYY-NNNN`, resets yearly.
- **`purchase_requests.purchase_order`** — o2o relation (enforces D9 at schema).
- **`delivery_addresses`** — seed one default record during 9a.1 (procurement can rename later). Generate-PO prefills `delivery_address` with the `is_default=true` row.
