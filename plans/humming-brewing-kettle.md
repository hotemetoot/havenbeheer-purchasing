# MVP012 — Submitter-selectable dept-stage approver

## Context

Today the PR's department-approval stage is *always* assigned to the department head
(`departments.main_approver`). The team wants the submitter to be able to **reassign that one
stage** per-PR to someone else in their department (an "assistant manager or whoever"), while
keeping the dept head informed. The dept stage stays a real approval — it is not skipped.

This **retires the MVP010 skip feature** (D29): the `skip_dept_approval` toggle is removed from
the workflow and the forms (the column is *kept*, unused, per the user's choice — drop later).
The custom-approver branch structurally takes the slot the skip branch occupied.

Chunk: `chunks/012-custom-approver-selection.md`. New decision: **D36** (supersedes D29).

### Live findings (verified this session, supersede the doc tables)
- **Active PR Approval version is `368983543906304`** (enabled, current, `versionStats.executed = 0`),
  NOT `368641179582464` as `project_current_state.md` records. Doc-lag to correct at session end.
  27 nodes, node **keys preserved** across revisions.
- **Approval-node assignee accepts variables** in this shape (proven live):
  `assignees: [{"filter":{"$and":[{"id":{"$eq":"{{VARIABLE}}"}}]}}]`
  - Procurement `ec2h8cqal32` uses a job-result var (`{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}`).
  - Dept Owner `cfg687cye3n` uses `{{$context.data.createdBy.mainDepartment.mainApproverId}}`.
  → The new node's assignee = `{{$context.data.custom_approver.id}}` (requires `custom_approver` in trigger appends).
- **Relevant branch structure (active version):**
  - `5hed96jh1u7` *"Is submitter the dept head?"* (condition) — **stays first, untouched.**
    - br=1 (submitter IS dept head) → `nkbguc8uo7z` update → pending_purchasing_review (auto-skip).
    - br=0 → `eafkgfa3axi` *"Skip dept approval requested?"* (the skip check — to be repurposed).
      - br=1 (skip) → `5h232imw9ss` notify dept head → `budfy1scwbw` update → pending_purchasing_review.
      - br=0 → `cfg687cye3n` **Dept Owner Approval** → br=2 `xqlzgk0326f` (approve→pending_purchasing_review) / br=1 `bm50djboga3` (return→info_requested) / br=-1 `1b06nufq3bi` (reject→rejected).
  - `ec2h8cqal32` **Procurement Approval** is the **continuation** after `5hed96jh1u7` (runs once the dept construct resolves on the approve path). Both dept branches converge here.

## Approach

Two-node branch (user-chosen). Repurpose the freed skip branch into a custom-approver branch with
its own approval node; the dept-head node stays as the default (br=0) path.

### Phase 012.1 — Data model (`nocobase-data-modeling`)
Add to `purchase_requests`:
- `use_custom_approver` — checkbox/boolean, default `false`.
- `custom_approver` — m2o → `users` (FK `customApproverId`). Set a title field display (users already
  have one).

### Phase 012.2 — UI (`nocobase-ui-builder`)
- **Create form `e76c40c8c79`:** add `use_custom_approver` checkbox + `custom_approver` picker after
  `needs_director_approval`. Linkage rule mirroring the existing `needs_director_approval →
  justification` rule: `custom_approver` **hidden** unless `use_custom_approver == true`, **required**
  when it is.
- **Picker scope = submitter's department, excluding self.** Apply a data scope on the `custom_approver`
  field filtering `users` by `mainDepartment.id == {{ current user's dept }}` **AND** `id != {{$user.id}}`
  (a submitter must not pick themselves). *Build detail to confirm:* the exact current-user-dept / current-user-id
  variable tokens available in a create-form field data scope (`{{$user.mainDepartment.id}}`, `{{$user.id}}` /
  `{{currentUser...}}`). If the dept token doesn't resolve in field data scope, fall back to a self-exclusion-only
  scope for v1 and note it (A3 becomes best-effort) — confirm with user before relaxing.
- **Detail popup `2b367dbd157`:** add `use_custom_approver` + `custom_approver` read-only.
- **Remove skip UI:** delete create-form wrapper `830iodzmcjo` and detail-popup wrapper `in24ndj91et`.

### Phase 012.3 — Workflow revision (`nocobase-workflow-manage`)
Revision `cv237r8h7k9` from `368983543906304`, **forcing the same key** via raw `--body`
(`{"key":"cv237r8h7k9","enabled":false,"current":false}`) to avoid the stray-copy CLI bug
(`feedback_workflow_revision_key_bug`). Work on the new disabled version, then enable.

1. **Trigger appends:** add `custom_approver` →
   `["createdBy","createdBy.mainDepartment","createdBy.mainDepartment.main_approver","createdBy.mainDepartment.secondary_approver","custom_approver"]`.
2. **Repurpose `eafkgfa3axi`** (the old skip condition): retitle *"Custom approver chosen?"*; change its
   calculation (basic engine) to an **AND** of `equal {{$context.data.use_custom_approver}} == true`,
   `notEqual {{$context.data.custom_approver.id}} != null`, **and** `notEqual {{$context.data.custom_approver.id}}
   != {{$context.data.createdById}}` (defense-in-depth: if a submitter somehow set themselves as custom
   approver, fall through to the normal dept-head path rather than self-approval). rejectOnFalse=false.
3. **br=1 (custom chosen) sub-branch:**
   - Keep `5h232imw9ss` notify; retitle *"Notify dept head — PR reassigned"*, update message text
     (still in-app channel `approval-todo-in-app-message`, receiver `mainApproverId`, `ignoreFail=true`).
   - **Replace** `budfy1scwbw` (plain update) with a **new approval node "Custom Approver Approval"**,
     built by **`flow-nodes duplicate` of `cfg687cye3n`** + its three outcome updates so the duplicate's
     **ProcessForm is structurally identical to the Dept Owner Approval form** (same fields, same
     editable/`readPretty` patterns incl. the MVP8-editable-on-dept fields) — user requirement. Then move
     the copy onto the `eafkgfa3axi` br=1 branch after the notify, and set **only** the copy's assignee to
     `[{"filter":{"$and":[{"id":{"$eq":"{{$context.data.custom_approver.id}}"}}]}}]`. Its three outcomes
     mirror the dept-head node: approve→`pending_purchasing_review`, return→`info_requested`,
     reject→`rejected` (each its own duplicated update node). Do not hand-build a fresh blueprint form
     (would diverge from the dept-head form and re-introduce the comment-model gap).
4. **br=0 (no custom):** `cfg687cye3n` Dept Owner Approval — **unchanged**.
5. **Convergence:** both dept branches resolve and flow continues to Procurement `ec2h8cqal32`
   (the existing continuation) on the approve path, exactly as today — no change needed there.

### Phase 012.4 — Comment models for the new approval node
The duplicated/new approval node needs per-action `CommentFormModel`s pre-created (as admin) and each
action's `commentFormUid` set, or a non-admin custom approver hits a `flowModels:save` 403 when opening
the task. (`feedback_approval_blueprint_comment_models`.) If `flow-nodes duplicate` copies the source
node's `commentFormUid`s, **verify they resolve**; create fresh ones if the copy reuses the dept node's.

### Phase 012.5 — Verify, then enable
Run A1–A7 (below) end-to-end via test users, then enable the new revision and disable the prior.
After revisioning but **before enabling**, verify the node count and branch integrity — revisions can
silently drop condition-branch nodes (CLAUDE.md rule); recreate any missing nodes.

### Phase 012.6 — Docs & state
- Add **D36** to `decisions.md` (`**Supersedes:** D29`; skip retired for custom-approver, column kept).
  Mark D29 superseded in `decisions-archive.md`.
- Update `design/users-and-roles.md` (line ~10, dept-owner row) and `design/permissions.md` (line ~24,
  drop the skipped-PR view note or reframe — the dept head still gets view via the existing scope).
- `roadmap.md`: mark MVP010 superseded by 012; add a 012 row.
- `project_current_state.md`: new fields, the revised workflow (new version id + new node keys),
  **correct the active-version doc-lag** (`368983543906304` → the new 012 version), note `skip_dept_approval`
  column is now dead, UI wrapper changes.

## Verification (A1–A7)

Test users: submitter **Oliver** (user 10, Operations; Operations `main_approver` = Oliver — note he IS
his own dept head, so use **Alice** user 9, Operations, as the non-head submitter for the branch tests).
Reassign target: another Operations user. Approver actions driven via UI (custom-action/approval tasks
can't be `workflows execute`'d without a user — `feedback_custom_action_execute_no_user`).

- **A1** (regression): Alice submits, checkbox **off** → dept task lands on Oliver (Operations head); approve → Procurement.
- **A2**: Alice submits, checkbox **on**, picks another Operations user → dept task lands on **that** user; Oliver gets an in-app FYI; approve → flow reaches Procurement.
- **A3**: `custom_approver` picker lists only Operations users **and excludes the submitter** (Alice not in her own list; best-effort note if the dept data-scope var is unavailable, but self-exclusion must hold).
- **A4**: linkage — picker hidden when checkbox off; required when on.
- **A4b**: the Custom Approver Approval task form is **structurally identical** to the Dept Owner Approval form (same fields/patterns).
- **A4c** (defense-in-depth): if a submitter is forced to custom_approver = self (e.g. via API), the condition falls through to the dept-head path — no self-approval.
- **A5**: Oliver submits (he *is* dept head) with checkbox on → auto-skip `5hed96jh1u7` still fires; dept stage skipped regardless of custom fields.
- **A6**: `skip_dept_approval` absent from both forms; no node reads/writes it; column still present in DB.
- **A7**: the new custom approver (non-admin) can open the task and Approve/Return/Reject without a 403.

Node logic (conditions/assignee) pre-validated with `nb api workflow flow-nodes test` before enabling.

## Risks
- **Branch-drop on revision** — verify node count post-revision (012.5).
- **Comment-model 403** — 012.4.
- **Picker dept-scope variable** — confirm token in field data scope (012.2); fallback noted.
- **In-place vs revision** — this version is unexecuted (`executed:0`), so in-place edit is technically
  allowed, but we revision anyway (canonical, keeps the live version intact until verified).
- **Approve/reject convergence** — rely on the existing approval-plugin behaviour where a reject ends the
  approval; the new node mirrors the dept-head node exactly, so its convergence behaviour matches.
