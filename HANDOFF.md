# HANDOFF — Role hardening, remaining phases (written 2026-06-11)

Context: the 2026-06-11 audit + remediation session completed **Phase 0** (member `ui.*` snippet
revert, comment models verified) and **Phase 1** (role restructure — see D38 and
`project_current_state.md` § Roles & ACL; user-verified end-to-end and committed). This file specs
the remaining phases. Read CLAUDE.md rules + the new auto-memories
(`feedback_acl_independent_resource_pitfalls`, `feedback_approval_form_render_update_grant`)
before executing. **Re-query active workflow versions live before touching any workflow.**

User-approved decisions already made (do not re-ask): fiona.finance as new Finance test user;
operations role bound to Operations dept; Board assignee data-driven from Procurement
main_approver (existing qProc query node); guards inside custom-action workflows are the accepted
protection model for trigger buttons (no per-workflow trigger ACL exists).

---

## Phase 2 — Data-driven approvers (replaces hardcoded Director [12] / Board [11])

1. Create user **fiona.finance** (Finance dept `363554454962177`, member base role).
2. Set `departments.main_approver`: Director dept `363554454962176` → Dana (12); Finance dept →
   fiona. (Procurement → Pat 11 and Operations → Oliver 10 already set.)
3. **finance role grants** (lesson from Phase 1 — approval forms render only with an update
   grant): give `finance` an independent `purchase_requests` row = view (all 37 fields, explicit
   list!) + render-enabler update (2 rejection fields, scopeId 10 "PR — director stage" or a
   finance-stage scope when one exists). Without this, fiona's future approval popups are blank.
4. **PR Approval revision** (key `cv237r8h7k9`, active was `369166026080256` — RE-QUERY FIRST):
   - Same-key revision via raw `--body '{"key":"cv237r8h7k9","enabled":false,"current":false}'`
     (CLI `revision` otherwise mints a new key — `feedback_workflow_revision_key_bug`).
   - Add a "Query Director dept" node (filter id `363554454962176`, appends `main_approver`)
     before the Director approval node; set Director node `sxvxwl498xg` assignees to the variable
     `{{$jobsMapByNodeKey.<newQueryKey>.main_approver.id}}` (filter-block form — see
     `feedback_approval_assignee_from_variable`).
   - Board node `01upqmcb1qy` assignees → `{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}`
     (qProc already queries Procurement dept with main_approver appended).
   - Verify node count = 31 (30 + the new query). Verify all approval-surface comment models
     exist (per-action `commentModelUid` under `stepParams.clickSettings.saveResource`).
   - `flow-nodes test` the new query + assignee resolution, enable, user round-trip test, then
     disable the old version stays automatic (current flag).
5. Drop the hardcoding note from state doc; record D-entry (data-driven approvers).

## Phase 3 — Cleanup (each irreversible step needs explicit user OK + rollback note)

1. **Stale fields** — JSON-snapshot each record set first, then drop:
   - `purchase_requests.needs_director_approval` (remove read-only popup display wrapper
     `p9acb4e35of` first) and `purchase_requests.skip_dept_approval` (dead since MVP012).
   - `purchase_orders.cancelled_at` (unused since D28).
   - `departments.secondary_approver`, `users.on_leave` (user-confirmed: fallback never built,
     system stays dynamic via main_approver edits).
   - After dropping, scrub the dropped names from ACL field whitelists (operations/procurement/
     director rows still list e.g. `needs_director_approval`, `skip_dept_approval`,
     `cancelled_at` — harmless but re-apply clean payloads) and from trigger appends if present.
2. **Test fixtures** — confirm the list with the user first:
   PRs PR-26-0008..0011 (ids 368984082874368, 368984082874369, 368984082874370, 368984084971520),
   POs PO-26-T1..T4 (ids 368984504401923, 368984531664899, 368984533762051, 368984533762055);
   candidate PR-26-0014 "olvire custom" (id 369155204186112, pending_purchasing_review) — ASK.
   Temporarily disable Guard A (`496ookqmg01`), PO immutability (`xvcsdv07c5j`), line immutability
   (`f3dkb37te22`); delete (lines → POs → PRs); re-enable all three; verify re-enabled.
3. **Drop the `test` collection** (0 records — re-verify before drop).
4. `purchase_requests.needs_director_approval` had defaultValue `true` (boolean) at audit time —
   moot once dropped; if retained, fix to `false`.

## Phase 4 — Docs + low-priority (mostly DONE 2026-06-11)

Already done at the Phase-1 session end: state doc, D38/D39, CLAUDE.md rules (ACL self-sufficiency,
render-enabler, live re-query, softened branch-drop warning), guidelines doc, auto-memories.
Remaining after Phases 2–3: update state doc + roadmap rows, D-entry for data-driven approvers,
delete this HANDOFF.md when all phases are complete.

## Low priority / follow-ups (user-approved "afterwards")

- `po_lines` titleField → `description` (m2o displays show raw IDs otherwise).
- Workflow executions retention (371 executions at audit) — prune or configure retention.
- **Board approval surface `xwd019rr78k` has only an Approve action** (no Reject/Return buttons)
  though the workflow has board reject/return outcome nodes — ask the user if intentional.
- **Scopes 3, 6–9** (`rolesResourcesScopes`) contain snake_case FK columns (`department_id`,
  `submitter_id`) and will 400 if ever bound — fix to camelCase like scope 2, or delete.
- **D39 follow-ups (draft stage removed by user):** the Cancel workflow guard
  (`kj9d7bnvw02`, status=="draft") now never matches → Cancel is effectively dead for PRs;
  scope 2's editable window is effectively only `info_requested`. Ask the user whether
  cancel-before-decision / edit-own-pending should exist; adjust the Cancel workflow condition
  and scope 2 accordingly. Also: status enum still contains `draft` and the field default is
  still `'draft'` — if the flow change is permanent, consider changing the default to
  `pending_dept_approval`… BUT the PR Approval root update node sets status anyway; verify how
  the user's "submit directly" form/flow actually sets status before touching anything.
- Pre-existing procurement `attachments`/`suppliers` rows reference dangling scopeId
  `363334209503233` (behaves as all-rows) — optionally re-apply with explicit null/all scope.
