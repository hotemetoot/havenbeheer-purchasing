# Havenbeheer Purchasing — Incremental Build Plan (v3)

**Status:** v3 supersedes v2 (and v1). All open questions and design discrepancies from v2 are now resolved — see §3 for the decision register. The build pivots away from the original "1 PR → many POs" design to a much simpler **1 PR → 1 PO** model, and the "projects with approved budgets" feature is removed from v1.

**How to use:** Take this file into a new chat session. Read it first, then continue with MVP1 verification.

---

## 0. Where we are right now

### What is already built and live in NocoBase

- **Collections** — `purchase_requests` only. Fields: `title`, `description`, `justification`, `submitter` (m2o users), `department` (m2o departments), `status` (single-select), `rejection_reason_category` (single-select), `rejection_comment` (textarea). Plus native `id`, `createdAt`, `updatedAt`, `createdBy`, `updatedBy`.
- **Departments** — Procurement, Director, Operations, Finance. Procurement and Director each have a linked role (`procurement`, `director`). All departments now have `main_approver` (m2o → users) and `secondary_approver` (m2o → users) fields for workflow routing. Operations: main_approver = Oliver (user 10). Procurement: main_approver = Pat (user 11).
- **Users** — `on_leave` (boolean, default false) field added. Each person sets this before going on leave; workflow checks it to route to secondary_approver instead.
- **Test users** — `alice.member` (id 9), `oliver.owner` (id 10), `pat.procurement` (id 11), `dana.director` (id 12). Default `member` role for all; Union role mode.
- **ACL** — wired in Phase 1.3 (member, dept owner, procurement, director scopes; field-level read-only for system fields).
- **Approval workflow** — single `approval`-typed workflow, key `p4n6dffjcgq`, active version ID `364960795000832` (enabled). 17 nodes:
  - Root update `1f6a1h52l9u` — sets status=pending_dept_approval, submitterId, departmentId
  - Query `yrl9kgkrb3x` (qProc) — fetches Procurement dept (ID 363554444476416) with `main_approver` appended
  - Query `b06ebhqags0` (qDept) — fetches submitter's main dept with `main_approver` and `secondary_approver` appended
  - Condition `5hed96jh1u7` — basic engine: true if `qDept.main_approver.id == applicant.id` (submitter IS main approver → skip dept stage)
    - br=1 (true / submitter IS main approver): Update `nkbguc8uo7z` sets status=pending_purchasing_review
    - br=0 (false): Approval#1 `cfg687cye3n` Dept Approval — assignees filter: `id $eq {{$jobsMapByNodeKey.b06ebhqags0.main_approver.id}}`
  - Approval#2 `ec2h8cqal32` Procurement — assignees filter: `id $eq {{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}`
  - Approval#3 `sxvxwl498xg` Director — assignees hardcoded `[12]` (Dana)
  - Each of the 3 approval nodes has 3 branch update children (approve/return/reject) — unchanged
- **Approval surfaces** — initiator `bp8yuyfsk3u` (taskCard `ne02s5dlk68`); Dept approver form approvalUid `rgcyt60s8pg` (taskCard `yyptfj0azru`); Procurement approvalUid `ylccjkdatwa` (taskCard `o4jc2ghrs4q`); Director approvalUid `8x5ktd74gwx` (taskCard `o1n99mp7sn7`).
- **Purchase Requests page** — `cuycec133qb`. Table with columns `title`, `submitter` (popup), `department` (popup), `status`, `createdAt`. Block actions Add New + Filter. Record actions View, Edit, Submit for Approval. Linkage rules: Edit hidden when status ∉ {draft, info_requested}; Submit hidden when status ≠ draft.

### MVP1 — verified and complete (as of 2026-05-17)

All four MVP1 scenarios verified:
- A. Happy path (Alice → Oliver → Pat → Dana → approved) ✓
- B. Dept-head edits while info_requested ✓
- C. Return from each approver → info_requested ✓
- D. Reject from any approver → rejected with reason fields ✓

Submit for Approval button works (wired as `RecordTriggerWorkflowActionModel`). No bridge workflow needed.

Routing redesign (dept owner → main_approver) verified 2026-05-17:
- Alice submits → Oliver (Operations main_approver) gets task ✓
- Oliver submits → dept stage skipped, Pat gets task directly ✓
- Pat submits → both dept + procurement skipped, Dana gets task ✓

