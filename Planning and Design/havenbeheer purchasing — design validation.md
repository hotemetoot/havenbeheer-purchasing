# Havenbeheer Purchasing — Design Validation

**Purpose:** This document captures every assumption and decision made so far about the Purchase Request (PR) data model and approval workflow. Use it to validate with the team that we understand how Havenbeheer actually works before any building begins.

**How to use:** Walk through each section with the team. For each item, ask: *is this how we actually do it, or want to do it?* Push back wherever reality differs from what's written here.

**Status:** Design phase. Nothing has been built. Anything here can still change.

---

## 1. Scope

### In scope (v1)
- Purchase Requests (PRs): submission, approval workflow, lifecycle
- Suppliers: collection + basic evaluation (issues, scores)
- Projects: budget linkage, on-the-fly budget tracking
- Multi-currency PRs with USD threshold
- Comments and attachments on PRs

### Explicitly NOT in scope (v1)
- Goods receipt / receiving (handled in PO model)
- Invoicing and payment (payment visibility only, in PO model)
- Budget accounting (the design supports tracking, not GL posting)
- Vendor selection process for big tenders
- Tax handling beyond storing the gross amount

### In scope (v1) — added after initial PR design
- Purchase Orders (PO) — see separate PO Design Validation document

### Deferred to v2
- Director-submitted PRs (no escalation path defined yet)
- Recurring / blanket PRs
- SLA / overdue tracking and alerts
- Multi-approver committees for very-high-value PRs
- PR templates
- Compliance review checkpoint
- Linked / parent-child PRs
- Approval workflow versioning (in-flight PRs when policy changes)

---

## 2. Process overview

### Normal happy path

```
Submitter creates draft (with or without quotation)
  → submits
  → Department Head approves
  → Procurement Reviewer sources quote if not provided, enters totals, approves
  → IF total_usd > threshold: Director approves
  → APPROVED
```

### Variants

| Scenario | Path |
|---|---|
| Department head submits | Skip dept approval → Procurement → (maybe) Director |
| Procurement member submits | Procurement head approves → straight to Director (skip purchasing review) |
| Procurement head submits | Skip dept approval AND skip purchasing review → straight to Director |
| Submitter cancels in draft or pending_dept_approval | Allowed |
| Submitter cancels when info_requested by dept head or procurement | Allowed |
| Submitter cancels when info_requested by director | **Not allowed** — procurement has already approved; only rejection path available |
| Approver returns for info | PR goes back to submitter as `info_requested`; `previous_status` records which stage returned it |
| Approver rejects | Terminal: status = rejected |

---

## 3. Status lifecycle

| Status | Meaning |
|---|---|
| `draft` | Being prepared by submitter; not yet in any approval queue |
| `pending_dept_approval` | Waiting for department head |
| `pending_purchasing_review` | Waiting for procurement reviewer; procurement may enter/complete quotation here |
| `pending_director_approval` | Waiting for director |
| `info_requested` | An approver returned the PR; waiting for submitter to revise/resubmit |
| `approved` | Final: PR may now drive a PO (within the eligibility window) |
| `rejected` | Terminal: PR is dead |
| `cancelled` | Terminal: submitter pulled it back |

---

## 4. Roles and approver assignment

| Role | How it's modeled in NocoBase | Used as approver where |
|---|---|---|
| Submitter | The user creating the PR | n/a |
| Department head | Native `department.heads` field (multiple supported) | Dept approval node |
| Procurement reviewer | Member of Procurement department + linked role | Purchasing review node |
| Director | Member of Director department + linked role | Director approval node |

### Backup / holiday coverage
- Use **multiple heads per department** + **Anyone** approval mode
- Built-in **Reassign** action for ad-hoc cases
- No custom delegation field

### Role principles
- NocoBase Role Union mode: **Union only** (users get the combined permissions of all assigned roles)
- Compose **simple atomic roles** (e.g., `can_export_records`, `is_first_aid_responder`)
- Always prefer native NocoBase concepts over custom roles when they overlap

---

## 5. Routing and threshold logic

### Threshold
- Single threshold defined in **USD**, applied to the quotation total **including tax**
- PRs at or below threshold: dept head + procurement is sufficient
- PRs above threshold: director also required
- Threshold value lives in the `approval_limits` collection (extensible — more rules likely to come)

