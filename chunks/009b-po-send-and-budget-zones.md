# 009b — Send PO + budget zones + zone 2/3 notifications

## Goal
Procurement can transition a draft PO to `sent`. The transition runs the budget-overrun guard (zones 1/2/3) and, in zone 2, notifies director + Finance head in-app.

## Scope (in)
- PO status transitions: `draft → sent`, `draft → cancelled`.
- **Budget overrun guard** at `draft → sent` (per PO design validation §5):
  - **zone 1:** cumulative PO total (USD) ≤ PR `quoted_total_usd` → proceed.
  - **zone 2:** PR < cumulative ≤ 110% PR → require `budget_override_comment`; in-app notify Director + Finance dept head (D19).
  - **zone 3:** > 110% → block.
  - Tolerance hardcoded at 110% (PO design decision 14).
- Under D9 there's only one PO per PR, but the zone logic still matters: procurement could inflate the PO above the approved PR amount.

## Scope (out)
- Receiving (9c), completion/closing (9d), printing (9e).
- Email notifications — D19, in-app only.

## Dependencies
- Requires 9a.

## Acceptance
- Z1: zone 1 → PO sent normally.
- Z2: zone 2 → require comment, send + in-app notify Director + Finance head.
- Z3: zone 3 → blocked at send.
- Manual verification by user.

## Phases
- **9b.1** Send-PO workflow + budget zone evaluation.
- **9b.2** In-app notification side-effects (Director + Finance dept head).
- **9b.3** Verify Z1–Z3.
