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
- **Prefer narrow independent grants over widening the strategy.** Example done right: procurement gets `create` on `attachments` only (approvers must upload files) instead of a global `create` that would let the role create PRs.
- **Policy decisions must map to enforced config.** If a decision says "role X cannot do Y" (Havenbeheer D25: procurement doesn't create PRs), verify the *union* of that user's roles actually denies Y — or record the decision explicitly as unenforced policy.

## 3. Snippets (configuration permissions)

- **Vanilla defaults:** admin `["pm", "pm.*", "ui.*"]`; member `["!ui.*", "!pm", "!pm.*"]`; derived business roles should negate all three.
- **`ui.*` un-negated on a non-admin role means those users can enter UI edit mode.** This shows up as a leftover debugging workaround (e.g. trying to fix approval-form `flowModels:save` 403s — the correct fix is pre-creating comment models, see auto-memory `feedback_approval_blueprint_comment_models`). Audit snippets on every role after any troubleshooting session.
- A role's `updatedAt` is a useful tell: a base role modified on a build/debug day deserves a diff against the vanilla defaults.

## 4. Approver assignment

- **Drive approver assignment from data, not hardcoded user IDs.** Put `main_approver` / `secondary_approver` (m2o → users) on the org collection (`departments`) and reference them in workflow assignees via variables (`{{$context.data.<assoc>.id}}` — requires the association in trigger appends). A hardcoded `[12]` in a workflow node means a personnel change requires a workflow revision instead of a record edit.
- **Don't model behavior you haven't built.** Fields like `secondary_approver` and `users.on_leave` that no workflow reads are a false promise — either wire the fallback or drop the fields.
- **Block self-approval server-side** (workflow condition comparing approver to `createdById`), not only via picker data scope — the scope is UX, the condition is the control.

## 5. Audit checklist (run periodically / before go-live)

1. `roles` list: for each role read `strategy.actions`, `snippets`, `default`, `allowConfigure`, `updatedAt`. Flag any non-admin role with `pm`/`ui.*` un-negated, and any strategy with `update`/`create`/`destroy` on it.
2. `systemSettings.roleMode` — if union, evaluate permissions as the union per user.
3. Per role: `roles.resources` with `actions` appended — check `usingActionsConfig` per row; for `true` rows, check field lists exclude workflow-managed columns; for `false` rows, know they are inert.
4. For every workflow-owned collection: attempt-list the columns a client could write (strategy roles → all). Confirm a guard or whitelist covers `status` and stamp fields.
5. Users: list with roles + departments; confirm no orphan users, no users holding `root`/`admin` unintentionally, test users documented.
6. Org data: approver fields populated for every department that a workflow routes through; no hardcoded assignee IDs in active workflow versions.
7. Booleans: check raw `defaultValue` types on flag fields (the CLI string-`"false"` coercion bug stores truthy defaults — see `feedback_fields_apply_boolean_default`).

## 6. Havenbeheer-specific state (as of 2026-06-11 audit — for follow-up)

- `member` snippets are `["!app", "!pm", "!pm.*", "ui.*"]` → **revert to `["!ui.*", "!pm", "!pm.*"]`** after confirming the approval flow still works (the `ui.*` grant was likely a 403 workaround).
- `member` strategy `view/update/create` + `usingActionsConfig: false` on `purchase_requests` → **`status`/`approved_at` are API-writable by any user** (self-approval bypass). Hardening MVP pending.
- `procurement` has independent `create` on `purchase_requests` (39 fields) → contradicts D25; remove or re-scope D25.
- `finance` role: `null` strategy, no users — intentional placeholder until the payment MVP.
- Director approval hardcodes user 12, Board hardcodes user 11; Director/Finance departments have `main_approver = NULL`; `secondary_approver`/`on_leave` fallback never built.
