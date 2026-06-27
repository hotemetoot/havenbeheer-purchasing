# MVP014 — continue: drawdown branch + Project-Approval surfaces (logic-first)

## Context

MVP014 (Projects & budget drawdown, D49) is partially built. Already live + CLI-verified:
`projects` collection, `purchase_requests.project` m2o, `committed_usd` recompute A/B
(`j2fp3wa4o1k` / `0mckvnf319y`), and both PR budget guards (`lylobzvlh5p` create / `ebq41ibq60r`
update). The **Project Approval** workflow `hzykothf9cx` exists but is **disabled — it has no
approval surfaces**, so it can't be enabled. And project-linked PRs don't yet skip the director:
the PR Approval workflow has no drawdown branch.

This session builds the two remaining **headless-logic** layers, then pauses for the user to verify
before the UI layer (014.5) is built next session. User decisions taken: **Operations** is the
project-creator role (mirrors PRs); **logic first, pause for E2E**.

## Live state (corrects doc-lag — verify again at execution start)

- **PR Approval** active = **`371882305585152`** (key `cv237r8h7k9`, 34 nodes, enabled+current).
  Doc records `371864957943808` (stale — user revised again after MVP015).
  - Drawdown insert point: **`ec2h8cqal32`** (Procurement Approval, id `…585173`) **br=2** →
    currently **`bizoy1sj87j`** (Director-decision condition, id `…585159`, br=2 up=ec2h8cqal32).
  - Terminal approved nodes already carry D50 notifications: `jy1365pvsce`→`hy95mz4oo5f`,
    `kj1zcmujub8`→`dproua9530i`, `8gqeq6djrfj`→`p53qqltz9v2`.
- **Project Approval** = **`371693220069376`** (key `hzykothf9cx`, current, **disabled**, 20 nodes,
  single version). Four approval nodes needing surfaces: `tkw661dvfjq` (Dept Owner),
  `ik1ixug5rrs` (Procurement), `su6sbibmoky` (Director), `vwuxv7zih9f` (Board).
- `projects` ACL = **greenfield** (0 rows). Roles: admin, director, finance, member, operations,
  procurement, root. Procurement already has `attachments` create (id `367892747780096`, D32) →
  board upload covered.

**CLAUDE.md rule:** re-query both active versions live before touching either workflow (the user
revises between sessions). Re-auth done at session start.

---

## Phase A — 014.4: PR-Approval drawdown branch

Project-linked, approved-project PRs must skip director + board (Procurement is final) but keep the
upstream dept-owner stage. Insert a condition after Procurement approves, before the director logic.

**Same-key revision** of `371882305585152` (workflow has executed — force same key via raw `--body`,
`feedback_workflow_revision_key_bug`). Work on the new disabled version, then enable.

1. **Trigger appends** — add `project` (so `$context.data.project.id` / `.status` / `.budget_usd`
   resolve). Without this the branch reads empty silently.
2. **Insert "Project drawdown?" condition** as the new **br=2 head on `ec2h8cqal32`**:
   - Leaves (basic engine, scalar equality — no inline arithmetic, `feedback_condition_inline_arithmetic`):
     `project.id != null` **AND** `project.status == "approved"`. (Confirm the null/empty calculator
     during execution; basic `$notEmpty`/`$eq`. Falls through to existing director logic if unset.)
   - **true →** new Update node `Project drawdown → Approved` (status=`approved`, `approved_at=now`)
     → **D50 notification** to requester only (`{{$context.data.createdById}}`, channel
     `approval-todo-in-app-message`, same title/content shape as the existing approved nodes; this is
     the 4th approved path D50 anticipates — Procurement is final, so **no** procurement-head ping).
   - **false →** reparent existing **`bizoy1sj87j`** under this condition's false branch (unchanged
     director→board logic).
3. **Verify before enabling** (CLAUDE.md): node count = 34 + (1 condition + 1 update + 1 notification)
   = **37**; every existing branch preserved; ProcessForm uids regenerate → confirm all approval
   comment models resolve (no `flowModels:save` 403 for approvers). `flow-nodes test` the new
   condition across {has approved project, has non-approved project, no project}.
4. **Enable** the new revision; disable predecessor (rollback path).

