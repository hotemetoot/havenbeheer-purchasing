# 002 — Cancel by submitter (draft only) ✓

**Verified:** 2026-05-24 by user.

## Goal
Submitter can cancel their own PR while it is still in `draft`. Once submitted (any non-draft status), cancellation is never allowed (D1).

## What was built
- `purchase_requests.cancellation_reason` (textarea) and `cancelled_at` (datetime).
- New status value `cancelled`.
- Cancel workflow (key `59ezifdoqvj`, type custom-action) — embedded Guard C: user.id == submitter.id AND status == "draft".
- Cancel PR Guard (key `8yngslauuj4`, request-interception) — server-side guard.
- Cancel button + popup form (built by user); linkage rule makes it visible only when status = `draft`.
- Field-level permissions on `cancellation_reason`.

## Live IDs
See [project_current_state.md](../project_current_state.md).

## Scenarios verified (C1–C4)
- C1: Cancel a draft → cancelled ✓
- C2: Try to cancel a submitted PR (any non-draft status incl. info_requested) → blocked ✓
- C3: Try to cancel someone else's draft PR → blocked ✓
- C4: MVP1 scenarios A–D still pass ✓
