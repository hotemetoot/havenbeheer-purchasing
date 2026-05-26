# Plan — Generate-PO round 3: restore inline guard, simplify line items, capture two NocoBase facts

## Context

Round 2 of MVP9a (relation repair, createdBy, embedded-guard removal, line_total_usd) is live and committed (commit `82101f5`). User testing surfaced three new issues that need a third round:

1. **Removing the embedded guard was wrong.** The Create-PO request-interception guard (`vgv8hcrtjvx`) is **0 executions** even after a duplicate PO was created by clicking the button with linkage rules disabled. NocoBase's request-interception trigger fires on direct HTTP API requests; the create node inside a custom-action workflow bypasses the HTTP middleware. The NocoBase docs (`triggers/request-interception.md`) explicitly list "Trigger workflow buttons" as **not supported** for the request-interception trigger. The only defence against duplicate Generate-PO clicks is an inline condition node in the Generate-PO workflow itself.

2. **`po_lines.line_total_usd` formula is broken.** Formula fields can only access fields on their own collection record — they cannot traverse relations. `{{purchase_order.fx_rate_to_usd}}` from `po_lines` returns nothing. The user chose the simplification path: **drop pricing from po_lines entirely**. Invoice amount is manually entered at the PO level; line items become quantity + receiving-tracking only.

3. **createdBy now works.** PO-2026-0003 has `createdById=11` (Pat). The user's manual edit and my CLI edit converged on `{{$context.user.id}}`. No further action needed.

Both #1 and #2 are general NocoBase facts the rest of the project (and future projects) will hit again — capture in auto-memory.

## Issues & fixes

### 1. Restore inline guard inside Generate-PO workflow

**Skill:** `nocobase-workflow-manage`. The active revision is `366595041853440` (executed 1+ time during validation) → revision first.

In the new revision, insert a condition node at the head (`upstreamId: null`), then chain query → create-PO → create-po_line off branch 1 of the condition.

**Condition node config** — use the **calculation-engine** format (operands / calculator) so the NocoBase UI can render it editable. Mirror the shape used by the separate guard `vgv8hcrtjvx` node `dba34lyg168`:

```json
{
  "rejectOnFalse": false,
  "engine": "basic",
  "calculation": {
    "group": {
      "type": "and",
      "calculations": [
        { "calculator": "equal",    "operands": ["{{$context.data.status}}", "approved"] },
        { "calculator": "equal",    "operands": ["{{$context.data.purchase_order}}", null] }
      ]
    }
  }
}
```

(Logical AND of: PR is approved AND no PO exists yet. Branch 1 = true → continue. False branch ends silently — same UX as round 1.)

### 2. Simplify po_lines — remove pricing

**Skill:** `nocobase-data-modeling`.

Delete from `po_lines`:
- `unit_price`
- `line_total`

(`line_total_usd` was already removed in commit `82101f5`'s context — verify it's gone, drop if still present.)

Remaining po_lines fields after simplification: `purchase_order`, `product`, `description`, `unit_of_measure`, `quantity_ordered`, `received_quantity`, `line_status`.

**Downstream impact:**
- Generate-PO workflow's "Create po_lines" node currently writes `unit_price: {{$context.data.quoted_total}}`. Drop that field from the create payload in the same revision used for fix #1.
- `purchase_orders.total` is pre-filled by the Generate-PO workflow from `pr.quoted_total` (still correct) and becomes manually editable post-invoice. The previously-planned 9a.4 "Total-maintenance workflow" is **cancelled** — no longer needed.

### 3. Auto-memory: two new feedback entries + MEMORY.md index update

**`feedback_request_interception_scope.md`** — request-interception workflows only fire for direct HTTP API operations (and `Create record` / `Update record` / `Delete record` buttons bound to the relevant action). They do **not** fire for:
- create / update / destroy nodes executed inside any other workflow (custom-action, schedule, collection trigger, etc.)
- Trigger-workflow buttons (those route through the `custom-action` trigger instead)
Implication: when a custom-action workflow creates a record, any pre-action guard you've put on that record's `create` is silent. The only protection against the workflow's own misuse is an inline condition node inside the same workflow. Plan defences accordingly — don't rely on global request-interception as a backstop for workflow-internal writes.

