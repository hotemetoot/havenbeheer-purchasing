# Decisions — currently effective

Design, implementation, and workaround decisions that still apply to the current build. Superseded entries live in [decisions-archive.md](decisions-archive.md).

Scope: this is not just design. Implementation choices ("we used a workflow because formulas can't aggregate", "we deferred X to MVP9d", "pattern Y was rejected because of NocoBase limitation Z") belong here. The "why" matters more than the "what" — future-you reads these to understand constraints, not to discover features.

When adding new entries, list affected downstream MVPs by number so step 3 of the session workflow catches forward references.

---

## D1 — Procurement cannot cancel stalled PRs
Only the original submitter can cancel a PR. Simpler Guard C. **Affects:** MVP2.

## D2 — Procurement-originated PRs always go to director
No threshold check on this path. **Affects:** MVP6 (moot under D25 — kept for historical context).

## D5 — Projects + project-budget bypass removed from v1 — **SUPERSEDED by D49 (2026-06-23)**
No `projects` collection, no `charge_to` field, no Guards B/D, no project-budget routing. Every PR follows the same flow. Deferred to v2. **Affects:** all MVPs. **Reversed by D49 (MVP014)** — projects + budget drawdown are now being built (USD envelope, separate approval ladder, hard-block guards).

## D6 — Supplier `current_rating` is manually maintained
Procurement edits on the supplier record. No computation. **Affects:** MVP7.

## D7 — Supplier scoring scale is 1–5 (5 best)
On `supplier_evaluations.score`. **Affects:** MVP7.