### Multi-currency
- Quote entered in any of three supported currencies (single-select); may be entered by submitter at submission or by procurement during review
- FX rate is **snapshotted when procurement finalises their review** (not at submission) — this is the definitive rate used for the threshold check
- USD-equivalent total is computed at procurement review completion and stored
- Threshold check uses the stored USD value
- FX rates maintained manually by Finance in the `fx_rates` collection
- If no fresh rate exists when procurement finalises: **warn** the reviewer, do not block

### Routing rules (in order of precedence)
1. If submitter is a head of their main department → skip dept approval
2. If submitter's main department = Procurement → skip purchasing review (always go to director)
3. If both above are true → skip both, straight to director
4. After purchasing review: if PR is charged to a project AND `project.is_director_approved = true` AND `quoted_total_usd ≤ project.remaining_budget` → approved directly (no director needed — director already signed off on the project budget)
5. After purchasing review: if `total_usd > threshold` AND rule 4 does not apply → director; else → approved

> ⚠️ **Workflow decision needed:** Rule 4 skips the director entirely for any PR within an approved project budget, regardless of amount. Confirm with Havenbeheer whether this is intentional — a $500K PR within a $2M approved project budget would bypass the director. If a per-PR amount cap is needed even for project PRs, define it before implementing the approval workflow.

---

## 6. Self-approval rules

| Case | Rule |
|---|---|
| Submitter is dept head of own dept | Allowed; routing skips dept approval |
| Submitter is in procurement | Allowed; routing skips purchasing review |
| Submitter is procurement head | Allowed; routing skips both stages, goes to director |
| Submitter is director | **Open question — deferred to v2** |

---

## 7. Return / info request mechanism

- Use NocoBase's **built-in Return action** (decisive, configurable target node)
- When an approver returns a PR: status becomes `info_requested`
- The approval workflow simultaneously sets `previous_status` to the status the PR held before the return (e.g., `pending_dept_approval`, `pending_purchasing_review`, `pending_director_approval`)
- `previous_status` is used only for the cancellation gate — it is not shown prominently in the UI
- The PR re-enters the submitter's queue
- After submitter resubmits, the workflow resumes from where it was returned (NocoBase tracks resume points internally)

---

## 8. Cancellation rules

| Status | Submitter can cancel? | Reason |
|---|---|---|
| `draft` | Yes | Not yet submitted |
| `pending_dept_approval` | Yes | No approval has occurred |
| `info_requested` (previous_status = `pending_dept_approval`) | Yes | Returned before dept head approved |
| `info_requested` (previous_status = `pending_purchasing_review`) | Yes | Returned by procurement; no director-level investment yet |
| `info_requested` (previous_status = `pending_director_approval`) | **No** | Procurement already approved; only rejection path available |
| `pending_purchasing_review` | No | In procurement's hands |
| `pending_director_approval` | No | In director's hands |
| `approved` / `rejected` / `cancelled` | No | Terminal — no further action |

Only the original submitter can cancel. Procurement can reject a PR but cannot cancel on the submitter's behalf.

**Open question:** Can anyone other than the submitter cancel a PR that's stuck in `pending_dept_approval` for a long time? (e.g., procurement killing a stalled PR.) Default: no.

---

## 9. Hard business rules (Before Action guards)

These rules are enforced at the data layer via NocoBase Before Action Events. They fire on every matching API request — they cannot be bypassed via UI or direct API call.

| # | Guard | Rule |
|---|---|---|
| 1 | **Immutability** | If status ∈ {approved, rejected, cancelled}, block all updates and deletes |
| 2 | **Submission validity** | Only PRs in `draft` may be submitted |
| 3 | **Threshold enforcement** | After procurement review: if `quoted_total_usd > threshold`, workflow must route to director — procurement cannot finalise without this check |
| 4 | **Director scope** | Director may only approve PRs that meet routing criteria (over threshold OR procurement-originated) |
| 5 | **Cancellation** | Only allowed from `draft`, `pending_dept_approval`, or `info_requested` where `previous_status` ≠ `pending_director_approval`. Only the original submitter may cancel. |
| 6 | **Required fields at submission** | Cannot submit without: `title`, `description`, `justification`, `charge_to`. If `charge_to = project`, `project` must be set. Quotation fields are optional at submission. |
| 7 | **Required fields at procurement review completion** | Procurement cannot finalise their review without: `quoted_total`, `quoted_currency`, `quotation_attachment`. If no FX rate exists for the currency: warn reviewer but do not block. |
| 8 | **Project XOR cost charge** | PR must charge to a project OR a department — exactly one. Enforced on create and update. |
| 9 | **Supplier admin restricted** | Only Procurement role may create new supplier records |