**`feedback_formula_field_scope.md`** — Formula fields (plugin `@nocobase/plugin-field-formula`) can only reference fields on the **same collection's record**. Expressions like `{{related.fieldName}}` (traversing an m2o, o2o, etc.) return nothing — silently, with no error. For cross-collection math:
- Denormalize the needed value as a real column and keep it in sync via a workflow, OR
- Compute server-side in a workflow create/update node and write to a regular number field.
Don't waste time trying to make a formula traverse a relation; the field always evaluates to empty.

Update `MEMORY.md` to add these two entries to the index.

### 4. Update `project_current_state.md`

- `po_lines` table: remove `unit_price`, `line_total`, `line_total_usd` from the field list. Add a one-line note that pricing was descoped (decision in this plan; round-3 entry in `decisions.md`).
- Generate-PO workflow: bump the documented active version id to the new revision created in fix #1. Add the embedded guard node to the node chain description.
- Append a stale-id entry for `366595041853440` (the post-round-2, pre-round-3 revision).
- Note that the planned 9a.4 Total-maintenance workflow is cancelled (PO `total` is manually entered post-invoice).

### 5. Add a D-entry to `decisions.md`

D-entry (next number — check the file for the latest D-NN before writing): "po_lines pricing descoped. line items track quantity + receiving only; PO `total` is manually entered from supplier invoice. Reason: formula fields can't traverse relations, denormalising fx_rate adds maintenance overhead, and pricing at line level isn't needed for current workflow scope. Affects: MVP9a (this revision), MVP9c (receiving) — receiving logic now only updates `received_quantity` and `line_status`, no $-impact calculations. MVP9d, MVP9e unaffected."

## Critical IDs

- Generate-PO workflow key: `2izsx8uv50r`. Current active version `366595041853440` (executed → revision required).
- Create-PO Guard key: `vgv8hcrtjvx`, id `366562380808192` — no changes this round.
- Generate-PO node keys to preserve across revision: `ay8dlnys4ef` (query), `ubg9mju1tjm` (create PO). The "Create po_lines" node's key has shifted (was `rkx04b82o7n`, currently `4p3q7oq3co5`) — value isn't referenced by any other node so the new key doesn't matter.
- Button: `28jh1q2camo` — no changes (still bound to `2izsx8uv50r`).

## Execution order

1. Drop `po_lines.unit_price` and `po_lines.line_total` (fix #2 data part).
2. Revision the Generate-PO workflow. In the new revision:
   - Insert condition node at the head (fix #1).
   - Move query node to branch 1 of the condition.
   - Update create-po_line node config to drop `unit_price` from the create payload (fix #2 workflow part).
   - Verify the create-PO node still carries `createdById: {{$context.user.id}}` from the previous revision.
   - Enable the new revision (sets it current, disables the old).
3. Write the two `feedback_*.md` memory files + update `MEMORY.md`.
4. Edit `project_current_state.md` (fix #4) and append the D-entry to `decisions.md` (fix #5).
5. Commit.

## Verification

After execution, run as `pat.procurement` in the browser:

1. **Inline guard works:** open an approved PR with no PO, disable the Generate-PO button's linkage rules via dev tools, click → workflow runs but creates no PO. Generate-PO workflow execution exists with the condition node ending in the false branch (no downstream jobs). No new PO row, no duplicate.
2. **Happy path still works:** open another approved PR with no PO (linkage rules re-enabled), click Generate-PO → PO created, default po_line created (no unit_price field on the line), `createdBy` = Pat, `purchase_order` resolves on the PR side.
3. **po_lines fields:** `fields list` on `po_lines` shows the trimmed set; UI for editing a po_line no longer offers unit_price or line_total.
4. **PO total stays editable:** open the new PO, edit `total` to a new value, save → persists. (Was previously expected to be workflow-overwritten; verify nothing recomputes it.)
5. **Separate guard still does its job:** as any user, `POST /purchase_orders` directly via API to a non-approved PR → 400 with the guard's error message and `Create-PO Guard` execution count increments.
6. **Memory written:** both new `feedback_*.md` files exist, MEMORY.md indexes them.

## Resolved choices

- Inline guard: **add back as calculation-engine condition** (UI-editable).
- po_lines pricing: **remove entirely** — drop unit_price, line_total. PO total manually entered.
- createdBy: **leave as-is**, current value works (no special preservation needed).
