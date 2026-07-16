# 009b — Send PO + budget zones + zone 2/3 notifications

## Goal
Procurement can transition a draft PO to `sent`. The transition runs the budget-overrun guard (zones 1/2/3) and, in zone 2, notifies director + Finance head in-app. Procurement can also close a draft PO with a reason + comment.

## Scope (in)
- PO status transitions: `draft → sent`, `draft → closed` (with reason+comment).
- **Cancel-into-close collapse**: drop `cancelled` from the PO status enum and `cancelled_at` field; add `no_longer_required` to `close_reason`. Two terminal states only: `completed`, `closed`. (D-entry to record at session end.)
- **Budget overrun guard** at `draft → sent` (per PO design validation §5):
  - **zone 1:** PO `total_usd` ≤ PR `quoted_total_usd` → proceed.
  - **zone 2:** PR < PO `total_usd` ≤ 110% PR → require `budget_override_comment`; in-app notify Director + Finance dept head (D19).
  - **zone 3:** > 110% → block.
  - Tolerance hardcoded at 110% (PO design decision 14).
- Under D9 there's only one PO per PR; zone logic still matters because procurement may inflate PO total above PR amount.

## Scope (out)
- Receiving (9c), close-from-non-draft (9d), completion (9d), immutability (9d), printing (9e).
- Email notifications — D19, in-app only.

## Dependencies
- Requires 9a.

## Acceptance
- Z1: zone 1 → PO sent normally.
- Z2: zone 2 → require comment, send + in-app notify Director + Finance head.
- Z3: zone 3 → blocked at send.
- Close-from-draft: draft PO + Close (reason + comment) → status=closed, closed_at set.
- Manual verification by user.

## Phases
- **9b.1** Send-PO custom-action workflow + budget zone evaluation.
- **9b.2** Close-PO from draft: update-record popup form + collection-trigger workflow stamping status=closed, closed_at.
- **9b.3** Zone-2 in-app notification side-effects (Director + Finance dept head).
- **9b.4** Send + Close buttons on PO surfaces.
- **9b.5** Verify Z1/Z2/Z3 + close-from-draft.

Detail in [plans/vast-dreaming-sloth.md](../plans/vast-dreaming-sloth.md).
