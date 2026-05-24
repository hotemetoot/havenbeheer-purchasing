# Handoff — 2026-05-24 — Start MVP4

Read the memory file first, then this document. Do NOT read the whole v3 plan — just the MVP4 section.

---

## Where we stopped

MVPs 1–3 are fully built and verified. The session ended after:
- Completing MVP3 UI (PR table columns, detail popup, procurement approval form)
- Simplifying the FX rate design (see D22 below)
- Updating memory file + this handoff

**The next thing to build is MVP4.**

---

## Critical design change made this session (D22)

**Original MVP3 design:** `fx_rates` collection + workflow nodes that look up the exchange rate at submit time and write provisional `quoted_total_usd`.

**What was actually built:** No FX collection. No workflow FX lookup. Instead:
- `fx_rate_to_usd` — plain number field, entered **manually** by the submitter or procurement on the PR form
- `quoted_total_usd` — **formula field** (`{{quoted_total}} * {{fx_rate_to_usd}}`, formula.js engine), always auto-computes, always current, read-only

**Consequence for MVP4:** Guard E no longer needs to look up or write an FX rate. It only needs to validate that `fx_rate_to_usd` IS NOT NULL (in addition to `quoted_total`, `quoted_currency`, `quotation_attachment`). The `quoted_total_usd` formula field will already contain the correct USD amount when Guard E passes.

---

## Active runtime state

### Workflows
| Workflow | Key | Active ID | Notes |
|---|---|---|---|
| PR Approval | `cv237r8h7k9` | `366087730298880` | enabled=true, 16 nodes |
| Cancel PR | `59ezifdoqvj` | `364980262862848` | enabled=true |
| Cancel PR Guard | `8yngslauuj4` | `364984924831744` | enabled=true, request-interception |

**The PR Approval workflow has many disabled versions under key `cv237r8h7k9`** — the user was creating revisions during testing. Always filter by the active version ID `366087730298880` when working with nodes.

### Approval surfaces (current active workflow)
| Stage | Node key | approvalUid | taskCardUid |
|---|---|---|---|
| Initiator (trigger) | — | `2zmok19gb2c` | `exgm0gh0mru` |
| Dept Owner | `cfg687cye3n` | `klak6hh6vu0` | `92sgwoqox8y` |
| Procurement | `ec2h8cqal32` | `qswcu5p6ihj` | `koo33nxd7gg` |
| Director | `sxvxwl498xg` | `42ay2w0j69v` | `j0ikk0gww0m` |

### Key node keys (stable across revisions)
- Root update: `1f6a1h52l9u`
- qProc (query Procurement dept): `yrl9kgkrb3x`
- Submitter-is-approver condition: `5hed96jh1u7`
- Skip dept update: `nkbguc8uo7z`
- Procurement Approve branch: `c2oafh9qf2y` → **this is where Guard E + threshold routing go**

### Procurement Approve branch — current content
Node `c2oafh9qf2y` (key, branch=2 of `ec2h8cqal32`) currently just sets status=`pending_director_approval`. MVP4 expands this branch with Guard E + threshold check before that status update.

---

## MVP4 build plan

### 4.1 — Data modeling (do this first, before touching the workflow)

**Create `approval_limits` collection:**
```
name: approval_limits
template: general
Fields:
  - name (input)
  - applies_to (select: global/role/department)
  - role (m2o → roles, nullable)
  - department (m2o → departments, nullable)
  - max_amount_usd (number)
  - notes (textarea)
```
Seed one row: name="Procurement → Director threshold", applies_to=global, max_amount_usd=1500

**Add `approved_at` field to `purchase_requests`:**
- interface: datetime
- title: "Approved At"
- This field is written when threshold routing short-circuits to approved (skips director)

### 4.2 — Guard E + threshold routing (workflow)

The active version ID `366087730298880` has `versionStats.executed > 0` — **create a revision first**.

```
nb api workflow workflows revision -e havenbeheer -j \
  --filter '{"$and":[{"key":{"$eq":"cv237r8h7k9"}},{"enabled":{"$eq":true}}]}'
```

Use the returned new ID for all subsequent node operations.

**Inside the Procurement Approve branch** (currently node `c2oafh9qf2y`), build Guard E + threshold as a chain inserted BEFORE the existing status update:

```
[Guard E condition] → pass → [Query approval_limits] → [Threshold condition]
                     → fail → [End node / error]        → at/below → [Update: status=approved, approved_at=now]
                                                         → above   → [existing Director Approval flow]
```

**Guard E condition node:**
- Type: condition, engine: basic
- AND group:
  - `{{$context.data.quoted_total}}` notEqual null
  - `{{$context.data.quoted_currency}}` notEqual null
  - `{{$context.data.quotation_attachment}}` notEqual null  ← check if array length > 0 or use notEmpty
  - `{{$context.data.fx_rate_to_usd}}` notEqual null
- rejectOnFalse: false (soft reject, workflow continues on branch 0)
  - branch 0 (false): End node — terminates the approval process with a message to Pat
  - branch 1 (true): continue to threshold check

**Query `approval_limits`:**
- Filter: `applies_to = 'global'`
- pageSize: 1

**Threshold condition:**
- `{{$jobsMapByNodeKey.<queryKey>.max_amount_usd}}` greaterThanOrEqual `{{$context.data.quoted_total_usd}}`
  - True (at/below threshold): Update node → `status=approved`, `approved_at={{$system.now}}`
  - False (above threshold OR quoted_total_usd is null): existing Director Approval node

**Important:** `quoted_total_usd` is a formula field. In workflow variable context, use `{{$context.data.quoted_total_usd}}` to read its computed value. Guard E ensures `fx_rate_to_usd` IS NOT NULL, so `quoted_total_usd` will be non-null when we reach the threshold check.

### 4.3 — Verification scenarios

- **T1:** Alice submits PR with `quoted_total=500`, `quoted_currency=USD`, `fx_rate_to_usd=1.0` → `quoted_total_usd=500`. Oliver → Pat approves → status goes straight to `approved`, `approved_at` populated. Dana never sees it.
- **T2:** Alice submits PR with `quoted_total=2000`, same rate → `quoted_total_usd=2000`. Pat approves → Dana receives task.
- **T3:** Alice submits PR with no quote fields → Pat tries to approve → Guard E blocks (branch 0 → End node).
- **T4:** Alice submits with `quoted_total=500` but no `fx_rate_to_usd` → Pat tries to approve → Guard E blocks at fx_rate_to_usd check. (Note: `quoted_total_usd` formula will return null when fx_rate_to_usd is null.)

---

## MVP5 (after MVP4 verified)

Guard A — request-interception on `purchase_requests` Update + Delete:
- If status ∈ {approved, rejected, cancelled} → block
- Else → pass through

Simple single-workflow build. See v3 plan §MVP5.

---

## Environment
- Env: `havenbeheer`, http://localhost:13000
- CLI: `nb` with OAuth auto-refresh
- UI page: `cuycec133qb` (Purchase Requests)