**CLI verification (A):** create a PR linked to a status=`approved` project via API; drive it through
dept→procurement approve; confirm it lands `approved` (not `pending_director_approval`). Regression:
an unlinked ≥ $300 PR still routes to director. A PR linked to a *non-approved* project falls to the
director path (and is independently blocked at submit by guard `lylobzvlh5p`).

---

## Phase B — 014.2b/c: Project-Approval surfaces + ACL + enable

The 4 approval nodes have no surfaces. Apply the approval blueprint per node, fix the comment-model
omission, add live-record display fields, wire ACL, then enable `hzykothf9cx`.

1. **Apply approval surfaces** to `tkw661dvfjq`, `ik1ixug5rrs`, `su6sbibmoky`, `vwuxv7zih9f`
   (blueprint creates each ProcessForm + Approve/Reject/Return actions).
2. **Pre-create per-action `CommentFormModel`s** (3 per node) and set each action's `commentFormUid`
   — the blueprint omits them → approvers 403 on `flowModels:save`
   (`feedback_approval_blueprint_comment_models`). Verify every action's `commentFormUid` resolves.
3. **ProcessForm display fields** — add readPretty `PatternFormItemModel`s for live record data
   (`feedback_approval_details_block_snapshot` — don't rely on the approvalInformation snapshot
   block; associations render blank there). Fields: `project_number`, `title`, `description`,
   `budget_usd`, `status`, `submitter`, `department`, `committed_usd`. **Board ProcessForm only:**
   add `approval_document` as **editable + required** (D32 board-upload pattern; ≥ $15k sign-off).
4. **ACL on `projects`** (greenfield; mirror PR setup, mind `feedback_acl_independent_resource_pitfalls`
   — self-sufficient per-row `view`, new roles need desktop routes):
   - **operations** — create + view (project creator).
   - **render-enabler `update` grant** (narrow fields + status scope) for every role whose users
     approve: **operations**/**finance** (dept owners), **procurement** (proc + board = Pat),
     **director** (Dana). ProcessForm renders only with SOME update grant
     (`feedback_approval_form_render_update_grant`).
   - Board upload: procurement `attachments` create already present (verify includes `create`).
5. **Enable** `hzykothf9cx`.

**Verification (B) — user task-center, no Projects page needed yet:** I create a test project via API
(< $15k and ≥ $15k variants). Each approver (Oliver/Fiona dept, Pat proc+board, Dana director) opens
their task from the NocoBase notification/task center and confirms: ProcessForm renders live data (no
403, no blanks), Approve/Reject/Return work, board form requires the document. Confirm a < $15k
project finishes at director; a ≥ $15k project routes to board then `approved`.

---

## Deferred to next session (after user E2E sign-off)

- **014.5 — UI:** Projects menu/page (table + create form + detail showing budget/committed/remaining
  + child PRs), **Close Project** button + custom-action workflow (status=`closed`; procurement/
  director), PR-form `project` picker (data scope = approved+open, **set via form UI** —
  `feedback_record_picker_datascope_not_cli`), and PR + projects **ACL field whitelists** (add
  `project` to PR create/update). The guard enforces server-side regardless of picker scope.
- **014.6 — full user E2E** A1–F2 from the chunk + finalize docs.

## Docs + commits (this session)

- Commit after Phase A verified, after Phase B verified (CLAUDE.md "this worked" milestones).
- Update `project_current_state.md`: corrected active PR-Approval version + new drawdown nodes; Project
  Approval enabled + surface/comment-model/ACL uids; mark 014.4 + 014.2b/c done, 014.5/014.6 pending.
- Append/extend the D49 status line in `decisions.md` (drawdown branch + surfaces built; list MVP014).
- Update roadmap MVP014 status line.
- Save any new cross-project NocoBase gotcha as `feedback_*.md` if one surfaces.

## Risks / traps (from auto-memory + chunk)

- **Workflow versioning** — both are executed; revision only, force same key via raw `--body`; verify
  node count + branches before enabling.
- **Whole new surface set** — comment models omitted by blueprint (403); pre-create + set
  `commentFormUid`. ProcessForm needs an update grant to render. Board upload needs attachments create.
- **Condition engine** — no inline arithmetic; scalar leaves only; prefer math.js only where a
  `$jobsMapByNodeKey` result is referenced.
- **Doc-lag** — re-query active PR-Approval version immediately before Phase A.
- **flow-nodes test** — works for condition/calculation, **400s on query nodes** — verify those by
  live readback.
