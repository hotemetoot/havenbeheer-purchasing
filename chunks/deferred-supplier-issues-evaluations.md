# Deferred — supplier_issues + supplier_evaluations

**Status:** postponed under D26. Not scheduled. Revisit when there's user demand for issue logging or formal evaluations.

## Goal (when picked up)
Capture supplier-side incidents (late delivery, wrong goods, quality issues) and structured periodic evaluations.

## Scope (in, when revived)
- `supplier_issues` collection — full schema per [Planning and Design/havenbeheer purchasing — design validation.md](../Planning%20and%20Design/havenbeheer%20purchasing%20—%20design%20validation.md) §11.
- `supplier_evaluations` collection — full schema; `score` 1–5 (per D7).
- ACL: any role can create supplier issues + evaluations; procurement edits/resolves.
- UI: list/detail pages for issues and evaluations on the supplier record.

## Dependencies
- Requires existing `suppliers` collection (already built — see [completed/007-suppliers.md](../completed/007-suppliers.md)).
- Independent of MVP8 and MVP9*.

## Acceptance (when revived)
- S3: anyone logs a supplier_issue → succeeds.
- S4: procurement resolves an issue → succeeds.
- Evaluations: any role creates, procurement edits, score is 1–5.

## Why deferred
Not blocking the PR/PO flow. Procurement can manually adjust `suppliers.current_rating` and `suppliers.notes` for now (per D6). Bring this back when there's a real need.
