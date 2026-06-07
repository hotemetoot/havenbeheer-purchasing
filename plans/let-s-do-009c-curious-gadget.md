# MVP 009c — PO Receiving

## Context

Procurement needs to record deliveries against a sent PO. The data model already
exists (`po_lines.received_quantity`, `po_lines.line_status`) from MVP9a, but nothing
yet *uses* them: receiving a delivery has no effect on line or PO status. This MVP wires
up the receiving loop — Procurement enters `received_quantity` per line, line status and
PO header status auto-derive, and Procurement is notified when a PO is fully received and
ready to complete (the next step, 9d).

Receiver = Procurement (per PO design doc flow line 46 "Procurement logs received
quantities per line"; D25 separation of duties — no separate receiver role exists).
Pricing is **out of scope** (D27 descoped line $-math): the design doc's "recalculate PO
total" step (workflow #2) is dropped — `total` is the manually-entered invoice value and
never derived from lines.

## Live-state facts already verified

- `po_lines.received_quantity` (double) and `po_lines.line_status` (select:
  `pending`/`partially_received`/`received`, default `pending`) already exist.
- `po_lines` has collection-level `logging: true` → **Record History already covers
  `received_quantity`** (9c.1's history requirement is satisfied; no change needed).
- Notification channel `approval-todo-in-app-message` (in-app-message) exists.
- Procurement dept id `363554444476416`, `main_approver` = Pat (user 11).
- The old disabled po_lines total-maintenance workflows (`jsgbxph9444`, `s4syz7vom4n`)
  are **already deleted** — no conflict.
- Receivable PO states: `sent`, `partially_received`, `received` (also accept `confirmed`
  for forward-compat even though no confirm action is built yet).

## Decisions for this build

- **R4 = hard guard** (request-interception on po_lines update), mirroring Guard A /
  Create-PO Guard.
- **Full-receive notification → Procurement main_approver (Pat)**, looked up via a Query
  node (role-stable), same shape as MVP010's FYI node `5h232imw9ss`.
- `line_status` stays a **workflow-maintained select** (design-faithful). Loop avoidance:
  the recompute trigger fires only when `received_quantity` is in the changed-field set,
  so the workflow's own `line_status`/header writes don't re-trigger it.

## Build

### Phase 9c.1 — fields (verify-only)
No field changes. `received_quantity`, `line_status`, and Record History all already
exist. Confirm `line_status` default `pending` (already true). Skip.

### Phase 9c.2 — Receive Guard (request-interception) — R4
New workflow, **request-interception**, sync, collection `po_lines`, action `update`.
Mirror Guard A (`496ookqmg01`) / Create-PO Guard (`vgv8hcrtjvx`) structure:
- Query node: load the referenced po_line's parent `purchase_order` (append
  `purchase_order`) — or query `purchase_orders` by the line's `purchaseOrderId`.
- Condition: parent PO `status` **NOT in** {`sent`, `confirmed`, `partially_received`,
  `received`}. (Use combined `$ne` with `$and` — `$notIn` is unsupported in this project;
  or an OR-of-equals on the receivable states inverted. Basic engine.)
  - true branch (not receivable): response-message ("This PO is not in a receivable
    state.") → end-process `endStatus: -1` (per `feedback_inline_guard_end_node`).
- Bulk-update caveat (D24) applies here too — single-record guard only; acceptable for MVP.

### Phase 9c.3 — PO Receiving recompute workflow
New workflow, **collection event** trigger, **sync**, collection `po_lines`:
- Trigger mode: `update`; **`changed: ["received_quantity"]`** (this is the loop guard —
  the workflow's own line_status/header writes won't re-fire it).
- Append on trigger: `purchase_order`.
- Node chain:
  1. **Calc current line_status** — condition cascade on the triggering line
     (`received_quantity` vs `quantity_ordered`):
     - `received_quantity >= quantity_ordered` AND `quantity_ordered > 0` → `received`
     - else `received_quantity > 0` → `partially_received`
     - else → `pending`
     Then an **Update node** on `po_lines` (filter id = trigger record id) writing the
     resolved `line_status`. (Arithmetic/compare split into separate condition nodes per
     `feedback_condition_inline_arithmetic`; prefer math.js per `feedback_prefer_mathjs_engine`.)
  2. **Aggregate A** — count `po_lines` where `purchase_order = <POID>` AND
     `line_status != 'received'`. (Runs after step 1 so the current line is reflected.)
  3. **Aggregate B** — count `po_lines` where `purchase_order = <POID>` AND
     `received_quantity > 0`.
  4. **Header condition cascade** (basic/math.js):
     - `A == 0` (all lines received) → Update PO `status = received` → **Query Procurement
       dept** (id `363554444476416`, append `main_approver`) → **Notification** node
       (channel `approval-todo-in-app-message`, receiver
       `{{...Procurement.mainApproverId}}` = Pat, `ignoreFail: true`, message "PO
       {{po_number}} is ready to complete.").
     - else `B > 0` → Update PO `status = partially_received` (covers R1 + the R3
       reverse: a corrected-down line that drops A>0 while B>0 reverts `received` →
       `partially_received`).
     - else (nothing received) → no header update (skip).
  - Header `status` writes are on `purchase_orders` (different collection) → never
    re-trigger this po_lines workflow.
- **Sync rationale:** immediate UI feedback for verification; runs in-transaction. Unlike
  the deleted `jsgbxph9444`, this won't error (no dropped-field refs) and never fires on
  line *create* (changed-filter + update-only), so it can't roll back Generate-PO's line
  inserts.

### Phase 9c.4 — Receiving UI — **USER-OWNED (out of my scope)**
The user will build the receiving UI themselves: exposing `received_quantity` as editable
(Procurement-only) and `line_status` read-only on the `po_lines` block of the PO detail
popup. I will not touch UI surfaces in this MVP. The two workflows (9c.2, 9c.3) are
designed to work with whatever UI drives a `received_quantity` update on a `po_lines`
record.

### Phase 9c.5 — Verify R1–R4 (manual, by user)
- **R1** partial receive (qty < ordered on one line) → that line `partially_received`,
  PO header `partially_received`, others unaffected.
- **R2** full receive on all lines → header `received`, Pat gets the in-app notification.
- **R3** correct a line down (`received` → below ordered) → line `partially_received`,
  header reverts `received` → `partially_received`.
- **R4** attempt receiving on a `draft` (or `completed`/`closed`) PO → blocked by the
  Receive Guard with the rejection message.

## Critical references / patterns to reuse
- Guard pattern: Guard A `496ookqmg01`, Create-PO Guard `vgv8hcrtjvx` (request-interception
  + Query → Condition → response-message → end(-1)).
- Notification node shape: MVP010 node `5h232imw9ss` (channel, receivers array,
  `ignoreFail`).
- Query-dept pattern: qProc `yrl9kgkrb3x` (Procurement dept + main_approver append).
- Engine/guard gotchas: `feedback_inline_guard_end_node`,
  `feedback_condition_inline_arithmetic`, `feedback_prefer_mathjs_engine`,
  `feedback_linkage_rules_user_roles`, `$notIn` unsupported (use `$ne`+`$and`).
- Skills: `nocobase-workflow-manage` (both workflows). UI (9c.4) is user-owned.

## Build / commit order (per CLAUDE.md)
1. Build 9c.2 Receive Guard → enable → checkpoint.
2. Build 9c.3 recompute workflow → enable.
3. 9c.4 UI — **user builds this themselves**.
4. User verifies R1–R4 (against their UI) → commit working config.
5. Session end: update `project_current_state.md` (new workflow keys/versions/node ids,
   UI surface ids), set roadmap 009c → built, add D-entry only if the plan changed during
   the build, commit.

## Verification
Manual end-to-end by the user (R1–R4 above), driving the real Procurement user through the
PO detail popup — custom/collection-trigger workflows can't be exercised via
`workflows execute` without a user context (`feedback_custom_action_execute_no_user`).
