# Havenbeheer PR — Permissions & Guards Reference

**Purpose:** Implementation-ready reference for all security rules on the Purchase Request workflow. Covers NocoBase Roles & Permissions configuration and Before Action Event guard designs.

**Scope:** Purchase Requests (`purchase_requests`), the `pr_quotations` child collection, and directly related collections. PO-specific rules are in the PO document.

**Status:** Design finalised except for items marked ⚠️ Open.

---

## 1. Architecture overview

Security is enforced in two layers. Both must be in place. Neither is sufficient alone.

**Layer 1 — Roles & Permissions (static)**
Configured in NocoBase's role management UI. Controls which roles can perform which actions on which records and fields. Uses the condition builder for data scopes. Enforced at the API level — not just UI hiding. Evaluated on every request before any data is touched.

**Layer 2 — Before Action Events (dynamic)**
NocoBase workflows that intercept create/update/delete requests before they are committed. Used for rules that depend on runtime conditions (status transitions, field combinations, cross-collection lookups). Also the backstop for API-level abuse that bypasses the UI. Cannot modify data — can only allow or block, with a response message.

UI-level hiding (block visibility, conditional rendering) is used for usability only. It is not considered a security control and is not documented here.

---

## 2. Roles

| Role identifier | Source | Who holds it |
|---|---|---|
| `member` | Default role | Every user automatically |
| `dept_head` | Department role | Manually granted to users who are the primary or backup approver of a department |
| `procurement` | Department role | Inherited by all members of the Procurement department |
| `director` | Department role | Inherited by all members of the Director department |
| `finance` | Department role | Inherited by all members of the Finance department |
| `admin` | Personal role | System administrators only |

**Role Union mode:** Union only. Users hold the combined permissions of all their roles simultaneously. A procurement member who is also a dept head holds both sets of permissions. Permissions always resolve to the maximum across all roles.

> **Note on approval routing vs. ACL roles:** The `dept_head` role above controls *what records people can see and edit* (the view/edit scope in Section 3). Approval routing — i.e., *which person receives the dept approval task* — is determined separately by the `departments.main_approver` and `departments.secondary_approver` fields (m2o → users). `departments.main_approver` is the primary assignee; if `main_approver.on_leave = true`, the task goes to `departments.secondary_approver` instead. These two mechanisms are independent: having the `dept_head` role does not automatically make someone the routing target, and vice versa.

---

## 3. Permissions matrix — `purchase_requests`

### Action permissions

| Action | `member` | `dept_head` | `procurement` | `director` | `finance` |
|---|---|---|---|---|---|
| Create | ✓ | ✓ | ✓ | ✓ | — |
| View | Own records | Dept records | All records | All records | All records |
| Edit | Own records (status-gated) | Own records (status-gated) | Procurement-stage records | — | — |
| Delete | — | — | — | — | — |
| Export | Own records | Dept records | All records | All records | All records |

**View scope conditions (condition builder):**

| Role | Condition |
|---|---|
| `member` | `submitter = currentUser` |
| `dept_head` | `department = currentUser.mainDepartment` | *(view scope based on dept membership — independent of routing)* |
| `procurement` | *(no condition — all records)* |
| `director` | *(no condition — all records)* |
| `finance` | *(no condition — all records)* |

With Union only mode, a dept head who is also a regular member sees the union of both conditions (own PRs OR department PRs). This is correct.

**Edit scope conditions:**

| Role | Condition | Rationale |
|---|---|---|
| `member` | `submitter = currentUser` AND (`status = draft` OR `status = info_requested`) | Submitters edit only their own PRs, only while they hold them |
| `dept_head` | Same as member (dept heads approve via workflow action, not by editing PR content) | |
| `procurement` | `status = pending_purchasing_review` OR `status = pending_rvC_approval` | Purchasing review stage for quotation work; RvC stage to upload signed board document. Own drafts covered via member union. |
| `director` | *(no edit scope — no edit permission)* | Approves via workflow action only |
| `finance` | *(no edit scope — no edit permission)* | Read-only on PRs |

**Delete:** No role has delete permission on `purchase_requests`. Not configured. Before Action Guard A provides the API-level backstop.

---

## 4. Permissions matrix — supporting collections

| Collection | `member` | `dept_head` | `procurement` | `director` | `finance` | `admin` |
|---|---|---|---|---|---|---|
| `pr_quotations` | View (via parent PR) | View (via parent PR) | Create, View, Edit, Delete (while parent PR is in `pending_purchasing_review`) | View | View | Full |
| `suppliers` | View all | View all | Create, View, Edit all | View all | View all | Full |
| `supplier_issues` | Create own, View all | Create own, View all | Full | View all | View all | Full |
| `supplier_evaluations` | Create own, View all | Create own, View all | Full | View all | View all | Full |
| `fx_rates` | View all | View all | View all | View all | Create, Edit all | Full |
| `approval_limits` | View all | View all | View all | View all | View all | Full (edit) |