---

## 10. Roles & Permissions — `purchase_requests` collection

### Access layer (Roles & Permissions — static, always-on)

These define who can reach the edit action at all, using NocoBase's condition builder on data scope. They are not sufficient alone — Before Action guards enforce the harder business rules on top.

| Role | Create | View scope | Edit scope | Delete |
|---|---|---|---|---|
| `member` | Yes | Own records (`submitter = currentUser`) | Own records + `status ∈ {draft, info_requested}` | No |
| `dept_head` | Yes | Department records (`department = currentUser.mainDepartment`) | Own records + `status ∈ {draft, info_requested}` | No |
| `procurement` | Yes | All records | `status = pending_purchasing_review` (own drafts covered via member role union) | No |
| `director` | Yes | All records | None — approves via workflow action only | No |
| `finance` | No | All records | None | No |

No role has delete permission on `purchase_requests`. Deletions are blocked at the permission layer, with the Before Action guard as API-level backstop.

### Field-level permissions

**System-only fields** — no role has edit permission; only workflows may write these:
`submitted_at`, `fx_rate_to_usd`, `quoted_total_usd`, `department` (snapshotted value), `approved_at`, `rejected_at`, `cancelled_at`, `previous_status`, `status`

**Submitter-editable fields** (member role, in draft/info_requested):
`title`, `description`, `justification`, `expenditure_type`, `charge_to`, `project`, `supplier`, `quoted_total`, `quoted_currency`, `needed_by`, `is_emergency`, `quotation_attachment`, `other_attachments`

**Procurement-editable fields** (procurement role, during pending_purchasing_review):
`quoted_total`, `quoted_currency`, `quotation_attachment`, `other_attachments`

**Workflow-only fields** (set by approval workflow nodes, never by user form):
`rejection_reason_category`, `rejection_comment`, `cancellation_reason`, `status`, `previous_status`, all timestamp fields

**Visible to all roles that can view the PR** (no restrictions):
`status`, `rejection_reason_category`, `rejection_comment`, `cancellation_reason`

---

## 11. Data model — collections

### Native NocoBase collections used as-is
- `users`
- `roles`
- `departments` (with `heads`, `members`, linked roles)
- Built-in **Comment Collection** plugin (used for PR discussion thread)

### Custom collections

#### `purchase_requests`

| Field | Type | Notes |
|---|---|---|
| `title` | text | Required at submission |
| `description` | textarea | Required at submission |
| `justification` | textarea | Required at submission — business case / why needed |
| `submitter` | belongsTo (users) | Auto-set on submission by workflow |
| `department` | belongsTo (departments) | **Snapshotted** from submitter.main_department at submission by workflow — not live FK |
| `expenditure_type` | single select | capex / opex / maintenance / consumables (for reporting only, not accounting) |
| `charge_to` | single select | `project` or `department` — required at submission |
| `project` | belongsTo (projects) | Required when charge_to = project |
| `supplier` | belongsTo (suppliers) | **Optional.** Advisory only — label: "Suggested supplier." Actual supplier confirmed at PO creation. |
| `quoted_total` | decimal | Includes tax, in `quoted_currency`. Optional at submission; required before procurement finalises review. |
| `quoted_currency` | single select | One of three supported currencies. Optional at submission; required before procurement finalises review. |
| `fx_rate_to_usd` | decimal | Snapshotted when procurement finalises review. Set by workflow only. |
| `quoted_total_usd` | decimal | = quoted_total × fx_rate_to_usd. Computed and stored by workflow when procurement finalises review. |
| `quotation_attachment` | attachment | Optional at submission; required before procurement finalises review. Single file or multi — see open question. |
| `other_attachments` | attachment (multi) | Specs, drawings, certificates, comparison docs |
| `status` | single select | See Section 3. Set by workflow only — never by user form. |
| `previous_status` | single select | Same values as `status`. Set by workflow when transitioning to `info_requested`. Used to determine cancellation eligibility. |
| `needed_by` | date | Optional target date |
| `is_emergency` | boolean | Flag for safety-critical / expedited handling |
| `rejection_reason_category` | single select | out_of_budget / policy_violation / wrong_supplier / duplicate / not_justified / other |
| `rejection_comment` | textarea | Free text, set by workflow on rejection |
| `cancellation_reason` | textarea | Free text, entered by submitter via Cancel form |
| `resubmitted_from` | belongsTo (purchase_requests) | Self-reference for new PRs created after rejection |
| `submitted_at` | datetime | Set by workflow at submission. Audit. |
| `approved_at` | datetime | Set by workflow at final approval. Used for PO eligibility window check. |
| `rejected_at` | datetime | Set by workflow on rejection. Audit. |
| `cancelled_at` | datetime | Set by workflow on cancellation. Audit. |

