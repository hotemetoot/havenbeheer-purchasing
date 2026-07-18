# 014 — Projects & budget drawdown

> **A pre-approved budget envelope that lets Procurement run multiple PRs without per-PR director
> approval.** A user creates a *project* (e.g. "Repair warehouse", $10,000), it goes through an
> approval ladder similar to a regular PR, and once approved, PRs linked to that project draw against
> the envelope. Project-linked PRs **skip the director (and board)** — Procurement is final — but are
> **hard-blocked** from collectively exceeding the project budget. Dept-owner approval still applies to
> each drawdown PR. See decision D49 (new).

> **Build status (2026-06-27):** 014.1 + 014.3 done (collection, m2o, recompute A/B, budget guards).
> **014.4 done** — PR-Approval drawdown branch (rev `372368060514304`; cond `492iwdlv0mr` → update
> `48myq8dpqza` + notif `kykl9gnqj9h`). **014.2b/c done** — Project Approval `hzykothf9cx` ENABLED with
> 4 approver surfaces + initiator (centralized) + ACL (operations/procurement/director). **Pending:**
> 014.5 remainder — **Close Project button only**, plus 014.6 user E2E.
>
> **Live inspection 2026-07-18** (describe-surface, following popup→template→template chains — the
> method that avoids reference-block false negatives): Projects page `71k045k77w2` BUILT (table:
> Project Number/Title/Status/Budget/Committed, Add new, View detail child page with remaining/committed
> and a linked-PRs sub-table). PR creation form BUILT with the `project` picker (template
> `0v8inq52okd` "New Purchase Request" → `n9f8v5vnhhc` "Form (Add new): Purchase Requests" → surface
> `e76c40c8c79`). PR whitelists BUILT (`project`+`projectId` on member create/update, operations,
> procurement, finance). Board `approval_document` BUILT, required:true on the Board Approval surface
> `x1v23aiqd0z` (workflow `hzykothf9cx` rev `373589018214400`). NOT built: a Close button anywhere on
> the Projects page tree (full resolved tree checked, no reference blocks hiding one).

## Interface brief — Complete Project button (last 014.5 item; human builds, suggestion sheet only)

The backend is done and verified: the **Complete Project** custom-action workflow (key `px2xvjaxoqf`,
D-entry 2026-07-05 renamed it from "Close") sets an approved project to `completed` + stamps
`completed_at`, and rejects any project that isn't `approved`. Only procurement holds the trigger
grant (R27, suite-green). The button is the only missing piece.

- **Where:** the Projects page (`71k045k77w2`) — either the detail (View) child page's action bar or a
  table row action. Detail page recommended: completing is deliberate, not a list-scan action.
- **Button:** a **Trigger workflow** button (one-click, not a form Submit — custom-action workflows
  only bind to these, see `feedback_workflow_form_button_pattern`), bound to workflow key
  `px2xvjaxoqf`. Pick the workflow by name "Complete Project" in the binding dropdown.
- **Confirmation:** enable the built-in "Secondary confirmation" — a completed project is locked by
  the D63 guard, so this is one-way in practice. Suggested text: "Complete this project? No new PRs
  can draw on it afterwards."