**Notes:**
- `pr_quotations` records are locked (no edit/delete) once the parent PR moves past `pending_purchasing_review`. Enforced via Before Action guard on `pr_quotations` (see Guard E notes).
- Only `procurement` can create supplier records. Enforced at the permission layer.
- Only `finance` can create or edit FX rates.
- Only `admin` can change `approval_limits` values (threshold amounts).

---

## 5. Field permissions — `purchase_requests`

### System-only fields (no role has edit permission — workflow writes only)

These fields must have edit permission explicitly removed for all roles. Only NocoBase workflows may set them.

| Field | Set by workflow when |
|---|---|
| `status` | Every status transition |
| `submitter` | PR submitted (set once, never changed) |
| `department` | PR submitted (snapshotted from submitter.mainDepartment) |
| `submitted_at` | PR submitted |
| `approved_at` | PR reaches `approved` status |
| `rvC_approved_at` | PR transitions from `pending_rvC_approval` to `approved` |
| `rejected_at` | PR reaches `rejected` status |
| `cancelled_at` | PR reaches `cancelled` status |
| `supplier` | Procurement selects a quotation (`pr_quotations.is_selected = true`); snapshotted from the selected quotation's supplier. Locked after that point — never editable by user form. |
| `quoted_total` | Same event as `supplier` above — auto-populated from selected quotation's `amount` |
| `quoted_currency` | Same event as `supplier` above — auto-populated from selected quotation's `currency` |
| `fx_rate_to_usd` | Procurement finalises review (definitive) |
| `quoted_total_usd` | Procurement finalises review (= `quoted_total × fx_rate_to_usd`) |
| `rejection_reason_category` | Approver rejects |
| `rejection_comment` | Approver rejects |

### Submitter-editable fields (member role, edit permitted in `draft` / `info_requested`)

`title`, `description`, `justification`, `expenditure_type`, `charge_to`, `needed_by`, `is_emergency`, `other_attachments`

Submitters no longer enter quotation data directly. Quotes are collected and entered by procurement via the `pr_quotations` child collection during purchasing review.

### Procurement-editable fields (procurement role, edit permitted in `pending_purchasing_review`)

`quote_strategy`, `sole_source_justification`, `supplier_selection_rationale`, `other_attachments`

Plus full CRUD on child `pr_quotations` records while the parent PR is in `pending_purchasing_review`.

Procurement does not edit title, description, justification, or other submitter fields.

### Procurement-editable fields (procurement role, edit permitted in `pending_rvC_approval`)

`rvC_approval_document` — single file attachment. This is the only field editable at this stage. Uploading this document and clicking "Record Board Approval" advances the PR to `approved`.

### Submitter-editable via dedicated Cancel form only

`cancellation_reason` — entered in the Cancel form. Set alongside `status = cancelled` by the cancel workflow. No general edit permission on this field.

### Visible to all roles that can view the PR (no field-level restriction)

`status`, `rejection_reason_category`, `rejection_comment`, `cancellation_reason`

---

## 6. Before Action Event guards

### Guard A — Immutability

| Property | Value |
|---|---|
| Trigger mode | Global (fires on all matching requests, regardless of button) |
| Actions intercepted | Update, Delete |
| Collection | `purchase_requests` |

**Logic:**
1. Query current record by ID from database
2. If current `status` ∈ {`approved`, `rejected`, `cancelled`} → **End (error):** *"This purchase request is closed and cannot be modified."*
3. Otherwise → pass through

**Notes:**
- This guard covers all updates, including API calls that bypass the UI
- **Exception:** `closed_for_new_pos` (boolean field) is exempt from this guard. It is an operational flag that may be set by procurement or by the 30-day expiry workflow even after the PR is `approved`. Implement this exception by checking whether the only field in the update payload is `closed_for_new_pos` — if so, pass through regardless of status.

---

### Guard B — Submission validation

| Property | Value |
|---|---|
| Trigger mode | Bound — attached to the "Submit for Approval" button only |
| Actions intercepted | Update |
| Collection | `purchase_requests` |

**Logic:**
1. Query current record by ID from database
2. If current `status` ≠ `draft` → **End (error):** *"Only a draft purchase request can be submitted."*
3. Check submitted data: `title` present → else **End (error):** *"A title is required."*
4. Check submitted data: `description` present → else **End (error):** *"A description is required."*
5. Check submitted data: `justification` present → else **End (error):** *"A justification is required."*
6. Check submitted data: `charge_to` set → else **End (error):** *"Please select whether this PR charges to a project or a department."*
7. If all pass → action executes; submission workflow sets `status`, `submitter`, `department`, `submitted_at`