**Note:** Approval history (who acted, when, comments) lives in the built-in NocoBase approval workflow log. We do not duplicate it on the PR.

#### `suppliers`

| Field | Type | Notes |
|---|---|---|
| `name` | text | Legal name |
| `display_name` | text | Short name shown in UI |
| `tax_id` | text | VAT / KvK / equivalent |
| `country` | single select | |
| `default_currency` | single select | Their typical quote currency |
| `payment_terms_days` | number | e.g., 30 |
| `status` | single select | active / inactive / blocked |
| `notes` | textarea | |
| `current_rating` | decimal | Manually maintained or computed — see open question |

#### `supplier_issues`

| Field | Type | Notes |
|---|---|---|
| `supplier` | belongsTo (suppliers) | Required |
| `purchase_request` | belongsTo (purchase_requests) | Optional — issue may be tied to a specific PR |
| `issue_type` | single select | quality / delivery / price / communication / compliance / other |
| `severity` | single select | minor / moderate / major / critical |
| `description` | textarea | Required |
| `reported_by` | belongsTo (users) | Auto-set |
| `reported_at` | datetime | Auto-set |
| `status` | single select | open / under_review / resolved / closed |
| `resolution` | textarea | |
| `resolved_at` | datetime | |

#### `supplier_evaluations`

| Field | Type | Notes |
|---|---|---|
| `supplier` | belongsTo (suppliers) | Required |
| `evaluator` | belongsTo (users) | Auto-set |
| `evaluation_date` | date | |
| `score` | number | Scale TBD (open question) |
| `evaluation_type` | single select | per_transaction / periodic_review |
| `purchase_request` | belongsTo (purchase_requests) | Optional, for per-transaction reviews |
| `comments` | textarea | |

#### `projects`

| Field | Type | Notes |
|---|---|---|
| `code` | text | Short identifier |
| `name` | text | |
| `description` | textarea | |
| `manager` | belongsTo (users) | |
| `department` | belongsTo (departments) | Owning dept |
| `status` | single select | planned / active / on_hold / closed — operational status only |
| `is_director_approved` | boolean | Default false. Set manually by admin/procurement when director has approved the project budget outside the system. Unlocks the within-budget PR routing bypass (see Section 5). |
| `start_date` | date | |
| `end_date` | date | Nullable |
| `approved_budget_usd` | decimal | Total director-approved budget for the project, in USD |
| `currency` | single select | Project's working currency |

**Budget tracking:** computed on the fly. `remaining_budget = approved_budget_usd − SUM(quoted_total_usd of all PRs charged to this project where status NOT IN {draft, rejected, cancelled})`. Pending PRs (submitted but not yet approved or rejected) reserve budget — they are included in the consumed total. Only draft, rejected, and cancelled PRs do not consume budget. Will revisit if performance becomes an issue.

#### `approval_limits`

| Field | Type | Notes |
|---|---|---|
| `name` | text | e.g., "Procurement → Director threshold" |
| `applies_to` | single select | role / department / global |
| `role` | belongsTo (roles) | When applies_to = role |
| `department` | belongsTo (departments) | When applies_to = department |
| `max_amount_usd` | decimal | The threshold value |
| `notes` | textarea | Why this limit exists |