## D8 — No supplier onboarding workflow
Procurement creates suppliers directly; immediately usable. ACL gate (Guard #9) is sufficient. **Affects:** MVP7.

## D9 — One PR → exactly one PO
Simpler than original "1 PR → many POs". `closed_for_new_pos` field on PR is moot under this model and is not built. **Affects:** MVP9a–e.

## D10 — PO generation is manual ("Generate PO" button)
Procurement clicks on the approved PR. No auto-creation. PO opens in `draft` pre-filled from the PR. **Affects:** MVP9a.

## D11 — Keep `po_lines`
Procurement may split the PR description into structured lines (UoM, qty, unit price) on the PO. **Affects:** MVP9a, 9c.

## D12 — PO budget-overrun zones
Keep 110% tolerance + zone 1/2/3 logic. Procurement may adjust line prices between PR and PO; overrun guard fires at `draft → sent`. Director + Finance head notified for zone 2; zone 3 blocked. **Affects:** MVP9b.

## D13 — Per-line `received_quantity`
Receiving model uses `po_lines.received_quantity` (fractional supported). **Affects:** MVP9c.

## D14 — Currencies at launch
USD, SRD, EUR. **Affects:** MVP3.

## D15 — `quotation_attachment` is multi-file
Future-proofs for multi-quote later. **Affects:** MVP3.

## D16 — Edit permission for approvers
Dept head can edit PR content while in their queue. Procurement and Director are read-only on PR content (procurement only fills its own quote fields). **Affects:** MVP1, ongoing ACL.

## D17 — Supplier `payment_terms` shape
Single-select from fixed list: Net30 / Net60 / Net90 / COD / Prepayment. **Affects:** MVP7.

## D18 — `resubmitted_from` field dropped
Rejected PRs do not formally link to a successor. Submitter creates a fresh PR.

## D19 — Notifications: in-app only
NocoBase native (workflow tasks + notification icon). No email/SMTP in v1. **Affects:** MVP9b.

## D20 — Director self-PRs deferred to v2
In v1 an assistant submits on Dana's behalf.

## D21 — Dept routing via `main_approver` + `secondary_approver`
Explicit `main_approver` (m2o → users) and `secondary_approver` (m2o → users) on `departments`. `users.on_leave` (boolean) controls fallback. Names are role-neutral ("approver", not "manager"). Replaced the unreliable `department.owners[]` array approach. **Affects:** MVP1 routing, all downstream.

**Why:** `department.owners[]` could be empty, multi-valued, or accidentally broken; the array shape made workflow filters fragile.

**How to apply:** Use `main_approver` for routing; check `on_leave` and fall back to `secondary_approver` if needed. Never reference `department.owners` in workflows.

## D22 — Manual FX rate entry on PR
User enters `fx_rate_to_usd` manually on the PR. `quoted_total_usd` is a formula field (`{{quoted_total}} * {{fx_rate_to_usd}}`, formula.js, read-only). No `fx_rates` collection. **Supersedes** the original design's FX-lookup workflow + `fx_rates` collection. **Affects:** MVP3, MVP4 (Guard E validates `fx_rate_to_usd IS NOT NULL` instead of doing a rate lookup).

**Why:** The original design had `fx_rates` collection + workflow nodes to look up rates at submit time. Built then deleted on 2026-05-24 — the lookup added complexity for no clear payoff. Manual entry gives procurement the rate they want without a separate maintenance burden.

**How to apply:** `fx_rate_to_usd` is just a number field. Guard E checks it is not null. `quoted_total_usd` requires no workflow writes.

## D23 — Manual `needs_director_approval` checkbox (instead of automatic threshold)
Submitter checks `needs_director_approval` on the PR form. Workflow conditions on the field. **Supersedes** D4 (USD director threshold $1,500) — the `approval_limits` collection was never built. Linkage rule on create form makes `justification` required when the checkbox is checked. **Affects:** MVP4.

**Why:** Routing rules weren't clear enough to automate ("is this above $1,500?" missed nuance like emergency procurement, capex vs opex). Manual checkbox shifts judgement to the submitter, which is where it belonged anyway.

**How to apply:** Workflow Procurement Approve branch conditions on this field — true → director path, false → approved immediately.

## D24 — Guard A bulk-update limitation (deferred)
Guard A does NOT intercept bulk update. Bulk-update requests send target IDs in `$context.params.filter.$and[0].id.$in`, not `$context.params.filterByTk`. Guard A's Query node looks up by `filterByTk` only, so bulk-update requests pass through. Fix requires a Script/JSON-query node to extract IDs from `$context.params.filter`, or a dedicated bulk-update workflow. **Deferred post-MVP5.** **Affects:** future hardening.

**Why:** Caught at MVP5 verification; not blocking single-record protection which is the main risk surface.

**How to apply:** If hardening bulk-update is requested, build either a Script node that reads from `$context.params.filter.$and[0].id.$in` or a separate request-interception workflow targeting `action=update` with the bulk shape.

## D26 — MVP7 descoped to suppliers only
`supplier_issues` and `supplier_evaluations` were postponed during MVP7. Only the `suppliers` collection + the optional `supplier` m2o field on `purchase_requests` were built. **Affects:** MVP7 scope; original MVP7 scenarios S3 and S4 are not applicable.

**Why:** Not blocking the PR/PO flow. Procurement can manually edit `suppliers.current_rating` and `suppliers.notes` as a placeholder (per D6). Bring issue logging + evaluations back when there's real demand.

**How to apply:** Treat `supplier_issues` and `supplier_evaluations` as not-built. Do not assume them as dependencies for MVP8 or MVP9*. Revival sketch lives in [chunks/deferred-supplier-issues-evaluations.md](chunks/deferred-supplier-issues-evaluations.md).

## D25 — Procurement staff are excluded from initiating PRs
Policy/ACL, not workflow logic. The "submitter's dept = Procurement → skip to director" routing variant is moot. The dept-owner skip (submitter IS dept approver → skip dept) was already implemented in MVP1 (condition `5hed96jh1u7`). **Supersedes** the original MVP6 scope. **Affects:** MVP6 (complete with no new build).

**Why:** Cleaner separation of duties — procurement reviews PRs, doesn't author them.

**How to apply:** ACL: `member` role used for submitting PRs; procurement-only roles do not get create-PR. No workflow change.

---

## D27 — po_lines pricing descoped
Line items track quantity + receiving only. `unit_price`, `line_total`, and `line_total_usd` are removed from `po_lines`. PO `total` is manually entered from the supplier invoice (no derivation from lines). **Affects:** MVP9a (this revision — Generate-PO workflow no longer writes `unit_price` on the default line; planned 9a.4 Total-maintenance workflow is cancelled); MVP9c (receiving) — only `received_quantity` and `line_status` change; no $-math on lines. MVP9d, MVP9e unaffected.

**Why:** Formula fields can only reference same-collection scalars (see `feedback_formula_field_scope`), so `line_total_usd` cannot traverse to `purchase_order.fx_rate_to_usd`. The denormalize-fx alternative would add a sync-workflow per PO update for a value not currently needed at line level. Pricing decisions in this domain happen at the PO header (supplier invoice = source of truth for $$), and line items are quantity-tracking artifacts. Simpler model overall.

**How to apply:** Don't restore the deleted fields. If a future MVP needs line-level USD reporting, denormalize `fx_rate_to_usd` onto `po_lines` and recompute line USD via a workflow update — don't try to formula-traverse the relation.

---

## D28 — Cancel collapsed into Close (two terminal PO states)
The PO `cancelled` status is removed. Cancelling a PO is now just closing it with an appropriate `close_reason` (e.g. `no_longer_required`). Two terminal states only: `completed` (happy path) and `closed` (everything else, always with a `close_reason` + `close_comment`). The former `draft → cancelled` action becomes `draft → closed`. **Affects:** MVP9b (built this way — Close PO workflow `close_po_draft` stamps `status=closed`, `closed_at`); MVP9a collection definition (`cancelled` dropped from `purchase_orders.status` enum; `no_longer_required` added to `close_reason`); MVP9d (close-from-non-draft builds on this single close path). **Supersedes** PO design-validation §3 (status state machine) and §8 guard #8 wherever they distinguish cancel from close.

**Why:** A separate `cancelled` state added a parallel terminal path and its own audit field (`cancelled_at`) without behavioural difference from a reason-tagged close. Collapsing them simplifies the state machine, the guards, and the UI (one Close button + reason picker instead of Cancel and Close).

**How to apply:** Treat `closed` as the only non-happy terminal state. Use `close_reason = no_longer_required` for what was previously "cancel". The `cancelled_at` field still physically exists on `purchase_orders` (drop was blocked by the irreversible-action guard) but is unused — no workflow writes it; safe to drop later with explicit user OK. Don't reintroduce a `cancelled` status.

---

## D29 — Optional submitter-chosen skip of dept-head approval
> **SUPERSEDED by D36 (2026-06-09).** The skip feature is retired; the dept stage is now always a real
> approval, optionally reassigned to a custom approver. `skip_dept_approval` is no longer read/written by
> any workflow and is off both forms (column retained, unused). Original D29 text kept below for history.

Submitters may opt to skip the department-head approval stage per PR via a
`skip_dept_approval` boolean (default false). When skipped, the dept head is **not** a
blocking approver but is **kept in the loop**: an in-app FYI notification to the submitter's
`mainDepartment.main_approver` (fallback `secondary_approver` when on leave, per D21) plus
view access to the PR. The pre-existing "submitter IS their own dept approver → auto-skip"
path (condition `5hed96jh1u7`) is unchanged and does **not** notify. **Affects:** MVP1
(approval workflow `cv237r8h7k9` — new condition branch + notify node, revisioned), MVP4
(toggle sits beside `needs_director_approval` on the create form). Built as MVP010.

**Why:** The team confirmed dept-head approval isn't always required, but the exact rule is
unclear and likely to stay fuzzy. Rather than encode a brittle rule, we add flexibility and
shift the judgment to the submitter — the same reasoning as D23 (manual
`needs_director_approval` over an automatic threshold). FYI-only (no pull-back) keeps it in
line with D19 (in-app only) and avoids re-injecting an approval mid-flight, which NocoBase
approval workflows don't support cleanly.

**How to apply:** Workflow branches: if submitter is NOT their own dept approver, test
`skip_dept_approval` — true → notify dept head + route to `pending_purchasing_review`;
false → existing Dept Owner Approval. No new status. Ensure the dept head can *open* a
skipped PR (verify the dept-owner view scope; widen only if it's task-driven). The skip is
not a pull-back mechanism — the dept head is informed, not gating.

---

## D30 — Mandatory director approval at ≥ $300 USD (floor on top of the manual checkbox)
Any PR whose `quoted_total_usd` is **≥ 300** must always route to the Director, regardless of
the submitter's `needs_director_approval` checkbox. This is a **floor added on top of** D23, not
a replacement: the checkbox still works as a *voluntary escalation* (a submitter can send a sub-
$300 PR to the Director), and the threshold forces the Director path even when the box is off.
The two combine as **OR** in the existing director-decision condition `bizoy1sj87j` (PR Approval
workflow `cv237r8h7k9`): `needs_director_approval == true` **OR** `quoted_total_usd >= 300`.
Boundary is **inclusive** (exactly $300.00 requires director). Threshold is **hardcoded** as
`300` (no config collection). **Partially supersedes** D23 for the director-decision node — D23's
"director routing is purely the submitter's checkbox" no longer holds; the checkbox is now the
*lower* bound of when the Director is involved. **Affects:** MVP4 (the director-decision
condition); implemented as a workflow revision (`367150157135872` → `367158084370432`), built +
verified 2026-05-30.

**Why:** The team wanted a hard guarantee that larger spends always reach the Director, while
keeping the manual-judgment flexibility of D23 for everything below the line. A floor (rather
than reverting to a pure threshold like the old $1,500 rule) preserves both: judgment below
$300, certainty at/above it.

**How to apply:** The threshold is evaluated on `quoted_total_usd` (the stored USD formula
field), read in the condition via `{{$jobsMapByNodeKey.ec2h8cqal32.data.quoted_total_usd}}`.
It computes to `0` when no quote is entered, so a missing quote never trips the floor. Basic
condition engine, `gte` calculator — no arithmetic/calculation node needed (the
`feedback_prefer_mathjs_engine` caveat is about `$jobsMapByNodeKey` *result* references, not
field-scalar comparisons). To change the threshold or boundary later, revision the workflow and
edit the single `gte` leaf on `bizoy1sj87j`.

---

## D31 — PR number is the source; PO number is derived by prefix swap
Every `purchase_requests` record now carries `pr_number`, an auto-`sequence` field
`PR-YY-NNNN` (2-digit year, 4-digit yearly-cycling counter, e.g. `PR-26-0004`). It is
assigned automatically at **PR creation** (`inputable: false`), so abandoned/cancelled
drafts leave gaps in the numbering — accepted. The matching purchase order takes the
**exact same number with the prefix swapped** (`PR-26-0004` → `PO-26-0004`) so the two
documents are visibly paired.

**Why two independent sequences were rejected:** PR and PO counters increment separately
and not every PR becomes a PO, so parallel sequences would drift and never match. The PR
**owns** the number; the PO **derives** it. Cross-relation formula fields can't read
`purchase_request.pr_number` from the PO side (see `feedback_formula_field_scope`), so the
derivation is done inside the Generate-PO workflow, which means `po_number` had to stop
being an auto-sequence.

**How it's built:**
- The old `po_number` **sequence** field on `purchase_orders` was deleted by the user and
  replaced with a plain `string`/`input` field that the workflow writes.
- Generate-PO workflow (`2izsx8uv50r`) revisioned to active version `367255610327040`: a
  new formula.js calculation node `umk9xiw5aio` computes
  `SUBSTITUTE({{$context.data.pr_number}}, "PR-", "PO-")`, and the Create-PO node
  (`ubg9mju1tjm`) assigns `po_number = {{$jobsMapByNodeKey.umk9xiw5aio}}`.
- Pre-existing PRs would stay `pr_number = null` (sequence only fires on new inserts), and a PO
  generated from a null-`pr_number` PR would get a blank `po_number` — but moot now: **all PR/PO/
  po_lines test data was cleared by the user on 2026-05-30** after verification, so the tables
  start empty. The sequence counter does not roll back on delete, so the first new PR will be
  `PR-26-0002` (`PR-26-0001` was consumed by the deleted verification PR).

Built + verified end-to-end 2026-05-30 (PR `PR-26-0001` → PO `PO-26-0001`). **Affects:**
MVP9a (Generate-PO), and any future receiving/reporting MVP that references PO numbering.

---

## D32 — Mandatory board approval at ≥ $15,000 USD (second floor, above the Director)
Any PR whose `quoted_total_usd` is **≥ 15000** must, *after* the Director approves, route to a
new **Board Approval** stage instead of going straight to `approved`. The board does not use the
app — they sign a hard copy — so the in-app step exists to **record** that decision: Procurement
(Pat, user 11) uploads the signed document and approves. This is a **floor on top of D30**
(director ≥ $300): a ≥ $15k PR already passes the director under D30, so the board branch always
hangs off the director-approve branch — there is no "board but no director" case. Boundary is
**inclusive** (exactly $15,000.00 requires board); threshold **hardcoded** as `15000`.

**Mechanism (chosen over a free-floating attachment + guarded button):** a 4th approval node
mirroring the existing three. The required signed-document attachment is enforced natively by a
**required field on the approval ProcessForm**, the task lands in Procurement's queue (won't be
forgotten), and reject/return come for free. New status value `pending_board_approval`. New field
`purchase_requests.board_approval_document` (multi-attachment). Implemented as a workflow revision
(`367158084370432` → `367885604880384`, key `cv237r8h7k9`): on the Director-approve branch a
condition `fro4hak78r9` (`gte`, reusing the proven D30 reference
`{{$jobsMapByNodeKey.ec2h8cqal32.data.quoted_total_usd}}`) routes **< $15k → approved** (existing
node `kj1zcmujub8`) and **≥ $15k → pending_board_approval → Board Approval node `01upqmcb1qy`
(assignee 11)** → approve/return/reject. Built + verified end-to-end 2026-06-02 (16,000 USD PR).
**Affects:** MVP4 (director-decision area); the PR Approval workflow lineage.

**ACL dependency (D32a):** recording board approval requires Procurement to **upload** the signed
file, which is a `create` on the `attachments` collection. Procurement's global strategy was
`view/trigger/update` (no create), so this 403'd. Granted a **narrow independent resource
permission**: procurement → `attachments` → `view/create/update` (scope all). Deliberately **not**
a global `create` (that would let procurement create PRs, violating D25). See auto-memory
`feedback_approver_attachment_upload_acl`.

**Build gotcha (not a decision, recorded for context):** the board approval form was built via
`applyApprovalBlueprint`, which omits the per-action `CommentFormModel`; approvers then 403 on
`flowModels:save` when the runtime tries to create it. Fixed by pre-creating three
`CommentFormModel`s (`bcmt_approve/reject/return`) and setting each action's `commentFormUid`. See
auto-memory `feedback_approval_blueprint_comment_models`.

**Why a floor, not a pure threshold:** same reasoning as D30 — preserves the manual-judgment
flexibility below the line while guaranteeing the largest spends always reach the board. To change
the threshold/boundary later, revision the workflow and edit the single `gte` leaf on `fro4hak78r9`.

---

## D33 — MVP9d scope: complete + broadened close + header/line immutability (no cancel)
PO completion/closing/immutability built 2026-06-07, **aligned to D28** (no `cancel` action, no
`cancelled` status — "cancel a draft" is close-with-reason, already in 9b). The original
`chunks/009d` cancel item is removed. Decisions taken:

- **Complete** is `received → completed` only (new sync custom-action workflow `qh7b3hc5q1r`).
- **Close** allows `{draft, sent, confirmed, partially_received} → closed`. `received` is
  **deliberately not closeable** — a received PO completes; to bail out, correct a line down to
  revert it to `partially_received`, then close. (Matches the PO design doc; user-confirmed.)
  - **Trigger-type correction (2026-06-07):** Close must capture `close_reason` + `close_comment`
    via a form, so it is a **post-action event** (`type:"action"`, sync, local mode, key
    `f8gpu17s6hq`) bound to the Close EditForm's **Submit**. The first 9d attempt wrongly used a
    `custom-action` workflow (`close_po_draft`) — a form Submit can only bind
    pre-action/post-action/approval, never custom-action — so it was unbindable and is now
    disabled + renamed "(deprecated custom-action)". `custom-action` is only for one-click
    "Trigger workflow" buttons (Send PO, Complete PO). See auto-memory
    `feedback_workflow_form_button_pattern` (corrected; this was the 2nd occurrence of the mistake).
- **Immutability covers header + lines** (user-confirmed): two request-interception guards
  (`xvcsdv07c5j` on `purchase_orders`, `f3dkb37te22` on `po_lines`) lock update+destroy when the
  PO status ∈ {completed, closed}. Same shape as PR Guard A; **D24 bulk-update limitation applies**
  (relies on `filterByTk`).
- **UI buttons are built by the user**, not the agent — consistent with the 9c receiving UI. An
  agent direct-insert of a `RecordTriggerWorkflowActionModel` into `flowModels` did **not** register
  into the normalized flow-surface readback (and so would not render reliably); build action buttons
  through the NocoBase UI (or the flow-surfaces authoring API), not raw `flowModels` create. The
  doc-recorded Close button `lylrxwl1b3g` had already been **removed by the user**, and a
  `TemplatePrintRecordActionModel` (MVP9e) was added by the user beside Send.

**Payment-vs-immutability caveat (D33a):** the PO immutability guard locks *all* updates on a
terminal PO, including `payment_status` / `payment_date`. The PO design says payment is orthogonal
to PO status (Finance updates at any stage). This is **not a conflict today** — no Finance payment
UI/workflow exists and the finance role strategy is `null` — so terminal-lock is safe. **When a
payment MVP is built**, add a carve-out so Finance can still set payment fields on a terminal PO
(e.g. exempt those fields, mirroring the `closed_for_new_pos` operational-flag exemption), rather
than loosening the whole guard.

**Affects:** MVP9d (this build); MVP9e (template printing — not started; only a bare "Template
print" button exists on the PO detail block, no template configured/tested); a future payment MVP
(must respect D33a).

---

## D34 — Complete PO requires an attached invoice + invoice total (USD)
Built 2026-06-09. A PO can no longer be marked `completed` without (a) an **attached invoice**
(`invoice` belongsToMany non-empty) and (b) a **positive invoice total in USD** (`total_usd > 0`),
in addition to the existing `status == "received"` gate (D33). Enforced in **two places**:

- **Workflow guard (hard stop)** — Complete PO workflow `qh7b3hc5q1r` revisioned
  `368746204954624` → **`368971625791488`** (same key; the predecessor had `versionStats.executed:3`
  so a revision was required despite the doc's stale `executed:0`). Trigger gains `appends:["invoice"]`.
  Node chain grows 4→8: `complete_guard` now AND's `total_usd > 0` (kept **basic** — returns false,
  not an error, on null `total_usd`; math.js throws on `null > 0`); a new `inv_count` calc
  (**math.js** `count({{$context.data.invoice}})`) feeds `complete_invoice_guard`
  (**math.js** `>= 1`), with its own reject message/end on the false branch.
- **Button linkage (UX mirror)** — Complete button `e60dce0bb2d` (now built by the user on PO
  detail block `g9xffr68350`) linkage `us98o7djgw0` gains two `$empty` items
  (`ctx.record.invoice`, `ctx.record.total_usd`) so the button hides until completable.

**Engine split (verified via `flow-nodes test`):** the basic condition engine has no
array-emptiness calculator (`empty`/`notEmpty` unregistered) and can't count arrays; math.js can't
string-compare and errors on `null > 0`. So status/total/null-safe checks → basic, array count →
math.js. (Reinforces auto-memory `feedback_prefer_mathjs_engine` with the inverse caveat:
math.js is wrong for string equality and null comparisons.)

**Edge note:** linkage `$empty` does not catch `total_usd == 0` (0 is a value); the server guard's
`> 0` does, so the button is the soft hint and the workflow is authoritative.

**Affects:** MVP9d (this change; C1 acceptance now includes no-invoice/no-USD-total rejection — needs
re-verification by the user driving the button). MVP9e (template printing) and the future payment
MVP unaffected.

---

## D35 — Close Guard: reject + message on a non-closeable close attempt
Built 2026-06-09. The Close PO workflow (`f8gpu17s6hq`) is a **post-action event** (`type:"action"`),
which by definition runs **after** the update and cannot reject the request or surface a message
(confirmed against the workflow trigger reference: `action` = Post-action Event; `request-interception`
= Pre-action Event). Consequently, a Close attempt on a `received` PO previously saved
`close_reason`/`close_comment` via the form's own update and then silently did nothing — no error, no
message. The PO immutability guard (`xvcsdv07c5j`, D33) only covers `completed`/`closed`, so `received`
(and any other non-closeable, non-terminal status) was a silent gap.

**Fix:** new request-interception (pre-action) workflow **Close Guard** `b6brl8r9c58`
(ver `368982201729024`, global, sync, action `update` on `purchase_orders`). Chain:
`close_guard_query` (load PO by `filterByTk`) → `close_guard_cond` (basic AND: `close_reason` present
in `$context.params.values` **and** current status NOT in {draft, sent, confirmed, partially_received})
→ response-message + end(-1). Mirrors the immutability-guard shape; the `values.<field>` close-attempt
test reuses the proven Receive-guard pattern so it does **not** fire on a normal edit that omits
`close_reason`.

**Design note:** the soft layer (button visibility) + the post-action stamper remain; this adds the
missing hard pre-action rejection, consistent with how PR/PO immutability is enforced. Verified via
`flow-nodes test` (block on received/completed close attempt; allow on sent/draft; no false-block on a
reason-less edit). **D24 bulk-update limitation applies.**

**Caveat:** detection keys on `close_reason` being present in the submitted values — keep
`close_reason`/`close_comment` out of any normal PO edit form (they belong to the Close popup only),
or a reason-bearing edit of a received PO would be blocked.

**Affects:** MVP9d (closeability acceptance C2 now actually messages the user). No downstream MVP impact.

---

## Living register

New entries go below in numeric order. When superseding a prior decision, mark the prior entry as superseded in [decisions-archive.md](decisions-archive.md) and add a `**Supersedes:** D#` line on the new entry.

---

## D36 — Submitter-selectable dept-stage approver (retires the skip)
**Supersedes:** D29 (MVP010 skip-dept-approval). Built as MVP012 (2026-06-09).

Submitters may **reassign the department-approval stage** to another person instead of skipping it.
Two new `purchase_requests` fields: `use_custom_approver` (boolean, default false) and
`custom_approver` (m2o → users). On the create form a checkbox reveals a required picker (scoped to the
submitter's department, excluding self — see ACL/UI note). When a custom approver is chosen, the
dept-stage approval task goes to **that** person and the department head receives an in-app FYI
notification. When not chosen, the existing Dept Owner Approval (dept head) runs unchanged. The
pre-existing "submitter IS their own dept approver → auto-skip" path (condition `5hed96jh1u7`) is
**unchanged and still evaluated first**.

**Why:** Same flexibility-over-brittle-rule reasoning as D23/D29 — the team wanted to redirect approval
up/sideways in the hierarchy per-PR (e.g. to an assistant manager) without encoding a fixed org chart.
The skip feature (D29) is retired in favour of this: the dept stage is now always a real approval, just
optionally reassigned, which keeps an explicit approver on every PR.

**How applied (workflow `cv237r8h7k9`, revision `369076269481984`, 30 nodes):** the old skip branch was
repurposed. Condition `eafkgfa3axi` (retitled "Custom approver chosen?") = AND of `use_custom_approver==true`,
`custom_approver.id != null`, and `custom_approver.id != createdById` (defense-in-depth: a self-pick falls
through to the dept-head path — no self-approval even if the picker is bypassed). br=1 → reused notify node
`5h232imw9ss` (FYI to dept head) → new approval node **Custom Approver Approval** `fifkfnqn9pm`
(assignee `{{$context.data.custom_approver.id}}`, built by duplicating the Dept Owner node so the
ProcessForm + comment models are identical) → approve/return/reject updates → converges to Procurement.
br=0 → Dept Owner Approval `cfg687cye3n` (dept head, unchanged). `custom_approver` added to trigger appends.

**Skip removal (workflow + UI only, column kept):** the `skip_dept_approval` field is no longer read or
written by any workflow and was removed from the create form (already absent — user had dropped it) and
the detail popup (read-only wrapper `in24ndj91et` removed). **The `skip_dept_approval` column is retained**
(unused) to avoid data loss — safe to drop later with explicit OK.

**ACL/UI note (D25/D36):** the custom_approver picker's department-scope + self-exclusion is set via the
form's "Set data scope" UI setting (the public CLI authoring API doesn't expose a data scope on the
record picker). Self-approval is independently blocked server-side by the workflow condition, so the
picker scope is UX-only.

**Affects:** MVP1 (approval workflow — repurposed branch + new approval node), MVP4 (create form toggle),
MVP010 (retired — D29 superseded). No impact on the director ($300, D30) / board ($15k, D32) stages.

---

## D37 — Sub-$300 default flips to Director; procurement `is_regular` is the opt-out
**Amends:** D30 (director $300 floor). **Retires the routing role of:** D23 (`needs_director_approval`).
Built as MVP013 (2026-06-09).

The director-decision rule below $300 is inverted. Previously (D23/D30): a sub-$300 PR was approved
directly **unless** the submitter ticked `needs_director_approval` — director was opt-*in*. Now the
**default below $300 is Director**, and Procurement gets an opt-*out*: a new
`purchase_requests.is_regular` boolean (default false), set by **Procurement on their approval form**,
sends a routine small spend (cleaning supplies, consumables, etc.) straight to `approved`.

Final routing at the director-decision condition `bizoy1sj87j` (after Procurement approves):
- **≥ $300** → Director, always (unchanged, D30 — inclusive boundary, hardcoded `300`).
- **< $300 AND `is_regular == true`** → approved directly (Procurement final).
- **< $300 AND not regular (default)** → Director.

**`needs_director_approval` is retired from routing** (user decision): the checkbox no longer affects
the condition. The **column is kept** (unused, parallel to `skip_dept_approval`) — safe to drop later
with explicit OK. It was already off the create form (user rebuilt that form in MVP012), so no
create-form change. `is_regular` is **not** on the create form (it is a procurement-review
classification, not a submitter field).

**How applied (workflow `cv237r8h7k9`, revision `369154168193024` → `369161752084480`, 30 nodes, same
key forced via raw `--body`):** condition `bizoy1sj87j` (retitled "Director required? (>= $300 OR not
regular)") is still a 2-leaf OR on the **basic** engine; the `needs_director_approval == true` (equal)
leaf was swapped for **`is_regular != true` (notEqual)**, reading
`{{$jobsMapByNodeKey.ec2h8cqal32.data.is_regular}}` (same node-data reference as `quoted_total_usd`,
since Procurement sets it during review). The `quoted_total_usd >= 300` (gte) leaf is unchanged. Branch
orientation unchanged: **true → Director** (`eg86l2ilhmk`), **false → approved** (`jy1365pvsce`).

**Why `!= true`, not `== false`:** null-safety. An unset/null `is_regular` must be treated as
not-regular → Director. `notEqual(null, true)` returns true on the basic engine (verified via
`flow-nodes test`: null+<300 → Director), whereas `equal(null, false)` would be false and wrongly route
a null sub-$300 PR to approved. The field's `default: false` is belt-and-suspenders on top.

**Why a procurement opt-out, not an auto-rule:** same flexibility-over-brittle-rule reasoning as
D23/D30 — "regular" is a manual judgment call (the team couldn't pin an exact rule), so it stays a
human classification, just moved to Procurement (who reviews the actual quote) instead of the submitter.
Threshold stays hardcoded `300`. To change later: revision the workflow and edit the two leaves on
`bizoy1sj87j`.

**UI:** `is_regular` is **editable** on the Procurement approval ProcessForm (new revision's grid
`03uy1easu6l`, CheckboxFieldModel wrapper `dcbp2xasi5f`) and **read-only** on the PR detail popup
(grid `16975baef39`, DisplayCheckboxFieldModel wrapper `6q8zzia1bt7`). No new ACL — Procurement already
edits its quote fields on the same form. The retired `needs_director_approval` read-only display remains
on the detail popup (harmless, historical).

**Affects:** MVP4 (director-decision area), MVP013 (this build); the PR Approval workflow lineage. No
impact on the dept/custom-approver stage (D36) or the board ≥ $15k stage (D32).

## D38 — Role hardening: view-only base, self-sufficient function roles, ACL over guards (2026-06-11)

**Decision:** `member` (base) and `director` strategies are **view-only**. Function roles carry
complete independent permissions: new dept-bound `operations` role owns PR create/update (update
scoped to own + editable statuses); `procurement` lost PR `create`/`importXlsx` (D25 now enforced)
and its update whitelists exclude workflow-managed columns (`status`, stamps, `po_number`,
`line_status`, derived totals). Workflow-managed fields are enforced read-only via **ACL field
whitelists, not request-interception guards** (user preference). Approver roles get a
**render-enabler** update grant (minimal fields, narrow status scope) so approval ProcessForms
render. Custom-action buttons stay protected by guards *inside* the workflows, not trigger ACL.

**Why:** strategy-mode ACL had no field whitelist — any user could write `status`/`approved_at`
by API (self-approval bypass); procurement's create violated D25.

**How to apply:** new roles follow the same pattern: explicit full-field `view` in every
independent row, base-role desktop routes copied, render-enabler if the role's users approve.
Never re-add `update`/`create` to the member strategy.

**Affects:** all future MVPs touching ACL; payment MVP (finance role needs the same treatment).
**Status:** effective.

## D39 — PR draft stage removed from the flow; users submit directly (2026-06-11)

**Decision:** the user removed the `draft` stage from the PR flow — creating a PR submits it
immediately. The `status` enum value `draft` and the field's `defaultValue: 'draft'` are
**retained** (data model untouched); the change is at form/flow level. May be reinstated later.

**Why:** simplification — the draft+submit two-step added friction without value at current scale.

**How to apply:** nothing should depend on PRs resting in `draft`: the Cancel workflow's guard
(`status=="draft"`) and ACL scope 2 ("PR — own and editable", status ∈ {draft, info_requested})
now effectively match only `info_requested`. Revisit both if cancel-before-decision or
edit-own-pending is still desired (see HANDOFF.md follow-ups).

**Affects:** Cancel PR flow (MVP2), scope 2 / operations role update window (D38), any future
chunk that assumes a draft stage.
**Status:** effective.

## D40 — Director and Board approvers are data-driven from departments.main_approver (2026-06-11)

**Decision:** the PR Approval workflow no longer hardcodes approver user ids. The Director
approval node resolves its assignee from the Director department's `main_approver` (via a new
"Query Director Dept" node, key `ld6gei5ybc5`, inserted before it); the Board approval node
resolves from the Procurement department's `main_approver` (reusing the existing qProc query
`yrl9kgkrb3x`). Both use the proven filter-block variable form
`{{$jobsMapByNodeKey.<queryKey>.main_approver.id}}`. Set `departments.main_approver` to change
an approver — no workflow edit needed. Director dept → Dana (12), Finance dept → fiona.finance
(14, new test user); Procurement (Pat 11) and Operations (Oliver 10) were already set.

**Why:** hardcoded `[12]`/`[11]` assignees survive personnel changes only by re-revisioning the
workflow; `main_approver` already drove the dept stage, so this completes the pattern (approved
in the 2026-06-11 audit session, HANDOFF.md Phase 2).

**How to apply:** PR Approval revision `369495666917376` (key `cv237r8h7k9`, 31 nodes) is active.
Future approver changes = update `departments.main_approver`. The `finance` role got the
render-enabler treatment per D38 (view 37 fields + update 2 rejection fields @ scope 10, member's
11 desktop routes) so fiona's future approval forms render. No finance approval stage exists yet —
fiona is groundwork for the payment MVP.

**Affects:** PR Approval lineage; the future payment/finance MVP; Phase 3 cleanup (HANDOFF.md).
**Status:** effective — built + user round-trip verified 2026-06-11 (PR-26-0019: Dana via query
node, Pat via qProc). Follow-on: the Board form's blank-fields issue (ApprovalDetailsModel renders
stored approval data, not the live record) was fixed by rebuilding the board ProcessForm on the
director pattern; see `feedback_approval_details_block_snapshot` in auto-memory.

