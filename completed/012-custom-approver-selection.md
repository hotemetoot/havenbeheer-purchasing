# 012 — Submitter-selectable dept-stage approver

> **Retires the MVP010 skip path (D29).** The per-PR `skip_dept_approval` toggle is replaced by a
> per-PR *custom approver* override. The dept stage is no longer skippable — it is always an
> approval, but the submitter may reassign it away from the dept head (with the dept head FYI-notified).
> `skip_dept_approval` is removed from the workflow + UI but the **column is kept** (unused) to avoid
> data loss — drop later with explicit OK. See decisions D36.

## Goal
On the PR create form the submitter can override who approves the department stage. It **defaults to
the department head** (unchanged behaviour, no field touched). A "custom approver" checkbox reveals a
picker scoped to the submitter's department; when a custom approver is chosen, the dept-stage approval
task goes to that person instead, and the department head receives an in-app FYI notification.

## Scope (in)
- **Two new `purchase_requests` fields:**
  - `use_custom_approver` — boolean, default false.
  - `custom_approver` — m2o → users; picker **filtered to the submitter's department**
    (`mainDepartment` = submitter's dept). No `departments` model change.
- **Create form (`e76c40c8c79`):** checkbox + linkage rule that reveals + requires `custom_approver`
  only when the checkbox is checked (mirror the `needs_director_approval` → `justification` pattern).
- **Detail popup (`2b367dbd157`):** both fields read-only.
- **PR Approval workflow revision (`cv237r8h7k9`):** after the existing auto-skip check
  `5hed96jh1u7` (submitter IS their own dept head → skip, unchanged, no notify), the false branch
  tests `use_custom_approver == true AND custom_approver != null`:
  - **true** → FYI-notify the dept head (in-app) → **new** Dept Approval node assigned to
    `{{$context.data.custom_approver.id}}` → converge to Procurement (`ec2h8cqal32`).
  - **false** → existing Dept Approval node `cfg687cye3n` (dept head) → Procurement.
  - Add `custom_approver` to the workflow **trigger appends** so the assignee path resolves.
- **Skip removal (workflow + UI only):** drop the skip condition `eafkgfa3axi` and update node
  `budfy1scwbw` from the new revision; the FYI notification node `5h232imw9ss` is **reused** (retargeted
  text) for the custom-approver notify. Remove the skip checkbox wrapper `830iodzmcjo` (create form)
  and the read-only wrapper `in24ndj91et` (detail popup).

## Scope (out)
- **Dropping the `skip_dept_approval` column** — kept, unused (D36). Drop later with explicit OK.
- **Any hierarchy/"assistant manager" model on `departments`** — the picker is just "anyone in the
  submitter's department"; no deputies relation, no ordered approver list.
- Reassigning the **procurement / director / board** stages — dept stage only.
- Pull-back / mid-flight reassignment after submission — the choice is fixed at creation.
- on_leave → secondary fallback for the custom approver (the submitter picks a live person).

## Dependencies
- Builds on the MVP1 approval workflow (`cv237r8h7k9`) as revised through D32/MVP011.
- Supersedes MVP010 (D29) behaviour.

## Acceptance
- A1: PR with checkbox **off** → dept stage task goes to the dept head exactly as today (regression).
- A2: PR with checkbox **on** + a chosen approver → dept stage task goes to **that** person; the dept
  head gets an in-app FYI notification; flow still converges to Procurement on approve.
- A3: the `custom_approver` picker only lists users in the submitter's department.
- A4: linkage — `custom_approver` is hidden when the checkbox is off and required when it is on.
- A5: auto-skip (submitter IS their own dept head) still skips the dept stage, regardless of the
  custom-approver fields.
- A6: `skip_dept_approval` no longer appears on either form and no workflow reads/writes it; the column
  still exists in the DB (unused).
- A7 (non-admin approver usability): the new dept approval node has pre-created per-action comment
  models so a non-admin custom approver can act without a `flowModels:save` 403.
- Manual verification by user (Pat/Oliver/Dana test users).

## Phases
- **012.1** Add `use_custom_approver` + `custom_approver` fields (`nocobase-data-modeling`).
- **012.2** Create-form checkbox + linkage + dept-scoped picker filter; detail-popup read-only;
  remove the two skip wrappers (`nocobase-ui-builder`).
- **012.3** Revise `cv237r8h7k9`: repurpose the skip branch into the custom-approver branch, add the
  new dept approval node (assignee `{{$context.data.custom_approver.id}}`), add `custom_approver` to
  trigger appends, reuse the notify node, drop skip nodes (`nocobase-workflow-manage`).
- **012.4** Pre-create per-action `CommentFormModel`s for the new dept approval node + set each action's
  `commentFormUid` (avoids the blueprint 403, see auto-memory `feedback_approval_blueprint_comment_models`).
- **012.5** Verify A1–A7 end-to-end (user-driven), then activate the revision.
- **012.6** Docs: add D36 (supersedes D29), update `design/users-and-roles.md` + `design/permissions.md`,
  mark roadmap MVP010 superseded, update `project_current_state.md`.

## Risks / known traps
- **Approval-node assignee from a variable** — verify early (012.3) that the new node's assignee
  resolves from `{{$context.data.custom_approver.id}}`. The existing dept node already uses a context
  path (`createdBy.mainDepartment.main_approver`), so this is expected to work; confirm before wiring forms.
- **Revision drops branch nodes** — after revisioning `cv237r8h7k9`, verify the full node count and
  recreate any dropped condition-branch nodes before enabling (CLAUDE.md NocoBase rule).
- **Comment-model 403** — every fresh approval node needs pre-created comment models (012.4).
- **Workflow versioning** — `cv237r8h7k9` has executed; revision required (never edit in place). Force
  the same key via raw `--body` to avoid the stray-copy CLI bug (`feedback_workflow_revision_key_bug`).
- **Auto-skip precedence** — keep `5hed96jh1u7` as the first check so a submitter who is their own dept
  head still skips, even if they also tick custom approver.

See [decisions.md](../decisions.md) (D36) and `project_current_state.md` for live IDs and node keys.

## As built (2026-06-09)

- **Fields:** `use_custom_approver` (boolean), `custom_approver` (m2o → users, FK `customApproverId`).
- **Workflow `cv237r8h7k9` revision `369076269481984`** (enabled + current; prior `368983543906304` retired).
  30 nodes. Condition `eafkgfa3axi` → "Custom approver chosen?" (incl. `custom_approver.id != createdById`
  self-exclusion). New approval node **`fifkfnqn9pm`** "Custom Approver Approval" (assignee
  `{{$context.data.custom_approver.id}}`, approvalUid `1a1zhqfmpdl`, taskCardUid `369lxzap6i2`); outcome
  updates `r8f85w1w1ze` (approve→pending_purchasing_review) / `8loza7mypxd` (return→info_requested) /
  `vhize11vzsg` (reject→rejected). Notify reused `5h232imw9ss`. Comment models `jlx5nh8qh0d`/`njquu85vbz0`/
  `etxsnz1y7zp` exist (duplicate carried them → no 403).
- **UI:** create form `e76c40c8c79` — checkbox `r9iu06my5ot`, picker `gfozpat06nw` (inner
  `mu4s7d3w0h2`/selector `ueeb9ybhmuc`), field-linkage rules show+require / hide. Detail popup
  `2b367dbd157` — added `use_custom_approver` (`7jjizc66ex2`) + `custom_approver` (`9tpfw54yy1e`)
  read-only; removed skip read-only `in24ndj91et`.
- **Deviations from plan:**
  - Create form already had **no** `skip_dept_approval` (and no `needs_director_approval`) — user had
    rebuilt it; only the detail-popup skip wrapper needed removing.
  - **Picker data scope is a manual UI step** — the public CLI authoring API exposes no data scope on the
    record picker, so the same-dept + exclude-self filter must be set via the form's "Set data scope" UI
    setting. Self-approval is hard-blocked server-side regardless (condition self-check), so this is UX-only.
- **Pending:** A1–A7 user verification; manual picker data-scope step; `skip_dept_approval` column drop
  (deferred, retained unused).
