# Plan — Optional "Skip Department Head" on PR submission

## Context

A team session revealed that the department head does **not** always need to approve a
purchase request before it reaches Procurement. The exact rule is unclear and likely to
stay fuzzy, so we add **flexibility instead of a new hard rule**: the submitter may opt to
skip the dept-head approval stage on a given PR. When they do, the dept head is **not** a
blocking approver but is **kept in the loop** — notified in-app and given view access to
the PR.

This mirrors the project's existing philosophy ([D23](../decisions.md): manual
`needs_director_approval` checkbox chosen over an automatic threshold *because the rules
weren't clear enough to automate*). We apply the same manual-judgment pattern to the dept
stage.

**Decided with user:** notification is **FYI-only** (no pull-back / re-injection — D19
in-app only); the toggle is a **submitter choice, always available, default OFF**
(dept approval required unless the submitter opts out).

## What exists today (relevant)

- PR Approval workflow `cv237r8h7k9`, active version `366549533655040` (18 nodes, approval
  type on `purchase_requests`). **Has already executed → edits require a NEW revision,
  then activate.** Never edit in place.
- It **already skips** the dept stage when the submitter *is* their own dept approver:
  condition node `5hed96jh1u7` → br=1 (true) Update `nkbguc8uo7z` → `pending_purchasing_review`;
  br=0 (false) → Dept Owner Approval `cfg687cye3n`.
- Trigger already appends `createdBy.mainDepartment.main_approver` and `.secondary_approver`
  — the dept head to notify is available without changing the trigger.
- PR create form: `CreateFormModel e76c40c8c79` (template `n9f8v5vnhhc`) — has the
  `needs_director_approval` checkbox we'll sit beside.
- No notification node has ever actually been built (zone-2 9b.3 was deferred). This is the
  **first** one — verify the in-app notification node works before relying on it.

## Approach

### 1. Data: new field on `purchase_requests`
- Add `skip_dept_approval` (checkbox / boolean, **default false**). Title-cased label e.g.
  "Skip department-head approval". Skill: `nocobase-data-modeling`.

### 2. Workflow: revise `cv237r8h7k9` to honor the toggle (skill: `nocobase-workflow-manage`)
Create a new revision of `cv237r8h7k9`. Restructure the dept-skip decision so the two skip
*reasons* stay distinct (only the toggle path notifies — notifying yourself is moot):

```
Condition 5hed96jh1u7  (existing): submitter IS dept main_approver?
  ├─ true  → Update nkbguc8uo7z → pending_purchasing_review        (unchanged, no notify)
  └─ false → Condition NEW: skip_dept_approval == true?
               ├─ true  → Notify dept head (FYI) → Update → pending_purchasing_review
               └─ false → Approval#1 Dept Owner Approval cfg687cye3n (unchanged)
```

- The notify node targets the submitter's `mainDepartment.main_approver`, falling back to
  `secondary_approver` when `main_approver.on_leave == true` (mirror existing routing per
  [D21](../decisions.md)). Keep it minimal — a single recipient pick; do not over-notify.
  If a clean fallback adds a whole branch, ship `main_approver`-only in v1 and note the
  fallback as a follow-up.
- The "true" toggle path reuses the existing `pending_purchasing_review` update target
  (`nkbguc8uo7z` or a sibling update) — do not invent a new status.

**Revision hazards (CLAUDE.md):**
- This workflow has many condition branches + 3 approval nodes. **Branch nodes can drop on
  revision.** After revisioning, verify the full node count and recreate any dropped
  branches BEFORE enabling.
- Revisioning mints **new approval/taskCard surface UIDs** for all three approval stages.
  Capture them for `project_current_state.md`; the old version's surfaces become stale IDs.

### 3. Access: dept head must be able to OPEN a skipped PR (skill: `nocobase-acl-manage`)
- **Verify first**, don't assume: check whether the existing dept-owner view scope (built
  MVP1) already grants view on department PRs independent of task assignment.
  - If it does → access is already covered; no ACL change. Done.
  - If view is effectively task-driven only → widen the dept-owner view scope so the
    `main_approver` of a department can view that department's PRs even with no task.
- Do **not** add redundant grants (member is base role — auto-memory
  `feedback_acl_member_base_role`).

### 4. UI: expose the toggle (skill: `nocobase-ui-builder`)
- Add `skip_dept_approval` to PR create form `e76c40c8c79`, placed near
  `needs_director_approval`.
- Add it **read-only** to the PR detail popup (`DetailsBlockModel 2b367dbd157`) for audit
  visibility (who chose to skip).
- Page using `purchase_requests` → ensure `defaults.collections.purchase_requests.fieldGroups`
  is set (CLAUDE.md `fieldGroups` requirement).

### 5. Docs (the "update the plan and design" ask)
- New **D-entry D29** in [decisions.md](../decisions.md): optional submitter-chosen dept-head
  skip; FYI notify + view access; default off; FYI-only (no pull-back). List affected MVPs:
  001 (approval workflow), 004 (sits beside `needs_director_approval`).
- Update [design/permissions.md](../design/permissions.md) (dept-head view access note) and
  [design/users-and-roles.md](../design/users-and-roles.md) (dept-head as FYI-notified party
  when skipped).
- Add a roadmap row (new **MVP 010 — optional skip-dept-approval**) in [roadmap.md](../roadmap.md).
- Create `chunks/010-skip-dept-approval.md` from the chunk template (scope in/out, phases,
  acceptance) — per the session workflow, draft + commit this BEFORE executing.
- At session end: update [project_current_state.md](../project_current_state.md) (new field,
  new active workflow version ID + node keys + new surface UIDs, old version → Stale IDs,
  UI changes) and commit.

## Critical files / IDs
- Workflow: `cv237r8h7k9` (active `366549533655040`), condition `5hed96jh1u7`, dept-skip
  update `nkbguc8uo7z`, Dept Owner Approval `cfg687cye3n`.
- PR create form `e76c40c8c79`; PR detail popup `2b367dbd157`.
- Docs: `decisions.md`, `roadmap.md`, `design/permissions.md`, `design/users-and-roles.md`,
  `project_current_state.md`, new `chunks/010-skip-dept-approval.md`.

## Verification (end-to-end, manual by user)
1. **Toggle OFF (default):** Alice submits a PR → Oliver (Operations main_approver) gets the
   dept approval task as before. (No regression.)
2. **Toggle ON:** Alice submits with skip checked → **no** dept task; PR lands directly in
   `pending_purchasing_review`; Oliver receives an in-app notification and can **open** the
   PR record.
3. **Submitter-is-approver path unchanged:** Oliver submits (toggle OFF) → dept stage still
   auto-skipped, no self-notification, no regression.
4. Procurement → director paths unchanged from the toggle-ON entry point.
5. Confirm node count after revision matches expected (no dropped branches) and the three
   approval surfaces resolve to the new version's UIDs.

## Open items / risks
- **First notification node ever** — verify the in-app notification node type exists/works
  (check `nocobase-plugin-manage` for the in-app message plugin) before building step 2's
  notify node. If unavailable, fall back to view-access-only + surface the PR in the dept
  head's list, and flag to user.
- on_leave fallback for the notify recipient: ship main-only if a branch adds disproportionate
  complexity.