## D41 — Stale-field & fixture cleanup; secondary-approver fallback fully removed (2026-06-12)

**Decision:** dropped the dead data-model remnants with user OK (HANDOFF.md Phase 3):
`purchase_requests.needs_director_approval` (retired from routing by D37) and
`.skip_dept_approval` (dead since MVP012/D36), `purchase_orders.cancelled_at` (unused since
D28), and the never-built secondary-approver/on-leave fallback — `departments.secondary_approver`
**plus its users-side mirror** `users.department_secondary_approver_of` (belongsTo, FK
`secondaryApproverId` on users) and both leftover FK scalars (`departments.secondaryApproverId`,
`users.secondaryApproverId`) and `users.on_leave`. Also deleted the 8 MVP9d test fixtures
(PR-26-0008..0011, PO-26-T1..T4 + their 2 lines; guards temporarily disabled then re-verified)
and dropped the empty `test` collection. PR-26-0014 "olvire custom" kept per user choice.

**Why:** the fallback feature was never built (system stays dynamic via `main_approver` edits per
D40); the rest was confirmed-dead routing/test noise. All values were NULL/false everywhere except
the two PR booleans (historical flags), snapshotted to `backups/snapshot-*-20260612.json` before
the drop. Fixture records snapshotted to `backups/fixtures-*-20260612.json`.

