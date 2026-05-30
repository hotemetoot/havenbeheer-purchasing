# Plan: PR number + matching PO number

## Context

Purchase orders already carry a `po_number` (auto-sequence `PO-YYYY-NNNN`, e.g. existing `PO-2026-0017`). Purchase requests have **no** number at all. The user wants:

1. A `pr_number` on each PR, formatted `PR-YY-NNNN` (2-digit year, 4-digit counter → e.g. `PR-26-0004`).
2. The PO that is generated from a PR to carry the **exact same** number, only with a `PO-` prefix instead of `PR-` (`PR-26-0004` → `PO-26-0004`), so the two documents are visibly paired.

**Why two parallel sequences won't work:** PR and PO sequence counters increment independently, and not every PR becomes a PO (the PO counter has already drifted to 17 through testing). They would never stay matched. The reliable design is: the **PR owns the number** (its own sequence), and the **PO derives its number from the linked PR** by swapping the prefix, inside the existing Generate-PO workflow. Formula fields can't read across the PR→PO relation ([feedback_formula_field_scope](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_formula_field_scope.md)), so the derivation must happen in the workflow, which means `po_number` must stop being an auto-sequence and become a value the workflow writes.

**Decisions (confirmed with user):** 2-digit year; `pr_number` assigned on PR **creation** (sequence auto-generates at insert — cancelled drafts will leave gaps, accepted); existing 10 PRs left **null** (sequence only fires on new inserts).

## Live-environment facts

- `purchase_orders.po_number` — old **sequence** field was just **deleted by the user**; the name is now free for a fresh string field (Phase 2).
- `purchase_orders.purchase_request` — m2o, FK `purchaseRequestId`.
- Generate-PO workflow key `2izsx8uv50r`, active version `366623590383616`; Create-PO node `ubg9mju1tjm` (custom-action, sync, on `purchase_requests`, appends `[supplier, purchase_order]`). `$context.data` is the PR, so `{{$context.data.pr_number}}` is available (scalar, no append needed).
- All data is test data — existing numbers don't matter.

---

## Phase 1 — Add `pr_number` sequence field to `purchase_requests`

Skill: `nocobase-data-modeling`.

Create field `pr_number`:
- type `sequence`, interface `sequence`, `inputable: false`
- patterns: `string "PR-"` → `date "YY"` → `string "-"` → `integer { digits: 4, start: 1, cycle: "0 0 1 1 *" }` (let NocoBase auto-assign a fresh integer `key`; do **not** reuse 29563).
- uiSchema title "PR Number".

Result: every **new** PR gets `PR-26-0001`, `PR-26-0002`, … at creation. The 10 existing PRs stay null.

## Phase 2 — Create `po_number` as a plain string field

The old `po_number` **sequence** field has already been **deleted by the user** (confirmed: no field named `po_number` and no PO-number column remains on `purchase_orders`). All data is test data — existing numbers don't matter.

Skill: `nocobase-data-modeling`. Create a fresh field `po_number`:
- type `string`, interface `input`, `inputable: true`.
- uiSchema title "PO Number".

This is the value the Generate-PO workflow writes (Phase 3). No sequence/auto-generation on the PO side anymore.

## Phase 3 — Revise Generate-PO workflow to derive `po_number`

Skill: `nocobase-workflow-manage`. Revise key `2izsx8uv50r` (from `366623590383616`) — **preserve node keys**, and after revision **verify the full node count and the false-branch nodes** (revision branch-drop gotcha; this workflow has a guard condition with a false branch carrying a response-message + end-process pair).

Changes inside the revision:
1. Insert a **calculation node** (formula.js engine) immediately before Create-PO node `ubg9mju1tjm`, on the guard's true branch:
   `SUBSTITUTE({{$context.data.pr_number}}, "PR-", "PO-")` → string result.
2. In Create-PO node `ubg9mju1tjm`, add field assignment `po_number = {{$jobsMapByNodeKey.<new-calc-node-key>}}`.

Then enable the new revision (force same key via `--body '{"key":"2izsx8uv50r",...}'` per [feedback_workflow_revision_key_bug](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_workflow_revision_key_bug.md)) and disable the old one.

**Edge case:** a PO generated from one of the older approved PRs that has no `pr_number` would get a blank `po_number` (SUBSTITUTE on null → empty). Acceptable (test data); if needed, backfill that PR's `pr_number` first.

## Phase 4 — Surface `pr_number` in the UI

Skill: `nocobase-ui-builder`. Add `pr_number` as **read-only** (it's server-generated) to:
- PR table block `l1e2iwdwau9` (a column).
- PR detail popup `2b367dbd157`.

Do **not** add it to the PR create form (auto-generated, not user-entered). `po_number` is already shown on PO surfaces.

## Phase 5 — Verification (end-to-end)

1. Create a new PR → confirm it shows `PR-26-0001` (next counter).
2. Run it through approval to `approved`.
3. Click Generate PO → confirm the new PO's `po_number` is `PO-26-0001` (prefix swapped, digits identical to the PR).
4. Confirm table/popup display the PR number.

## Files / state to update at session end

- `project_current_state.md`: new `pr_number` field; `po_number` inputable change (or recreate); new Generate-PO version id + calc node key; UI additions; bump the existing version to Stale IDs.
- `decisions.md`: D-entry for PR-numbering + PO-number-derived-from-PR; affected downstream: any future receiving/reporting MVP that references PO numbering.
- Commit after the chunk/plan, after each verified phase, and after the state update.