Currently one row will exist (the procurement → director threshold). Collection structure exists to support future rules without schema change.

#### `fx_rates`

| Field | Type | Notes |
|---|---|---|
| `currency_code` | single select | e.g., EUR |
| `usd_rate` | decimal | Multiplier: amount_in_currency × usd_rate = amount_usd |
| `effective_date` | date | |
| `updated_by` | belongsTo (users) | Audit |

**Lookup:** when procurement finalises their review, find latest rate for the PR's currency where `effective_date ≤ today`. If none exists or the latest is stale (rule TBD), warn reviewer but do not block.

---

## 12. Project budget linkage

- Each PR is `charge_to` either a **project** or its **department** (the department itself acts as a cost center)
- PRs charged to a project consume from `project.approved_budget_usd`
- Remaining budget is computed live: `approved_budget_usd − SUM(quoted_total_usd of all PRs charged to this project where status NOT IN {draft, rejected, cancelled})`
- **Pending PRs reserve budget** — any PR from `pending_dept_approval` onwards (excluding `rejected` and `cancelled`) is counted against the budget. Draft PRs do not reserve budget.
- If a PR would push the project over its remaining budget: submission is blocked with an error. The project budget must be adjusted (by admin, outside the system) before the PR can proceed.
- Budget adjustment (increasing `approved_budget_usd`) is out of scope for v1 — done manually by admin.

---

## 13. Comments and attachments