**How to apply (observed platform behavior):** NocoBase auto-scrubbed the dropped names from ACL
field whitelists (view lists went 37→35 on their own), but does NOT touch UI display models or
workflow trigger appends: removed live UI nodes `p9acb4e35of` (PR popup), `2fbb3d11461`
(departments table column), `b1d31ddeafc` (users table column) via flow-surfaces remove-node, and
removed `createdBy.mainDepartment.secondary_approver` from the PR Approval trigger appends — done
as an in-place config edit on the user's brand-new active version `369536223739904` (executed=0,
so no revision needed). Stale references on dead approval surfaces from disabled versions were
left as-is (not rendered).

**Affects:** none downstream — a future on-leave/fallback feature would re-add fields from scratch.
**Status:** effective — drops verified by collection-field readback; guards re-verified blocking
after re-enable (Guard A, PO immutability, line immutability).

## D42 — Cancel PR retired; PO add-line quick-create fix (2026-06-12)

**Decision:** Cancel-by-submitter (MVP2) is retired. The PR `draft` stage no longer exists in the
flow (D39 — users submit directly), so the Cancel workflow's guard (`status=="draft"`) could never
match again. With user OK ("retire cancel"): removed the Cancel button `b197e8120a3` (EditAction +
popup form with `cancellation_reason`) from the PR detail popup `2b367dbd157`, and deleted **all
versions** of both workflows — Cancel Purchase Request (key `59ezifdoqvj`, 2 versions) and Cancel
PR Guard (key `8yngslauuj4`, 4 versions). Backups: `backups/cancel-button-b197e8120a3-20260612.json`
+ `backups/cancel-workflows-20260612.json`.

**Kept:** `purchase_requests.cancellation_reason` + `.cancelled_at` fields and the `cancelled`
status enum value (historical data may exist; nothing writes them anymore). Scope 2's editable
window is effectively `info_requested` only — acceptable, no change.

**Same session (PO add-line bug):** "Name already exists" when adding a PO line was the
`unit_of_measure` select on the add-line form (`d8c864bef73`) having quick-create
(`quickCreate:"quickAdd"`) — a typed entry submits `{name:"kg",...}` WITHOUT id, so the server
creates a duplicate `units_of_measure` and hits the unique `name` constraint. Set
`quickCreate:"none"` (raw flowModels patch; flow-surfaces configure didn't persist this key).
Also set `po_lines.titleField` → `description` (was `id`).

**Corrected finding:** scopeId `363334209503233` on procurement attachments/suppliers rows is NOT
dangling — it's the built-in "All records" scope in `dataSourcesRolesResourcesScopes` (a separate
table from the numbered `rolesResourcesScopes`). Doc note removed. Scopes 3/6–9 are referenced
only by 8 **orphaned** `dataSourcesRolesResourcesActions` rows (parents deleted during role
hardening) — inert; fix/delete left pending (permission-blocked this session).

**Affects:** none downstream. A future "cancel pending PR" feature would be a new build (new
workflow + button), not a revival.
**Status:** effective — cancel workflows verified gone (0 rows for both keys), button readback null.