- **Visibility linkage:** show only when `status == approved` (any other status would just get the
  workflow's reject message). Optionally also hide for non-procurement via
  `ctx.user.roles.title` `$includes` "Procurement" (capitalized title, not the lowercase name —
  `feedback_linkage_rules_user_roles`); the server enforces the role either way.
- **After success:** stay on the current popup/page with a refresh, so the status badge flips to
  Completed immediately (`feedback_updaterecord_no_block_refresh`: trigger-workflow buttons refresh
  correctly with afterSuccess "stay").
- **Quick self-test:** as Pat on an approved project → confirm → badge shows Completed; the same
  button on a draft project should be hidden (or rejected with the workflow's message if shown); a
  new PR linked to the completed project must be blocked (R28).

## Goal
- A `projects` collection holds a budget envelope (USD) + scope description, approved via its own
  ladder (dept → procurement → director → board ≥ $15k), reusing existing steps and thresholds.
- `purchase_requests.project` (optional m2o) links a PR to an approved project.
- A project-linked PR routes **dept owner → procurement → approved** (director + board skipped).
- The sum of a project's non-rejected/cancelled child PRs (`quoted_total_usd`) is **hard-blocked** at
  PR submit from exceeding `projects.budget_usd`.
- Projects are **closed manually** (a Close button); a closed/non-approved project blocks new PRs.

## Decisions locked (brainstorm 2026-06-21)
1. **Budget currency:** USD-only — single `budget_usd` number. Multi-currency deferred.
2. **Over-budget PR:** hard block at submit (request-interception, D47 pattern) with a dynamic
   "remaining budget" message. Drawdown counts **all child PRs except `rejected`/`cancelled`** (reserve
   on submit, so two in-flight PRs can't both "fit" then bust the cap).
3. **Drawdown PR ladder:** dept owner **still applies**; director + board skipped.
4. **Project approval:** a **separate** workflow, reusing the PR ladder's spine and the D32 board
   threshold; **drops** the custom-approver branch (D36) and the `is_regular`/$300 nuance (D37) —
   director always reviews an envelope.
5. **Close:** manual (a Close Project button). No auto-close on budget exhaustion.
6. **Project envelope passes through the Procurement stage** (full PR-ladder mirror).
7. **`project_number` sequence** `PRJ-YY-NNNN` (mirrors `pr_number` D31).

## Scope (in)

### New collection `projects`
- `project_number` — sequence, `PRJ-YY-NNNN`, `inputable:false` (D31 pattern).
- `title` — input, required, **title field** (`feedback_related_record_title_field` — referenced by the
  PR m2o, so a title field is mandatory).
- `description` — vditor/textarea (scope of work).
- `budget_usd` — number (USD envelope cap; the figure the budget guard checks).
- `status` — select: `draft`, `pending_dept_approval`, `pending_purchasing_review`,
  `pending_director_approval`, `pending_board_approval`, `info_requested`, `approved`, `rejected`,
  `closed`.
- `submitter` — m2o → users (owner; createdBy).
- `department` — m2o → departments (drives D40 dept-owner assignee resolution).
- `approval_document` — attachment (multi), board sign-off; editable+required on the Board ProcessForm
  only (D32 pattern, ≥ $15k).
- `approved_at` — datetime.
- `rejection_reason_category` (select) / `rejection_comment` (textarea) — reuse PR pattern.
- `committed_usd` — number, **workflow-maintained** running sum of child-PR drawdown (mirrors PO
  `lines_total` recompute, D47); powers a UI "remaining = budget − committed" display without a
  relation-traversing formula (which fails silently, `feedback_formula_field_scope`).
- `purchase_requests` — o2m → purchase_requests (inverse of the PR m2o).

### New relationship
- `purchase_requests.project` — m2o → projects, FK `projectId`, **nullable** (regular PRs leave blank).
- Add `project` (+ `project.status`, `project.budget_usd`) to the **PR Approval trigger appends**.

### Project Approval workflow (new, separate)
A trimmed clone of the PR Approval spine, type `approval`, collection `projects`:
- Set status `pending_dept_approval` → query Procurement dept (board assignee = Pat).
- Auto-skip condition "submitter is dept main approver?" (reuse PR pattern) → skip dept stage.
- **Dept Owner Approval** (assignee `{{$context.data.createdBy.mainDepartment.main_approver.id}}`, D40).
- **Procurement Approval** (decision 6).
- **Director Approval** — always (assignee via query node on Director dept, D40). No `is_regular`/$300.
- **Board ≥ $15k** (reuse D32 threshold, read `budget_usd`) → Board Approval requiring
  `approval_document` upload.
- Terminal updates: `approved` + `approved_at`; `rejected`; `info_requested` (return).
- Pre-create per-action `CommentFormModel`s (`feedback_approval_blueprint_comment_models`); add a
  render-enabler `update` grant per approver role (`feedback_approval_form_render_update_grant`); grant
  board `create` on attachments (`feedback_approver_attachment_upload_acl`).

### PR Approval revision — drawdown skip branch
- **Re-query the live active version first** (`workflows` filter `{"current":true,"enabled":true}`,
  key `cv237r8h7k9`; last known `370060903907328`). Revision required (executed) — force same key via
  raw `--body` (`feedback_workflow_revision_key_bug`).
- Insert one condition node **after Procurement approves (`ec2h8cqal32` br=2), before** the existing
  director-decision `bizoy1sj87j`:
  - **"Project drawdown?"** — AND: `project.id != null` AND `project.status == approved`.
    Read from `{{$context.data.project.*}}` (needs the trigger append). Use math.js
    (`feedback_prefer_mathjs_engine`) or basic-engine `!=`/`==` scalar leaves (no inline math).
    - **true** → Update → `approved`, `approved_at=now` (skip director + board).
    - **false** → existing `bizoy1sj87j`, unchanged.
- The dept-owner stage is upstream → still applies (decision 3).
- After revision, **verify full node count + every branch preserved** before enabling (CLAUDE.md rule);
  ProcessForm uids regenerate — comment models must carry over (no 403 for Pat).

### Budget hard-block guard (new)
`request-interception`, global, sync; actions create + update on `purchase_requests`. D47 PO-budget
pattern:
- Skip unless `params.values.project` (or queried PR's `project`) is set.
- Query the project; reject if `project.status != approved` (can't draw on unapproved/closed envelope).
- Query sibling child PRs, **exclude `rejected`/`cancelled`**, exclude self on update; calculation node
  (math.js) sums their `quoted_total_usd`; compare `Σ + thisPR.quoted_total_usd > budget_usd`.
- Over-cap → response-message (dynamic "Remaining budget: $X") + end-process `endStatus:-1`
  (`feedback_inline_guard_end_node`).
- Arithmetic in a **separate calculation node**, never inline in the condition
  (`feedback_condition_inline_arithmetic`).

### `committed_usd` recompute (new)
Collection-trigger workflow(s) on `purchase_requests` (create/update/delete affecting `project` or
`quoted_total_usd` or `status`): recompute the parent project's `committed_usd` = Σ non-rejected/cancelled
child `quoted_total_usd`. Mirrors PO recompute A/B (D47) — may need split workflows per the
mode-array constraint (modes [1,2,4,3]).

### Close Project
- Custom-action button (procurement/director) → workflow sets `status=closed`. Manual (decision 5).
- A closed project fails the guard's `status == approved` check → no new PRs.

### ACL + UI
- New `projects` ACL mirroring PR setup: submitter create/view, approver view + render-enabler update,
  procurement close; mind `feedback_acl_independent_resource_pitfalls` (self-sufficient view per row;
  new roles get zero desktop routes).
- Add `project` to PR create/update **field whitelists**.
- Projects menu/page: table + create form + detail (showing budget / committed / remaining + child PRs).
- Four project approval ProcessForms; Close button.
- `project` picker on the PR create form; data scope = approved + open projects, **set via form UI**
  (`feedback_record_picker_datascope_not_cli`); enforced server-side by the guard regardless.

## Scope (out)
- Multi-currency project budgets (USD-only for now, decision 1).
- Auto-close / "exhausted" status on hitting 100% (manual close only, decision 5).
- Per-PR partial-budget reservations / encumbrance accounting beyond the simple sum.
- Project editing after approval (budget changes post-approval) — out unless raised; treat approved
  envelope as fixed.
- Reusing PR Approval for projects (explicitly a separate workflow, decision 4).

## Dependencies
- PR Approval workflow `cv237r8h7k9` (re-query live active version before revising).
- Reuses: D31 numbering, D32 board threshold + attachment-upload ACL, D40 data-driven assignees, D47
  budget-guard + recompute patterns, D48 currency handling (USD path).

## Acceptance
- **Project ladder:** A1 dept→proc→director approves a < $15k project → `approved`. A2 ≥ $15k project →
  board stage appears, requires `approval_document`, then `approved`. A3 reject/return at each stage
  behaves like PR. A4 submitter-is-dept-head auto-skips dept stage.
- **Drawdown routing:** B1 PR linked to an approved project, ≥ $300 → still **skips director** (status
  `approved` after Procurement). B2 same but unlinked PR ≥ $300 → director as before (regression).
  B3 dept-owner stage still runs on a project PR.
- **Budget block:** C1 child PRs summing < budget → allowed. C2 a PR that pushes Σ over budget →
  blocked with a remaining-budget message. C3 exactly == budget → allowed (≤). C4 two in-flight PRs
  that individually fit but jointly exceed → the second is blocked (reserve-on-submit). C5 PR linked to
  a non-approved or closed project → blocked.
- **Close:** D1 Close sets `closed`; D2 a new PR against a closed project → blocked.
- **committed_usd:** E1 reflects Σ of non-rejected child PRs; E2 updates on PR status change to
  rejected (drops out of the sum).
- **ACL/usability:** F1 each approver renders + submits their project ProcessForm without a 403
  (comment models + render grant present). F2 board upload works (attachments create grant).
- Manual end-to-end verification by user (Pat/Oliver/Dana/Fiona test users).

## Phases
- **014.1** — `projects` collection (+ `project_number` sequence) + `purchase_requests.project` m2o +
  `committed_usd` recompute workflow(s) (`nocobase-data-modeling`, `nocobase-workflow-manage`).
- **014.2** — Project Approval workflow + approval surfaces + pre-created comment models + render-enabler
  + attachment-create grants (`nocobase-workflow-manage`, `nocobase-acl-manage`).
- **014.3** — Budget hard-block guard (request-interception) (`nocobase-workflow-manage`).
- **014.4** — PR Approval revision: insert the project-drawdown skip branch; add `project` to trigger
  appends (`nocobase-workflow-manage`).
- **014.5** — UI: Projects page/forms/detail, Close button, PR-form `project` picker; PR + projects ACL
  field whitelists (`nocobase-ui-builder`, `nocobase-acl-manage`).
- **014.6** — Verification A1–F2 (user-driven) + docs: D49, roadmap MVP014, `project_current_state.md`
  (new collection/fields/workflows/IDs), finalize "As built".

## Risks / known traps
- **Whole new approval workflow = whole new surface set.** Comment models omitted by the blueprint →
  403 on `flowModels:save` for approvers; pre-create them and set each action's `commentFormUid`
  (`feedback_approval_blueprint_comment_models`). ProcessForm renders only with SOME `update` grant on
  `projects` (`feedback_approval_form_render_update_grant`). Board upload needs `create` on attachments
  (`feedback_approver_attachment_upload_acl`).
- **Workflow versioning** — `cv237r8h7k9` has executed; revision only, force same key via raw `--body`
  (`feedback_workflow_revision_key_bug`); verify node count + branches before enabling.
- **Re-query active PR-Approval version live** before revising — the user revises it between sessions;
  the doc lags repeatedly (last known `370060903907328`).
- **Condition engine** — no inline arithmetic in condition nodes (`feedback_condition_inline_arithmetic`);
  sum siblings in a calculation node, prefer math.js (`feedback_prefer_mathjs_engine`).
- **Formula can't traverse relations** (`feedback_formula_field_scope`) — `committed_usd`/remaining must
  be workflow-maintained, not a formula on `projects`.
- **Interception assoc-create has no source id** (`feedback_request_interception_assoc_create_no_source`)
  — if PRs are ever created as a `projects.purchase_requests` association, inject `projectId` via the
  form Submit's assign-field-values.
- **Boolean/string default coercion** (`feedback_fields_apply_boolean_default`) — verify any boolean
  defaults store real booleans.
- **Picker data scope not CLI-settable** (`feedback_record_picker_datascope_not_cli`) — user sets the
  approved/open project scope in the form UI; guard enforces server-side regardless.
- **ACL independent-resource pitfalls** (`feedback_acl_independent_resource_pitfalls`) — new collection
  needs self-sufficient per-row `view`; new approver roles start with zero desktop routes.
- **OAuth** — re-auth (`nb env auth havenbeheer`) before live work (done at session start 2026-06-21).
- **Size** — this is a large MVP; if the build runs long, 014.1–014.4 (data + logic) can land and be
  verified before 014.5 (UI) without leaving the system in a broken state (the guard + routing work
  headlessly; UI is the last layer).

See [decisions.md](../decisions.md) and `project_current_state.md` for live IDs and node keys.
