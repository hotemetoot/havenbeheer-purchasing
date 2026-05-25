# 001 — Three-stage approval ✓

**Verified:** 2026-05-17

## Goal
Establish the core 3-stage approval flow (dept → procurement → director) with approve / return / reject actions, plus a dept-owner skip when the submitter is the department's main approver.

## What was built
- `purchase_requests` base fields: title, description, justification, submitter (m2o users), department (m2o departments), status, rejection_reason_category, rejection_comment.
- Departments: Procurement, Director, Finance, Operations. `main_approver` and `secondary_approver` (m2o users) on each. `users.on_leave` (boolean).
- ACL: member, dept owner, procurement, director scopes; field-level read-only on system fields. See [decisions.md](../decisions.md) D21.
- PR Approval workflow (`approval` type) with dept-owner-skip condition, three approval nodes (Dept, Procurement, Director), each with approve/return/reject branches.
- Purchase Requests page (UID `cuycec133qb`), table block with View / Edit / Submit-for-Approval record actions.
- Submit-for-Approval action wired as `RecordTriggerWorkflowActionModel` — no bridge workflow needed.

## Live IDs (current)
See [project_current_state.md](../project_current_state.md) for the active workflow key (`cv237r8h7k9`) and node IDs. The original workflow key/version IDs noted in the v3 plan (`p4n6dffjcgq` / `364960795000832`) are stale; the workflow was rebuilt in subsequent MVPs.

## Scenarios verified (A–D)
- A. Happy path (Alice → Oliver → Pat → Dana → approved) ✓
- B. Dept-head edits while info_requested ✓
- C. Return from each approver → info_requested ✓
- D. Reject from any approver → rejected with reason fields ✓

Routing redesign verified:
- Alice submits → Oliver (Operations main_approver) gets task ✓
- Oliver submits → dept stage skipped, Pat gets task directly ✓
- Pat submits → both dept + procurement skipped, Dana gets task ✓
