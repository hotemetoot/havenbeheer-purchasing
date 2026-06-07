# MVP9d — PO completion / closing + immutability

## Context

PO lifecycle so far: 9a (create), 9b (`draft → sent` budget zones, `draft → closed`), 9c
(receiving → `partially_received` / `received`). The PO can now reach `received` but has **no
way to finalize**, the Close action only works from `draft` (its own guard message says "Full
close lands in MVP9d"), and terminal POs are **not locked** — only PR records have an
immutability guard (Guard A). MVP9d closes these gaps so a PO has proper terminal states.

**Scope correction (important):** the chunk file `chunks/009d-*.md` still lists a **cancel
(draft → cancelled)** action and a `cancelled` status. That is superseded by **D28** — `cancelled`
was collapsed into `closed`; "cancel a draft" is just "close a draft with a reason", which 9b
already built. So MVP9d has **no cancel action and no `cancelled` status**. The chunk file will be
reconciled to D28 as part of this work.

**User-confirmed scope decisions:**
- Immutability covers **header + lines** (full chunk C4).
- Closeable set = `{draft, sent, confirmed, partially_received}`. A `received` PO is **completable
  only** (matches the PO design doc); to bail out of a received PO, correct a line down first
  (reverts to `partially_received`), then close.

**Doc-lag caught during planning (fix in project_current_state.md at session end, not part of the
build):** live active versions differ from what the doc records — Send PO `367086330314752`
(doc says `366981771362304`), PR Approval `368641179582464` (doc says `367885604880384`),
Receiving recompute `368710576439296` (doc says `368072534523904`). Trust the live IDs.

## Outcome

Procurement can **Complete** a received PO and **Close** any non-terminal PO with a reason.
Once `completed` or `closed`, the PO header and its `po_lines` are immutable (edits/deletes
blocked server-side), mirroring PR Guard A.

---

## Phase 9d.1 — Complete action (`received → completed`)

New custom-action workflow + button, mirroring the **Send PO** pattern (`send_po`: guard
condition → fail message/end on false, update on true).

- **Workflow** `complete_po` (custom-action, **sync**, collection `purchase_orders`, no appends):
  - `complete_guard` (condition, basic): `status == "received"`, `rejectOnFalse:false`.
    - br=0 (false) → `complete_fail_msg` (response-message: "Complete is only available for a
      fully-received PO.") → `complete_fail_end` (end, `endStatus:-1`). *(per
      `feedback_inline_guard_end_node`)*
    - br=1 (true) → `complete_update` (update `purchase_orders` where `id={{$context.data.id}}`,
      set `status="completed"`, `completed_at="{{$system.now}}"`).
- **Button** "Complete PO" on PO surfaces — `RecordTriggerWorkflowActionModel` bound to
  `complete_po` (set `workflowKey` via `nb api resource update --resource flowModels`, **not**
  flow-surfaces configure — per CLAUDE.md). Place on PO table-row popup + PO detail popup
  (`g9xffr68350`), alongside Send (`slybgc23q1i`) / Close (`lylrxwl1b3g`).
  - Linkage rules (copy the Send button's two-rule shape):
    - Hide when `record.status != "received"`.
    - Procurement-only: hide when `ctx.user.roles.title` `$notIncludes` `"Procurement"`.

## Phase 9d.2 — Broaden Close (`sent / confirmed / partially_received → closed`)

`close_po_draft` (`366780629319680`) has **executed=0**, so its guard can be **edited in place**
(no revision needed — workflow-versioning rule only applies after first execution). Keep the
existing popup-form pattern (close_reason + close_comment required → submit triggers the workflow).

- **Edit guard node** `close_guard_draft` (currently `equal status,"draft"`): change to an **OR
  group** (basic engine) of `equal status` against each of `draft`, `sent`, `confirmed`,
  `partially_received`. (`$notIn`/`$in` not usable in condition leaves — use OR of `equal`, per
  CLAUDE.md.)
- **Edit** `close_guard_msg` text → "Close is not available for a completed or closed PO."
- **Rename** workflow title `Close PO (from draft)` → `Close PO`.
- **Close button** (`lylrxwl1b3g`) linkage: change "hide when `record.status != "draft"`" to hide
  when `record.status` is one of the terminal/non-closeable set (`completed`, `closed`,
  `received`) — i.e. show for draft/sent/confirmed/partially_received. Express as the inverse the
  same way the codebase does (OR of `$eq` conditions, since `$notIn` is unsupported). Keep the
  procurement-only rule.

## Phase 9d.3 — PO header immutability guard (mirror Guard A)

New **request-interception** workflow on `purchase_orders`, modeled on Guard A
(`496ookqmg01`) and the Create-PO guard (`vgv8hcrtjvx`):

- `Guard: PO Immutability` (request-interception, global, **sync**; actions: `update` + `destroy`
  on `purchase_orders`).
  - Query node — fetch the target PO by `{{$context.params.filterByTk}}`.
  - Condition (OR): `status == "completed"` OR `status == "closed"` →
  - br=1 (true): response-message ("This PO is finalized and can no longer be edited.") →
    end (`endStatus:-1`).
- **D24 bulk-update limitation applies** (Guard relies on `filterByTk`; bulk update via
  `filter.$and[0].id.$in` bypasses it) — document, do not fix (C5).

## Phase 9d.4 — `po_lines` immutability guard

New **request-interception** workflow on `po_lines` (separate from the existing Receive Guard
`mhfp4d15uee`, which only blocks `received_quantity` on non-receivable POs):

- `Guard: PO Line Immutability` (request-interception, global, **sync**; actions: `update` +
  `destroy` on `po_lines`).
  - Query node — fetch the target line by `{{$context.params.filterByTk}}`, **append
    `purchase_order`**.
  - Condition (OR): `purchase_order.status == "completed"` OR `== "closed"` →
  - br=1 (true): response-message ("Lines of a finalized PO can no longer be edited.") →
    end (`endStatus:-1`).
- Workflow-internal update nodes bypass request-interception (`feedback_request_interception_scope`),
  so the 9c receiving recompute is unaffected.

## Phase 9d.5 — Reconcile chunk file to D28

Edit `chunks/009d-po-completion-closing-immutability.md`: remove the cancel action and the
`cancelled` status from Scope/Acceptance; restate terminal states as `{completed, closed}`;
restate the closeable set and the header+lines immutability decision. (Done during execution —
not in plan mode.)

---

## No data-model changes

All needed fields already exist on `purchase_orders`: `completed_at`, `closed_at`, `close_reason`,
`close_comment` (`status` enum already has `completed` + `closed`; no `cancelled`). No new fields,
no collection edits.

## Build order & commits (per CLAUDE.md "this worked" milestones)

1. 9d.1 Complete workflow + button → verify C1 → commit.
2. 9d.2 Broaden Close (edit guard + button linkage) → verify C2 → commit.
3. 9d.3 + 9d.4 immutability guards → verify C4 → commit.
4. Update `project_current_state.md` (new workflows, broadened close, doc-lag version fixes) +
   reconcile chunk file + add a D-entry only if the build deviated → commit.

Show intended live changes (entities/nodes, CLI category `nocobase-workflow-manage` /
`nocobase-ui-builder`, expected UI result) and **wait for approval before each live change**, per
CLAUDE.md. The two new request-interception guards and the in-place Close edit are reversible
(disable/revert); flag explicitly but no separate rollback doc needed.

## Verification (manual, by user — tables are empty post-D31 cleanup, so create fresh data)

End-to-end via the PO surfaces (page `liwmklclbnc`, detail popup `g9xffr68350`):

- **C1 (Complete):** take a PO to `received` (generate → send → receive all lines). Complete
  button visible (procurement) → click → status `completed`, `completed_at` set. Complete button
  hidden on non-received POs.
- **C2 (Close, broadened):** on a `sent` (and a `partially_received`) PO, Close button visible →
  popup requires reason + comment → submit → status `closed`, `closed_at` set. Confirm Close is
  **hidden/blocked** on a `received` and on an already-terminal PO.
- **C3 (draft close still works):** close a `draft` PO → `closed` (regression of 9b path).
- **C4 (immutability):** on a `completed` and a `closed` PO, attempt a header field edit and a
  line edit/delete → both blocked with the guard message. Confirm a non-terminal PO still edits
  normally.
- **C5 (bulk-update caveat):** documented as deferred (D24-style), not fixed.

Node configs can be smoke-tested pre-button with `nb api workflow flow-nodes test`; custom-action
workflows **cannot** be driven by `workflows execute` (no user context —
`feedback_custom_action_execute_no_user`), so drive the real button for C1/C2.
