# Havenbeheer PR — Permissions & Guards Reference

**Purpose:** Implementation-ready reference for all security rules on the Purchase Request workflow. Covers NocoBase Roles & Permissions configuration and Before Action Event guard designs.

**Scope:** Purchase Requests (`purchase_requests`) and directly related collections. PO-specific rules are in the PO document.

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
| `dept_head` | Department role | Inherited when set as head of a department |
| `procurement` | Department role | Inherited by all members of the Procurement department |
| `director` | Department role | Inherited by all members of the Director department |
| `finance` | Department role | Inherited by all members of the Finance department |
| `admin` | Personal role | System administrators only |

**Role Union mode:** Union only. Users hold the combined permissions of all their roles simultaneously. A procurement member who is also a dept head holds both sets of permissions. Permissions always resolve to the maximum across all roles.

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
| `dept_head` | `department = currentUser.mainDepartment` |
| `procurement` | *(no condition — all records)* |
| `director` | *(no condition — all records)* |
| `finance` | *(no condition — all records)* |

With Union only mode, a dept head who is also a regular member sees the union of both conditions (own PRs OR department PRs). This is correct.

**Edit scope conditions:**

| Role | Condition | Rationale |
|---|---|---|
| `member` | `submitter = currentUser` AND (`status = draft` OR `status = info_requested`) | Submitters edit only their own PRs, only while they hold them |
| `dept_head` | Same as member (dept heads approve via workflow action, not by editing PR content) | |
| `procurement` | `status = pending_purchasing_review` | Procurement edits only PRs in their queue; own drafts covered via member union |
| `director` | *(no edit scope — no edit permission)* | Approves via workflow action only |
| `finance` | *(no edit scope — no edit permission)* | Read-only on PRs |

**Delete:** No role has delete permission on `purchase_requests`. Not configured. Before Action Guard A provides the API-level backstop.

---

## 4. Permissions matrix — supporting collections

| Collection | `member` | `dept_head` | `procurement` | `director` | `finance` | `admin` |
|---|---|---|---|---|---|---|
| `suppliers` | View all | View all | Create, View, Edit all | View all | View all | Full |
| `supplier_issues` | Create own, View all | Create own, View all | Full | View all | View all | Full |
| `supplier_evaluations` | Create own, View all | Create own, View all | Full | View all | View all | Full |
| `projects` | View all | View all | View all | View all | View all | Full |
| `fx_rates` | View all | View all | View all | View all | Create, Edit all | Full |
| `approval_limits` | View all | View all | View all | View all | View all | Full (edit) |

**Notes:**
- Only `procurement` can create supplier records. No Before Action guard needed — the permission layer enforces this.
- Only `finance` can create or edit FX rates.
- Only `admin` can change `approval_limits` values (threshold amounts).
- `projects` is read-only for all non-admin roles through this module; project management is out of scope for v1.

---

## 5. Field permissions — `purchase_requests`

### System-only fields (no role has edit permission — workflow writes only)

These fields must have edit permission explicitly removed for all roles. Only NocoBase workflows may set them.

| Field | Set by workflow when |
|---|---|
| `status` | Every status transition |
| `previous_status` | Transition to `info_requested` (set to the status just before the transition); cleared on resubmit |
| `submitter` | PR submitted (set once, never changed) |
| `department` | PR submitted (snapshotted from submitter.mainDepartment) |
| `submitted_at` | PR submitted |
| `approved_at` | PR reaches approved status |
| `rejected_at` | PR reaches rejected status |
| `cancelled_at` | PR reaches cancelled status |
| `fx_rate_to_usd` | Procurement finalises review (definitive); optionally also at submission as provisional — see ⚠️ below |
| `quoted_total_usd` | Same as fx_rate_to_usd |
| `rejection_reason_category` | Approver rejects |
| `rejection_comment` | Approver rejects |

### Submitter-editable fields (member role, edit permitted in draft / info_requested)

`title`, `description`, `justification`, `expenditure_type`, `charge_to`, `project`, `supplier`, `quoted_total`, `quoted_currency`, `needed_by`, `is_emergency`, `quotation_attachment`, `other_attachments`

Quotation fields (`quoted_total`, `quoted_currency`, `quotation_attachment`) are optional — the submitter may or may not have a quote at submission.

### Procurement-editable fields (procurement role, edit permitted in pending_purchasing_review)

`quoted_total`, `quoted_currency`, `quotation_attachment`, `other_attachments`

Procurement enters or completes the quotation during their review. They do not edit title, description, justification, or other submitter fields.

### Submitter-editable via dedicated Cancel form only

`cancellation_reason` — entered in the Cancel form. Set alongside status = cancelled by the cancel workflow. No general edit permission on this field.

### Visible to all roles that can view the PR (no field-level restriction)

`status`, `previous_status`, `rejection_reason_category`, `rejection_comment`, `cancellation_reason`

