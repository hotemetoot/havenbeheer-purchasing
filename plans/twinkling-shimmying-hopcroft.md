# Plan — 014: Projects & budget drawdown

## Context

Why this change: Procurement currently runs every spend through the full PR ladder, including
per-PR director (and board ≥ $15k) approval. For recurring scopes of work (e.g. "Repair warehouse",
$10,000) that means repeated director sign-off on small drawdowns against an already-blessed budget.

MVP014 introduces a **pre-approved budget envelope**: a `projects` record is approved once through a
ladder mirroring the PR ladder; afterwards, PRs linked to that project draw against the envelope and
**skip director + board** (Procurement is final), while **dept-owner approval still applies** to each
drawdown. The collective spend of a project's child PRs is **hard-blocked** from exceeding the
envelope. This reverses the original D5 deferral ("no projects in v1"); it lands as new decision **D49**.

Source of truth for the design: [chunks/014-projects-and-budget-drawdown.md](../chunks/014-projects-and-budget-drawdown.md)
(decisions locked 2026-06-21). This plan folds in the **live-verified** workflow state from session start.

### Live state verified at planning time (doc lagged)
- **Active PR-Approval** = `370060903907328` (key `cv237r8h7k9`, 31 nodes, updated 2026-06-15).
  `project_current_state.md` still records `369536223739904` — **doc is stale, fix at session end.**
- The version **reads `executed: 0` but HAS actually executed** — the user pruned execution history,
  which resets the counter. So the counter is **not** a reliable "never ran" signal; treat this version
  as **immutable → same-key revision required** for 014.4 (no in-place edit).
- Insertion-point nodes confirmed live: **`ec2h8cqal32`** Procurement Approval (node id `370060906004481`);
  its **br=2 (approve)** child is **`bizoy1sj87j`** "Director required? (>= $300 OR not regular)". The
  drawdown condition inserts between them.
- Trigger appends on the live version: `createdBy`, `createdBy.mainDepartment`,
  `createdBy.mainDepartment.main_approver`, `custom_approver`.
- **Roadmap has no 014 row** (table stops at 013) — add it in 014.6.

### 014.4 must be a same-key revision (NOT an in-place edit)
The active version's `executed: 0` is an artifact of the user deleting execution history — the version
**has run**, so it is immutable. 014.4 uses a same-key revision via raw `--body` to preserve key
`cv237r8h7k9` (`feedback_workflow_revision_key_bug`), then verifies node count, every branch, and that
all approval-surface comment models carried over (no Pat 403) before enabling. Do **not** rely on the
`executed` counter to judge whether in-place editing is safe — pruned history resets it to 0.

---

## Phase 014.1 — Data model: `projects` + PR link + committed_usd recompute
Skills: `nocobase-data-modeling`, `nocobase-workflow-manage`.

New collection **`projects`** (title field = `title`; FK target so a title field is mandatory —
`feedback_related_record_title_field`):
- `project_number` — sequence `PRJ-YY-NNNN`, `inputable:false` (D31 pattern).
- `title` (input, required, **title field**), `description` (textarea/vditor), `budget_usd` (number).
- `status` (select): `draft`, `pending_dept_approval`, `pending_purchasing_review`,
  `pending_director_approval`, `pending_board_approval`, `info_requested`, `approved`, `rejected`, `closed`.