### What is NOT yet built (next: MVP2)

MVP2 — Cancel by submitter. See §MVP2 below.

---

## 1. Guiding principles

1. **Smallest possible slice first.** Each MVP demoable end-to-end by a human.
2. **Native over custom.** Form-required, native approval nodes, native data-scopes, native owners. Custom JS and Before Action guards last, not first.
3. **One concern per MVP.** If it touches two concerns, split it.
4. **Stop and validate.** Each MVP ends with a manual test pass by the user before opening the next.
5. **Skip everything not strictly required.** Including fields. Adding fields later is cheap; removing them is not.

---

## 2. Skills used

- `nocobase-env-manage`, `nocobase-plugin-manage`, `nocobase-data-modeling`, `nocobase-acl-manage`, `nocobase-workflow-manage`, `nocobase-ui-builder`, `nocobase-data-analysis`, `nocobase-utils`. No `nocobase-dsl-reconciler`.

---

## 3. Decision register (resolved from v2 open items)

### Resolved this session

| # | Topic | Decision |
|---|---|---|
| D1 | Procurement cancel of stalled PRs | **No.** Only the original submitter can cancel. Simpler Guard C. |
| D2 | Procurement-originated PRs → director | **Always to director**, regardless of amount. No threshold check on this path. |
| D3 | Stale FX rate threshold | **Only warn when no rate exists at all.** Any FX rate ≤ today is acceptable. No age check in Guard E. |
| D4 | USD director threshold | **$1,500 USD.** Single row in `approval_limits` (applies_to = global). |
| D5 | Projects + project-budget bypass | **Removed from v1 scope.** No `projects` collection, no `charge_to` field, no `project` field, no Guards B/D, no project-budget routing. Every PR follows the same flow. Defer to v2. |
| D6 | Supplier `current_rating` | **Manually maintained** by procurement on the supplier record. No computation. |
| D7 | Supplier scoring scale | **1–5** (5 best). On `supplier_evaluations.score`. |
| D8 | New supplier onboarding workflow | **No.** Procurement creates suppliers directly; immediately usable. Permission gate (Guard #9) is sufficient. |
| D9 | PR → PO cardinality | **One PR → exactly one PO.** Simpler model than the original PO design's "1 PR → many POs". |
| D10 | PO generation trigger | **Procurement clicks "Generate PO" on the approved PR.** No auto-creation on approval. The PO opens in `draft` pre-filled from the PR (description, supplier, price, currency, etc.). |
| D11 | PO line items | **Keep `po_lines`.** Procurement may split the PR description into structured lines (with UoM, qty, unit price) when generating the PO. |
| D12 | PO budget-overrun zones | **Keep the original 110% tolerance + zone 1/2/3 logic.** Procurement can adjust line prices between PR and PO; the overrun guard fires at `draft → sent`. Director + head of Finance notified for zone 2; blocked for zone 3. |
| D13 | Receiving model | **Per-line `received_quantity`** on `po_lines`. Matches the original PO design. |
| D14 | Currencies at launch | **USD, SRD, EUR.** |
| D15 | Quotation attachment | **Multi-file.** Future-proofs for multi-quote later. |
| D16 | Edit permission for approvers | **Dept head can edit PR content while in their queue.** Procurement and Director are read-only on PR content (procurement only fills its own quote fields). |
| D17 | Supplier `payment_terms` shape | **Single-select** from fixed list: Net 30 / Net 60 / Net 90 / COD / Prepayment. |
| D18 | `resubmitted_from` field | **Dropped.** Rejected PRs do not formally link to a successor. Submitter creates a fresh PR. |
| D19 | Notifications | **In-app only** (NocoBase native — workflow tasks + notification icon). No email/SMTP. |
| D20 | Director self-PRs | **Deferred to v2.** Director cannot submit their own PR in v1. If they need to, an assistant submits on their behalf. |

### Discrepancy resolved

- **`closed_for_new_pos` field.** Moot under the new 1 PR → 1 PO model (D9). Once procurement generates the PO from a PR, the PR is "consumed" — there can be no more POs against it. No expiry workflow needed, no flag on the PR. The PR permissions doc was right to remove it; the PO design doc's references to it are obsolete and will be ignored.

| D21 | Dept approval routing model | **Explicit `main_approver` + `secondary_approver` fields on `departments` (m2o → users).** `users.on_leave` (boolean) controls fallback: when true, workflow routes to `secondary_approver` instead of `main_approver`. Replaced the `department.owners[]` array approach which was unreliable (could be empty, multiple entries, or accidentally broken). Names kept role-neutral ("approver" not "manager") to avoid hierarchy implications. |
| D22 | FX rate entry in MVP3 | **User enters `fx_rate_to_usd` manually on the PR.** The original design had a separate `fx_rates` collection + workflow FX-lookup nodes at submit time. Simplified 2026-05-24: `fx_rate_to_usd` is a plain number field edited by the submitter or procurement; `quoted_total_usd` is a **formula field** (`{{quoted_total}} * {{fx_rate_to_usd}}`, formula.js) that auto-computes whenever either input changes. `fx_rates` collection was created then deleted. D3 (stale FX rate warning) is now moot — there is no rate lookup. Guard E now validates `fx_rate_to_usd` IS NOT NULL instead of looking up an FX rate. |
| D23 | MVP4 director routing | **Manual `needs_director_approval` checkbox instead of automatic `approval_limits` threshold.** Original plan used an `approval_limits` collection ($1,500 USD → skip director, above → director). Simplified 2026-05-24: submitter checks `needs_director_approval` on the PR form. Workflow conditions on that field. `approval_limits` collection never built. Linkage rule on create form makes `justification` required when checkbox is checked. |
| D24 | Guard A bulk update | **Guard A does not intercept bulk update (known limitation, deferred).** Bulk update sends target IDs in `$context.params.filter.$and[0].id.$in`, not `$context.params.filterByTk`. The Guard A query node looks up by `filterByTk` only, so bulk-update requests pass through. Fix requires a Script/JSON-query node to extract IDs from `$context.params.filter`, or a dedicated bulk-update workflow. Deferred post-MVP5. |
| D25 | MVP6 Procurement submitter routing | **Procurement staff cannot initiate purchase requests.** Original MVP6 included routing for "submitter's dept = Procurement → skip dept + procurement, always to director." Instead: Procurement members are excluded from submitting PRs by policy/ACL. The dept-owner skip (submitter IS dept approver → skip dept) was already implemented in MVP1 (condition `5hed96jh1u7`). No new workflow restructuring needed. MVP6 is complete. |

### Items deferred to v2 (do not implement in v1)

- Director-submitted PRs (D20)
- Recurring / blanket PRs
- SLA / overdue tracking and alerts
- Multi-approver committees for very-high-value PRs
- PR templates
- Compliance review checkpoint
- Linked / parent-child PRs
- Approval workflow versioning
- Multi-quote requirement above some threshold
- **Projects + project budget tracking (D5)**
- Email notifications via SMTP

### Operational ownership questions (answered by runtime ACL, not by build decisions)

These don't change what's built — the system just grants/denies based on role. The specific person filling each role is a runbook concern, not a v1 design decision.

- Who owns FX rate updates → answer: Finance role members (already in the permissions matrix)
- Who can change `approval_limits` values → answer: admin only (already in the permissions matrix)
- Who maintains supplier records → answer: any procurement role member (already in the permissions matrix)

---

## 4. MVP roadmap

The new shape, after removing projects (D5) and simplifying PO (D9–D13):

| MVP | One-line scope |
|---|---|
| 1 (current) | 3-stage approval, approve/return/reject from day 1 — **just needs verification + submit-button decision** |
| 2 | Cancel by submitter (draft only); `cancellation_reason`; Guard C |
| 3 | Quotation fields + currency + FX rate + provisional USD; no threshold logic yet |
| 4 | USD threshold ($1,500) + skip-director routing; `approval_limits` collection; Guard E (procurement finalisation) |
| 5 | Guard A (PR immutability when terminal) |
| 6 | Submitter-role routing variants (dept head, procurement member, procurement head) |
| 7 | Suppliers, supplier_issues, supplier_evaluations, optional `supplier` field on PR |
| 8 | Comments + attachments (multi `quotation_attachment`, `other_attachments`); soft fields (`is_emergency`, `expenditure_type`, `needed_by`) |
| 9a | PO collection + po_lines + lookups (`delivery_addresses`, `units_of_measure`, `products` stub); Generate-PO button on approved PR |
| 9b | PO send + budget zones (110% tolerance) + zone 2/3 in-app notifications |
| 9c | PO receiving (per-line `received_quantity`); status auto-derivation |
| 9d | PO completion / closing / cancellation; PO immutability when terminal |
| 9e | PO template printing (Word → PDF) |

Each MVP block below has its own "what it includes / does NOT include / phases / verification". Re-decide scope at the start of each MVP.

---

## MVP1 — verification + submit-button decision (in progress)

### What's left

1. Run the four scenarios (A happy path, B dept-head edits, C return, D reject).
2. Observe what happens when Alice clicks **Submit for Approval**.
   - If status moves to `pending_dept_approval`: button works. Proceed.
   - If nothing happens or status doesn't change: pick (A) drop the button or (B) add a thin `custom-action` bridge workflow.
3. After deciding, re-run scenarios A–D once with the chosen path.
4. Confirm Oliver (dept owner) sees Alice's PR in the global Workflow Tasks menu and Approve/Return/Reject all work.
5. Confirm Pat and Dana can act in turn.
6. Confirm rejected PRs land with both `rejection_reason_category` and `rejection_comment` populated.

### Critical files / artifacts

- Workflow ID `363982109736960` (key `idezsq1k1ts`)
- Approval surfaces: `apz6gdy0z6z`, `n7n6x0xg3t0`, `wdty2zx7de7`, `8yyu6ofo1ww`
- Page `cuycec133qb`, table block `l1e2iwdwau9`
- Submit-for-Approval action `jonczu8szrj` (may be removed in step 2)

### Decision to record at end of MVP1

Either "submit-from-table works", or "submission goes through Workflow Tasks", or "submit-from-table uses bridge workflow X". Note in a new memory file so MVP6 (routing variants) can build on the same primitive.

---

## MVP2 — Cancel by submitter

### What it includes

- One new field on `purchase_requests`:
  - `cancellation_reason` (textarea) — entered via dedicated Cancel form only
- New status value `cancelled`. New timestamp `cancelled_at`.
- Cancel button on PR detail/row — opens a small popup for the reason, triggers a cancel workflow.
- **Guard C** (Cancellation, permissions doc §6):
  - operator must equal record's `submitter` (per D1)
  - status must be `draft` — once submitted, cancellation is never allowed regardless of status
- Field-level permissions update for `cancellation_reason`.

### What it does NOT include

- Procurement cancelling on submitter's behalf (D1: no).
- Cancellation from `info_requested` or any post-submission status — once submitted, a PR cannot be cancelled.
- Re-submission of cancelled PRs (terminal).

### Phases

- **2.1** Add `cancellation_reason` field and `cancelled` status value.
- **2.2** Build the cancel workflow (`custom-action` type, single Update node).
- **2.3** Build Guard C (request-interception workflow).
- **2.4** Add Cancel button + popup form + linkage rule (visible only when status = `draft`).
- **2.5** Verify: C1 cancel a draft → cancelled. C2 try to cancel a submitted PR (any non-draft status, including `info_requested`) → blocked. C3 try to cancel someone else's draft PR → blocked. C4 scenarios A–D from MVP1 still pass.

---

## MVP3 — Quotation, currency, FX rate, provisional USD ✓ COMPLETE (2026-05-24)

### What was built (per D22 simplification)

- ~~New collection `fx_rates`~~ — created then deleted; replaced by manual entry (D22).
- New fields on `purchase_requests`:
  - `quoted_total` (decimal)
  - `quoted_currency` (single-select USD/SRD/EUR)
  - `fx_rate_to_usd` (decimal, **user-entered** — submitter or procurement enters rate manually)
  - `quoted_total_usd` (**formula field**, formula.js: `{{quoted_total}} * {{fx_rate_to_usd}}`, auto-computes, read-only)
  - `quotation_attachment` (attachment, **multi**, per D15)
- Procurement approval form: `quoted_total`, `quoted_currency`, `fx_rate_to_usd`, `quotation_attachment` editable; `quoted_total_usd` readPretty.
- PR table: `quoted_total`, `quoted_currency` columns added.
- PR detail popup: all 5 quote fields visible (read-only display).
- Approval workflow simplified to 16 nodes (no FX-lookup nodes).

### What it does NOT include

- Threshold routing, `approval_limits`, Guard E — all in MVP4.

---

## MVP4 — Threshold routing + Guard E

### What it includes

- New collection `approval_limits` (name, applies_to single-select, role m2o nullable, department m2o nullable, max_amount_usd decimal, notes).
- Seed one row: "Procurement → Director threshold", applies_to = global, max_amount_usd = **1500** (per D4).
- New field `approved_at` (datetime) on `purchase_requests` — written when threshold route short-circuits to approved.
- Approval workflow revision: after procurement Approve branch, evaluate `quoted_total_usd` vs threshold. At-or-below → mark approved, set `approved_at`, end. Above (or null) → continue to director.
- **Guard E** (procurement review finalisation, permissions doc §6) — condition nodes inside procurement Approve branch (per D22, no FX lookup needed):
  - validates `quoted_total` IS NOT NULL
  - validates `quoted_currency` IS NOT NULL
  - validates `quotation_attachment` IS NOT NULL
  - validates `fx_rate_to_usd` IS NOT NULL
  - if any missing → end/block; if all present → pass through to threshold check
  - Note: `quoted_total_usd` is a formula field — no need to write it; it auto-computes from `quoted_total` × `fx_rate_to_usd`
  - D3 (stale FX rate warning) is moot under D22 — there is no rate lookup.

### What it does NOT include

- Submitter-role routing variants (MVP6).

### Phases

- **4.1** Create `approval_limits` collection + seed threshold row. Add `approved_at` datetime to `purchase_requests`.
- **4.2** Build Guard E inside procurement Approve branch.
- **4.3** Update procurement Approve branch with threshold query + routing condition.
- **4.4** Verify: T1 USD 500 quote (rate entered, USD total ≤ 1500) → Pat approves → straight to approved, Dana skips. T2 USD 2000 quote → Dana receives task. T3 missing fx_rate_to_usd → Guard E blocks. T4 null quoted_total_usd (formula returns null when inputs missing) → Guard E blocks at fx_rate_to_usd check.

---

## MVP5 — Guard A (immutability)

### What it includes

- **Guard A** (permissions doc §6) — request-interception on `purchase_requests`, fires on every Update / Delete:
  - if status ∈ {approved, rejected, cancelled} → block
  - else pass through
- ACL hardening: explicit denial of `update` / `destroy` for terminal statuses.

### Phases

- **5.1** Build Guard A.
- **5.2** Verify: I1 edit approved via API → blocked. I2 edit rejected via API → blocked. I3 edit cancelled via API → blocked. I4 edit draft → succeeds.

---

## MVP6 — Submitter-role routing variants ✓ COMPLETE (2026-05-24, D25)

**Design change (D25):** Procurement staff are excluded from initiating PRs by policy/ACL — the routing variant "submitter's dept = Procurement → skip to director" is moot. The dept-owner skip (submitter IS dept approver → skip dept approval) was already implemented in MVP1 (condition node `5hed96jh1u7` in the PR Approval workflow). No new workflow restructuring needed.

Verified routing as-built:
- R1 Operations member (alice) → normal 3-stage ✓ (MVP1)
- R2 Oliver (Operations owner) submits → skips dept, straight to Procurement ✓ (MVP1)
- R3/R4 Procurement staff → excluded from submitting PRs (ACL, MVP7+)

---

## MVP7 — Suppliers + supplier_issues + supplier_evaluations

### What it includes

- New collections (per PR design §11):
  - `suppliers` (name, display_name, tax_id, country, default_currency, **`payment_terms` single-select per D17 (Net30/Net60/Net90/COD/Prepayment)**, status, notes, **`current_rating` manual per D6**)
  - `supplier_issues` (full schema from §11)
  - `supplier_evaluations` (full schema; `score` 1–5 per D7)
- Optional `supplier` field on `purchase_requests` (m2o, "Suggested supplier" label).
- ACL: only procurement creates/edits `suppliers` (Guard #9); all roles view. Suppliers immediately usable on creation (D8 — no onboarding workflow).
- All roles create supplier issues and evaluations; procurement edits/resolves.

### Phases

- **7.1** Create the 3 collections.
- **7.2** Add optional `supplier` field to PR.
- **7.3** Configure ACL.
- **7.4** Build list/detail pages for suppliers, issues, evaluations.
- **7.5** Verify: S1 procurement adds a supplier → succeeds. S2 alice tries → blocked. S3 anyone logs an issue → succeeds. S4 procurement resolves → succeeds. S5 PR submits with or without `supplier`.

---

## MVP8 — Comments + attachments + soft fields

### What it includes

- Enable native **Comment Collection** plugin on `purchase_requests`.
- Add remaining soft fields to PR:
  - `expenditure_type` (single-select: capex / opex / maintenance / consumables)
  - `is_emergency` (boolean — UI flag only, no routing change per design decision 43)
  - `needed_by` (date)
  - `other_attachments` (attachment, multi)
- Update PR table + detail + forms to surface these.

### Phases

- **8.1** Enable Comment Collection.
- **8.2** Add 4 new fields.
- **8.3** Update forms + detail.
- **8.4** Verify: all fields save and display; comments persist across approvals.

---

## MVP9a — PO collection + po_lines + lookups + Generate-PO button

### What it includes

- New collections:
  - `delivery_addresses` (name, address, is_default boolean, status)
  - `units_of_measure` (name, abbreviation, status)
  - `products` (name, description, default_uom, status) — v1 stub only
  - `purchase_orders` (per PO design §9 — `po_number` sequence, `purchase_request` m2o, `supplier` m2o, `delivery_address` m2o, `status`, `currency`, `fx_rate_to_usd`, `total`, `total_usd`, `payment_status`, `payment_date`, `expected_delivery_date`, `quotations` attachment-multi, `attachments` attachment-multi, `supplier_note`, `internal_notes`, `budget_override_comment`, `close_reason`, `close_comment`, audit timestamps)
  - `po_lines` (per PO design §9 — `purchase_order` m2o, `product` m2o optional, `description`, `unit_of_measure` m2o, `quantity_ordered`, `unit_price`, `line_total` formula, `line_total_usd` formula, `received_quantity`, `line_status`)
- Add `address` (textarea) to `suppliers`.
- **Generate-PO button** on `purchase_requests` table/detail — visible only when `status = approved` AND no PO exists yet (per D9 — one PR → one PO).
- Generate-PO action: creates a draft PO pre-filled with PR fields:
  - `supplier` ← `pr.supplier`
  - `currency` ← `pr.quoted_currency`
  - `fx_rate_to_usd` ← `pr.fx_rate_to_usd`
  - one default po_line: description from `pr.description` (or `pr.title`), unit_price from `pr.quoted_total`, quantity 1
  - `quotations` copied from `pr.quotation_attachment`
- Procurement edits po_lines: split into structured lines (description, UoM, qty, unit price), add/remove lines.
- PO total maintained by workflow (sum of `po_lines.line_total`) since NocoBase formula fields cannot aggregate child records (PO design decision 12).
- **Guard:** cannot create PO against a PR with status ≠ approved (per PO design Guard #1).

### What it does NOT include

- Sending, budget zones, notifications (9b)
- Receiving (9c)
- Completion / closing (9d)
- Template printing (9e)
- Multi-PO per PR — explicitly out (D9)

### Phases

- **9a.1** Create 4 lookup/header collections + `po_lines`.
- **9a.2** Add `address` to `suppliers`.
- **9a.3** Build PO list + detail page.
- **9a.4** Build Generate-PO action on approved PR (workflow that creates PO + 1 default line).
- **9a.5** Build small workflow to maintain PO `total` from `po_lines.line_total`.
- **9a.6** Verify: PO1 generate PO from approved PR → succeeds, one default line. PO2 generate PO from non-approved PR → button hidden, API blocked. PO3 PR with an existing PO → Generate-PO button hidden. PO4 add/edit/remove lines → total updates correctly. PO5 ACL: only procurement can edit po_lines.

---

## MVP9b — Send PO + budget zones + zone 2/3 notifications

### What it includes

- PO status transitions: `draft → sent`, `draft → cancelled`.
- **Budget overrun guard** (PO design §5) at `draft → sent`:
  - zone 1: cumulative PO total (USD) ≤ PR `quoted_total_usd` → proceed
  - zone 2: PR < cumulative ≤ 110% PR → require `budget_override_comment`; in-app notify Director + Finance dept head (per D19 in-app only)
  - zone 3: > 110% → block
  - tolerance hardcoded at 110% (PO design decision 14)
- Note: under D9 there's only one PO per PR, but the zone logic still matters — procurement could inflate the PO price above the approved PR amount.

### Phases

- **9b.1** Build the send-PO workflow + budget zone evaluation.
- **9b.2** In-app notification side-effects to director + Finance owner(s).
- **9b.3** Verify: Z1 zone 1 → PO sent normally. Z2 zone 2 → require comment, send + notify. Z3 zone 3 → blocked.

---

## MVP9c — PO receiving

### What it includes

- `po_lines.received_quantity` (decimal, supports fractional units per PO design §9).
- `po_lines.line_status` (single-select pending / partially_received / received) — workflow-maintained.
- Status auto-derivation on PO: all lines `received` → PO becomes `received`; reversible when corrected downward.
- In-app notification when all lines received: "PO X ready to complete" → procurement.
- Record History enabled on `po_lines.received_quantity` (PO design §9 note).

### Phases

- **9c.1** Add receiving fields to po_lines (may already exist from 9a — verify).
- **9c.2** Build the receiving workflow (recompute line_status + PO status).
- **9c.3** In-app notification.
- **9c.4** Verify: partial, full, corrected-down scenarios.

---

## MVP9d — PO completion / closing / cancellation + immutability

### What it includes

- Complete action (status `received → completed`, manual procurement action).
- Close action (status `sent / confirmed / partially_received → closed`, required `close_reason` single-select + `close_comment` textarea).
- Cancel action (status `draft → cancelled`).
- PO immutability guard when status ∈ {completed, closed, cancelled} — same pattern as PR Guard A.
- Audit timestamps: `sent_at`, `confirmed_at`, `completed_at`, `closed_at`, `cancelled_at`.

### Phases

- **9d.1** Add status transition actions.
- **9d.2** Build PO immutability guard.
- **9d.3** Verify: each transition + immutability gate.

---

## MVP9e — PO template printing

### What it includes

- Enable Template Printing plugin. Build the Word `.docx` template (PO header, supplier, delivery address, lines).
- LibreOffice on server for PDF output.
- Action button on PO detail: "Generate PDF" → produces PO document.
- `supplier_note` prints; `internal_notes` does not.

### Phases

- **9e.1** Confirm plugin enabled, LibreOffice installed (handoff to `nocobase-env-manage` if needed).
- **9e.2** Build `.docx` template.
- **9e.3** Wire action button.
- **9e.4** Verify: PDF output matches template.

---

## 5. Notes on the existing implementation that the new session must be aware of

- **Phase 7 workflow registry** in memory (`project_phase7_workflows.md`) is a record of the abandoned build. Do not act on those IDs.
- **Dept approval routing uses `main_approver` field, not `department.owners`.** `departments.main_approver` (m2o → users) and `departments.secondary_approver` (m2o → users) are the routing source. `users.on_leave` (boolean) determines which is used. Do not use `department.owners` for any workflow logic.
- **`fieldGroups` requirement on whole-page blueprints.** Any future page using `purchase_requests` will need `defaults.collections.purchase_requests.fieldGroups` (and similar for `users` because the `submitter` association generates a view popup with >10 fields).
- **`triggerWorkflow` action type.** Setting `workflowKey` via `flow-surfaces configure` is not supported. We set it directly via `nb api resource update --resource flowModels`. MVP1 verification confirmed the button works — no bridge workflow needed.
- **`$notIn` operator** not supported in linkage rule conditions — use combined `$ne` with `$and`.
- **Workflow revision behavior:** When creating a revision of a workflow that has condition branches, the branch nodes may be dropped from the copy. Verify the full node count after revision and recreate missing nodes as needed before enabling.

---

## 6. Verification checklist for this plan

Before starting work in a new chat session:

- Read the three design documents and this plan top to bottom.
- The three design documents on disk have been updated in line with the decision register in §3 of this plan. Where the docs reference superseded designs (e.g. the old "1 PR → many POs", `closed_for_new_pos`, `projects` collection), the obsolete entries are explicitly marked as removed/superseded so the reasoning behind the change stays traceable.
- Confirm MVP1 is the next thing — four scenarios + submit-button decision.

---

## 7. Open items remaining

**None for v1 build decisions.** All the v2 "still open" items are now answered (see §3 decision register).

The only thing left is the **runtime question from MVP1**: does the existing `RecordTriggerWorkflowActionModel` button actually trigger the approval-typed workflow? That's a verification result, not a design decision.

---

*End of plan v3.*