⚠️ **Open — provisional USD total:** When a submitter enters a quote at submission, the PR enters `pending_dept_approval` with a quoted amount in a foreign currency but no USD equivalent. The dept head cannot assess whether the PR will require director approval. **Recommendation:** the submission workflow computes a provisional `quoted_total_usd` (using the latest available FX rate, same lookup as the definitive snapshot) and writes it immediately. The procurement finalisation workflow then overwrites it with the definitive value. Requires a decision before workflow design begins.

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
- No exceptions — the former `closed_for_new_pos` field has been removed; PO eligibility is checked at PO creation time
- Procurement's "Close for new POs" operational flag is no longer in the model

---

### Guard B — Submission validation

| Property | Value |
|---|---|
| Trigger mode | Bound — attached to the "Submit for Approval" button only |
| Actions intercepted | Update |
| Collection | `purchase_requests` |

**Logic:**
1. Query current record by ID from database
2. If current `status` ≠ `draft` → **End (error):** *"Only a draft purchase request can be submitted."* (Prevents API-level re-submission; the Resubmit button for info_requested PRs uses a separate action.)
3. Check submitted data: `title` present → else **End (error):** *"A title is required."*
4. Check submitted data: `description` present → else **End (error):** *"A description is required."*
5. Check submitted data: `justification` present → else **End (error):** *"A justification is required."*
6. Check submitted data: `charge_to` set → else **End (error):** *"Please select whether this PR charges to a project or a department."*
7. If `charge_to = project`: check `project` is set → else **End (error):** *"Please select a project, or change 'charge to' to Department."*
8. If `charge_to = department`: check `project` is null → else **End (error):** *"You linked a project but selected 'charge to Department'. Remove the project link or switch to Project."*
9. If `quoted_total` and `quoted_currency` are present in submitted data AND `charge_to = project` AND `project` is set: query `project.approved_budget_usd` and compute remaining budget (sum of `quoted_total_usd` for all PRs on this project where status NOT IN {draft, rejected, cancelled, and the current PR ID}). If `quoted_total_usd_provisional > remaining_budget` → **End (error):** *"This PR would exceed the project's remaining budget of [amount]. Please adjust the project budget or reduce the requested amount."*
10. If all pass → action executes; submission workflow sets `status`, `submitter`, `department`, `submitted_at`, and provisional `quoted_total_usd` if quote data is present

**Notes:**
- Quotation fields are NOT validated for presence at submission — they are optional
- The budget check in step 9 only fires when quote data is present AND the PR is charged to a project; no quote = no budget check at this stage
- The provisional USD total for the budget check uses the latest available FX rate (same lookup as Guard E step 6–7); if no rate exists, skip the budget check at submission — Guard E will catch it definitively
- FX presence check has moved to Guard E (procurement finalisation)

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
3. Check: current `status` ∈ {`draft`, `pending_dept_approval`, `info_requested`} → else **End (error):** *"This purchase request cannot be cancelled at its current stage."*
4. If `status = info_requested`: check `previous_status` ≠ `pending_director_approval` → else **End (error):** *"This request was returned by the Director after procurement approval. It can no longer be cancelled — please resubmit or contact Procurement."*
5. If all pass → action executes; cancel workflow sets `status = cancelled`, `cancelled_at`, writes `cancellation_reason` from form input

**Notes:**
- The Cancel button opens a small form where the submitter enters `cancellation_reason` before confirming
- Procurement cannot cancel on a submitter's behalf; they may only reject

---

### Guard D — Project / charge consistency

| Property | Value |
|---|---|
| Trigger mode | Global |
| Actions intercepted | Create, Update |
| Collection | `purchase_requests` |

**Logic:**
1. If `charge_to` and `project` are not present in the submitted data → pass through (neither field was touched in this update)
2. If `charge_to = project` AND `project` is null → **End (error):** *"Please select a project, or change 'charge to' to Department."*
3. If `charge_to = department` AND `project` is not null → **End (error):** *"You linked a project but selected 'charge to Department'. Remove the project link or switch to Project."*
4. Otherwise → pass through

---

### Guard E — Procurement review finalisation

| Property | Value |
|---|---|
| Trigger mode | Bound — attached to the "Complete Review / Approve" button in procurement's review form only |
| Actions intercepted | Update |
| Collection | `purchase_requests` |