- **Comments:** use NocoBase's built-in Comment Collection plugin, linked to PR records. Threaded, rich text, user-tracked. Used for informal discussion (e.g., "is this price negotiable?")
- **Approval comments:** captured natively in approval workflow history (approver's note when passing/rejecting/returning)
- **Quotation attachment:** dedicated field on PR. May be added by submitter at submission or by procurement during review. Single file or multi — see open question.
- **Other attachments:** multi-file field for specs, drawings, certificates, comparison documents. Editable by submitter and procurement.

---

## 14. Supplier management

- Suppliers are pre-vetted. **Only Procurement role** can create new supplier records (enforced via Before Action guard #9)
- Departments needing a new supplier describe the request in the PR description; Procurement onboards the supplier separately, then resubmits
- Issue logging via `supplier_issues` — anyone can log; Procurement reviews and resolves
- Scoring via `supplier_evaluations` — periodic reviews and/or per-transaction feedback
- Open question: how is `supplier.current_rating` derived? Manually entered, or computed from evaluations?

---

## 15. PO eligibility

A PR may drive a Purchase Order only when:
1. `status = approved`
2. `approved_at` is within the eligibility window (currently 30 days — hardcoded in PO creation workflow)

The PO creation workflow checks both conditions. There is no flag on the PR itself — eligibility is computed at the moment of PO creation.

---

## 16. Open questions for the team

These need answers before we finalise.

**Process and policy**

1. Director-submitted PRs — what's the escalation path? (deferred to v2 unless team has a strong view)
2. Can anyone other than the submitter cancel a PR that's stuck in `pending_dept_approval`? (e.g., procurement killing a stalled one)
3. Is `is_emergency` a workflow-routing flag (changes who/how it's approved), or just a UI flag for humans to expedite manually?
4. Multi-quote requirement: does Havenbeheer require multiple quotes above some threshold? If yes, threshold value, and is sole-source justification needed when only one quote is provided?
5. Over-budget PRs: if a PR would push a project over its approved budget, block / warn / allow?
6. Procurement-originated PRs: confirm "always go to director regardless of amount" (option A from earlier) — even small purchases?

**Numbers**

7. Threshold value (USD) above which director approval is required
8. List of three supported currencies
9. Supplier scoring scale (1–5? 1–10?)
10. FX rate update cadence and stale threshold (when does "no fresh rate" trigger the warning to the procurement reviewer?)

**Modelling details**

11. Quotation attachment: single file or multiple?
12. Supplier `current_rating`: manually maintained or computed from evaluations?
13. Should new suppliers go through an approval workflow themselves, or is procurement adding them informally enough?

**People and ownership**

14. Who owns the FX rate updates in Finance, and how often?
15. Who owns the threshold value in `approval_limits`? Who's authorised to change it?
16. Who maintains supplier records — single procurement person or whole department?

---

## 17. Decisions log (for traceability)

For reference. Each line is a decision already made and not under active discussion.

1. PR is an approval artifact only; immutable once approved
2. Use built-in Return action + `info_requested` status; workflow sets `previous_status` on transition to `info_requested` (for cancellation gate only — not for workflow resume, which is tracked internally by NocoBase)
3. PR has free text + optional quotation attachment + optional total + currency at submission; no line items at PR level
4. PR's department = submitter's main department, snapshotted at submission by workflow
5. Per-role approval limits in a separate collection (extensible)
6. FX rate snapshotted when procurement finalises their review (not at submission); manual rate maintenance by Finance
7. Use native NocoBase Departments
8. Backup approver = multiple heads + Anyone agreement mode; no custom delegate field
9. Built-in approval history is sufficient; no custom audit collection
10. Cancellation allowed from: `draft`, `pending_dept_approval`, `info_requested` where `previous_status` ≠ `pending_director_approval`. Only the original submitter may cancel.
11. Role Union mode: Union only
12. No sub-departments in v1
13. Purchasing and Director are modelled as Departments with linked Roles
14. Department head submits → skip dept approval node
15. Procurement member submits → skip purchasing review, always to director
16. Procurement head submits → skip both, straight to director
17. Department heads always hand off to purchasing (cannot fully approve a PR alone)
18. `department.heads` is the source of truth for "is dept head"; no custom is_manager role
19. Currencies: single-select on PR (3 supported)
20. FX rate freshness: warn, don't block (warning shown to procurement reviewer at finalisation)
21. Justification field on PR, separate from description
22. No cost_centers collection; departments serve as cost centers
23. Project budget tracking computed on the fly; no ledger collection in v1. Formula: `approved_budget_usd − SUM(quoted_total_usd where status NOT IN {draft, rejected, cancelled})`. Pending PRs reserve budget; drafts do not.
41. `projects` collection has `is_director_approved` boolean (default false). Set manually by admin when director approves project budget outside the system. Required for the within-budget PR routing bypass.
42. Over-budget PRs are blocked (hard error), not warned. Project budget must be adjusted before submission can proceed. Budget adjustment is out of scope for v1 (manual admin action).
43. `is_emergency` is a UI/reminder flag only — no routing or workflow branching. It signals to procurement and finance to prioritise ordering and payment.
24. Suppliers are a first-class collection; only procurement can add them
25. Supplier evaluation via `supplier_issues` and `supplier_evaluations` collections
26. Tax handling out of scope — gross amounts only, used for threshold check
27. Rejection and cancellation reasons captured as structured fields on PR; visible to all roles that can view the PR
28. Comments via built-in NocoBase Comment Collection plugin
29. Two attachment fields on PR: dedicated quotation + multi-file other attachments; both editable by submitter (at draft stage) and procurement (during review)
30. Urgency = `needed_by` date + `is_emergency` boolean
31. Expenditure type field on PR for reporting purposes only
32. Resubmission link via self-referencing `resubmitted_from` field on a newly created PR (not editing the rejected one)
33. `supplier` field on PR is optional and advisory — actual supplier selected at PO level
34. Quotation fields (`quoted_total`, `quoted_currency`, `quotation_attachment`) are optional at submission. Procurement enters or completes them during purchasing review if not provided by submitter. Both paths are valid.
35. PO eligibility: `status = approved` AND `approved_at` within 30-day window, checked at PO creation. No flag on the PR itself.
36. Required fields at submission: `title`, `description`, `justification`, `charge_to` (+ `project` if charge_to = project). Quotation fields are not required at submission.
37. `status` and all system-computed fields are written only by workflows — never by user form submission. All status transitions are workflow-driven and tied to specific action buttons.
38. No role has delete permission on `purchase_requests`; delete is blocked at the permissions layer with Before Action guard as API-level backstop.
39. Procurement edit scope on `purchase_requests`: `status = pending_purchasing_review`. Own draft access comes via member role union.
40. `previous_status` field added to `purchase_requests` — single select, same values as `status`. Set by workflow on transition to `info_requested`. Used solely for cancellation eligibility; not displayed prominently in UI.

---

*End of validation document.*
