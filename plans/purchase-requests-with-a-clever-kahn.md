# Board approval tier (≥ $15,000 USD)

## Context

The team wants a hard guarantee that very large purchases reach the **board**, but the
board will not use the app — they sign a hard-copy document. So after the **Director**
approves, a PR whose `quoted_total_usd` is **≥ $15,000** must not jump straight to
`approved`. Instead it parks at a new `pending_board_approval` status until someone records
the board's signed decision inside the app. Only when the signed document is attached can the
PR be approved manually.

This is the same "floor" reasoning as **D30** (mandatory director approval at ≥ $300), one
tier higher and sitting *after* the director. Because $15,000 ≥ $300, any board-level PR
already passes through the director under D30, so the board branch always hangs off the
director-approve branch — there is no "board but no director" case to handle.

### Is there a better way? — chosen approach

Rather than a free-floating attachment field plus a guarded "approve" button (more moving
parts: field + request-interception guard + button + linkage rules, and no reject path), we
add a **4th approval stage** that mirrors the three existing ones. Its task form carries a
**required** board-document attachment, so NocoBase natively enforces "attach the signed scan
before you can approve." It lands in Procurement's task queue (won't be forgotten) and gives
return/reject for free (board declines → reject the PR). Decided with the user:

- **Mechanism:** 4th approval node "Board Approval", shown only for PRs ≥ $15k.
- **Confirmer / assignee:** Procurement (Pat, user **11**) — records the board's decision.
- **Threshold:** inclusive, hardcoded `15000` (mirrors D30's hardcoded `300`).

## Changes

### 1. New field on `purchase_requests`
- `board_approval_document` — **attachment, multi-file** (mirror `quotation_attachment` per
  D15; the board may sign several pages). Skill: `nocobase-data-modeling`.

### 2. New `status` enum value
- Add `pending_board_approval` to `purchase_requests.status`, placed after
  `pending_director_approval` (suggest color `purple`/`geekblue`). Live enum confirmed; current
  values do **not** include it. Skill: `nocobase-data-modeling`.

### 3. Revise the PR Approval workflow (`cv237r8h7k9`)
Revision the active version `367158084370432` → new version, **forcing the same key** via raw
`--body` (`feedback_workflow_revision_key_bug`): `revision --filter-by-tk 367158084370432
--body '{"key":"cv237r8h7k9","enabled":false,"current":false}'`. After revision, **verify the
node count (currently 21) and recreate any dropped condition-branch nodes** before enabling
(CLAUDE.md branch-drop caveat).

Restructure the **Director-approve branch** (`sxvxwl498xg` br=2). Today it is:

```
Director approve (br=2) → Update kj1zcmujub8 (status=approved, approved_at=now)
```

becomes:

```
Director approve (br=2)
  └─ Condition  board_check  — quoted_total_usd >= 15000   (basic engine, gte; mirror D30)
       read from {{$jobsMapByNodeKey.sxvxwl498xg.data.quoted_total_usd}}
       (stored USD formula field; computes to 0 with no quote → missing quote never trips it)
       ├─ br=0 (false, < 15k) → Update kj1zcmujub8 (status=approved, approved_at=now)  [moved here]
       └─ br=1 (true, ≥ 15k)  → Update (status=pending_board_approval)
                                  └─ Approval#4  "Board Approval"  → assignee hardcoded [11] Pat
                                       ├─ approve (br=2)  → Update (status=approved, approved_at=now)  [new node]
                                       ├─ return  (br=1)  → Update (status=info_requested)            [new node]
                                       └─ reject  (br=-1) → Update (status=rejected)                  [new node]
```

Note `kj1zcmujub8` (the existing approved-update) moves onto the **false** branch; the board
path needs its **own** approved-update node since a node can only sit in one place.

**Board Approval process form (the gate):** include `board_approval_document` on the
Approval#4 ProcessForm and set it **required**. This is what enforces "must attach before
approve." Show the PR fields read-only (same posture as the director form). Verify required
validation actually blocks the Approve submission on this NocoBase build (approval ProcessForm
required-field enforcement) — if it does not block, fall back to an inline condition guard on
the approve branch (`board_approval_document` not empty → else response-message +
end-process(-1), per `feedback_inline_guard_end_node`).

Skill: `nocobase-workflow-manage`. Record the new version ID, all four approval surfaces
(approvalUid + taskCardUid), and the new node keys in `project_current_state.md`; move the old
`367158084370432` surfaces to **Stale IDs**.

### 4. UI surfaces
- **PR detail popup** (`2b367dbd157`): add `board_approval_document` read-only display so the
  signed doc is visible on the record. Skill: `nocobase-ui-builder`.
- Status chip will render `pending_board_approval` automatically from the enum.
- No create-form change (the field is filled by Procurement at the board stage, not at submit).

### 5. ACL
- Procurement already has `update` on `purchase_requests` via strategy-based ACL (state-file
  note), so Pat can write `board_approval_document`. Confirm at verification; widen only if the
  approve submission is blocked by ACL. Skill: `nocobase-acl-manage` (only if needed).

### 6. No change needed
- **Guard A immutability** (`496ookqmg01`): locks update/destroy only when status ∈
  {approved, rejected, cancelled}. `pending_board_approval` is non-terminal, so attaching the
  doc is allowed. No edit.
- **Generate-PO** (`2izsx8uv50r`): fires only at `status=approved`, which the board path
  eventually reaches. No edit.

### 7. Record the decision
Append **D32** to `decisions.md` — "Mandatory board approval at ≥ $15,000 USD (second floor,
above the Director)". Note: floor on top of D30; inclusive `15000` hardcoded; implemented as a
4th approval stage with a required signed-document attachment; assignee Procurement.
**Affects:** MVP4. Add a roadmap line if we treat it as a tracked item.

## Files / entities touched
- Live NocoBase: `purchase_requests` (field + enum), workflow `cv237r8h7k9` (revision),
  PR detail popup `2b367dbd157`.
- Docs: [project_current_state.md](../project_current_state.md), [decisions.md](../decisions.md),
  [roadmap.md](../roadmap.md).

## Verification (end-to-end, via the real UI / approval tasks)
1. **Board path:** create a PR with `quoted_total` = 15000, currency USD, `fx_rate_to_usd` = 1
   (so `quoted_total_usd` = 15000), `needs_director_approval` off. Route through dept (or skip)
   → Procurement approve → Director approve. **Expect status = `pending_board_approval`**, not
   `approved`, and a Board Approval task in Pat's queue.
2. **Required-attachment gate:** as Pat, open the board task and click Approve **without**
   attaching → expect it to be blocked. Attach a signed PDF → Approve → **status=`approved`**,
   `approved_at` set, `board_approval_document` populated and visible on the PR popup.
3. **Boundary below:** PR with `quoted_total_usd` = 14999 (or 500) → Director approve goes
   **straight to `approved`**, no board task created.
4. **Inclusive boundary:** exactly 15000 takes the board path (covered by step 1).
5. **Reject / return:** board reject → `status=rejected`; board return → `info_requested`.
6. **Downstream intact:** Generate PO still works on a board-approved PR (status=approved).

## Commit checkpoints (per CLAUDE.md)
- Commit this plan file before any execution.
- Commit after the field+enum land and verify.
- Commit after the workflow revision is verified end-to-end.
- Commit `project_current_state.md` + `decisions.md` (D32) + `roadmap.md` at session end.