**Logic:**
1. Query current record by ID from database
2. Check: current `status` = `pending_purchasing_review` → else **End (error):** *"This action is only valid for PRs in the purchasing review stage."* (API-level protection)
3. Check submitted data or current record: `quoted_total` present and > 0 → else **End (error):** *"A quoted total is required before this purchase request can be approved."*
4. Check submitted data or current record: `quoted_currency` set → else **End (error):** *"Please set the quote currency."*
5. Check submitted data or current record: `quotation_attachment` present → else **End (error):** *"Please attach at least one quotation document."*
6. Query `fx_rates` for `currency_code = quoted_currency` where `effective_date ≤ today`, order by `effective_date` descending, limit 1
7. If no FX rate found → **End (success status)** with warning message: *"No FX rate found for [currency]. The USD equivalent cannot be calculated. Finance must update the rate before the Director threshold check can run. You may still approve — the workflow will flag this."*
8. Compute `quoted_total_usd` using the FX rate found. If `charge_to = project` AND `project` is set: query remaining budget (sum of `quoted_total_usd` for all PRs on this project where status NOT IN {draft, rejected, cancelled} AND ID ≠ current PR). If `quoted_total_usd > remaining_budget` → **End (error):** *"This PR would exceed the project's remaining budget of [amount]. The project budget must be adjusted before this request can be approved."*
9. If all pass → action executes; procurement finalisation workflow writes `fx_rate_to_usd`, `quoted_total_usd` (definitive), then continues routing (project-budget bypass check or threshold check → director or approved)

**Notes:**
- Step 3–5 check both submitted data AND current record values. Procurement may have entered the quote fields earlier in the same session (they're already on the record), so the guard must not require them to be in the submitted data object specifically — only that they exist somewhere on the record.
- Step 7 uses success-status End node so the response displays as a warning, not a hard error

---

## 7. Workflow-triggered field writes

These fields are never set by user form input. They are set exclusively by workflow nodes. Documenting here to ensure no edit permissions are accidentally granted for them.

| Field | Trigger event | Written by |
|---|---|---|
| `status` | Every status transition | Approval workflow / cancel workflow / submit workflow |
| `previous_status` | Transition **to** `info_requested` | Approval workflow (Return node) — set to status before return |
| `previous_status` (clear) | Transition **out of** `info_requested` | Resubmit workflow — set to null |
| `submitter` | First submission | Submit workflow |
| `department` | First submission | Submit workflow (snapshot of submitter.mainDepartment) |
| `submitted_at` | First submission | Submit workflow |
| `fx_rate_to_usd` | Procurement finalises review | Procurement finalisation workflow (definitive) |
| `quoted_total_usd` | Procurement finalises review | Procurement finalisation workflow (definitive) |
| `fx_rate_to_usd` (provisional) | Submission, if quote data present | Submit workflow (provisional — overwritten at procurement stage) |
| `quoted_total_usd` (provisional) | Submission, if quote data present | Submit workflow (provisional — overwritten at procurement stage) |
| `approved_at` | Status → approved | Approval workflow |
| `rejected_at` | Status → rejected | Approval workflow |
| `cancelled_at` | Status → cancelled | Cancel workflow |
| `rejection_reason_category` | Approver submits rejection | Approval workflow |
| `rejection_comment` | Approver submits rejection | Approval workflow |
| `cancellation_reason` | Submitter submits cancel form | Cancel workflow |

---

## 8. Open items

Items resolved are noted inline. Remaining items are ordered by implementation impact.

### Resolved

| # | Decision |
|---|---|
| 1 | **Provisional USD at submission** — confirmed. Submit workflow computes provisional `quoted_total_usd` if `quoted_total` and `quoted_currency` are present. Overwritten definitively at procurement finalisation. |
| 3 | **Multi-quote requirement** — deferred to v2. Data model supports it (multi-file `quotation_attachment`). A future Guard E extension can check quote count against a value threshold when policy is defined. |
| 4 | **`is_emergency` routing** — closed. UI/reminder flag only. No workflow branching. Signals to procurement and finance to prioritise. |
| 2 | **Over-budget PRs** — hard block (error). Guard B checks remaining budget at submission if a quote is present. Guard E checks definitively at procurement finalisation. Remaining budget = `approved_budget_usd − SUM(quoted_total_usd where status NOT IN {draft, rejected, cancelled})`. Budget adjustment is a manual admin action outside the system. |

### Still open — workflow decisions needed before building approval workflow

| # | Item | Impact if unresolved |
|---|---|---|
| 5 | ⚠️ **Project-budget routing bypass** — PRs within an approved project budget skip the director entirely. Confirm whether any per-PR amount cap applies even for project PRs (e.g., a $500K PR within a $2M approved project budget would bypass the director). | Affects routing condition in the approval workflow; no data model change needed either way |
| 6 | ⚠️ **Procurement always to director** (Q6) — confirm procurement-originated PRs always go to director regardless of amount and project status | Affects approval workflow routing condition |
| 7 | ⚠️ **Stale FX rate threshold** (Q10) — at what age does a rate trigger the Guard E warning? Currently warns only if no rate exists at all | Affects Guard E step 7 — add age condition once policy is defined |
| 8 | ⚠️ **Cancellation of stalled PRs** (Q2) — can procurement cancel a PR stuck in `pending_dept_approval`? | If yes: Guard C operator check needs an OR condition for procurement role |

---

*End of permissions and guards reference.*
