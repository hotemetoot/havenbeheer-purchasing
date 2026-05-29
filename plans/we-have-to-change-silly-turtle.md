# Plan — Mandatory director approval at ≥ $300 USD

## Context

Today, whether a PR goes to the Director is driven **entirely** by the submitter's manual
`needs_director_approval` checkbox (D23 — we deliberately replaced the old automatic $1,500
threshold with submitter judgment). The team now wants a hard floor: **any PR whose USD total
is $300 or more must always go to the Director**, regardless of the checkbox.

This is not a return to a pure-threshold model — it's a hybrid. The checkbox stays as a
*voluntary escalation* (a submitter can still route a small PR to the Director), and the $300
threshold is added as a *mandatory floor* on top of it. The two combine as **OR**: director
required if the box is checked **OR** the USD total is ≥ $300.

Decided with the user:
- Boundary is **inclusive**: exactly $300.00 requires director approval (`≥`, calculator `gte`).
- Threshold is **hardcoded** as `300` in the condition node (like the 110% cap in Send-PO).
  No config collection (consistent with D22/D23 — avoid config tables in v1).

## Where the change lands

The decision point already exists in the **PR Approval workflow** (key `cv237r8h7k9`, active
version `367150157135872`): after Procurement approves (Approval#2 `ec2h8cqal32`), condition
node **`bizoy1sj87j` "Needs Director Approval?"** routes:
- true → Update `eg86l2ilhmk` → `pending_director_approval` → Director Approval `sxvxwl498xg`
- false → Update `jy1365pvsce` → `approved`

Current config of `bizoy1sj87j` (basic engine, verified live):
```json
{ "rejectOnFalse": false, "engine": "basic",
  "calculation": { "group": { "type": "and", "calculations": [
    { "calculator": "equal",
      "operands": ["{{$jobsMapByNodeKey.ec2h8cqal32.data.needs_director_approval}}", true] }
  ] } } }
```

### Target config (the only logic change)
Switch the group to **`or`** and add a `gte` leaf against the USD total:
```json
{ "rejectOnFalse": false, "engine": "basic",
  "calculation": { "group": { "type": "or", "calculations": [
    { "calculator": "equal",
      "operands": ["{{$jobsMapByNodeKey.ec2h8cqal32.data.needs_director_approval}}", true] },
    { "calculator": "gte",
      "operands": ["{{$jobsMapByNodeKey.ec2h8cqal32.data.quoted_total_usd}}", 300] }
  ] } } }
```

Why this is safe / simple:
- `quoted_total_usd` is a stored numeric formula field already present in the approval node's
  data snapshot (same place the existing `needs_director_approval` operand reads from). Live
  samples confirm clean numbers (`394.74`, `200`) and **`0` when no quote is entered** — so a
  missing quote can never trip the floor. No arithmetic / calculation node is needed (the
  basic-engine `feedback_prefer_mathjs_engine` caveat was about `$jobsMapByNodeKey` *result*
  references, not field-scalar comparisons like this one).

## Rejected alternatives
- **Auto-flip `needs_director_approval` when total ≥ 300** (a separate workflow/linkage):
  more moving parts, muddies "who decided", and the total/FX are often only finalized at the
  procurement stage — so the flip would have to happen there anyway, exactly where the
  condition already runs. No benefit over editing the condition.
- **Configurable threshold collection:** over-engineering for a value that rarely changes;
  against D22/D23 philosophy. Revisit only if the team asks.

## Implementation (must be a workflow revision — never edit the active version in place)

This workflow has executed, so per the NocoBase versioning rule it cannot be edited live.
Use the `nocobase-workflow-manage` skill. Steps:

1. **Create a same-key revision** of `cv237r8h7k9` from version `367150157135872`, disabled.
   Force the key via raw `--body` to avoid the CLI minting a stray new key
   (`feedback_workflow_revision_key_bug`):
   `... workflows revision --filter-by-tk 367150157135872 --body '{"key":"cv237r8h7k9","enabled":false,"current":false}'`
2. **Verify node integrity on the new version.** This workflow has condition branches, which
   the CLI revision can silently drop (`feedback_workflow_revision branch drop` rule). Confirm
   the new version has **21 nodes** and that the full branch structure documented in
   `project_current_state.md` (dept-skip, skip_dept_approval, all three approvals + their
   approve/return/reject branches) is intact. Recreate any dropped nodes before proceeding.
3. **Edit `bizoy1sj87j`** (look it up by `key` on the *new* version id — its numeric id will
   differ) to the target config above (group → `or`, add the `gte … quoted_total_usd … 300`
   leaf).
4. **Activate** the new version (`enabled=true, current=true`); the old version auto-disables.
5. Pause for user before activation if anything in step 2 looked off.

### Files / records touched
- Live NocoBase only — new workflow version of `cv237r8h7k9`. No collection or UI changes.
- Docs: `project_current_state.md` (record new active version id + the new dept/director
  surface UIDs the revision generates, and move `367150157135872` to Stale IDs), `decisions.md`
  (new D-entry: "Director approval mandatory at ≥ $300 USD — floor added on top of the manual
  checkbox; supersedes the pure-D23 routing for the director decision; affects MVP4").

## Verification (end-to-end, after activation)

Drive a PR through to the procurement-approve step and confirm the branch taken. Three cases:

| Case | `needs_director_approval` | `quoted_total_usd` | Expected after Procurement approves |
|---|---|---|---|
| A — floor trips | false | ≥ 300 (e.g. SRD 15000 @ 38 ≈ 394.7) | → `pending_director_approval` (Director queue) |
| B — boundary | false | exactly 300.00 (USD 300 @ rate 1) | → `pending_director_approval` (inclusive) |
| C — below floor, box off | false | < 300 (e.g. 200) | → `approved` directly (no director) |
| D — voluntary escalation | true | < 300 | → `pending_director_approval` (checkbox still works) |

Check the workflow execution's job for node `bizoy1sj87j` to confirm which branch fired, and
the resulting PR `status`. Use a fresh PR per case (Guard A makes approved/rejected PRs
immutable). Confirm via the Director's task list that cases A/B/D actually land in Dana's queue.

## Commit checkpoints
- After this plan is approved (before execution) — plan file.
- After activation + the four verification cases pass — `project_current_state.md` +
  `decisions.md` (new D-entry).
