# Plan — Generate-PO workflow & PO relation fixes

## Context

After the first pass of MVP9a (PO collection + Generate-PO button), several issues were uncovered during validation:

- The relation between `purchase_requests` and `purchase_orders` is malformed: the inverse `purchase_requests.purchase_order` is declared as `obo` / `belongsTo` (FK-holder), and a stray `purchase_requests.purchaseRequestId` bigInt column exists. As a result, the inverse field is empty after PO generation, and any downstream code that checks "does this PR already have a PO?" misbehaves.
- The Generate-PO workflow doesn't set `createdById` on the new `purchase_orders` row, so the audit trail says nobody created it.
- The Generate-PO workflow has an embedded condition-node guard, but a separate `request-interception` guard (`Guard: Create PO (PR must be approved)`, key `vgv8hcrtjvx`) already exists on `purchase_orders.create`. The embedded guard is JSON-filter format which doesn't render usefully in the NocoBase condition-node UI.
- The separate guard's condition currently checks the broken `purchaseRequestId` column, so it won't be correct once the relation is fixed.
- `po_lines.line_total_usd` (formula) from the chunk plan was never created.
- The user discovered authoring tips during this session that should be captured for future work (role-based linkage rules, related-record title fields, currency-rate convention).

This plan addresses all of the above and updates auto-memory so we don't repeat the same mistakes.

## Issues & fixes

### 1. Repair the PR ↔ PO relation

**Goal:** keep a single 1:1 relation, FK on `purchase_orders`, virtual hasOne inverse on `purchase_requests`.

**Current state (broken):**
- `purchase_orders.purchase_request` — `m2o` / `belongsTo`, FK `purchaseRequestId` on `purchase_orders` (correct, keep as-is)
- `purchase_requests.purchase_order` — `obo` / `belongsTo`, FK `purchaseRequestId` (WRONG — declares the FK on the PR side)
- `purchase_requests.purchaseRequestId` — `integer` / `bigInt` (stray column, created as side effect)

**Fix (skill: `nocobase-data-modeling`):**
1. Delete `purchase_requests.purchase_order` (broken inverse).
2. Delete `purchase_requests.purchaseRequestId` (stray FK column) — confirmed OK to drop. Any existing data is from the broken state.
3. Re-create the inverse so NocoBase generates `purchase_requests.purchase_order` as a proper hasOne (`oho`) virtual field — no FK column on `purchase_requests`. Path: use the m2o "create inverse field" option on `purchase_orders.purchase_request` if exposed via the CLI; otherwise create the field manually as hasOne with `target=purchase_orders`, `foreignKey=purchaseRequestId` (on target), `sourceKey=id`.
4. Verify via `fields list`: `purchase_orders.purchase_request` m2o intact with FK `purchaseRequestId`; `purchase_requests.purchase_order` is hasOne; no `purchaseRequestId` column on `purchase_requests`.

### 2. Generate-PO workflow: set `createdById`

**Skill:** `nocobase-workflow-manage`.

The active workflow has been executed at least once (during validation), so this requires creating a new revision first.

1. Revision the current Generate-PO workflow (`vgv8hcrtjvx`'s create cousin — wait, that's the guard. The Generate-PO is key `2izsx8uv50r`, id `366569458696192`).
2. Update the **Create purchase_orders** node (`key=ubg9mju1tjm`) to add `createdById: "{{$context.user.id}}"` to `params.values`.
3. Confirm `$context.user.id` is the correct path — if not, use whatever path the workflow trigger surfaces for the triggering user (check via context inspection on the workflow).
4. Re-enable the new revision.

### 3. Remove the embedded guard in Generate-PO

The separate `request-interception` guard `vgv8hcrtjvx` is the canonical defence; the embedded condition node is double-protection in a format the NocoBase UI can't render.

**Decision:** remove the embedded guard. Revised workflow shape: Query default delivery address → Create PO → Create po_line (3 nodes, all on the main chain, no condition branching). Easiest implementation: in the new revision, delete the condition node and re-parent the query node as the head (`upstreamId: null`), then chain the rest sequentially.

### 4. Update separate guard `vgv8hcrtjvx` to use the new inverse field

After fix #1, the condition node `dba34lyg168` in workflow `vgv8hcrtjvx` will be checking a field (`purchaseRequestId`) that no longer exists on the queried PR. Update it.

Replace the second operand of the calculation:
- `{{$jobsMapByNodeKey.ww4mxz67ge8.purchaseRequestId}} != null`
- with `{{$jobsMapByNodeKey.ww4mxz67ge8.purchase_order}} != null`

This requires either appending `purchase_order` in the query node `ww4mxz67ge8` (so the hasOne is loaded), or filtering directly in a separate query against `purchase_orders` where `purchaseRequestId = pr.id`. Cleaner: append the inverse.

