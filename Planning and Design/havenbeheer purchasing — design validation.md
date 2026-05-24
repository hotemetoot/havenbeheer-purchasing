# Havenbeheer Purchasing — Design Validation

**Purpose:** This document captures every assumption and decision made so far about the Purchase Request (PR) data model and approval workflow. Use it to validate with the team that we understand how Havenbeheer actually works before any building begins.

**How to use:** Walk through each section with the team. For each item, ask: *is this how we actually do it, or want to do it?* Push back wherever reality differs from what's written here.

**Status:** Design phase. Nothing has been built. Anything here can still change.

---

## 1. Scope

### In scope (v1)
- Purchase Requests (PRs): submission, approval workflow, lifecycle
- Suppliers: collection + basic evaluation (issues, scores)
- Multi-currency PRs with USD threshold
- Comments and attachments on PRs
- Three-tier approval routing (dept → procurement → director → RvC where applicable)
- Quotation management: three-quote requirement or sole-source justification

### Explicitly NOT in scope (v1)
- Goods receipt / receiving (handled in PO model)
- Invoicing and payment (payment visibility only, in PO model)
- Annual investment budget ("inkoopbegroting") — not modelled; budget discipline assumed to happen outside the system
- Project budgets — removed from scope
- Cashflow approval gate by Finance Manager — not modelled (Finance has view-only access)
- Vendor tender processes beyond three-quote requirement
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
Submitter creates draft
  → submits
  → Department Head approves
  → Procurement Reviewer collects quotes, selects supplier, enters totals, approves
  → IF total_usd > low_threshold ($1,500): Director approves
  → IF total_usd > high_threshold ($15,000): Procurement uploads signed RvC document → APPROVED
  → APPROVED