**Notes:**
- Quotation fields are NOT validated at submission — quotes are collected by procurement, not the submitter
- Project budget checks have been removed from this guard — project budget tracking is out of scope for v1

---

### Guard C — Cancellation

| Property | Value |
|---|---|
| Trigger mode | Bound — attached to the "Cancel PR" button only |
| Actions intercepted | Update |
| Collection | `purchase_requests` |

**Logic:**
1. Query current record by ID from database
2. Check: `operator` (Before Action Event variable) = record's `submitter` field → else **End (error):** *"Only the original submitter can cancel this purchase request."*
3. Check: current `status` = `draft` → else **End (error):** *"This purchase request cannot be cancelled once submitted."*
4. If all pass → action executes; cancel workflow sets `status = cancelled`, `cancelled_at`, writes `cancellation_reason` from form input

**Notes:**
- Cancellation is only possible from `draft`. Once submitted, the PR cannot be cancelled regardless of which stage it is in — including when returned to `info_requested`. The submitter must resubmit or contact Procurement if a PR is stuck.
- The Cancel button opens a small form where the submitter enters `cancellation_reason` before confirming
- Procurement cannot cancel on a submitter's behalf; they may only reject
- Admin role bypasses this guard entirely via full system permissions. Admin uses a direct status edit rather than the Cancel button and is not subject to the submitter check or status restrictions.

---

### Guard D — Procurement review finalisation

*(Previously Guard E. Guard D (project/charge consistency) has been removed — project budget tracking is out of scope for v1.)*

| Property | Value |
|---|---|
| Trigger mode | Bound — attached to the "Complete Review / Approve" button in procurement's review form only |
| Actions intercepted | Update |
| Collection | `purchase_requests` |

**Logic:**
1. Query current record by ID from database
2. Check: current `status` = `pending_purchasing_review` → else **End (error):** *"This action is only valid for PRs in the purchasing review stage."*
3. Check: `quote_strategy` is set on the current record → else **End (error):** *"Please select a quote strategy (three quotes or existing supplier) before completing your review."*
4. Query `pr_quotations` where `purchase_request = current PR ID`
5. If `quote_strategy = three_quotes`:
   - Check: count of quotation records ≥ 3 → else **End (error):** *"At least three quotations are required. Please add quotation records before completing your review."*
   - Check: all quotation records have an `attachment` → else **End (error):** *"All quotation records must have a document attached."*
   - Check: exactly one quotation record has `is_selected = true` → else **End (error):** *"Please mark exactly one quotation as the selected quote."*
   - Check: `supplier_selection_rationale` is set on the PR → else **End (error):** *"Please provide a rationale explaining why the selected quotation was chosen."*
6. If `quote_strategy = existing_supplier`:
   - Check: count of quotation records ≥ 1 → else **End (error):** *"Please add at least one quotation record, even for an existing supplier."*
   - Check: the quotation record has an `attachment` → else **End (error):** *"The quotation record must have a document attached."*
   - Check: exactly one quotation record has `is_selected = true` → else **End (error):** *"Please mark the quotation as selected."*
   - Check: `sole_source_justification` is set on the PR → else **End (error):** *"Please provide a justification for using an existing supplier without competitive quotes."*
7. Verify that the selected quotation has a `supplier` set → else **End (error):** *"The selected quotation must have a supplier linked."*
8. At this point `quoted_total`, `quoted_currency`, and `supplier` on the PR should already be set (auto-populated when `is_selected` was set). Verify they are present on the current record → else **End (error):** *"Quote total, currency, and supplier must be set. Re-select the winning quotation to populate these fields."*
9. Query `fx_rates` for `currency_code = quoted_currency` where `effective_date ≤ today`, order by `effective_date` descending, limit 1
10. If no FX rate found, OR if the most recent rate's `effective_date` is more than 30 days before today → **End (success status)** with warning: *"The FX rate for [currency] is missing or older than one month. Finance must update the rate before the Director threshold check can run. You may still approve — the workflow will flag this."*
11. If all pass → action executes; procurement finalisation workflow writes `fx_rate_to_usd`, `quoted_total_usd` (definitive), then routes based on threshold checks

**Notes:**
- Steps 5–6 check both `pr_quotations` records AND fields on the PR itself. The `is_selected` flag on a quotation record triggers an auto-population workflow that writes `supplier`, `quoted_total`, `quoted_currency` back to the parent PR. By the time Guard D fires, these should already be present.
- Step 10 uses success-status End node so the response displays as a warning, not a hard error
- `pr_quotations` records become locked immediately after this guard passes and the workflow fires (status moves past `pending_purchasing_review`)

