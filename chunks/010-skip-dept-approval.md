# 010 — Optional skip-dept-approval

## Goal
Let the submitter optionally skip the department-head approval stage on a PR. When skipped,
the dept head is not a blocking approver but is kept in the loop: notified in-app and able
to view the PR. Default is OFF (dept approval required). Same manual-judgment philosophy as
D23.

## Scope (in)
- `purchase_requests.skip_dept_approval` (boolean, default false).
- PR Approval workflow (`cv237r8h7k9`) revision: when the submitter is NOT their own dept
  approver, branch on the toggle — true → notify dept head (FYI) + route to
  `pending_purchasing_review`; false → existing Dept Owner Approval. The pre-existing
  "submitter IS dept approver → skip" path is unchanged and does not notify.
- In-app FYI notification to the submitter's `mainDepartment.main_approver` (fallback to
  `secondary_approver` when `main_approver.on_leave`, mirroring D21; main-only acceptable
  for v1 if fallback adds a whole branch).
- Dept-head view access to a skipped PR (verify existing dept-owner view scope first; widen
  only if it's task-driven).
- UI: toggle on PR create form (next to `needs_director_approval`); read-only on PR detail
  popup for audit.

## Scope (out)
- Pull-back / re-injection of dept approval after skip (FYI-only, D19). Deferred unless a
  real need emerges.
- Per-department "approval required" default (admin-set policy). Could layer on later if a
  pattern emerges; out for now since rules are unclear and per-PR flexibility is wanted.
- Email/SMTP — D19, in-app only.

## Dependencies
- Requires MVP1 (approval workflow + dept-owner skip condition) and MVP4 (sits beside
  `needs_director_approval`).

## Acceptance
- S1: toggle OFF (default) → dept approval task fires as today (no regression).
- S2: toggle ON → no dept task; PR lands in `pending_purchasing_review`; dept head gets an
  in-app notification and can open the PR.
- S3: submitter-is-approver path unchanged (auto-skip, no self-notification).
- S4: procurement → director paths unchanged from the toggle-ON entry point.
- S5: post-revision node count intact (no dropped branches); 3 approval surfaces resolve to
  the new version.
- Manual verification by user.

## Phases
- **10.1** Add `skip_dept_approval` field (default false).
- **10.2** Verify in-app notification node availability (plugin + workflow node type).
- **10.3** Revise approval workflow: new condition branch + notify node; verify node count.
- **10.4** Dept-head view access (verify scope; widen if needed).
- **10.5** UI: create-form toggle + read-only on detail popup.
- **10.6** Verify S1–S5.

Detail in [plans/i-have-to-make-resilient-wall.md](../plans/i-have-to-make-resilient-wall.md).
