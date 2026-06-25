# 015 — "PR approved" notifications

Status: verified (user walkthrough 2026-06-24)

> **Closes a feedback gap: today nothing notifies anyone when a PR reaches `approved`.** Adds in-app
> notification nodes to the PR Approval workflow so that on final approval the **original requester** is
> told, and the **head of procurement** (Pat) is told *only* when Procurement is **not** the final
> approver. See decision D50.

## Goal
On `status → approved`, send an in-app notification reading `PR-26-NNNN "Title" has been approved.`:
- **Requester always** (the PR's `createdBy`).
- **Head of procurement** additionally — **only on the Director-approved path**.
- **Not** the head of procurement when Procurement itself is the final approver (regular < $300), nor on
  the Board-approved path (user decision — board sign-off is the requester's concern, procurement
  already saw it pass their stage).

## Scope (in)
- **PR Approval workflow revision (`cv237r8h7k9`):** three new **notification** nodes, each appended as
  the downstream of one of the three (and only three) terminal nodes that set `status = approved`:
  | Terminal node | Path | Receivers |
  |---|---|---|
  | `jy1365pvsce` Procurement Approved (No Director) | regular < $300, Procurement final | requester only |
  | `kj1zcmujub8` Director Approved | < $15k director path | requester **+ head of procurement** |
  | `8gqeq6djrfj` Board Approved | ≥ $15k board path | requester only |
- All three: channel `approval-todo-in-app-message` (the only configured channel), title
  `PR approved: {{$context.data.title}}`, content `{{{$context.data.pr_number}}} "{{$context.data.title}}" has been approved.`,
  `ignoreFail: true`, deep-link to the PR view.
- Requester = `{{$context.data.createdById}}`; head of procurement = `{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}`
  (the existing root query node `yrl9kgkrb3x`, which runs upstream of all branches).

## Scope (out)
- **Email / other channels** — only the in-app channel exists; email would need SMTP setup. Deferred.
- **Notifications on reject / return / info-requested** — this chunk is approval-only.
- **Using the `submitter` field instead of `createdBy`** — `createdBy` is what the whole workflow routes
  on and is always populated; `submitter` is an optional m2o not maintained by the workflow.
- Any approval-form / routing logic change — untouched.

## Dependencies
- Builds on PR Approval `cv237r8h7k9` (active `370060903907328` at session start).
- Reuses the root query node `yrl9kgkrb3x` (Pat) added for D40 data-driven assignees.

## Acceptance
- A1 (regular < $300, Procurement final): approve → **requester only** gets "PR approved …"; Pat does not.
- A2 (director < $15k): director approves → **requester + Pat** both get it.
- A3 (board ≥ $15k): board approves → **requester only**; Pat does not.
- A4: notification title/body renders the PR number + title correctly and links to the PR.
- A5 (no regression): approval forms (dept/custom/procurement/director/board) still render with their
  customizations (slim board form + required `board_approval_document`, `is_regular` checkbox on
  procurement) and approvers can approve without a `flowModels:save` 403.

## Phases
- **015.1** Same-key revision of `cv237r8h7k9` (force key via raw `--body`; new version disabled). ✓
- **015.2** Add three notification nodes by duplicating the existing notification node and overriding
  config (no `create` subcommand exists; `duplicate` clones a single node + gives a working config). ✓
- **015.3** Verify wiring (each terminal node's downstream = its notification node) + configs. ✓
- **015.4** Enable the new version (auto-disables predecessor). ✓
- **015.5** User live walkthrough A1–A5 (CLI can't drive approval clicks). ✓ **PASSED 2026-06-24.**
- **015.6** Docs: D50, roadmap row, `project_current_state.md` (new version + node keys), this As-built.

## Risks / known traps
- **Workflow versioning** — `cv237r8h7k9` has executed; revision required, never edit in place. Forced
  same key via raw `--body` (`feedback_workflow_revision_key_bug`).
- **Surface regeneration** — revisioning mints new approval surface uids. Historically (≈20 prior
  revisions) the clone preserves form customizations; A5 confirms this live. Rollback if a form is broken.
- **`yrl9kgkrb3x` availability** — that query node runs at the root, upstream of all three terminals, so
  its job result is in `$jobsMapByNodeKey` on every approved path (already proven for board/procurement
  assignees).
- **Rollback** — re-enable predecessor `370060903907328` (`resource update --values '{"enabled":true,"current":true}'`).

## As built (2026-06-24)

- **Workflow `cv237r8h7k9` revision `370060903907328` → `371864957943808`** (enabled + current; same key
  forced via raw `--body`; predecessor auto-disabled). 31 → **34 nodes** (3 notification nodes added).
- **Three notification nodes** (created by duplicating existing notification node, new ids/keys):
  - `hy95mz4oo5f` — downstream of `jy1365pvsce` (Procurement no-director) — receivers `[createdById]`.
  - `dproua9530i` — downstream of `kj1zcmujub8` (Director) — receivers `[createdById, {{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}]`.
  - `p53qqltz9v2` — downstream of `8gqeq6djrfj` (Board) — receivers `[createdById]`.
  - All: channel `approval-todo-in-app-message`, title `PR approved: {{$context.data.title}}`, content
    `{{{$context.data.pr_number}}} "{{$context.data.title}}" has been approved.`, `ignoreFail: true`,
    url `/admin/cuycec133qb/view/ceaecc4498c/filterbytk/{{$context.data.id}}`.
- **New approval surface uids on this revision** (regenerated by the revision): trigger approvalUid
  `kag2bc9wrq7`/taskCardUid `uxw4q4agtye`; Procurement `li2jfcxa8dl`/`bpta19xtqk2`; Dept
  `a54gfhbawdy`/`hcpbe6rn93u`; Custom `qehdzrghvic`/`prs357bu9ih`; Director `80b19uw01we`/`82g9tfjkmj7`;
  Board `m3ajd5fxxt5`/`42dyyh3m3sg`.
- **Verification:** node wiring + configs CLI-verified. **A1–A5 user walkthrough PASSED 2026-06-24** (requester-only on regular<$300 + board paths, requester+Pat on director path, approval forms render with customizations, no 403).
- **Decision:** D50.
