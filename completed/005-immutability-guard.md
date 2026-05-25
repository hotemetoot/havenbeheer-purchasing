# 005 — Guard A (PR immutability when terminal) ✓

**Verified:** 2026-05-24 by user. **Known limitation:** D24 (bulk-update bypass — deferred).

## Goal
Block edit / delete on any `purchase_request` whose status is terminal (`approved`, `rejected`, `cancelled`).

## What was built
- Guard A workflow: key `496ookqmg01`, version ID `366217145548800`.
- Type: request-interception, global, sync. Actions intercepted: update + destroy on `purchase_requests`.
- Node chain: Query (`q33wtlxitr1`) → Condition (status ∈ {approved, rejected, cancelled}, key `nbs3zmsr60x`) → branch 1: response-message + end(endStatus:-1).

## Scenarios verified
- I1: edit approved via API → blocked ✓
- I2: edit rejected via API → blocked ✓
- I3: edit cancelled via API → blocked ✓
- I4: edit draft → succeeds ✓
- I5: edit info_requested → succeeds ✓
- I6: edit pending_* → succeeds ✓

## Known limitation (D24, deferred)
Bulk update sends target IDs via `$context.params.filter.$and[0].id.$in`, not `filterByTk`. The Query node only looks up by `filterByTk` → returns nothing → condition false → guard passes. Fix requires a Script/JSON-query node to extract IDs from `$context.params.filter`, or a dedicated bulk-update workflow. Deferred post-MVP5. See [decisions.md](../decisions.md) D24.