This is also a frozen-version edit, so revision first.

### 5. Add missing `po_lines.line_total_usd` formula

Per the chunk plan, `po_lines.line_total_usd` should exist as `formula.js`: `{{line_total}} / {{purchase_order.fx_rate_to_usd}}` (division, matching the corrected convention).

Skill: `nocobase-data-modeling`. Add the field via `fields apply`.

### 6. Save NocoBase patterns to auto-memory

These are generic NocoBase patterns, useful in any NocoBase project. Save as `feedback_*.md` files in auto-memory.

- **`feedback_linkage_rules_user_roles.md`** — When restricting an action button or block by role, use the path `{{ ctx.user.roles.title }}` with operator `$includes` / `$notIncludes` (users can have multiple roles, so a singular `role $ne` check is wrong). The value must be the role's **title** (capitalized, e.g. `"Procurement"`), not the internal `name` (lowercase `procurement`).
- **`feedback_related_record_title_field.md`** — When a collection is referenced by an m2o / o2m on another collection, set a `title` field on the referenced collection (typically via Collection Settings → Title field). Without one, NocoBase renders the record ID instead of a human-readable label in detail blocks, popups, and select dropdowns.
- **`feedback_currency_rate_convention.md`** — Confirmed: in this project, `fx_rate_to_usd` stores **units of local currency per 1 USD** (e.g. 35 SRD per 1 USD). The USD value is therefore `local_total / fx_rate_to_usd`. The field name is misleading — the general lesson is to sanity-check rate direction by writing the unit math before writing the formula.

### 7. Update `project_current_state.md`

After all fixes land:
- Add the Generate-PO workflow and the separate Create-PO Guard (with their post-revision IDs).
- Note that `purchase_requests.purchaseRequestId` no longer exists and `purchase_requests.purchase_order` is now hasOne.
- Update the documented `quoted_total_usd` and `total_usd` formulas to use division.
- Add the new `line_total_usd` field.
- Capture the PO button UID (`28jh1q2camo`) and the linkage-rule patterns now in use.

## Critical files / IDs

- **Generate-PO workflow:** key `2izsx8uv50r`, id `366569458696192` (has executed → revision required).
- **Separate Create-PO Guard:** key `vgv8hcrtjvx`, id `366562380808192`. Condition node `dba34lyg168`. Query node `ww4mxz67ge8`.
- **Generate-PO button:** `28jh1q2camo` on PR table block `l1e2iwdwau9` and detail popup `2b367dbd157` — no changes needed (user already fixed linkage rules).
- **Collections touched:** `purchase_requests`, `purchase_orders`, `po_lines`.

## Verification

After all changes:

1. **Relation sanity:** `fields list` on `purchase_requests` shows `purchase_order` (hasOne, virtual, no FK column), no `purchaseRequestId` column. On `purchase_orders`, `purchase_request` (m2o, FK `purchaseRequestId`) is unchanged.
2. **Generate-PO end-to-end:** As `pat.procurement`, click Generate PO on an approved PR with no PO → new PO created, `createdById` = Pat's user id, `purchase_request` set, default po_line created, `purchase_requests.purchase_order` now resolves to the new PO when appended.
3. **Inverse appears:** Open the PR detail popup → the `purchase_order` field shows the newly created PO (not empty).
4. **Re-click is blocked:** Click Generate PO again on the same PR → button is hidden (linkage rule's `$notEmpty` on `purchase_order` now fires correctly).
5. **API bypass blocked:** Direct `POST /purchase_orders` referencing a non-approved PR → separate guard returns the error message and `endStatus: -1`.
6. **Line USD:** `po_lines.line_total_usd` exists and computes correctly for a line in a non-USD PO.
7. **Memory written:** Three `feedback_*.md` files in auto-memory plus a `MEMORY.md` index entry for each.

## Resolved choices

- Embedded guard in Generate-PO → **remove**.
- Stray `purchase_requests.purchaseRequestId` column → **drop**.
- Missing `po_lines.line_total_usd` formula → **add now**.
- `fx_rate_to_usd` convention → **local currency per 1 USD** (division is correct in the USD formulas).

## Execution order

To minimise rework, apply in this order:

1. Repair the PR↔PO relation (fix #1) — this is the foundation; everything else references the corrected fields.
2. Update separate guard `vgv8hcrtjvx` (fix #4) — once `purchase_order` is a clean hasOne, switch its condition to use it.
3. Revision the Generate-PO workflow (fixes #2 + #3 in a single revision): drop the condition node, add `createdById` on the create-PO node.
4. Add `po_lines.line_total_usd` (fix #5).
5. Write the three auto-memory entries (fix #6).
6. Update `project_current_state.md` and commit.
