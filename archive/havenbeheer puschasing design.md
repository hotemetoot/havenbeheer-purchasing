---

# Purchase Request (PR) — Workflow & Guards

**NocoBase‑oriented conceptual summary**

This document summarizes the **Purchase Request (PR)** model, approval logic, and enforcement rules as designed for **NocoBase v2**, using **Approval workflows** and **Before Action Events** correctly and deliberately.

---

## 1. Core Design Principles

### Separation of Concerns

- **Approval workflows** handle *human decisions* (pass / reject / return)
- **Before Action Events** enforce *hard business rules*
- **Collection fields** represent the authoritative business state

Approval nodes **do not enforce legality**.
Before Action Events **must enforce non‑negotiable rules**.

---

## 2. PR as a Business Object

### Purpose of a Purchase Request

- A PR is an **approval artifact**
- Once approved or rejected, it is **complete and immutable**
- Execution (purchasing, receiving, payment) happens **outside** the PR

---

## 3. PR Status Model

### Stored `status` values

draft

pending_dept_approval

pending_purchasing_review

pending_director_approval

approved

rejected

cancelled

### Important

- `info_requested` is **not** a real status
- Info requests are handled as a **temporary detour**, not a lifecycle phase

---

## 4. Required PR Fields (Minimum)

| Field | Purpose |
| --- | --- |
| `status` | Authoritative PR lifecycle state |
| `total_amount` | Threshold logic |
| `department_id` | Determines dept approver |
| `submitter_id` | Ownership |
| `return_to_status` (nullable) | Resume point after info request |
| `submitted_at` | Audit |
| `approved_at` | Audit |
| `rejected_at` | Audit |

---

## 5. PR Approval Workflow (Structure)

### High‑level flow

Draft

→ Dept Head Approval

→ Purchasing Review

→ (≤ threshold) Approved

→ (> threshold) Director Approval → Approved

There are **three Approval nodes**, each with a single responsibility.

---

## 6. Approval Nodes (Responsibilities Only)

### 1. Department Head Approval

**Purpose:** Validate business need

- Approver: department head (dynamic)
- Actions: Pass / Reject / Return
- Outcomes:
  - Pass → `pending_purchasing_review`
  - Reject → `rejected` (terminal)
  - Return → set `return_to_status = pending_dept_approval`

---

### 2. Purchasing Review

**Purpose:** Commercial review + threshold check

- Approver: purchasing role/group
- Actions: Pass / Reject / Return
- Outcomes:
  - Pass → next step depends on threshold (guarded)
  - Reject → `rejected`
  - Return → set `return_to_status = pending_purchasing_review`

> Threshold enforcement is **not** done in the Approval node itself.

---

### 3. Director Approval

**Purpose:** High‑value oversight

- Approver: director role
- Actions: Pass / Reject / Return
- Outcomes:
  - Pass → `approved`
  - Reject → `rejected`
  - Return → set `return_to_status = pending_director_approval`

---

## 7. “Info Requested” (Return) Pattern

- Implemented using the **Return action** in Approval nodes
- On Return:
  - `return_to_status` is set
  - main `status` remains unchanged
- On resubmission by submitter:
  - PR resumes exactly at `return_to_status`
  - `return_to_status` is cleared

This avoids creating an artificial `info_requested` state.

---

## 8. Before Action Guards (Critical)

All rules below are enforced using **Before Action Event workflows**.

### Guard 1 — Immutability

**Rule:** Approved, rejected, or cancelled PRs cannot be modified.

- Applies to: Update / Delete / Edit line items
- Condition:

IF status IN (approved, rejected, cancelled)

→ intercept action

---

### Guard 2 — Submission Validity

**Rule:** Only draft PRs may be submitted.

IF status != draft

→ intercept submission

---

### Guard 3 — Threshold Enforcement (Most Important)

**Rule:** Purchasing cannot approve above threshold.

- Applies when purchasing attempts **Pass**

IF approver_role = purchasing

AND total_amount > THRESHOLD

AND approval_action = Pass

→ intercept

This prevents bypassing policy via UI or API.

---

### Guard 4 — Director Scope

**Rule:** Low‑value PRs must never reach the director.

IF entering_director_approval

AND total_amount ≤ THRESHOLD

→ intercept

---

### Guard 5 — Cancellation Rules

**Rule:** Submitter may only cancel early‑stage PRs.

IF status IN (pending_purchasing_review, pending_director_approval)

→ intercept cancellation

---

## 9. What the PR Workflow Explicitly Does *Not* Handle

Out of scope by design:

- Budget accounting
- Vendor selection
- Purchase Order creation
- Receiving or fulfillment
- Payment logic

These belong to **PO workflows or later layers**, not PR.

---

## 10. Why This Fits NocoBase Well

✅ Approval nodes used only for human decisions
✅ Before Action Events enforce real authority
✅ State lives in data, not workflow illusion
✅ Threshold logic cannot be bypassed
✅ Clean audit trail
✅ Easy to extend without breaking the model

---