## D43 — Inert ACL scopes 3/6–9 deleted (2026-06-13)
Deleted the 5 unused `rolesResourcesScopes` rows (3 "PR — own department", 6 "PO — submitter
view", 7 "PO — department view", 8 "PO line — submitter view", 9 "PO line — department view")
and their 8 orphaned `dataSourcesRolesResourcesActions` rows. Chose delete over camelCase-fix.

**Why:** All 5 parent `dataSourcesRolesResources` rows were already gone (deleted during role
hardening), so the action rows were inert — nothing rendered or enforced them. The scopes also
carried snake_case FK columns (`submitter_id`, `department_id`) that would 400 if bound. A future
department/submitter PO-visibility feature would re-author scopes via the ACL UI anyway, so
keeping broken dead rows added only clutter.

**How to apply:** A scope with no live action row referencing it is dead config — verify parent
`dataSourcesRolesResources` existence before assuming a scope is "in use". Live-verify after
deletes (count remaining scopes; confirm 0 dangling `scopeId` references). Backup
`backups/acl-scopes-3-6-9-DELETED-20260613.json`.

**Affects:** none downstream — no role or action referenced these. Active scopes 2/4/5/10 untouched.
**Status:** effective — live-verified 4 scopes remain (2,4,5,10), 0 orphan rows, 0 dangling refs.

## D44 — Guard execution retention: auto-delete resolved only (2026-06-13)
Set `options.deleteExecutionOnStatus: [1]` on all 6 request-interception guards (`496ookqmg01`,
`vgv8hcrtjvx`, `mhfp4d15uee`, `xvcsdv07c5j`, `f3dkb37te22`, `b6brl8r9c58`). Status `1` = RESOLVED
(guard allowed the action through) → auto-deleted. Statuses `-1` (guard blocked a bad mutation)
and `-2` (error) are retained for audit/debugging. Pruned the 71 pre-existing resolved executions.

**Why:** The guards fire on every update/destroy and the resolved (allowed) executions are pure
noise that accumulate unbounded (103 rows across 6 guards at this audit). The meaningful records
are the blocks (someone attempted a forbidden mutation) and errors — those stay.

**How to apply:** `deleteExecutionOnStatus` is a runtime retention setting in `workflows.options`;
update it in place via `resource update` on the current workflow version — **no revision needed**
(it is not part of the flow definition). For an interception guard, status `1` = allowed-through;
the deliberate block ends `-1` (via the end-process `endStatus:-1` node). Manifest backup
`backups/guard-resolved-executions-DELETED-20260613.json`.

**Affects:** none downstream — retention/observability only, no flow-logic change.
**Status:** effective — live-verified: all 6 options carry `[1]`; 32 guard executions remain (27×-1, 5×-2), 0 resolved.

## D45 — PO line-create guard for terminal POs (2026-06-13)
Added request-interception guard `polncreateg1` blocking `po_lines:create` when the parent PO is
`completed`/`closed`. Closes the gap left by the update/destroy-only Line Immutability guard
(`f3dkb37te22`). Reads the parent FK from `{{$context.params.values.purchase_order}}` → covers both
create routes (see resolution).

**Why:** new lines could still be appended to a finalized PO. A guard is the server backstop.
Initial finding (live probe): the **association** route `purchase_orders.lines:create` (add-line
form) doesn't expose the source PO id to request-interception — `values.purchase_order`,
`purchaseOrderId`, `filterByTk`, `associatedIndex`, `sourceId` all empty (FK injected after the
guard) — so a query-the-parent guard couldn't see it on that route.

**Resolution (user, 2026-06-13):** rather than relying on a frontend form-hide, set the add-line
form Submit button's **assign-field-values** to inject `purchase_order = {{ ctx.popup.record.id }}`
(button `8373f6c1297`, form `fd22f7bcaed`). That puts the parent PO id into the submitted `values`,
so the same guard query resolves on the association route too. Verified server-side (association
replay with the FK in values → block on a completed PO). Form-hide on terminal POs is now optional
UX, not the control.

**How to apply:** create-interception can only read the FK from `{{$context.params.values.<fk>}}`.
To guard a sub-table/association create by parent status, add the parent FK to the form action's
assign-field-values (`{{ ctx.popup.record.id }}`) so it lands in the body. Keep the guard query
`failOnEmpty:false` + condition `rejectOnFalse:false` so a missing FK fails open (no false block).
See auto-memory `feedback_request_interception_assoc_create_no_source`.

**Affects:** PO line immutability (MVP9d). No flow-logic change to existing workflows.
**Status:** effective + **fully verified 2026-06-13** — flow-nodes test + live direct-create probe + live association replay (completed→block, draft→allow); **user confirmed the real add-line form blocks on a terminal PO and allows on a draft PO** (`{{ ctx.popup.record.id }}` resolves). Fixtures cleaned up.

## D46 — PO rework: Issue-gated lifecycle, Send/budget-zones retired, print gated, PR-copied fields locked (2026-06-14)

Reworked the PO process. **New lifecycle:** `draft → issued → (partially_received) → received →
completed`; **close from `{draft, issued, partially_received}`** (a fully `received` PO can no longer
be closed — it completes). New status value **`issued`** (the user rejected `printed`) + stamp
`issued_at`. **Supersedes** the `draft → sent` Send step and its budget-overrun zones (MVP9b).

**Why / what changed:**
- The PO already copies supplier / price / currency / fx-rate / total from the approved PR
  (Generate-PO). **Procurement may no longer edit those** — removed `supplier`, `total`, `currency`,
  `fx_rate_to_usd` (plus the auto-added `issued_at` stamp) from procurement's `purchase_orders`
  **update** field whitelist (D38 ACL-whitelist enforcement; the user separately sets them `readPretty`
  on the form). Procurement still edits lines, `delivery_address`, `supplier_note`, `internal_notes`.
- **Send is gone, sending happens outside the system.** The Send button was **repurposed** into an
  **"Issue PO"** button (same `RecordTriggerWorkflowActionModel` uid `slybgc23q1i`, same linkage
  hide-unless-`draft`+Procurement) rebound from `send_po` to the new **`issue_po`** custom-action
  workflow. `send_po` (and its budget zones 1/2/3) **disabled** — budget-overrun checking is retired.
- **"Issue PO" is the completeness gate.** `issue_po` (custom-action, sync) guards: `status==draft`
  AND `supplierId`/`deliveryAddressId`/`currency` not null AND `total>0` AND ≥1 line
  (math.js `count({{$context.data.lines}})`); pass → `status=issued`, `issued_at=now`; fail → reject +
  message (mirrors Send/Complete inline-guard shape). The **Print** button (`templatePrint`,
  unchanged) got a linkage rule **hiding it until `status ∈ {issued, partially_received, received,
  completed}`**. Because `issued` is only reachable through the Issue guard, "you can't print an
  incomplete PO" is a **hard** guarantee achieved via the status gate.
- **Why not gate/advance on print directly:** the spike (see auto-memory
  `feedback_noncrud_action_workflow_triggers`) proved `templatePrint` is **not** workflow-triggerable —
  post-action fires only on create/update; global request-interception is CRUD-only. So a status-
  advancing custom-action button is the mechanism. Also re-confirmed: template-print **streams the PDF
  to the browser only** (no save-to-record/attach), so the "auto-attach PDF to the PO" idea was dropped
  — procurement downloads + emails (and may manually attach).
- **Receiving/close rewired** (same-key revisions): Receive Guard `mhfp4d15uee`
  (`368072131870720`→`369914942128128`→**`369970105614336`**) adds `issued` to the receivable set;
  Close PO `f8gpu17s6hq` (`368791950131200`→**`369914944225280`**) and Close Guard `b6brl8r9c58`
  (`368982201729024`→`369914946322432`→**`369970388729856`**) closeable set →
  `{draft, issued, partially_received}`. Receiving recompute `ork27v016yo` unchanged (sets header from
  quantities). Complete path unchanged. **Message fix (2nd revision each):** the Receive Guard and
  Close Guard rejection messages still said "sent"/"sent, confirmed" — corrected to "issued"
  wording. (Node edits 400 with "Nodes in executed workflow could not be reconfigured" — must
  revision to a fresh unexecuted version, edit while disabled, then enable.)

**How applied:** new workflow `issue_po` (id `369914017284096`, 8 nodes, mirrors Complete's
guard/count/reject/update shape; `count` via math.js, scalar/null checks via basic — D34 engine split).
Status enum gained `issued` (geekblue) after `draft`; `sent`/`confirmed` kept inert for history.

**Build notes (reusable):** generic `flow_nodes:create` does NOT auto-maintain `downstreamId` — set it
explicitly on sequential (non-branch-head) nodes; branch heads use `upstreamId`+`branchIndex`. Patching
an **already-registered** flowModel (the Send button → Issue PO; the Print linkage) via raw
`flowModels:update` is fine (the no-render caveat is only for raw *create*).

**Affects:** MVP9b (Send/zones retired), MVP9c (receiving from `issued`), MVP9d (close set), MVP9e
(print gated). No PR-side impact.
**Status:** **built + user-verified end-to-end 2026-06-14.** Logic validated via `flow-nodes test` +
config readbacks; the user then confirmed the full checklist live: Issue button renders/clicks
(incomplete→rejected with message, complete→`issued`+`issued_at`), Print appears only once issued,
procurement ACL blocks editing supplier/total/currency/fx-rate (lines/address/notes still editable),
receiving from `issued` works, and close from `{draft, issued, partially_received}` (received→blocked).
E2E also surfaced two stale "sent" rejection messages (Receive Guard + Close Guard) — corrected (see
revision note above). The user set the 4 PR-copied fields `readPretty` on the PO form.

## D47 — PO line pricing + per-line budget hard-block in PR currency (2026-06-14)

Re-introduced line-level pricing on the PO (partly **reverses D27**, which had dropped line pricing)
and a **per-line budget hard-block** that prevents the sum of PO lines from exceeding the **approved PR
amount, in the PR's own currency** (partly **reverses D46**, which retired budget checking). Enforcement
is **per line at create/update** (not at the Issue gate) so the invariant `Σ(line_total) ≤
PR.quoted_total` holds continuously and **no line-freeze is needed** — lines stay editable for
corrections; only an edit that actually breaches the ceiling is blocked.

**Why per-line (not Issue-gate + freeze):** a check only at Issue would let lines be added after issuing
and an over-budget PO printed, forcing a line-freeze after issue — which makes legitimate corrections
(wrong description, small price fix) impossible without revert-to-draft churn. Per-line enforcement keeps
the PO correctable. The cost — "printed == final snapshot" is given up — is handled with a
**`needs_reprint`** flag instead of locking.

**Currency is same-by-construction:** PO `currency`/`fx_rate_to_usd` are PR-copied and ACL-locked (D46),
so `PO.currency == PR.quoted_currency` always. The check is a **pure same-currency numeric compare**
(`Σ(line_total)` vs `PR.quoted_total`) — **no USD/FX**. Ceiling is `quoted_total` (PR amount in its own
currency), NOT `quoted_total_usd`. Verified live: SRD 10000 PR blocks at "10400 SRD over 10000 SRD".

**Data model:**
- `po_lines.unit_price` (double, in PO currency; auto-added to procurement create/update whitelist).
- `po_lines.line_total` (formula.js `ROUND({{quantity_ordered}} * {{unit_price}}, 2)`, double) — a
  same-record formula, so it computes and **persists to a real column** (confirmed aggregatable).
- `purchase_orders.lines_total` (double, **new** — sum of lines; workflow-maintained, read-only). The
  existing `total` (titled "Invoice Total") is **left untouched** — invoiced vs ordered-from-lines are
  intentionally distinct. `lines_total` removed from procurement's PO create/update whitelist.
- `purchase_orders.needs_reprint` (boolean, default false; workflow-maintained, removed from procurement
  create/update whitelist).

**Workflows (all new unless noted):**
- **Recompute A** `5ukanitoy74` (collection, sync, mode 3 = create+update, `changed:[quantity_ordered,
  unit_price]`) and **Recompute B** `pnvp0dtitum` (collection, sync, mode 4 = delete). Two workflows
  because the collection-trigger `mode` only accepts `[1,2,4,3]` — no triple combo. Each: query PO →
  aggregate `sum(line_total)` for the PO → write `lines_total`; if PO `status != draft` → set
  `needs_reprint=true`. Keyed off `purchaseOrderId` scalar (delete-safe; appends unreliable on delete).
- **Budget create guard** `8u81nd3vxhc` (request-interception, `po_lines:create`, sync, global): gate on
  price+qty present → query PO+PR → `aggregate sum(line_total)` existing → `N(sum)+qty*price` (formula.js
  `N()` coalesces the empty-set null to 0 — the first-line case) → if `> quoted_total` reject with a
  dynamic PR-currency message + `end(-1)`.
- **Budget update guard** `c9c14tyn876` (request-interception, `po_lines:update`, sync, global): **skip
  unless `quantity_ordered` or `unit_price` is in the payload** (so `received_quantity`/receiving writes
  pass straight through) → query line+PO+PR → `aggregate sum(line_total)` over **other** lines
  (`id != filterByTk`) → coalesce effective qty/price via `IF(ISBLANK({{values.x}}), stored, {{values.x}})`
  (handles partial updates) → `N(sum)+eff_qty*eff_price` → reject if over.
- **`issue_po`** revised (same-key revision `370019772465152`, old `369914017284096` retired): kept all
  completeness checks; **added "every line priced"** — `aggregate count(unit_price>0)` must equal
  `count(lines)`, else reject; and `issue_update` now also sets `needs_reprint=false`. No budget check in
  the gate (per-line guards already guarantee the ceiling).

**Reprint affordance:** post-issue line edits set `needs_reprint=true`; cleared via a **"Mark reprinted"**
button (manual ack — `templatePrint` is non-CRUD/unhookable, see
`feedback_noncrud_action_workflow_triggers`, so it can't auto-clear on print). *(UI surfaces + print
template price columns: see Status.)*

**Build notes (reusable):**
- Collection-trigger `mode` rejects combined create+update+delete (7) — only `[1,2,4,3]`; split delete
  into its own workflow.
- `ISBLANK("")` is **false** in this formula.js (empty string ≠ blank), but `ISBLANK(null)` is true and
  `N(null)=0`; use `N()` to coalesce a null aggregate sum, and `IF(ISBLANK(...))` to coalesce a possibly-
  absent `$context.params.values.<field>` to its stored value.
- `response-message` **supports variable templates** (`{{$jobsMapByNodeKey...}}`, nested assoc paths) —
  used to echo the over-budget amount + PR currency.
- Two request-interception workflows **stack** on the same `resource:action` (terminal guard + budget
  guard both fire on `po_lines:create`; first to `end(-1)` wins) — verified live.
- NocoBase **auto-adds new fields to existing role field-whitelists** on field create; scrub
  workflow-managed fields (`lines_total`, `needs_reprint`) out of procurement's PO create/update lists.

**Affects:** MVP9a (PO line pricing back), MVP9b (budget block returns, per-line + PR currency, replaces
the retired zones), MVP9e (print template needs price columns), any future Payment MVP.
**Status:** **core built + verified live via CLI (root) 2026-06-14** — formula compute, recompute A/B
(create/update/delete), create-guard block+allow incl. first-line null coalesce, update-guard
block+allow incl. partial-update coalesce + exclude-self, `received_quantity` skips the guard while
receiving advances status, `needs_reprint` flips on post-issue edit, interception stacking. **Pending
user UI walkthrough:** the `issue_po` all-priced gate (custom-action can't be driven headless), the
`needs_reprint` indicator + "Mark reprinted" button placement, and adding `unit_price`/`line_total`/
`lines_total` columns to the print template.

**Update 2026-06-14 (later same day) — reprint feature fully removed.** After UI testing, the reprint
mechanism kept mis-refreshing and the user dropped it entirely. Sequence of facts learned + actions:
- A plain `updateRecord` button + `refreshTargetBlocks` eventflow does **not** refresh its host block
  (no `afterSuccess` cycle); only `RecordTriggerWorkflowActionModel` refreshes — see
  `feedback_updaterecord_no_block_refresh`. The fix attempt (trigger-workflow button bound to a tiny
  "clear flag" workflow) worked mechanically but the user chose to remove the whole feature.
- **Removed:** banner + "Mark reprinted" button (UI); clear-flag workflow **destroyed**; `needs_reprint`
  field **dropped** (ACL auto-scrubbed). Recompute A/B **revised** to drop their condition+flag nodes →
  now `lines_total`-only (`5ukanitoy74` v`370047322750976`, `pnvp0dtitum` v`370047503106048`).
  `issue_po` **revised** to v`370047775735808` to drop the `needs_reprint=false` write (all-priced check
  retained). Swept all current workflows: no node references `needs_reprint`.
- **Print template** trimmed to a single **Order Total** (`lines_total`); Invoice Total + Invoice Total
  (USD) rows removed; line columns right-aligned except Description. Live print binding reads a **hashed**
  filename in `printingTemplates`, not the friendly name — see `feedback_template_print_hashed_filename`.
- **Unchanged / still active:** the per-line budget guards (`8u81nd3vxhc` create, `c9c14tyn876` update)
  and the `lines_total` recompute — i.e. the budget hard-block (the core of D47) stands. Only the
  reprint-snapshot affordance is gone; post-issue line edits are simply allowed with no flag.

## D48 — USD auto-sets fx_rate_to_usd = 1 and hides the rate field on all PR forms (2026-06-21)

When `quoted_currency == 'USD'`, `fx_rate_to_usd` must be `1` (the USD formula divides by it —
`quoted_total / fx_rate_to_usd`, rate is local-per-USD per `feedback_currency_rate_convention`). Users
previously typed the `1` by hand. Now the FX-rate field is **auto-set to 1 and hidden** on USD, and
**shown + required** on SRD/EUR — applied as **form linkage rules** (not a workflow), on all three
surfaces where currency is set: the **create form** (`e76c40c8c79`, grid `5c325101ecc`), the
**Procurement ProcessForm** (grid `x30gs70f47k`) and the **Dept Owner ProcessForm** (grid
`pqflpr2l3u4`). The PO side needs nothing — PO currency/fx is PR-copied and ACL-locked (D46), so
currency is only ever set on these three PR forms.

**Why linkage, not a server workflow:** currency can only be set on these three forms, so per-form
linkage covers every path with no extra workflow to version. Confirmed by the user that linkage on
approval ProcessForms persists across workflow revisions (a revision **copies** the forms with new
uids, carrying their `eventSettings.linkageRules` along) — so the rules survive future PR-Approval
revisions. (My initial worry that revisions wipe approval-form linkage was wrong.)

**How built (each grid, native `stepParams.eventSettings.linkageRules.value`, raw `flowModels` update —
NOT the `set-field-linkage-rules` CLI, which uses a different `when`/`then` shape and would force a
translation of the existing rules):**
- Rule "USD FX rate = 1 (hide)" — when `quoted_currency $eq USD`: `linkageAssignField fx_rate_to_usd=1`
  + `linkageSetFieldProps state=hiddenReservedValue` + `state=notRequired`.
- Rule "Non-USD FX rate (show + require)" — when `quoted_currency $or {SRD,EUR}`:
  `linkageSetFieldProps state=visible` + `state=required`.
- The two approval forms already had a user-built "USD FX" assign-1 rule; those were **extended in
  place** (hide + notRequired actions added) rather than duplicated. The create form had neither rule.

**Two gotchas hit + fixed:**
1. `linkageSetFieldProps.fields` references the field's **ItemModel uid** (create `b199fc86a08`, proc
   `evq2pdr51us`, dept `xgar21mj94z`), not the field name; `linkageAssignField.targetPath` uses the
   field **name** (`fx_rate_to_usd`).
2. **`hiddenReservedValue`** (not plain `hidden`) is the hide state that still submits the value — so
   the hidden USD field's `1` persists on save.
3. **Assign `mode`**: `mode:"default"` writes the field's *initialValue* (only fills when empty) — so a
   value typed under SRD survived a switch to USD (the bug the user caught). **`mode:"assign"`** writes
   `{value}` and overwrites unconditionally. All three USD assign items use `mode:"assign"`. See
   auto-memory `feedback_linkage_assign_field_mode`.

**New behaviour:** `fx_rate_to_usd` is now **required** when SRD/EUR is selected (was optional). Intended
correctness win, user-accepted.

**Reversibility:** original linkage JSON for all three grids backed up to
`backups/linkage-{create,proc,dept}-*-20260621.json`; rollback = re-write those `linkageRules`.

**Affects:** MVP3 (currency/FX entry), MVP1/MVP4 (the dept + procurement approval forms). No workflow,
collection, or ACL change. **Status:** built + **user-verified in the UI 2026-06-21** (USD hides + sets
1; SRD→10→switch-to-USD now correctly overwrites to 1; SRD/EUR show + require).

## D49 — Projects + project-budget drawdown (2026-06-23, partial build) — REVERSES D5
Reverses D5's v1 deferral (this is v2). A new **`projects`** collection holds a **USD budget envelope**
approved via its own ladder; PRs linked to an approved project draw against it, **skip director + board**
(Procurement is final) but **still require dept-owner approval**, and are **hard-blocked** from collectively
exceeding `budget_usd`.

**Decisions locked (brainstorm 2026-06-21):** (1) USD-only budget — single `budget_usd`, multi-currency
deferred. (2) Over-budget = **hard block at submit** (request-interception, D47 pattern) with a dynamic
remaining-budget message; drawdown counts **all child PRs except rejected/cancelled** (reserve-on-submit,
≤ budget allowed). (3) Drawdown PR ladder = dept-owner still applies; director + board skipped. (4) Project
Approval is a **separate** workflow reusing the PR-ladder spine + D32 board threshold, **dropping** the D36
custom-approver branch and the D37 is_regular/$300 nuance — director always reviews an envelope. (5) Close
is **manual** (a Close Project button); no auto-close on exhaustion. (6) The envelope passes through the
Procurement stage (full mirror). (7) `project_number` = `PRJ-YY-NNNN` (D31 pattern).

**Built + CLI-verified this session (014.1, 014.3):** `projects` collection, `purchase_requests.project`
m2o (FK `projectId`, nullable) + reverse o2m, `committed_usd` recompute workflows A `j2fp3wa4o1k` / B
`0mckvnf319y`, PR budget create guard `lylobzvlh5p` + update guard `ebq41ibq60r` (all enabled). **Built but
DISABLED (014.2a):** Project Approval workflow `hzykothf9cx` (22-node logic; needs surfaces). **Pending:**
014.2b/c approval surfaces + comment models + ACL; 014.4 PR-Approval drawdown skip-branch (insert a
"Project drawdown?" condition on `ec2h8cqal32` br=2 before `bizoy1sj87j`: `project.id != null` AND
`project.status == approved` → approved, else existing director logic) + add `project` to PR-Approval
trigger appends; 014.5 UI (Projects page/forms/Close, PR `project` picker) + PR/projects ACL whitelists;
014.6 user E2E (A1–F2).

**Doc-lag noted:** live active PR Approval = `370060903907328` (not the doc-recorded `369536223739904`);
its `executed` counter is 0 only because the user pruned execution history — the version HAS run, so 014.4
is a same-key revision, not an in-place edit.

**Affects:** **MVP014** (new). Downstream: any future PR-routing or budget MVP must account for the project
drawdown branch on PR Approval (`cv237r8h7k9`) and the two global PR budget guards. Supersedes **D5**.

**Update 2026-06-27 (014.4 + 014.2b/c built + CLI-verified; pending user E2E).**
- **014.4 — PR-Approval drawdown branch.** Same-key revision of `cv237r8h7k9` (live active was
  `371882305585152`, NOT the doc-recorded `371864957943808` — user re-revised after MVP015) →
  **`372368060514304`** (enabled+current; predecessor `371882305585152` disabled = rollback; 34→**37
  nodes**). Added `project` to trigger appends. Inserted condition **`492iwdlv0mr`** "Project drawdown?"
  as the new **br=2 head of `ec2h8cqal32`** (Procurement Approval): basic AND `notEqual(project.id,null)`
  + `equal(project.status,"approved")` — true (br=1) → update **`48myq8dpqza`** (status=approved,
  approved_at=now) → notification **`kykl9gnqj9h`** (requester only, D50 — Procurement is final so no
  proc-head ping); false (br=0) → the existing `bizoy1sj87j` director/board logic (moved intact).
  `flow-nodes test` passed all 3 scenarios (approved project→true, non-approved→false, no project→false).
  Approval surfaces regenerated on the revision but are structurally identical to the live source (no
  comment models / no inline `commentFormUid` on either — comment forms are simply off, so no 403).
- **014.2b/c — Project Approval surfaces + ACL + ENABLED.** `hzykothf9cx` (`371693220069376`) now
  **enabled+current**. Applied approval blueprints to the 4 nodes: Dept `tkw661dvfjq`→`5kjtfn7jwml`,
  Procurement `ik1ixug5rrs`→`u3het26bp1s`, Director `su6sbibmoky`→`mr8tjeafu5x` (each approve/reject/
  return, actions `[2,-1,1]`); Board `vwuxv7zih9f`→`1udja3xnsex` (approve/reject `[2,-1]` + editable
  `approval_document` in the ProcessForm). Each approver surface = `approvalInformation` (6 scalar
  display fields: project_number/title/description/budget_usd/status/committed_usd) + `approvalApprover`
  (actions; board adds the upload). **No `commentFormUid` configured** (mirrors live PR forms → no 403).
  Built the **initiator surface** (workflow `approvalUid` `nqqhwey5int`: ApplyFormModel w/ title+
  description+budget_usd + auto `approvalSubmit`) and set **`centralized:true`** so real users launch a
  project approval from the approval to-do center (the minimal E2E-create path until 014.5's Projects
  page; reconcile centralized vs page-form there). **ACL** (`apply-data-permissions`, scope all):
  **operations** create[title,description,budget_usd]/view[22]/update[title,description,budget_usd,
  rejection_*]; **procurement** view[22]/update[rejection_*,approval_document]; **director** view[22]/
  update[rejection_*]. Procurement already had `attachments` create (D32) → board upload covered.
- **Blueprint gotcha:** the documented `apply-approval-blueprint` baseline is wrong on two keys — each
  block needs a **`key`** and the resource init field is **`resource`** (not `resourceInit`).
- **Deferred to 014.5/014.6:** Projects page/table/detail + Close Project button+workflow; PR-form
  `project` picker + PR `project` create/update field whitelists; make board `approval_document`
  **required**; user E2E A1–F2 (real users: Alice/Oliver create+submit, Oliver/Pat/Dana approve).

---

## D50 — Notify on PR approval (requester always; head of procurement only on the director path)

**Decision:** When a PR reaches `approved`, send an in-app notification `PR-26-NNNN "Title" has been
approved.` to the **original requester** (`createdBy`) on every path. Additionally notify the **head of
procurement** (Pat, via the root query node `yrl9kgkrb3x`) **only on the Director-approved path** — NOT
when Procurement itself is the final approver (regular < $300) and NOT on the Board-approved path.

**Why:** Previously nothing notified anyone on approval (user feedback gap). Procurement should not be
pinged when they are the final approver (they already know) nor for board sign-off (the board stage is the
requester's concern; procurement already passed it through their own review stage).

**How to apply:** Three in-app notification nodes on PR Approval `cv237r8h7k9`, one appended as the
downstream of each terminal `status=approved` node — `jy1365pvsce` (requester only), `kj1zcmujub8`
(requester + procurement), `8gqeq6djrfj` (requester only). Channel `approval-todo-in-app-message` (only
configured channel; email deferred — needs SMTP). Requester = `{{$context.data.createdById}}`; head of
procurement = `{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}`. Required a same-key revision (workflow
has executed). As-built version + node keys in [chunks/015-pr-approved-notifications.md](chunks/015-pr-approved-notifications.md)
and `project_current_state.md`.

**Affects:** **MVP015** (new). Downstream: any future change to PR-Approval terminal `approved` nodes, or a
14.4 drawdown branch that adds a fourth approved path, must add the matching notification.

**Status:** effective (user walkthrough A1–A5 passed 2026-06-24).

## D51 — Duplicate a finalized PR (Duplicate-to-form, approved/rejected only) (2026-06-25)

**Decision:** A PR in a **final state** (`approved` or `rejected`) can be duplicated into a new PR via a
**Duplicate** record action on the PR detail popup `2b367dbd157`, configured in **"Duplicate to form"** mode
(the built-in `@nocobase/plugin-action-duplicate`). It opens a pre-filled create form; the user edits, then
submits to create a brand-new PR. A linkage rule hides the button in every non-final state.

**Why:** Two recurring needs surfaced — (1) **repetitive purchases** (re-order the same thing without
re-typing), and (2) **re-applying a rejected PR after changes** (a rejected PR is immutable/terminal, so the
practical path is to clone it, fix the issue, and resubmit). Restricting to approved/rejected keeps the button
out of in-flight PRs where a duplicate would just create confusion. "Duplicate to form" (not "Direct
duplicate") is deliberate: the new PR must be reviewed/edited before it exists, never created silently with a
stale copy of the original's values.

**How it behaves:** the duplicate action auto-excludes primary/foreign keys, unique fields (`pr_number`),
sequence fields, and timestamp/user-tracking fields, so the clone gets a fresh `pr_number`, default `status`,
and new audit stamps. m2o pickers (`supplier`, `department`, `custom_approver`, `project`) are copied as
**references** (link to the same targets); the PR collection has no sub-form/sub-table fields, so nothing is
deep-copied. The new PR then enters the normal PR Approval flow from the top like any fresh submission.

**Scope:** PR only. POs are not hand-duplicated (they're workflow-generated from approved PRs), so no
equivalent action on the PO block.

**Affects:** none structurally (UI-only, no collection/field/workflow/ACL change). Forward note: if a future
MVP adds new unique or system-managed PR fields, confirm the duplicate template still excludes them; if the PR
gains sub-table fields, decide per-field whether they should deep-copy or reference.

**Status:** effective (user-built in the UI; doc-only capture). Button uid not captured — no CLI read/describe
path for nested flowModels actions (`use`/`parentId` not filterable); record it next time the popup is edited.

## D52 — Budget-safe PO line-item import: cap moved to the Issue gate + import hidden on non-draft (2026-06-27)

**Decision:** Procurement can bulk-**import** PO line items (for large orders). Because import bypasses **all**
`po_lines` request-interception guards — the D47 per-line budget block **and** the D45/D46 terminal guards —
two complementary controls keep it safe, **supplementing D47 (not reversing it)**:
- **A. Budget check at the Issue gate.** `issue_po` now aggregates `Σ(line_total)` for the PO and rejects if
  it exceeds `purchase_request.quoted_total` (same currency; PO currency is PR-locked, D46/D47). Issue is the
  chokepoint every PO crosses to become printable (Print is gated on `status ∈ {issued,…}`, D46), so an
  over-budget PO can sit in `draft` but can't be issued or printed — regardless of how the lines were created.
- **B. Import hidden unless `draft` + Procurement.** A linkage rule on the import button (user-built in the UI,
  on the PO popup Line Items sub-table) hides it on any non-draft PO and for non-Procurement roles, so lines
  can't be added behind an already-issued PO.

**Why not keep enforcement purely per-line (D47):** D47 chose per-line enforcement *over* an Issue-gate check
specifically to avoid freezing lines after issue — but that assumed **every** line-creation path passes through
request-interception. Import is a new path that escapes it (pre-action interception never fires on import,
verified). So the Issue gate is the net for imported lines; the D47 per-line guards stay for manual entry.

**How applied (Part A, built + user-verified live 2026-06-27):** same-key revision of `issue_po`
`370047775735808` → **`372351365087232`** (enabled+current; predecessor disabled = rollback). Added
`purchase_request` to trigger appends; inserted 4 nodes on the all-priced (`x01errm96yk` br=1) branch before
`issue_update`: `kkk684uupcd` (aggregate sum `line_total` where `purchase_order.id == {{$context.data.id}}`) →
`hksnw304p3b` (math.js `{{$jobsMapByNodeKey.kkk684uupcd}} > {{$context.data.purchase_request.quoted_total}}`)
→ br=1 over: `0udjhd90ljj` (response-message, echoes total + ceiling + currency) → `3ba6bu5e6un` (end −1);
br=0 within (≤, empty) → converges to `issue_update`. Strict `>`, so spending exactly the PR amount is allowed.
Part B import action + hide rule are **user-built in the UI** (import template/field-map/trigger-workflow toggle
are UI-only — not CLI-authorable). The import attaches lines to the correct PO (no orphans); Part A's live
aggregate therefore counts imported lines, so the cap applies to them.

**Import Pro enabled** (`@nocobase/plugin-action-import-pro`) with per-row "trigger workflow" on — fires
collection events (not request-interception), used only for the `lines_total` recompute/observability, never
for the cap.

**KNOWN ISSUE — PARKED (not critical; the cap is unaffected).** With per-row trigger on, importing a line
fires the `po_lines` create collection event, but **Recompute A (`5ukanitoy74`, sync) sees
`$context.data.purchaseOrderId = null`** — the event fires before the association FK lands on the snapshot
(saved row is correct; no orphan). So `lines_total` isn't recomputed on import (it stays stale until a manual
line touch). **Not a safety gap:** the Issue-gate cap aggregates lines *live* and the imported lines carry the
FK, so the budget block still works on imported POs. **Fix when picked up:** re-query the line by its own
`{{$context.data.id}}` (appends `purchase_order`) for the FK **and** flip Recompute A to async (the FK only
lands post-commit, so a sync re-query still returns null). Both changes needed. See auto-memory
`feedback_collection_event_assoc_fk_null`.

**Affects:** MVP9a/D47 (per-line guards retained; cap now *also* at Issue), MVP9e (print still gated on
`issued`). No PR-side impact. Forward note: any future non-interception line-creation path (another import
surface, an API bulk write) is covered by the Issue gate but **not** by the per-line guards.

**Status:** Part A built + user-verified live 2026-06-27 (over-budget Issue rejected, within-budget issues;
import button + hide rule work). Recompute-on-import fix parked (above).

## D53 — Project-budget cap enforced in the PR Approval workflow, not the request-interception guards (2026-06-28)

**Amends:** D49 (project budget hard-block). **Same class of finding as D52 + D45-import:** a
request-interception guard is bypassed by a non-CRUD write path, so enforcement moves into the workflow.

**Problem:** D49's project-budget block was built as `request-interception` on `purchase_requests:create`
+ `:update` (guards `lylobzvlh5p` / `ebq41ibq60r`). But Procurement enters the quote on the **approval
ProcessForm**, and the approval plugin's submit writes the record through its own path that **bypasses
request-interception entirely** (the update guard logged **0 executions** on the real path — confirmed).
So the cap was never enforced where the quote is actually set; **PR-26-0055** (a $110k quote against a
$10k project) was approved. This is the same bypass family as D52 (import escapes po_lines guards) and the
documented `feedback_request_interception_scope` (workflow-internal / plugin writes skip interception).

**Two bugs fixed together:**
- **Blank-quote crash (create+update guards).** The guards' calc node did
  `... + {{values.quoted_total}} / {{values.fx_rate_to_usd}}`; a **blank `quoted_total` renders as an empty
  string** in this `formula.js` engine → `N(0) +  / 1` SyntaxError → the sync guard *threw* → generic
  "workflow or action failed, please contact administrator" whenever a project PR was created with no quote
  (the normal case — Procurement fills the quote later). Fixed by `N()`-wrapping every `$context.params.values.*`
  param (blank→0, no parse break) + a `IF(N(fx)==0,1,N(fx))` divide-by-zero guard; update guard's
  `IF(ISBLANK(...))` effective-value nodes (which returned a wrong `false` on a blank param) rewritten the same
  way. **Engine note:** evals JS-style — `=` is assignment, use `==`; never write a raw `{{param}}/{{param}}`
  (wrap in `N()`); `$jobsMapByNodeKey` results render as real `null` (safe). See auto-memory
  `feedback_formula_blank_param_empty_string`. Create `lylobzvlh5p` → ver `372589928710144`; update
  `ebq41ibq60r` → ver `372590052442112` (both same-key revisions, predecessors disabled = rollback).
- **Enforcement hole (the cap itself).** Added a **server-side backstop in PR Approval `cv237r8h7k9`**: same-key
  revision `372368060514304` → **`372600911495168`** (enabled+current; predecessor disabled; **37→41 nodes**).
  On the drawdown true-branch (`492iwdlv0mr` br=1), the old approve `48myq8dpqza`→notify `kykl9gnqj9h` was
  replaced by: aggregate `wt7bh1uh2gn` (Σ `quoted_total_usd` of the project's child PRs, status notIn
  rejected/cancelled — **includes this PR**, whose formula USD is saved by approve-time) → condition
  `8ra9iw4f61z` (math.js `Σ > project.budget_usd`) → **br=1 over** = update `3o2q8urkutu` status=rejected +
  dynamic over-budget `rejection_comment` → notify `xtr5t4xy1gq`; **br=0 within (≤ budget)** = recreated approve
  `47fd05ite4i` → notify `fvbrc41tdl2`. Strict `>` so exactly == budget is allowed (matches D49 C3).

**Behavior decision (user):** an over-budget project PR is **auto-rejected** at the Procurement-approve step
(not returned/info_requested, not routed to Director). The **UI guardrail** (show remaining budget on the
Procurement form + hide/disable Approve when the entered quote overruns) is the **user's to build** and is a
UX layer only — RunJS is frontend-only and bypassable, so the workflow backstop is the real enforcement.

**Why move enforcement and keep the interception guards too:** the create guard still does real work (blocks
linking to a non-approved/closed project, and *does* fire on create); both interception guards stay enabled as
defense-in-depth for any **direct-API** PR edit. They simply can't see the approval-form path, which the
backstop now covers.

**Affects:** MVP014 (D49 enforcement model). Forward note: the project budget is now enforced at PR-approval
time; the request-interception guards are a secondary net for direct writes, not the primary control.

**Status:** all three changes built + CLI-verified (expressions via `flow-nodes test`; structure via readback,
41 nodes, all branches intact). **Pending user E2E:** over-budget project PR → auto-rejected; within-budget →
approved. User deleting PR-26-0055.

**Amendment (2026-06-28, same day) — commit on approval, not on submit.** User asked why budget commits at
quote-entry (a pending PR with a quote was consuming budget) and proposed committing only on approval — which
also removes a UI re-edit double-count. Adopted. **`committed_usd` now counts only `status == approved`** child
PRs (was all non-rejected/cancelled). The cap is still enforced because the **backstop runs at approval** and
counts already-approved siblings + this PR; the second of two in-flight PRs is caught when it's approved (the
first is then approved and counted). Trade vs reserve-on-submit: a pending PR no longer reserves budget, so an
over-budget PR is flagged at its approval rather than at quote entry — fine for sequential approvals.
**Four coordinated same-key revisions** (all enabled+current; predecessors disabled = rollback):
- Recompute A `j2fp3wa4o1k` → `372610306736128`: agg `stf49k2lx11` filter `status == approved`.
- Recompute B (delete) `0mckvnf319y` → `372610338193408`: agg `hsshy332wo1` filter `status == approved`.
- Backstop (PR Approval `cv237r8h7k9`) `372600911495168` → `372610390622208`: agg `wt7bh1uh2gn` filter
  `project.id == X AND (status == approved OR id == thisPR)` — counts approved siblings **plus** this PR, and
  reads this PR's live quote without a `$context.data` timing dependency.
- Update-guard `ebq41ibq60r` `372590052442112` → `372610438856704`: agg `i4uayouh3va` filter `status == approved`
  excl self (`dj27n84thia` then adds this PR's effective quote).

Net: `remaining_usd = budget − Σ(approved)`, and a pending PR is never in it → **UI rule is simply
`entered_quote_usd > remaining_usd`** (no re-edit caveat). The create-guard `lylobzvlh5p` aggregate was left as
the broader filter (it only ever runs at create, where the PR has no quote, so its budget arm is moot — it still
enforces "project must be approved"). **Pending user E2E unchanged.**

---

## D54 — System roleMode set to only-use-union (2026-07-02)

**Decision:** `systemSettings.roleMode` is `only-use-union` — every user's effective permissions are always the union of all their assigned roles; there is no per-session single-role selection.

**Why:** Lets roles be composed as small additive building blocks (a user's access is always the sum of their roles, so grants never need to be duplicated across roles for a multi-role user to have them). Also prevents end users from accidentally switching their active role to one with less access and losing functionality.

**How to apply:** When reasoning about any role's restriction, a derived role's negation (a snippet, a strategy limit) has no effect if `member` or any other role the user holds already grants it — tighten the most-permissive role a user holds, not the derived one. See `role-acl-guidelines.md` §1 (written for `allow-use-union`; the union-always behavior it describes is now unconditional, not a switchable option).

**Affects:** none yet (system-wide setting, not chunk-specific)
**Status:** active

**Retrofit note (2026-07-02):** discovered live during the `nb-project-suite` retrofit drift report — `role-acl-guidelines.md` and `project_current_state.md` both still said `allow-use-union` (dated 2026-06-11); this entry documents the change going forward. Dated today per the retrofit's rule for undocumented decisions found in `project_current_state.md`, not backdated to when the change actually happened (unknown).

---

## D55 — Fixed `director`'s `purchase_requests` ACL: scoped update, dropped stray create (2026-07-02)

**Decision:** `director`'s `update` action on `purchase_requests` is now scoped to `status == pending_director_approval` only (new reusable scope, `rolesResourcesScopes` id 11, key `vycg3aal69u`, name "PR — pending director approval"). `director`'s `create` action on `purchase_requests` (fields: `["signature"]`, no scope) was removed entirely.

**Why:** Found during the `nb-project-suite` retrofit's Step 6 ACL re-audit — `role-acl-guidelines.md` §6 said director's render-enabler update grant was "scoped to director/board stages" (matching the D38 render-enabler pattern), but live config had `scopeId: null` (unscoped — director could update those 5 fields, including `signature` and the rejection fields, on a PR at **any** status, not just its own approval stage). Confirmed as an oversight, not intentional, by the user. Separately, an undocumented `create` action existed on the same role/collection — also confirmed unintentional; the actual intent ("director can add a signature to an existing PR") is already covered by the `update` action's `signature` field, and D25 forbids approver-role PR creation.

Note: the existing scope id 10 ("PR — director stage") covers **two** statuses (`pending_director_approval`, `pending_board_approval`) and is correctly used by `finance`'s render-enabler grant (per D40, groundwork for a future finance/payment stage — board approval itself belongs to Procurement per D32, not director). Deliberately did **not** reuse scope 10 for director; created a narrower single-status scope instead, since director's own approval only ever happens at `pending_director_approval`.

**How to apply:** `director` on `purchase_requests` now has exactly 2 actions: `view` (37 fields, unscoped) and `update` (5 fields: `project`, `projectId`, `rejection_comment`, `rejection_reason_category`, `signature`; scoped to `pending_director_approval` via scope id 11). No `create` action. Verified live via readback (`roles data-source-resources get --appends actions`).

**Affects:** `role-acl-guidelines.md` §6 (corrected in the same commit); `tests/plan.yaml` (new director rules should assert this scoping).
**Status:** effective — written and readback-verified 2026-07-02.

---

## D56 — PO deletion locked down: no PO destroy, PO-line destroy only while draft (2026-07-02)

**Decision:** two changes, same principle (deletions minimal, for auditability — user's rule):
1. `procurement`'s `destroy` action on `purchase_orders` **removed entirely** (ACL). Procurement can no longer delete a PO at any status — a PO is closed (not-yet-received) or completed (fully received) instead, never deleted.
2. New request-interception workflow `Guard: PO Line Destroy — block once PO issued` (id `373256900640768`, key `v61hc3ou3pa`, enabled) blocks `destroy` on `po_lines` whenever the parent PO's status is anything other than `draft`. Procurement may still delete a mistaken line while the PO is draft, but not once issued.

**Why:** Found during the `nb-project-suite` retrofit's Step 6 ACL/workflow re-audit — procurement's ACL grant for `purchase_orders` `destroy` was unscoped (only the completed/closed immutability guard applied, leaving draft/issued/partially_received/received POs fully deletable), and the same was true one level down for `po_lines`. User confirmed both are unwanted: never delete a PO; a line may only be deleted pre-issue.

**How to apply:** `procurement` on `purchase_orders` now has exactly 4 actions (`trigger`, `view`, `create`, `update`) — no `destroy`. The new guard queries the line's parent PO by `filterByTk`, condition checks `purchase_order.status != "draft"` → reject with "Cannot delete a PO line once the PO has been issued." Existing `Guard: PO Line Immutability` (`f3dkb37te22`) is untouched and still separately governs `update` (stays editable outside `draft`, e.g. during receiving) plus its own `completed`/`closed` destroy lock — now redundant for destroy but harmless (first guard to reject wins).

**Affects:** `tests/plan.yaml` (new purchase_orders/po_lines destroy rules should assert this).
**Status:** effective — both parts written and readback-verified 2026-07-02 (ACL via `apply-data-permissions`; workflow: 4 nodes, query → condition → response-message → end, mirrors the sibling guard's shape).
