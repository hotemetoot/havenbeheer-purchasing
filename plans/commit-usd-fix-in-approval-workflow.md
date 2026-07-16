# Plan: fix `committed_usd` — commit at approval, inside the PR Approval workflow

**Status:** EXECUTED 2026-07-16 — built + E2E-verified live; see D78 in decisions.md for the
as-built record. Two deviations from this plan: (1) the write node needed `individualHooks: true`
(the Phase 3 contingency fired — `remaining_usd` stayed stale on the silent write), costing a
second revision (final enabled: `375705420496896`); (2) the delete recompute had the same
formula-staleness flaw and was also revised (`375705873481728` enabled, old disabled).
Approvals in Phase 3 were driven via `approvals:create` / `approvalRecords:submit` as the real
signed-in test users (the runner's documented path) after the automated browser could not land
clicks in the approver modal; the modal's rendering was visually verified once. Drafted 2026-07-15;
reviewed + amended 2026-07-16.
**Env:** `havenbeheer` — NocoBase at http://localhost:13000, canonical tree `~/nocobase-dev/havenbeheer`.

**Review findings (2026-07-16, verified live against enabled revision 375674676248576):**
- Core premise CONFIRMED: aggregate `wt7bh1uh2gn` filters
  `project.id == current AND (status == approved OR id == {{$context.data.id}})` —
  it includes the PR being approved, so writing its result at approval is correct
  and idempotent. `project` is in the trigger appends, so
  `{{$context.data.project.id}}` resolves.
- Disable-not-keep-both CONFIRMED right: the recompute is `sync:true` on the hook
  write, the approval workflow is async; if both ran, the recompute (approved-only
  filter, no self-inclusion) could overwrite the correct total with a stale one.
- Two gaps added below: (a) verify approved PRs are locked against status/amount
  edits before claiming delete is the only decrease path (Phase 0); (b)
  `remaining_usd` is a formula recomputed in save hooks — the new node's
  `individualHooks: false` may skip it (Phase 3 contingency).
- Test-suite impact added to wrap-up: R29's `committed_usd: 5000` state case was
  green despite the bug (committed lags one approval; the last chain's recompute
  covered the earlier siblings) — the suite cannot detect this bug as written.
  Regression case must assert committed after the FIRST approval.

---

## The problem (one paragraph)

A project's `committed_usd` is not updating when a project-linked PR is approved.
`committed_usd` is maintained by a standalone collection-event workflow
(`Project Commit: recompute (create/update)`, key `j2fp3wa4o1k`). That workflow only
fires on **hook-firing field writes** to a PR (quote entry, etc.). The approval that
flips a PR to `approved` is written by the PR Approval workflow's update node with
`individualHooks: false` — a silent bulk write that does **not** fire the collection
event. So the recompute runs only *before* approval (status still pending). Since
**D53 (2026-06-28)** the recompute counts only `status == approved` PRs, and the
recompute never runs at a moment the PR is approved → the approved amount is never
counted → `committed_usd` stays at its pre-approval value (0).

Proof gathered this session: across the last 200 recompute executions the PR's own
snapshot status was only ever `draft` / `pending_dept_approval` /
`pending_purchasing_review` — never `approved`. Running the recompute's own aggregate
by hand returns the correct 2000, so the logic is fine; only the trigger timing is wrong.

## The fix (business rule)

Commit budget **at the moment of approval**, from inside the PR Approval workflow —
the one place that knows the approval just happened and already computes the committed
total. All project-linked PRs funnel through a single approval node, so one update
node covers procurement / director / board approvals alike. Non-project PRs never
touch `committed_usd`.

- **Add** one update node to the PR Approval workflow that writes the already-computed
  committed total onto the project, on the **not-over-budget** branch, right after the
  PR is set to approved.
- **Disable** (not delete) the standalone create/update recompute — its job is now done
  by the in-approval node. Disable rather than delete so it's a trivial rollback.
- **Keep** the delete recompute enabled — it covers the one decrease-event the
  in-approval node structurally can't: an approved PR being deleted.

Accepted residual gap: if someone sets a PR's status to `approved` **directly via
API/admin**, bypassing the approval workflow, `committed_usd` won't update. Normal
approvals always run through the plugin, so this is accepted (noted in D78).

---

## Live IDs (verified 2026-07-15 — RE-VERIFY at run time via nb-drift-scout)

| Thing | ID / key |
|---|---|
| PR Approval workflow (enabled, current) | id `375674676248576`, key `cv237r8h7k9`, type `approval` |
| Insertion-point node: `Project drawdown → Approved` | key `47fd05ite4i` (id `375674680442898`) — branch 0 (not-over-budget) of `Over project budget?` (key `8ra9iw4f61z`); its downstream is notification `fvbrc41tdl2` |
| Aggregate holding the committed total | node key `wt7bh1uh2gn` (`Project committed (Σ child quoted_total_usd)`) |
| Recompute to DISABLE (create/update) | id `372610306736128`, key `j2fp3wa4o1k`, enabled+current |
| Recompute to KEEP (delete) | id `372610338193408`, key `0mckvnf319y`, enabled+current |
| Data fix target | project PRJ-26-0079, id `375663792029696` → `committed_usd = 2000`, `remaining_usd` (formula) → 8000 |

> **Why re-verify:** the app is source of truth. A revision remaps nothing if keys are
> forced, but confirm the enabled approval-workflow id and that node keys `47fd05ite4i`
> and `wt7bh1uh2gn` still exist in the current revision before touching anything.

---

## New node to add

Insert **after** `Project drawdown → Approved` (`47fd05ite4i`), before its notification,
in the new revision. Config (mirrors the existing update nodes' shape):

```json
{
  "collection": "projects",
  "usingAssignFormSchema": false,
  "assignFormSchema": {},
  "params": {
    "individualHooks": false,
    "filter": { "$and": [ { "id": { "$eq": "{{$context.data.project.id}}" } } ] },
    "values": { "committed_usd": "{{$jobsMapByNodeKey.wt7bh1uh2gn}}" }
  }
}
```
Title: `Write committed_usd to project`. `individualHooks: false` is correct here —
the write targets `projects`, and nothing listens on `projects` updates
(`remaining_usd` is a formula field that recomputes on save; the delete recompute
listens on `purchase_requests`, not `projects`). No loop risk.

---

## Steps (execute phase by phase; pause after each)

### Phase 0 — drift check
1. Run `nb-drift-scout` for scope: workflow `cv237r8h7k9` (PR Approval), workflows
   `j2fp3wa4o1k` / `0mckvnf319y` (recompute pair), collection `projects`
   (`committed_usd`, `remaining_usd`), project PRJ-26-0079. Confirm the IDs/keys above.
   Report any drift before proceeding.
1b. **Verify approved-PR immutability** (added 2026-07-16): the "delete is the only
   decrease path" claim in the fix holds only if no role/guard path can take a PR
   out of `approved` or edit an approved PR's `quoted_total` / `fx_rate_to_usd`.
   Read the `purchase_requests` ACL grants (update scopes + field whitelists per
   role) and any request-interception guards on `purchase_requests:update`.
   - If approved PRs are locked → note "verified" in D78.
   - If an edit path exists → STOP, report it, and decide with Alexander whether
     to keep the create/update recompute enabled or accept the gap explicitly.

### Phase 1 — revise the approval workflow and add the node
2. **This workflow has executed → cannot edit in place.** Create a new revision.
   - Use the `nocobase-workflow-manage` skill for the revision.
   - **Trap (memory `feedback_workflow_revision_key_bug`):** the CLI `workflows revision`
     command mints a *new* key (stray copy). Force the **same key** `cv237r8h7k9` via a
     raw `--body` so the new version stays same-lineage.
   - **Trap (approval blueprint):** this is an `approval`-type workflow with approval
     nodes (Dept Owner, Custom Approver, Procurement, Director, Board). After revision,
     verify each approval node in the new revision has its approver surface + working
     comment models (memory: `feedback_approval_blueprint_comment_models`,
     `feedback_flow_nodes_duplicate_single_node`). If any comment model is missing,
     pre-create it as admin and set the action's `commentFormUid`.
3. In the **new** revision, add the update node above, wired between `47fd05ite4i` and
   its downstream notification `fvbrc41tdl2`. Confirm node keys carried over from the
   revision; if they were remapped, find the copies of `47fd05ite4i` and `wt7bh1uh2gn`
   in the new revision and use those.
4. Read back the new revision's tree; confirm the not-over-budget branch is now
   `Project drawdown → Approved` → `Write committed_usd to project` → notification.
5. **Enable** the new revision, **disable** the old (`375674676248576`).
6. **STOP — confirm with Alexander before the E2E test** (this is the first live approval
   on the new revision).

### Phase 2 — disable the redundant recompute
7. Disable `Project Commit: recompute (create/update)` (id `372610306736128`,
   key `j2fp3wa4o1k`): `resource update --resource workflows --filter-by-tk 372610306736128 --values '{"enabled":false}'`.
8. Leave `Project Commit: recompute (delete)` (`372610338193408`) **enabled**. Confirm
   it's still enabled after.

### Phase 3 — E2E verification (test gate)
9. Create a small test project (approved, budget e.g. 5000) and a project-linked PR
   under it (quote e.g. 1000). Drive it through the real approval UI as the proper
   signed-in users (procurement etc.) — **not** admin, **not** `workflows execute`
   (memory: custom/approval workflows can't be driven headless).
10. After approval, read the project: `committed_usd` == 1000, `remaining_usd` == 4000.
    **Contingency (added 2026-07-16):** `remaining_usd` is a formula recomputed in
    save hooks; the new node writes with `individualHooks: false`, which may skip
    the recompute (same setting as the old recompute node, so not a regression —
    but check). If `committed_usd` is right and `remaining_usd` is stale: first
    confirm nothing listens on `projects` updates (collection-event workflows),
    then flip the new node to `individualHooks: true` and re-test.
11. Approve a second project-linked PR (e.g. 1500) on the same project → `committed_usd`
    == 2500 (proves the node writes the full aggregate, not an increment).
12. If green, continue. If not, roll back (Phase 5) and diagnose.

### Phase 4 — one-off data correction for PRJ-26-0079
13. Recompute-by-hand check: sum of `quoted_total_usd` where `project.id = 375663792029696`
    AND `status = approved` (expected 2000, from PR-26-0275).
14. Set it: `resource update --resource projects --filter-by-tk 375663792029696 --values '{"committed_usd":2000}'`.
15. Read back: `committed_usd` == 2000, `remaining_usd` == 8000 (formula auto-recomputes
    on save; if it didn't, save any field on the project to force it, or investigate).

### Phase 5 — rollback (only if needed)
- Re-enable the create/update recompute (`372610306736128` → `enabled:true`).
- Disable the new approval revision, re-enable the old (`375674676248576`).
- The node addition lives only in the new revision, so disabling it fully reverts.

---

## Wrap-up (per CLAUDE.md session-end routine)

- **Append D78 to decisions.md** (text below).
- **docs/user-guide.md:** no user-visible label change (committed/remaining already
  displayed); only note the timing fix if the guide describes when commitment happens.
- **roadmap.md:** update status if this maps to a roadmap line.
- **Backup (write-once):**
  `nb backup create --output "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Nocobase/Backups/havenbeheer/havenbeheer_$(date +%Y-%m-%d_%H%M).nbdata"`
- **Commit** after: the D78 entry, and after the verified workflow change.
- **tests/plan.yaml (mandatory, added 2026-07-16):**
  - Reword two rule texts that name the old mechanism (business outcome unchanged):
    - R26: "committed_usd (maintained by the recompute workflow)" → written at
      approval by the PR Approval workflow (D78); delete recompute still covers
      decreases.
    - R29: "the project's committed amount recomputes from approved PRs only" →
      the committed amount is written at the moment of approval from inside the
      approval workflow, equal to the sum of approved PRs including this one.
  - **Add a first-approval regression case**: assert `committed_usd` is correct
    immediately after the FIRST project-linked PR approval (e.g. state-assert
    `committed_usd: 1000` after pr_within's chain, before the next sibling runs).
    The existing final-state-only R29 case passed under the buggy behavior
    (committed lagged one approval; the last chain's hook write covered earlier
    siblings) — it cannot catch this bug.
  - Sweep stale revision-id comments (plan.yaml cites revision 373617786945536;
    live is 375674676248576 and will change again with the new revision).
  - Run the full suite via `nb-test` and get it green before closing the chunk.

---

## D78 entry to append to decisions.md

```
## D78 — committed_usd written at approval, inside the PR Approval workflow (2026-07-15)

**Decision:** The project `committed_usd` is now written by a new update node inside the
PR Approval workflow (`cv237r8h7k9`), on the not-over-budget branch right after
`Project drawdown → Approved` (`47fd05ite4i`), writing the already-computed aggregate
`wt7bh1uh2gn` onto the project. The standalone `Project Commit: recompute (create/update)`
(`j2fp3wa4o1k`) is **disabled** (not deleted — trivial rollback). The delete recompute
(`0mckvnf319y`) stays enabled.

**Why:** D53's amendment moved the commit count to `status == approved`, but the recompute
is a collection-event workflow that only fires on hook-firing field writes (quote entry,
pre-approval). The approval's status→approved write uses `individualHooks: false` (silent
bulk update) and never fires it, so the approved amount was never counted and
`committed_usd` stuck at its pre-approval value (0). Proof: 200/200 recompute executions
snapshotted the PR as pending, never approved. The in-approval aggregate already computes
the correct total for the budget check and then discarded it; this decision stops
discarding it.

**How to apply:** Commit updates happen at approval, from inside the approval workflow.
Do not rely on the create/update recompute (disabled). All project-linked PRs funnel
through the single `Project drawdown → Approved` node, so one write covers procurement/
director/board. Decrease-on-delete still handled by `0mckvnf319y`.

**Accepted gap:** setting status `approved` directly via API/admin (bypassing the approval
plugin) will not update `committed_usd`. Not a real operational path.

**Affects:** MVP with project budgets (D47/D49/D53 lineage). One-off correction applied to
PRJ-26-0079 (committed 2000 / remaining 8000).

**Status:** built + E2E-verified live <fill date>. Rollback = re-enable `j2fp3wa4o1k`,
revert to the prior approval revision.
```