---

### Guard E — RvC document required

| Property | Value |
|---|---|
| Trigger mode | Bound — attached to the "Record Board Approval" button only |
| Actions intercepted | Update |
| Collection | `purchase_requests` |

**Logic:**
1. Query current record by ID from database
2. Check: current `status` = `pending_rvC_approval` → else **End (error):** *"This action is only valid for PRs awaiting board approval."*
3. Check: `rvC_approval_document` is present in submitted data or on current record → else **End (error):** *"Please upload the signed board approval document before recording approval."*
4. If all pass → action executes; workflow sets `rvC_approved_at`, transitions `status` to `approved`

**Notes:**
- Only procurement role has edit permission at `pending_rvC_approval` status (see Section 3), so the permission layer already limits who can trigger this button
- The button is only visible in the UI when `status = pending_rvC_approval`; the guard provides the API-level backstop

---

## 7. Workflow-triggered field writes

These fields are never set by user form input. They are set exclusively by workflow nodes.

| Field | Trigger event | Written by |
|---|---|---|
| `status` | Every status transition | Approval workflow / cancel workflow / submit workflow |
| `submitter` | First submission | Submit workflow |
| `department` | First submission | Submit workflow (snapshot of submitter.mainDepartment) |
| `submitted_at` | First submission | Submit workflow |
| `supplier` | `pr_quotations.is_selected` set to true | Quotation selection workflow — snapshotted from selected quotation's supplier |
| `quoted_total` | `pr_quotations.is_selected` set to true | Quotation selection workflow — snapshotted from selected quotation's amount |
| `quoted_currency` | `pr_quotations.is_selected` set to true | Quotation selection workflow — snapshotted from selected quotation's currency |
| `fx_rate_to_usd` | Procurement finalises review | Procurement finalisation workflow (definitive) |
| `quoted_total_usd` | Procurement finalises review | Procurement finalisation workflow (= `quoted_total × fx_rate_to_usd`) |
| `approved_at` | Status → `approved` | Approval workflow |
| `rvC_approved_at` | Status → `approved` via "Record Board Approval" action | RvC approval workflow |
| `rejected_at` | Status → `rejected` | Approval workflow |
| `cancelled_at` | Status → `cancelled` | Cancel workflow |
| `rejection_reason_category` | Approver submits rejection | Approval workflow |
| `rejection_comment` | Approver submits rejection | Approval workflow |
| `cancellation_reason` | Submitter submits cancel form | Cancel workflow |

**Note on `supplier`, `quoted_total`, `quoted_currency`:** These are written when procurement marks a quotation as selected (`is_selected = true`), not when they finalise their review. This means the PR shows the selected supplier and amount while still in `pending_purchasing_review`, which is intentional — it gives approvers visibility before the PR reaches their queue. Once written, these fields are locked (system-only; no user edit permission).

---

## 8. Open items

### Resolved

| # | Decision |
|---|---|
| 1 | **Provisional USD at submission** — removed. Submitters no longer enter quote data. Quotes are collected by procurement in `pr_quotations`. The definitive `quoted_total_usd` is set when procurement finalises their review. |
| 2 | **Over-budget PRs** — project budget tracking removed from scope for v1. No budget checks in guards. |
| 3 | **Multi-quote requirement** — in scope for v1. Implemented in Guard D with `quote_strategy`, `pr_quotations` child collection, `sole_source_justification`, and `supplier_selection_rationale`. |
| 4 | **`is_emergency` routing** — closed. UI/priority flag only. No workflow branching. |
| 5 | **Project-budget routing bypass** — removed. Project budget tracking is out of scope for v1. |

### All items resolved

| # | Decision |
|---|---|
| 6 | **Procurement always to director** — confirmed. Procurement-originated PRs always route to director regardless of amount. No amount-based shortcut for procurement. |
| 7 | **Stale FX rate threshold** — confirmed. A rate older than 30 days triggers the Guard D warning. Updated in Guard D step 10. |
| 8 | **Cancellation of stalled PRs** — confirmed. Procurement cannot cancel a PR in `pending_dept_approval`. They may reject it instead. Guard C unchanged — only the original submitter can cancel. |
| 9 | **`is_selected` change after initial selection** — resolved. Free re-selection is allowed while the PR is in `pending_purchasing_review`. The existing lock on `pr_quotations` (enforced when status moves past `pending_purchasing_review`) ensures `is_selected` cannot be changed after procurement finalises. No special workflow logic required. |

---

*End of permissions and guards reference.*
