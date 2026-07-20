# Role & ACL Guidelines (NocoBase)

Distilled from the 2026-06-11 audit of this app. Written to be reusable in any NocoBase project; Havenbeheer-specific examples are marked as such.

---

## 1. Role architecture

- **One base role (`member`) + thin derived roles per function** (e.g. `procurement`, `director`, `finance`). Every user holds `member`; derived roles only *add* permissions. Never duplicate a grant on a derived role that the base role already provides.
- **Mirror departments with roles only when the role changes permissions.** A role with a `null` strategy and no resource permissions (Havenbeheer's `finance`) is an empty shell — acceptable as a placeholder for a planned MVP, but record that intent, otherwise it reads as misconfiguration.
- **Check `systemSettings.roleMode` before reasoning about any restriction.** Under `allow-use-union` a user's effective permission can be the **union of all their roles** — a restriction on a derived role is meaningless if the base role's strategy already grants the action. Tighten the base role first; widen via derived roles.

## 2. Strategy vs. independent resource permissions

- **Global `strategy.actions` has no field whitelist and no scope.** A role on strategy access can write *every field of every record* of every collection via the REST API — regardless of what forms show. Treat strategy as a coarse default for low-risk collections only.
- **`usingActionsConfig: false` makes configured resource rows inert.** Rows can exist in `rolesResources` that look like field whitelists but do nothing because the flag is off. When auditing, always read the flag, not just the rows.
- **Any collection whose lifecycle a workflow owns needs hard enforcement.** Either:
  - (a) set `usingActionsConfig: true` per role and whitelist fields, **excluding workflow-managed columns** (`status`, `approved_at`, stamps, derived totals); or
  - (b) add a request-interception guard that rejects client writes carrying those columns (detect via `{{$context.params.values.<field>}} != null`).
  Form-level `readPretty` is UI-only and protects nothing at the API layer.
- **Independent rows must be self-sufficient.** A `usingActionsConfig: true` row **suppresses the global strategy for that collection — even under role union** ("permissions add up" does not rescue it). Every independent row needs its own `view` action, even when the row exists only to grant create/update.
- **`fields: []` means NO fields, not all fields.** Always resolve the collection's full field list from metadata and write it explicitly (including `id`, stamps, `createdBy`/`updatedBy`, FK scalars). An empty list renders a near-empty table.
- **New roles have zero desktop route permissions.** Users whose active session role is the new role see no menu at all. Copy the base role's grants: `desktop-routes list --role-name member` → `desktop-routes set --role-name <new>`.
- **Prefer narrow independent grants over widening the strategy.** Example done right: procurement gets `create` on `attachments` only (approvers must upload files) instead of a global `create` that would let the role create PRs.
- **Policy decisions must map to enforced config.** If a decision says "role X cannot do Y" (Havenbeheer D25: procurement doesn't create PRs), verify the *union* of that user's roles actually denies Y — or record the decision explicitly as unenforced policy.
- **Custom row-level scopes: two tables exist, only one is enforced.** `dataSourcesRolesResourcesScopes` (`nb api acl data-sources roles-resources-scopes ...`, snowflake ids) is read by the ACL engine. `rolesResourcesScopes` (generic `nb api resource ... --resource rolesResourcesScopes`, small integer ids) **looks identical in shape and is a completely valid-looking config — but is silently never enforced** in this NocoBase version (2.1.0-beta.47, confirmed live 2026-07-02, Havenbeheer D57). A `scopeId` pointing at the dead table passes every readback check (stored correctly, correct filter, correctly referenced by the action) while granting unscoped access in practice. **Readback proves config was written, not that it's enforced** — the only real proof is one live HTTP call as a real non-admin user against the specific scoped action. Always create new custom scopes via `data-sources roles-resources-scopes`, never the bare `rolesResourcesScopes` resource name.

## 3. Snippets (configuration permissions)

- **Vanilla defaults:** admin `["pm", "pm.*", "ui.*"]`; member `["!ui.*", "!pm", "!pm.*"]`; derived business roles should negate all three.
- **`ui.*` un-negated on a non-admin role means those users can enter UI edit mode.** This shows up as a leftover debugging workaround (e.g. trying to fix approval-form `flowModels:save` 403s — the correct fix is pre-creating comment models — see `nb-bootstrap`'s `references/gotchas.md`, "Blueprint omits comment models"). Audit snippets on every role after any troubleshooting session.
- A role's `updatedAt` is a useful tell: a base role modified on a build/debug day deserves a diff against the vanilla defaults.

## 4. Approver assignment

- **Drive approver assignment from data, not hardcoded user IDs.** Put `main_approver` / `secondary_approver` (m2o → users) on the org collection (`departments`) and reference them in workflow assignees via variables (`{{$context.data.<assoc>.id}}` — requires the association in trigger appends). A hardcoded `[12]` in a workflow node means a personnel change requires a workflow revision instead of a record edit.
- **Don't model behavior you haven't built.** Fields like `secondary_approver` and `users.on_leave` that no workflow reads are a false promise — either wire the fallback or drop the fields.
- **Block self-approval server-side** (workflow condition comparing approver to `createdById`), not only via picker data scope — the scope is UX, the condition is the control.
- **Approval ProcessForms render only when the role has an `update` grant on the bound collection** — even pure-display forms; the render check ignores data scope. A view-only approver sees the pending task but an empty popup on click. Fix with a **render-enabler grant**: `update` with minimal fields + a narrow scope (e.g. status ∈ the stages that role approves). Required for *every* role whose users can be approval assignees — including roles whose users may be picked as custom/dynamic approvers.

## 5. Audit checklist (run periodically / before go-live)

1. `roles` list: for each role read `strategy.actions`, `snippets`, `default`, `allowConfigure`, `updatedAt`. Flag any non-admin role with `pm`/`ui.*` un-negated, and any strategy with `update`/`create`/`destroy` on it.
2. `systemSettings.roleMode` — if union, evaluate permissions as the union per user.
3. Per role: `roles.resources` with `actions` appended — check `usingActionsConfig` per row; for `true` rows, check field lists exclude workflow-managed columns; for `false` rows, know they are inert.
4. For every workflow-owned collection: attempt-list the columns a client could write (strategy roles → all). Confirm a guard or whitelist covers `status` and stamp fields.
5. Users: list with roles + departments; confirm no orphan users, no users holding `root`/`admin` unintentionally, test users documented.
6. Org data: approver fields populated for every department that a workflow routes through; no hardcoded assignee IDs in active workflow versions.
7. Booleans: check the raw `defaultValue` on every flag field and confirm it is a real JSON boolean or `null`, never the **string** `"false"` — a string is truthy, so a field that reads "default false" in the UI would create records already flagged true. Read it with `nb api data-modeling collections fields list --collection-name <c> -j` and look at the raw value, not the form. (Checked 2026-07-20 on `purchase_requests`: `is_regular`, `is_emergency`, `use_custom_approver` all store `null` — clean.)

## 6. Havenbeheer-specific state (updated 2026-07-02, retrofit drift report)

Resolved as of the 2026-06-11 role-hardening (details now in `decisions.md` D38, D40; historical detail also in git history of the retired `project_current_state.md`):
- New dept-bound `operations` role owns PR create/update (update scoped to own + editable statuses); procurement's PR `create`/`importXlsx` removed (D25 now enforced); procurement update whitelists exclude workflow-managed columns.
- `director` got the render-enabler grant (view 37 fields + update 3 fields — `rejection_comment`, `rejection_reason_category`, `signature` — scoped to `pending_director_approval` only). **Corrected 2026-07-02 (D55, then D57, then D58):** this update grant was live-unscoped (an oversight) and carried a stray, undocumented `create` action; both fixed. D55's first scope fix used the wrong (dead) scope table — D57 corrected it to the enforced table and runtime-verified the fix with a real test user, not just a readback. D58 then dropped `project`/`projectId` from the field list — no stated reason for director to reassign a PR's project, not needed for the approval form to render.
- `finance` role got the same render-enabler treatment once `fiona.finance` was created as an approver (D40) — update scoped to `pending_director_approval`/`pending_board_approval`, groundwork for a future finance/payment stage. No finance approval stage exists yet. **Corrected 2026-07-02 (D57):** the original scope (old id 10) lived in the dead scope table — never actually enforced since 2026-06-11, latent because no finance approval stage existed to expose it. Repointed to a new scope in the enforced table; old row deleted.
- Scopes 3, 6–9 (the broken snake_case ones) were deleted rather than fixed (D43).

**Corrections found during the 2026-07-02 retrofit drift report (see `decisions.md` D54):**
- **`systemSettings.roleMode` is now `only-use-union`**, not `allow-use-union` as originally recorded here — deliberate (D54), not a regression. Every user's effective permissions are the union of all their roles, unconditionally; there is no per-session single-role selection anymore. This makes §1's "a restriction on a derived role is meaningless if the base role already grants it" true **always**, not just under union mode.
- **`member`'s `ui.*` snippet is currently un-negated** (not vanilla) — deliberate development convenience (any test user can enter UI edit mode without switching to admin), **not** yet reverted. Because of the `only-use-union` setting above, this currently grants UI-edit access to every user in the app. Tracked in `notes.md` under "Before go-live" — must be re-negated before real end users get accounts.

Resolved since 2026-06-11 (superseding this section's original "still open" list): approver assignment is fully data-driven per D40 — Director/Board/Procurement/Operations approvals resolve from `departments.main_approver`, no hardcoded user ids. Verified live 2026-07-02: all 4 departments have `main_approver` set (Procurement→11, Director→12, Finance→14, Operations→10).
