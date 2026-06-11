# Decisions — currently effective

Design, implementation, and workaround decisions that still apply to the current build. Superseded entries live in [decisions-archive.md](decisions-archive.md).

Scope: this is not just design. Implementation choices ("we used a workflow because formulas can't aggregate", "we deferred X to MVP9d", "pattern Y was rejected because of NocoBase limitation Z") belong here. The "why" matters more than the "what" — future-you reads these to understand constraints, not to discover features.

When adding new entries, list affected downstream MVPs by number so step 3 of the session workflow catches forward references.

---

## D1 — Procurement cannot cancel stalled PRs
Only the original submitter can cancel a PR. Simpler Guard C. **Affects:** MVP2.

## D2 — Procurement-originated PRs always go to director
No threshold check on this path. **Affects:** MVP6 (moot under D25 — kept for historical context).

## D5 — Projects + project-budget bypass removed from v1
No `projects` collection, no `charge_to` field, no Guards B/D, no project-budget routing. Every PR follows the same flow. Deferred to v2. **Affects:** all MVPs.

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
