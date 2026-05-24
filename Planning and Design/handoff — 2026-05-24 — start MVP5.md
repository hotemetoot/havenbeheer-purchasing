# Handoff — 2026-05-24 — Start MVP5

Read the memory file first, then this document. Do NOT read the whole v3 plan — just the MVP5 section.

---

## Where we stopped

MVPs 1–4 are fully built and verified. The session ended after:
- Completing MVP4: `needs_director_approval` checkbox, `approved_at` field, workflow routing condition, UI linkage rule
- Updating memory file (below)
- This handoff

**The next thing to build is MVP5.**

---

## Critical design change made this session (D23 — simplified MVP4)

**Original MVP4 design:** automatic threshold-based routing via an `approval_limits` collection ($1,500 USD → skip director, above → director).

**What was actually built:** No `approval_limits` collection. Instead:
- `needs_director_approval` (boolean checkbox, default false) — user sets manually on the PR form
- After Procurement approves:
  - If `needs_director_approval = true` → sets `pending_director_approval` → Director Approval runs
  - If `needs_director_approval = false` → sets `status=approved`, `approved_at={{$system.now}}` immediately
- Both paths (no-director auto-approve AND director approve) now write `approved_at`
- Linkage rule on the create form: when `needs_director_approval` is checked, `justification` becomes required

---

## Active runtime state

### Fields added in MVP4
| Field | Interface | Notes |
|---|---|---|
| `needs_director_approval` | checkbox (boolean) | default false; set by submitter |
| `approved_at` | datetime | written on final approval (both paths) |

### Workflows
| Workflow | Key | Active ID | Notes |
|---|---|---|---|
| PR Approval | `cv237r8h7k9` | `366087730298880` | enabled=true, 18 nodes |
| Cancel PR | `59ezifdoqvj` | `364980262862848` | enabled=true |
| Cancel PR Guard | `8yngslauuj4` | `364984924831744` | enabled=true, request-interception |

### PR Approval workflow — updated node chain (Procurement Approve branch)
After Procurement approves, the flow is now:

```
ec2h8cqal32 (Procurement Approval)
  branch 2 (approve): bizoy1sj87j (CONDITION: needs_director_approval == true?)
    branch 1 (true): eg86l2ilhmk (Update: status=pending_director_approval)
                       → sxvxwl498xg (Director Approval)
                           branch 2 (approve): kj1zcmujub8 (Update: status=approved, approved_at=now)
                           branch 1 (return): z1x6ghkmr2t (Update: status=info_requested)
                           branch -1 (reject): t2odlgyqdra (Update: status=rejected)
    branch 0 (false): jy1365pvsce (Update: status=approved, approved_at=now)
  branch 1 (return): pket0lgmjyk (Update: status=info_requested)
  branch -1 (reject): 01vfxfgw6s3 (Update: status=rejected)
  main downstream: null (Director is now nested inside condition branch 1)
```

### Approval surfaces (unchanged from MVP3)
| Stage | Node key | approvalUid | taskCardUid |
|---|---|---|---|
| Initiator (trigger) | — | `2zmok19gb2c` | `exgm0gh0mru` |
| Dept Owner | `cfg687cye3n` | `klak6hh6vu0` | `92sgwoqox8y` |
| Procurement | `ec2h8cqal32` | `qswcu5p6ihj` | `koo33nxd7gg` |
| Director | `sxvxwl498xg` | `42ay2w0j69v` | `j0ikk0gww0m` |

### UI
- **Purchase Requests page:** `cuycec133qb`
- **Create form** (template `n9f8v5vnhhc`, target `e76c40c8c79`): `needs_director_approval` checkbox added after `justification`; linkage rule requires `justification` when checkbox is checked
- **PR detail popup** (`2b367dbd157`): `needs_director_approval` display field added after `justification`

---

## MVP5 build plan

### One-line scope
Build **Guard A** — a request-interception workflow that blocks Update and Delete on `purchase_requests` when the record is in a terminal status (`approved`, `rejected`, `cancelled`).

### What Guard A does
- Trigger: request-interception on `purchase_requests`, fires on `update` AND `destroy`
- Reads the current record's `status`
- If `status ∈ {approved, rejected, cancelled}` → rejects the request (error message to user)
- Otherwise → passes through (no-op)

### 5.1 — Build Guard A

The Cancel PR Guard (`8yngslauuj4`) was built in MVP2 using the same pattern (request-interception). Use that as a reference.

Create a new **request-interception** workflow:
- Type: `request-interception`
- Collection: `purchase_requests`
- Actions: `update` AND `destroy` (both)
- Sync: true (must be synchronous to block the request)

Node chain:
```
[Condition: is status terminal?]
  engine: basic
  condition: status IN {approved, rejected, cancelled}
    — use: status == "approved" OR status == "rejected" OR status == "cancelled"
    — NocoBase does not support $in on basic engine; use three $eq checks with $or logic
  rejectOnFalse: true  ← hard stop if condition is TRUE (terminal)

Wait — rejectOnFalse semantics:
  rejectOnFalse: true means: if condition is FALSE, reject/end workflow (passes through)
  So: condition should be TRUE for the "block" case

Actually, re-check which branch is "block":
  The condition node with rejectOnFalse:true terminates on branch 0 (false).
  We want to BLOCK when status is terminal (true case) and PASS when status is non-terminal (false case).
  → Set rejectOnFalse: false and put the rejection in branch 1 (true)
  OR: invert the condition (status NOT terminal) with rejectOnFalse: true

Recommended approach (same as Cancel Guard):
  Condition: status == "draft" OR status == "pending_dept_approval" OR ... (all non-terminal statuses)
  rejectOnFalse: true  → if condition is false (i.e. status IS terminal) → request is rejected/blocked
```

Simpler alternative — check the Cancel Guard structure with:
```
nb api workflow workflows get -e havenbeheer -j \
  --filter '{"$and":[{"key":{"$eq":"8yngslauuj4"}},{"enabled":{"$eq":true}}]}' \
  --appends '["nodes"]'
```
Mirror that pattern for Guard A, adapting the condition to check terminal statuses.

### 5.2 — Verify

| # | Test | Expected result |
|---|---|---|
| I1 | Edit an `approved` PR (change title) | Blocked with error |
| I2 | Edit a `rejected` PR | Blocked with error |
| I3 | Edit a `cancelled` PR | Blocked with error |
| I4 | Edit a `draft` PR | Succeeds |
| I5 | Edit a `pending_dept_approval` PR | Succeeds |
| I6 | Edit a `pending_purchasing_review` PR | Succeeds |
| I7 | Delete a `cancelled` PR | Blocked with error |
| I8 | Delete a `draft` PR | Succeeds (if delete is even available) |

**Note:** The `approved_at` field was just added in MVP4. You can test I1 by finding an approved PR from T1/T2 test runs. If no approved PRs exist yet, run a quick T1 scenario to create one.

---

## Environment
- Env: `havenbeheer`, http://localhost:13000
- CLI: `nb` with OAuth auto-refresh
- UI page: `cuycec133qb` (Purchase Requests)

---

## MVP6 preview (after MVP5 verified)

Submitter-role routing variants — see v3 plan §MVP6:
- Submitter IS dept owner → skip dept approval
- Submitter's dept = Procurement → skip dept + procurement, always to director (D2)
- Both → skip both

This requires restructuring the existing PR Approval workflow. Plan for significant node work.