```

### Variants

| Scenario | Path |
|---|---|
| Value ≤ $1,500 | Dept Head → Procurement → Approved (no director, no RvC) |
| $1,501 – $15,000 | Dept Head → Procurement → Director → Approved |
| > $15,000 | Dept Head → Procurement → Director → RvC (external) → Approved |
| Dept main approver submits | Skip dept approval → Procurement → (threshold-dependent) |
| Procurement member submits | Skip purchasing review → Director (skip dept review) |
| Procurement main approver submits | Skip dept approval AND skip purchasing review → Director |
| Submitter cancels in draft | Allowed |
| Submitter cancels after submission (any non-draft status, including `info_requested`) | **Not allowed** — once submitted, a PR cannot be cancelled |
| Approver returns for info | PR goes back to submitter as `info_requested` |
| Approver rejects | Terminal: status = rejected |

---

## 3. Status lifecycle

| Status | Meaning |
|---|---|
| `draft` | Being prepared by submitter; not yet in any approval queue |
| `pending_dept_approval` | Waiting for department head |
| `pending_purchasing_review` | Waiting for procurement reviewer; procurement collects quotes, selects supplier, enters totals here |
| `pending_director_approval` | Waiting for director |
| `pending_rvC_approval` | Director approved; awaiting external board (RvC) sign-off. Procurement uploads signed board document to advance. |
| `info_requested` | An approver returned the PR; waiting for submitter to revise/resubmit |
| `approved` | Final: PR may now drive a PO (within the eligibility window) |
| `rejected` | Terminal: PR is dead |
| `cancelled` | Terminal: submitter pulled it back |

---

## 4. Roles and approver assignment

| Role | How it's modeled in NocoBase | Used as approver where |
|---|---|---|
| Submitter | The user creating the PR | n/a |
| Department approver | `departments.main_approver` (m2o → users) — one designated person per department | Dept approval node |
| Department backup approver | `departments.secondary_approver` (m2o → users) — optional; covers when main approver is absent | Dept approval node (when `main_approver.on_leave = true`) |
| Procurement reviewer | `departments.main_approver` of the Procurement department | Purchasing review node |
| Director | Hardcoded user (Dana, id 12) in workflow config | Director approval node |

### Backup / holiday coverage
- Each department has an optional `secondary_approver` field (m2o → users).
- Each user has an `on_leave` boolean field (default false). The approver sets this before going on leave and clears it on return.
- Workflow logic at runtime: if `main_approver.on_leave = true` and `secondary_approver` is set → task goes to `secondary_approver`. If `secondary_approver` is not set, task falls back to `main_approver` (fail-safe).
- Built-in **Reassign** action remains available for ad-hoc hand-off outside this mechanism.

### Role principles
- NocoBase Role Union mode: **Union only** (users get the combined permissions of all assigned roles)
- Compose **simple atomic roles** (e.g., `can_export_records`, `is_first_aid_responder`)
- Always prefer native NocoBase concepts over custom roles when they overlap

---

## 5. Routing and threshold logic

### Two thresholds

Both values live in the `approval_limits` collection (two rows):

| Row name | Value | Effect |
|---|---|---|
| `procurement_to_director` | $1,500 USD | PRs at or below this value: dept + procurement is sufficient, no director needed |
| `director_to_rvC` | $15,000 USD | PRs above this value: director approval is required AND RvC external approval required |

PRs between $1,501 and $15,000 require director but not RvC. PRs above $15,000 require both.

### Multi-currency
- Quote entered in any of three supported currencies (single-select); entered by procurement during review after collecting quotes
- FX rate is **snapshotted when procurement finalises their review** — this is the definitive rate used for threshold checks
- USD-equivalent total is computed at procurement review completion and stored
- Threshold checks use the stored USD value
- FX rates maintained manually by Finance in the `fx_rates` collection
- If no fresh rate exists when procurement finalises: **warn** the reviewer, do not block

### Routing rules (in order of precedence)
1. If submitter = `main_approver` of their main department → skip dept approval
2. If submitter's main department = Procurement → skip purchasing review (always go to director)
3. If both above are true → skip both, straight to director
4. After purchasing review: if `quoted_total_usd ≤ 1,500` → approved directly (no director needed)
5. After director approval: if `quoted_total_usd ≤ 15,000` → approved; if `> 15,000` → pending_rvC_approval

---

## 6. Self-approval rules

| Case | Rule |
|---|---|
| Submitter = `main_approver` of own dept | Allowed; routing skips dept approval |
| Submitter is in procurement | Allowed; routing skips purchasing review |
| Submitter = `main_approver` of Procurement dept | Allowed; routing skips both stages, goes to director |
| Submitter is director | **Open question — deferred to v2** |

---

## 7. Return / info request mechanism

- Use NocoBase's **built-in Return action** (decisive, configurable target node)
- When an approver returns a PR: status becomes `info_requested`
- The PR re-enters the submitter's queue
- After submitter resubmits, the workflow resumes from where it was returned (NocoBase tracks resume points internally)
- Return is not available at `pending_rvC_approval` — by that stage both director and procurement have approved; only rejection is possible

---

## 8. Cancellation rules

| Status | Submitter can cancel? | Reason |
|---|---|---|
| `draft` | Yes | Not yet submitted — the only stage where cancellation is allowed |
| `pending_dept_approval` | **No** | Once submitted, the PR cannot be cancelled |
| `pending_purchasing_review` | **No** | Once submitted, the PR cannot be cancelled |
| `pending_director_approval` | **No** | Once submitted, the PR cannot be cancelled |
| `pending_rvC_approval` | **No** | Once submitted, the PR cannot be cancelled |
| `info_requested` | **No** | Returned to submitter but still considered submitted — cannot be cancelled |
| `approved` / `rejected` / `cancelled` | No | Terminal — no further action |

Only the original submitter can cancel, and only while the PR is still in `draft`. Procurement can reject a PR but cannot cancel on the submitter's behalf. If a PR is stuck in an approval queue, procurement or admin may reject it — there is no cancel path from any post-submission status.

---

## 9. Hard business rules (Before Action guards)

These rules are enforced at the data layer via NocoBase Before Action Events. They fire on every matching API request — they cannot be bypassed via UI or direct API call.

| # | Guard | Rule |
|---|---|---|
| 1 | **Immutability** | If status ∈ {approved, rejected, cancelled}, block all updates and deletes |
| 2 | **Submission validity** | Only PRs in `draft` may be submitted |
| 3 | **Threshold enforcement** | After procurement review: workflow routes to director if `quoted_total_usd > 1,500`; routes to RvC stage if `quoted_total_usd > 15,000` after director approves |
| 4 | **Director scope** | Director may only approve PRs in `pending_director_approval` |
| 5 | **Cancellation** | Only allowed from `draft`. Once submitted, cancellation is not permitted regardless of status. Only the original submitter may cancel. |
| 6 | **Required fields at submission** | Cannot submit without: `title`, `description`, `justification`, `charge_to`. Quotation fields are not required at submission. |
| 7 | **Required fields at procurement review completion** | Procurement cannot finalise without: `quote_strategy`; if `three_quotes` → ≥ 3 entries in `pr_quotations` each with attachment, exactly one with `is_selected = true`, plus `supplier_selection_rationale`; if `existing_supplier` → ≥ 1 quotation entry with attachment, plus `sole_source_justification`. `supplier` must be set (auto-populated from selected quotation). `quoted_total`, `quoted_currency` must be set. If no FX rate exists for the currency: warn reviewer but do not block. |
| 8 | **RvC document required** | Cannot advance from `pending_rvC_approval` to `approved` without `rvC_approval_document` attached |
| 9 | **Supplier admin restricted** | Only Procurement role may create new supplier records |

---

## 10. Roles & Permissions — `purchase_requests` collection

### Access layer (Roles & Permissions — static, always-on)

| Role | Create | View scope | Edit scope | Delete |
|---|---|---|---|---|
| `member` | Yes | Own records (`submitter = currentUser`) | Own records + `status ∈ {draft, info_requested}` | No |
| `dept_head` | Yes | Department records (`department = currentUser.mainDepartment`) | Own records + `status ∈ {draft, info_requested}` | No |
| `procurement` | Yes | All records | `status = pending_purchasing_review` (own drafts covered via member role union) + `status = pending_rvC_approval` (to upload RvC document) | No |
| `director` | Yes | All records | None — approves via workflow action only | No |
| `finance` | No | All records | None | No |

No role has delete permission on `purchase_requests`.

### Field-level permissions

**System-only fields** — no role has edit permission; only workflows may write these:
`submitted_at`, `fx_rate_to_usd`, `quoted_total_usd`, `department`, `approved_at`, `rejected_at`, `cancelled_at`, `rvC_approved_at`, `status`, `supplier` (locked after `pending_purchasing_review`)

**Submitter-editable fields** (member role, in draft/info_requested):
`title`, `description`, `justification`, `expenditure_type`, `charge_to`, `needed_by`, `is_emergency`, `other_attachments`

**Procurement-editable fields** (procurement role, during pending_purchasing_review):
`quote_strategy`, `sole_source_justification`, `supplier_selection_rationale`, `other_attachments`
Plus full CRUD on child `pr_quotations` records

**Procurement-editable fields** (procurement role, during pending_rvC_approval):
`rvC_approval_document`

**Workflow-only fields** (set by approval workflow nodes, never by user form):
`rejection_reason_category`, `rejection_comment`, `cancellation_reason`, `status`, all timestamp fields, `supplier` (snapshotted from selected quotation when procurement finalises)

**Visible to all roles that can view the PR** (no restrictions):
`status`, `rejection_reason_category`, `rejection_comment`, `cancellation_reason`

---

## 11. Data model — collections

### Native NocoBase collections used as-is
- `users` — extended with `on_leave` (boolean, default false): approver sets this before going on leave
- `roles`
- `departments` — extended with `main_approver` (m2o → users) and `secondary_approver` (m2o → users) for workflow routing. Native `heads`/`owners` field is not used for routing.
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
| `expenditure_type` | single select | capex / opex / maintenance / consumables — reporting only, no routing effect |
| `charge_to` | single select | `project` or `department` — required at submission |
| `supplier` | belongsTo (suppliers) | Set by workflow from selected `pr_quotations` entry when procurement finalises review. **Locked after that point.** Not editable by user form. |
| `quote_strategy` | single select | `three_quotes` / `existing_supplier`. Required before procurement can finalise review. |
| `sole_source_justification` | textarea | Required when `quote_strategy = existing_supplier`. Written motivation for not seeking competitive quotes. |
| `supplier_selection_rationale` | textarea | Required when `quote_strategy = three_quotes`. Explains why the selected quote was chosen over the others. |
| `quoted_total` | decimal | Includes tax, in `quoted_currency`. Auto-populated from selected quotation when procurement finalises. |
| `quoted_currency` | single select | One of three supported currencies. Auto-populated from selected quotation. |
| `fx_rate_to_usd` | decimal | Snapshotted when procurement finalises review. Set by workflow only. |
| `quoted_total_usd` | decimal | = quoted_total × fx_rate_to_usd. Computed and stored by workflow when procurement finalises review. |
| `rvC_approval_document` | attachment | Single file. Required to advance from `pending_rvC_approval` to `approved`. Uploaded by procurement. |
| `other_attachments` | attachment (multi) | Specs, drawings, certificates, comparison docs |
| `status` | single select | See Section 3. Set by workflow only — never by user form. |
| `needed_by` | date | Optional target date |
| `is_emergency` | boolean | UI/priority flag only — no routing or workflow branching. Signals to procurement and finance to prioritise. |
| `rejection_reason_category` | single select | out_of_budget / policy_violation / wrong_supplier / duplicate / not_justified / other |
| `rejection_comment` | textarea | Free text, set by workflow on rejection |
| `cancellation_reason` | textarea | Free text, entered by submitter via Cancel form |
| `resubmitted_from` | belongsTo (purchase_requests) | Self-reference for new PRs created after rejection |
| `submitted_at` | datetime | Set by workflow at submission |
| `approved_at` | datetime | Set by workflow at final approval. Used for PO eligibility window check. |
| `rvC_approved_at` | datetime | Set by workflow when advancing from `pending_rvC_approval` to `approved` |
| `rejected_at` | datetime | Set by workflow on rejection |
| `cancelled_at` | datetime | Set by workflow on cancellation |

**Note:** Approval history (who acted, when, comments) lives in the built-in NocoBase approval workflow log. We do not duplicate it on the PR.

#### `pr_quotations`

Child collection of `purchase_requests`. Each row represents one supplier quote collected during procurement review.

| Field | Type | Notes |
|---|---|---|
| `purchase_request` | belongsTo (purchase_requests) | Required |
| `supplier` | belongsTo (suppliers) | Required |
| `amount` | decimal | Quote total, in `currency` |
| `currency` | single select | 3 supported currencies |
| `quote_date` | date | |
| `attachment` | attachment | The actual quote document. Required. |
| `is_selected` | boolean | The quote procurement recommends. Exactly one per PR may be true. Enforced by Before Action guard. |
| `notes` | textarea | Optional commentary |

**Guards on `pr_quotations`:**
- Only procurement role may create/edit/delete entries
- Entries are locked when the parent PR status moves past `pending_purchasing_review`
- Only one entry per PR may have `is_selected = true`
- When `is_selected` is set to true, the parent PR's `supplier`, `quoted_total`, and `quoted_currency` are updated by workflow

#### `suppliers`

| Field | Type | Notes |
|---|---|---|
| `name` | text | Legal name |
| `display_name` | text | Short name shown in UI |
| `address` | textarea | |
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
| `purchase_request` | belongsTo (purchase_requests) | Optional |
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

#### `approval_limits`

| Field | Type | Notes |
|---|---|---|
| `name` | text | e.g., "Procurement → Director threshold" |
| `applies_to` | single select | role / department / global |
| `role` | belongsTo (roles) | When applies_to = role |
| `department` | belongsTo (departments) | When applies_to = department |
| `max_amount_usd` | decimal | The threshold value |
| `notes` | textarea | Why this limit exists |

**Two rows on go-live:**
1. `procurement_to_director` — $1,500 USD
2. `director_to_rvC` — $15,000 USD

#### `fx_rates`

| Field | Type | Notes |
|---|---|---|
| `currency_code` | single select | e.g., EUR |
| `usd_rate` | decimal | Multiplier: amount_in_currency × usd_rate = amount_usd |
| `effective_date` | date | |
| `updated_by` | belongsTo (users) | Audit |

**Lookup:** when procurement finalises their review, find latest rate for the PR's currency where `effective_date ≤ today`. If none exists or the latest is stale (rule TBD), warn reviewer but do not block.

---

## 12. PO eligibility

One PR drives exactly **one** Purchase Order. A PO can only be created against a PR when:
1. `status = approved`
2. `approved_at` is within the eligibility window (currently 30 days — hardcoded in PO creation workflow)
3. No PO already exists against this PR (enforced by guard in PO collection)

The PO creation workflow checks all three conditions.

---

## 13. Comments and attachments

- **Comments:** use NocoBase's built-in Comment Collection plugin, linked to PR records. Threaded, rich text, user-tracked.
- **Approval comments:** captured natively in approval workflow history
- **Quotation documents:** stored as attachments on individual `pr_quotations` child records
- **RvC document:** dedicated `rvC_approval_document` field on PR — single file, uploaded by procurement after board approval
- **Other attachments:** multi-file field for specs, drawings, certificates. Editable by submitter (draft/info_requested) and procurement (during purchasing review)

---

## 14. Supplier management

- Suppliers are pre-vetted. **Only Procurement role** can create new supplier records (Before Action guard #9)
- Issue logging via `supplier_issues` — anyone can log; Procurement reviews and resolves
- Scoring via `supplier_evaluations` — periodic reviews and/or per-transaction feedback
- Open question: how is `supplier.current_rating` derived?

---

## 15. Open questions for the team

All questions resolved. No open items remain.

**Resolved**

| # | Question | Answer |
|---|---|---|
| 1 | Director-submitted PRs escalation path | Deferred to v2 |
| 2 | Who else can cancel a stalled PR in `pending_dept_approval`? | No one — cancellation is only possible in `draft`. Procurement or admin may reject a stuck PR instead. |
| 3 | Does `is_emergency` ever affect routing? | No — priority/reminder flag only, no workflow branching |
| 4 | Are the 2018 thresholds still current? | Yes — $1,500 (procurement → director) and $15,000 (director → RvC), in USD only; other currencies converted via exchange rate |
| 5 | Which currencies are supported? | USD, SRD, EUR |
| 6 | Supplier scoring scale? | 1–5 |
| 7 | FX rate stale threshold | 30 days |
| 8 | `supplier.current_rating` — computed or manual? | Manually maintained by procurement |
| 9 | New supplier approval workflow needed? | No — procurement adds informally, no workflow required |
| 10 | Who updates FX rates, and how often? | All Finance members can update; no fixed schedule |
| 11 | Who can change threshold values in `approval_limits`? | Admin only |
| 12 | Who maintains supplier records? | All procurement members |

---

## 16. Decisions log

1. PR is an approval artifact only; immutable once approved
2. Use built-in Return action + `info_requested` status
3. PR has free text + quotations child collection; no line items at PR level
4. PR's department = submitter's main department, snapshotted at submission by workflow
5. Per-role approval limits in a separate collection (extensible) — two rows on go-live: $1,500 and $15,000
6. FX rate snapshotted when procurement finalises their review; manual rate maintenance by Finance
7. Use native NocoBase Departments
8. Backup approver = `departments.secondary_approver` (m2o → users, optional) + `users.on_leave` (boolean). When `main_approver.on_leave = true`, workflow routes to `secondary_approver`. If none set, falls back to `main_approver`. Built-in Reassign action covers ad-hoc hand-off.
9. Built-in approval history is sufficient; no custom audit collection
10. Cancellation allowed from `draft` only. Once submitted, a PR cannot be cancelled regardless of status (including `info_requested`). Only the original submitter may cancel. Procurement may reject a stuck PR but cannot cancel on the submitter's behalf.
11. Role Union mode: Union only
12. No sub-departments in v1
13. Purchasing and Director are modelled as Departments with linked Roles
14. Department head submits → skip dept approval node
15. Procurement member submits → skip purchasing review, always to director
16. Procurement head submits → skip both, straight to director
17. Department heads always hand off to purchasing (cannot fully approve a PR alone)
18. `departments.main_approver` (m2o → users) is the source of truth for dept approval routing. `departments.secondary_approver` covers absences. No custom "is manager" role — routing is field-based, not role-based. Native `department.heads` / `owners` is not used for workflow routing.
19. Currencies: single-select on PR (3 supported)
20. FX rate freshness: warn, don't block
21. Justification field on PR, separate from description
22. No cost_centers collection; departments serve as cost centers
23. No project budget tracking — removed from scope
24. Suppliers are a first-class collection; only procurement can add them
25. Supplier evaluation via `supplier_issues` and `supplier_evaluations` collections
26. Tax handling out of scope — gross amounts only, used for threshold check
27. Rejection and cancellation reasons captured as structured fields on PR; visible to all roles that can view the PR
28. Comments via built-in NocoBase Comment Collection plugin
29. Other attachments field on PR: multi-file, editable by submitter and procurement
30. Urgency = `needed_by` date + `is_emergency` boolean
31. Expenditure type field on PR for reporting purposes only — no routing effect
32. Resubmission link via self-referencing `resubmitted_from` field on a newly created PR
33. `supplier` field on PR is set by workflow from selected quotation; locked after procurement review finalises; not editable by user form
34. RvC approval is external (board meeting); procurement uploads signed document to advance PR to `approved`
35. `rvC_approval_document` attachment required to advance from `pending_rvC_approval` — enforced by Before Action guard
36. Three-quote requirement: `quote_strategy` field (three_quotes / existing_supplier) required at procurement review; each path has mandatory supporting fields and quotation records
37. Quotation records in `pr_quotations` child collection — replaces single `quotation_attachment` field
38. Exactly one `pr_quotations` entry per PR may have `is_selected = true`; selecting it auto-populates `supplier`, `quoted_total`, `quoted_currency` on the parent PR
39. `is_emergency` is a UI/priority flag only — no routing or workflow branching
40. No role has delete permission on `purchase_requests`
41. Annual inkoopbegroting not modelled — out of scope for v1
42. Cashflow gate (Finance Manager) not modelled — Finance has view-only access only
43. Same approval procedure applies to all purchase types (no routing differences by expenditure type)
44. One PR → one PO (enforced by guard on PO collection)
45. `quoted_total`, `quoted_currency`, `supplier` on PR auto-populated from selected quotation when procurement finalises; stored as fields for threshold check and audit trail
46. Supported currencies: USD, SRD, EUR — used as single-select values on `pr_quotations.currency`, `purchase_requests.quoted_currency`, `purchase_orders.currency`, and `fx_rates.currency_code`
47. Approval thresholds confirmed: $1,500 USD (procurement → director) and $15,000 USD (director → RvC). All threshold checks use USD; non-USD quotes are converted via snapshotted FX rate.
48. Supplier evaluation score: 1–5 scale, integer, manually entered on `supplier_evaluations`
49. `supplier.current_rating`: manually maintained by any procurement member — not computed from evaluations
50. New supplier onboarding: informal — any procurement member adds directly, no approval workflow
51. FX rate maintenance: any Finance member may create or update rates; no fixed update schedule. Stale threshold (30 days) triggers warning to procurement reviewer at finalisation.
52. `approval_limits` values editable by admin only
53. Supplier records maintained by all procurement members (no single owner)
54. Admin role bypasses all user-facing guards and can perform any action system-wide

---

*End of validation document.*