- `submitter` (m2o → users), `department` (m2o → departments).
- `approval_document` (attachment, multi) — board sign-off.
- `approved_at` (datetime), `rejection_reason_category` (select), `rejection_comment` (textarea).
- `committed_usd` (number, **workflow-maintained** running Σ of child-PR `quoted_total_usd`; not a
  formula — formulas can't traverse relations, `feedback_formula_field_scope`).
- `purchase_requests` (o2m → purchase_requests, inverse of the PR m2o).

New relationship **`purchase_requests.project`** — m2o → projects, FK `projectId`, **nullable**.

**committed_usd recompute** — collection-trigger workflow(s) on `purchase_requests`, recompute parent
project `committed_usd` = Σ non-`rejected`/`cancelled` child `quoted_total_usd`. Mirror PO recompute
A/B (D47): may need a **split** across two workflows because collection `mode` only accepts `[1,2,4,3]`
(create+update in one, delete in another). Aggregate sum in a query/aggregate node, write via update node.

**Traps:** any boolean default must store a real boolean (`feedback_fields_apply_boolean_default`) —
applies only if we add a boolean; verify. Confirm the sequence renders `PRJ-26-0001` on first create.

## Phase 014.2 — Project Approval workflow + surfaces + ACL render plumbing
Skills: `nocobase-workflow-manage`, `nocobase-acl-manage`.

New **separate** workflow, type `approval`, collection `projects` — a trimmed clone of the PR spine:
- Root: set `pending_dept_approval`; query Procurement dept (board assignee = Pat).
- Auto-skip condition "submitter is dept main approver?" → skip dept stage (reuse PR pattern).
- **Dept Owner Approval** — assignee `{{$context.data.createdBy.mainDepartment.main_approver.id}}` (D40).
- **Procurement Approval** (envelope passes through Procurement — decision 6).
- **Director Approval** — **always** (assignee via query node on Director dept, D40). No `is_regular`/$300,
  no custom-approver branch (drops D36/D37 — decision 4).
- **Board ≥ $15k** (reuse D32 threshold, reading `budget_usd`) → Board Approval requiring
  `approval_document` upload.
- Terminals: `approved` + `approved_at`; `rejected`; `info_requested` (return).
- Trigger appends: `createdBy`, `createdBy.mainDepartment`, `createdBy.mainDepartment.main_approver`.

**Whole-new-surface plumbing (the chunk's #1 risk):**
- Pre-create each action's `CommentFormModel` and set `commentFormUid` — blueprint omits them →
  approver 403 on `flowModels:save` (`feedback_approval_blueprint_comment_models`).
- Add a narrowly-scoped **render-enabler `update` grant** on `projects` for every approver role —
  ProcessForm renders only with SOME update grant (`feedback_approval_form_render_update_grant`).
- Grant board role **`create` on attachments** for the upload (`feedback_approver_attachment_upload_acl`).

## Phase 014.3 — Budget hard-block guard (request-interception)
Skill: `nocobase-workflow-manage`. D47 PO-budget pattern.

`request-interception`, global, sync; actions **create + update** on `purchase_requests`:
- Skip unless `params.values.project` set (create) / queried PR has `project` (update).
- Query the project; **reject if `status != approved`** (no draw on unapproved/closed envelope → also
  covers the closed-project block, C5/D2).
- Query sibling child PRs, **exclude `rejected`/`cancelled`**, **exclude self** on update; **separate**
  calculation node (math.js) sums their `quoted_total_usd` (`feedback_condition_inline_arithmetic`,
  `feedback_prefer_mathjs_engine`).
- Compare `Σ + thisPR.quoted_total_usd > budget_usd` (≤ allowed, so exact == budget passes, C3).
- Over-cap → response-message with dynamic "Remaining budget: $X" + end-process `endStatus:-1`
  (`feedback_inline_guard_end_node`).
- Reserve-on-submit (counting all non-terminal children) is what blocks two in-flight PRs that each
  fit but jointly bust the cap (C4).

## Phase 014.4 — PR Approval: insert drawdown skip branch + `project` append
Skill: `nocobase-workflow-manage`. **Same-key revision** of `370060903907328` (it has executed; the
`executed:0` counter is a pruned-history artifact). Re-query the live active version id first.

- Add `project` (+ `project.status`, `project.budget_usd`) to the **trigger appends** so
  `{{$context.data.project.*}}` resolves.
- Insert one **condition node "Project drawdown?"** on **`ec2h8cqal32` br=2** (Procurement-approve;
  node id `370060906004481` on the current version), **before** the existing `bizoy1sj87j`:
  - AND: `project.id != null` AND `project.status == approved` (scalar `!=`/`==` leaves, no inline math;
    math.js or basic engine).
  - **true** → Update → `approved`, `approved_at = now` (skip director + board).
  - **false** → existing `bizoy1sj87j` director-decision, **unchanged** (rewired under the new
    condition's false branch).
- Dept-owner stage is upstream of Procurement → untouched, still applies (decision 3, B3).
- Revision mechanics: `revision --filter-by-tk <activeId> --body '{"key":"cv237r8h7k9","enabled":false,"current":false}'`
  (`feedback_workflow_revision_key_bug`), build the branch, then **before enabling** verify node count,
  every original branch preserved, and all referenced comment models exist (no Pat 403) — CLAUDE.md rule.
  Note ProcessForm uids regenerate; recapture them for the docs.

## Phase 014.5 — UI + ACL field whitelists
Skills: `nocobase-ui-builder`, `nocobase-acl-manage`.

- **Projects ACL** mirroring PR setup: submitter create/view, approver view + render-enabler update,
  procurement close. Self-sufficient per-row `view`; new approver roles start with **zero desktop
  routes** — grant them (`feedback_acl_independent_resource_pitfalls`). No global `create` for approvers
  (D25). New collection suppresses strategy view → every row needs explicit view.
- Add `project` to PR **create/update field whitelists**; add the projects field whitelists.
- **Projects page**: table + create form + detail block (showing budget / committed / **remaining =
  budget − committed** display + child PRs). Four project approval ProcessForms. **Close button.**
- **`project` picker** on the PR create form; data scope = approved + open projects **set via the form
  UI** (`feedback_record_picker_datascope_not_cli`) — the guard enforces server-side regardless.
  Watch RecordSelect quick-create (`feedback_record_select_quickcreate_unique`): set `quickCreate:none`.

### Close Project (part of 014.5)
- Custom-action button (procurement/director) → workflow sets `status=closed` (manual — decision 5).
- A closed project fails the guard's `status==approved` check → blocks new PRs (D2).

## Phase 014.6 — Verification + docs
**User-driven** end-to-end with the test users (Pat 11, Oliver 10, Dana 12, Fiona 14):
- **Project ladder:** A1 < $15k → dept→proc→director→`approved`. A2 ≥ $15k → board stage appears,
  requires `approval_document`. A3 reject/return at each stage. A4 submitter-is-dept-head auto-skips dept.
- **Drawdown routing:** B1 project-linked PR ≥ $300 → **skips director** (`approved` after Procurement).
  B2 unlinked PR ≥ $300 → director as before (regression). B3 dept-owner stage still runs on a project PR.
- **Budget block:** C1 Σ < budget allowed; C2 PR pushing Σ over → blocked w/ remaining-budget msg;
  C3 exactly == budget allowed; C4 two in-flight that jointly exceed → 2nd blocked; C5 non-approved/closed
  project → blocked.
- **Close:** D1 Close → `closed`; D2 new PR against closed project → blocked.
- **committed_usd:** E1 reflects Σ non-rejected children; E2 updates when a child flips to rejected.
- **ACL:** F1 each approver renders + submits their project ProcessForm without 403; F2 board upload works.

Docs at session end: add **D49** to [decisions.md](../decisions.md) (reverses D5; list downstream
MVPs); add the **roadmap 014 row**; update [project_current_state.md](../project_current_state.md)
(new collection/fields, `projects` workflows + node keys/ids, PR-Approval **active=`370060903907328`**
doc-lag fix + the inserted drawdown node, budget guard, ACL, UI surfaces). Commit per the
"this worked" milestone rule.

---

## Sequencing / safety notes
- **Build order is incremental and non-breaking.** 014.1–014.4 (data + logic) can land and be verified
  headlessly before 014.5 (UI) — the guard + routing work without the UI layer. If the build runs long,
  stop after 014.4 without leaving the system broken (chunk "Size" note).
- **Every live change** is shown to the user (intended change / CLI category / expected UI result) and
  approved before execution, per CLAUDE.md. Irreversible steps (none expected here beyond normal
  create) get explicit confirmation.
- **Commit checkpoints:** after each manually-verified phase, and the docs commit at session end.
- **Re-auth** if the OAuth token lapses mid-session (`nb env auth havenbeheer`).

## Verification tooling
- `nb api resource list --resource flow_nodes --filter '{"workflowId":<id>}'` to confirm node counts/branches.
- `nb api workflow flow-nodes test` for calculation/condition nodes (NOT query nodes — 400s,
  `feedback_flow_nodes_test_coverage`); verify query nodes via live data readback.
- Custom-action workflows can't be `workflows execute`'d headless (no user,
  `feedback_custom_action_execute_no_user`) → user drives those buttons (Close Project, drawdown submit).
- Live data readbacks (`nb api resource list`) after each workflow run to confirm status transitions
  and `committed_usd` sums.
