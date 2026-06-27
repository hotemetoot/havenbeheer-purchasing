# Plan — MVP 016: budget-safe PO line-item import

Chunk: [chunks/016-po-line-import-budget-safe.md](../chunks/016-po-line-import-budget-safe.md) (committed `40ccbcb`). Decision to record: **D52**.

## Context
Procurement wants to bulk-**import** PO line items for large orders. Import (base or Pro) bypasses **all**
`po_lines` request-interception guards, so the D47 per-line budget block (`Σ(line_total) ≤ PR.quoted_total`)
and the D45/D46 terminal guards never fire on imported rows — an import could silently push a PO over the
approved PR amount and then be printed. D47 deliberately enforced per-line *instead of* at the Issue gate,
but that assumed every line-creation path hits request-interception; import is a new path that escapes it.

Fix = two complementary controls, **supplementing** D47 (not reversing it):
- **A.** Add the budget check to the **Issue PO gate** — the chokepoint every PO crosses to become
  printable. Over-budget → reject, PO stays `draft`, can't print.
- **B.** Add the Import action to the PO popup Line Items tab, **hidden unless the PO is `draft`** (+
  Procurement only), so lines can't be imported after issue. Per-row "trigger workflow" enabled so
  Recompute A refreshes `lines_total` and the user can observe import behavior (collection-event only — it
  does **not** enforce the cap; A does).

## Live state verified this session
- `issue_po` active = **`370047775735808`** ("Issue PO copy", current+enabled). Doc's `370019772465152`
  is **stale**.
- Node chain (keys stable across revision): `issue_guard` → br1 `issue_count` → `issue_lines_guard`
  → `uxpi9ufle06` (aggregate count priced) → `x01errm96yk` (all-priced?) → **br1 `issue_update`**
  (the insertion point); reject branches `issue_fail_msg/end`, `issue_lines_msg/end`, `lmojp8hz5kd`/`l3zu2zraqf2`.
- `@nocobase/plugin-action-import` enabled; `@nocobase/plugin-action-import-pro` now enabled (user).

## Part A — `issue_po` budget check (skill: `nocobase-workflow-manage`)

`issue_po` has executed → **must same-key revision** (force key `issue_po` via raw `--body`), build
disabled, then enable. Predecessor `370047775735808` is the rollback target.

Intended node changes on the new version:
1. **Trigger appends:** add `purchase_request` (currently `[lines]`).
2. **Insert before `issue_update`, on `x01errm96yk` br=1:**
   - `issue_sum_lines` — aggregate **sum** `line_total` where `purchase_order.id == {{$context.data.id}}`
     (mirror of D47 `sum_lines`).
   - `issue_over` — condition, **math.js**: `{{$jobsMapByNodeKey.issue_sum_lines}} > {{$context.data.purchase_request.quoted_total}}`.
     - br=1 (over) → `issue_over_msg` (response-message, dynamic: echo `Σ line_total` + `quoted_currency`
       + the PR ceiling) → `issue_over_end` (end, `endStatus:-1`).
     - br=0 (within) → `issue_update`.
   - **Rewire:** `x01errm96yk` br=1 downstream `issue_update` → `issue_sum_lines`.
3. Set `downstreamId` explicitly on the new sequential nodes (generic `flow_nodes:create` doesn't
   auto-maintain it — D46 build note); branch reject head uses `upstreamId`+`branchIndex`.

Expected UI: clicking **Issue PO** on a draft PO whose lines exceed the PR amount → rejected with the
over-budget message; PO stays `draft`, Print stays hidden. Within-budget / all-priced / ≥1-line → issues
as before.

Null-safety: lines are guaranteed ≥1 and all-priced upstream, so the sum is numeric; if `quoted_total`
could be null on an edge PO, interpose an `N()` coalesce calc node before the compare (D47 precedent).

## Part B — Import action + hide rule (skill: `nocobase-ui-builder`)

1. Add an **Import** action to the PO popup's **Line Items** sub-table (association `purchase_orders.lines`).
   - Field map: `description`, `quantity_ordered`, `unit_price` (+ other procurement-editable line fields).
     **Not** `line_total` (persisted formula, computes from qty×price).
   - Enable per-row **"trigger workflow"** so Recompute A `5ukanitoy74` fires per imported row.
2. **Linkage rule** on the Import button (action: hide): visible only when parent PO `status == draft`
   **AND** role Procurement — read parent status via `ctx.popup.record.status` (same popup-record context
   the add-line Submit uses for `ctx.popup.record.id`, D45); Procurement gate as on other PO buttons
   (`ctx.role $notIncludes "Procurement"`).

Expected UI: on a draft PO the Import button shows in Line Items for Procurement; on any non-draft PO (or
non-Procurement role) it's hidden.

## Build-time verifications (can't confirm read-only — do during execution)
- **FK attachment (critical):** imported rows must get `purchase_order` set from the association/popup
  source. If base/Pro import doesn't auto-set it, require a `purchase_order` column in the template.
  Without the FK, rows orphan and the issue-gate aggregate misses them.
- **Linkage context:** confirm the import button's linkage resolves `ctx.popup.record.status`; if a
  block-level sub-table action exposes a different context, adjust the reference.

## Verification (user-driven — custom-action + import can't run headless)
- **B1** manual over-budget line still blocked per-line (D47 regression).
- **B2** import over PR amount onto draft → import OK, **Issue rejected** w/ message, PO stays draft, no print.
- **B3** import within budget → **Issue succeeds** → `issued`+`issued_at`, Print appears.
- **B4** Import button hidden on any non-draft PO.
- **B5** Import button hidden for non-Procurement.
- **B6** imported rows attach to parent PO + `line_total` computes.
- **B7** normal issue (within-budget, all-priced, ≥1 line) still works; incomplete/unpriced still rejected.
- **B8** import-trigger on → Recompute A fires → `lines_total` refreshes; draft `needs_reprint` stays false.

CLI-checkable: `issue_over` condition via `flow-nodes test`; node wiring via readback. Aggregate not
test-coverable (`feedback_flow_nodes_test_coverage`) → verify via live data.

## Rollback
Re-enable predecessor `370047775735808` (`resource update --values '{"enabled":true,"current":true}'`);
remove the import action + linkage from the surface.

## Docs at session end
D52 in decisions.md; roadmap row 016; project_current_state.md (new `issue_po` version + node keys, import
action + linkage uids); chunk As-built. Commit after each verified phase.

## Sequence
A first (revision built disabled → wired → enabled → CLI-checked), then B (import action → linkage),
then user walkthrough B1–B8, then docs.
