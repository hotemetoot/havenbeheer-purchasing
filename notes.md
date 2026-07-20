# Notes

Non-queryable context: traps, reasons behind manual changes, and environment facts that `nb api` can't surface on its own. Queryable facts (current collections, fields, roles, workflow state) live only in the running app — query it, don't look here. Decisions with lasting rationale live in `decisions.md`.

Migrated 2026-07-02 from the retired `project_current_state.md` (see D-entries in `decisions.md` for anything decision-shaped — most of that file's content was already captured there).

---

## How to write for Alexander

See auto-memory `feedback_plain_language_concrete_examples` (the single home): plain language, every rule/test as a concrete story with a named person, explain unavoidable technical terms on first use. Non-negotiable in everything he reads.

## Drift / open issues

- **R42's bulk-import clause can never be automated — it is a permanent manual check.** R42 says the PO's Lines Total catches up "no matter how the line arrived — typed by hand, written by a workflow, or bulk-imported". The first two have runner cases; bulk-imported cannot, because import is a UI action `runner.py` has no way to drive. **The check:** import PO lines via the UI onto a draft PO, then confirm Lines Total equals the sum of the imported lines. Re-run it after any change to the recompute workflows (`1ugka88lngm` create/update, `pnvp0dtitum` delete) — it is the one path no test covers, and the exact scenario the async reload was built for (on import-created rows the trigger payload's PO link is empty). **Status lives in one place: go-live case B8** in [docs/go-live.md](docs/go-live.md) — don't record it here.

## Before go-live

Full go-live runbook (app readiness + VPS rebuild + migration + prod backups): [docs/go-live.md](docs/go-live.md).

- **DONE 2026-07-18 — full-app dead-scope audit** (the D57 re-run below): all 245 ACL action rows cross-checked against live parents and live scopes. PASS — every dangling-scope reference (ids 2/4/5/10/11) sits on an orphaned action row with no parent grant; legacy `rolesResources`/`rolesResourcesActions` tables are empty. Result recorded in docs/go-live.md §1.4.
- **`member` role's `ui.*` snippet is intentionally un-negated** (should be `!ui.*` per vanilla defaults in `role-acl-guidelines.md` §3). Alexander uses this deliberately during development so any test user can enter UI edit mode without switching to admin. Because `systemSettings.roleMode` is `only-use-union` (D54), this grants **every user in the app** UI-edit access right now, not just a convenience toggle. **Must be reverted (re-negated) before real end users get accounts.**
- **`fiona.finance` (user id 14) holds only the `member` role, not `finance`.** Found 2026-07-02 while investigating D57 — D40 (2026-06-11) says she was created specifically to get the finance render-enabler treatment, but the role assignment itself was apparently never done (or was later dropped). No current impact (no finance approval stage exists yet to expose it), but the `finance` role should be assigned to her before that stage gets built, or the render-enabler grant will look configured but do nothing for her specifically.
- **Payment control sits on `procurement`, not `finance`, as a deliberate interim (D59).** `procurement`'s PO `create`/`update` whitelists include `payment_status`/`payment_date`. D33a assigns payment to Finance, but there are no finance users yet, so procurement holds it. When finance users are created, move these set-rights to `finance`, drop them from procurement, and add the terminal-PO carve-out D33a describes. Procurement keeps *view* of payment regardless.
- **Receiving sits on `procurement`, not a warehouse role, as a deliberate interim (D59).** `procurement` updates `po_lines.received_quantity`. No warehouse role exists yet; if one is added, move receiving to it. Until then procurement records receiving.

## Test/demo user personas (NOT the automated suite's fixtures)

`alice.member`, `oliver.owner`, `pat.procurement`, `dana.director`, `simon.supervisor`, `fiona.finance` are long-lived, manually-created personas used for UI walkthroughs and demos — not the `nb-test` runner's ephemeral `test_<name>@test.local` fixtures. The test suite must not assume these users, touch their data, or clean them up; if suite fixtures are needed, seed separate `test_*` accounts.

**Correction 2026-07-02:** Alexander clarified these personas are themselves dev/test-only (nothing here is a real production identity — this is local dev, and go-live migration moves only settings/ACL/workflows, never data or these accounts). They're fine for the test suite to use directly, including changing their passwords to a shared value (`nbtest`) — the constraint above about "must not assume/touch/clean up" was more caution than necessary and can be relaxed.

**Done 2026-07-02 (fourth session):** `oliver.owner`/`pat.procurement`/`dana.director`/`fiona.finance`'s live passwords are now actually `nbtest` (verified via sign-in as all 4) — an earlier session's note that this was already done didn't hold up on re-check. See "Approval-chain test fixtures" below for the fully-verified mechanism.

## Approval-chain test fixtures — how the runner drives real approvals

A fixture that needs a PR or project at `status: approved` (or further) must be driven through the real approval workflow — status is not settable on create (no role's create whitelist includes it, and guards check the real record anyway).

- `runner.py`'s `fixtures.approvals` block drives a fixture record through real approval decisions once, up front, before any cases run — see `nb-project-suite`'s `plan.example.yaml` and `nb-test/SKILL.md` Pitfalls.
- `approvalRecords:submit` only accepts `status: 2` (approve) or `status: -1` (reject) — there is no `status: 1` for "return." Returning is a separate action, `approvalRecords:return` (no `status` field, just `comment`/`returnToNodeKey`). Director returns REQUIRE `returnToNodeKey` (the node has `returnTo: 1`; a plain return 400s).
- Plain `<collection>:create` does not enter an approval workflow at all — use the `trigger_workflow:` field on `fixtures.records` entries.
- Use the real personas above (`dana.director`=id 12, `pat.procurement`=id 11, `fiona.finance`=id 14, `oliver.owner`=id 10 — all set as the relevant `departments.main_approver`, see D40) as `fixtures.users` entries with `existing: true` and the shared `nbtest` password — the runner then signs in only, never touches their nickname/role. Don't create synthetic approver users: driving the real chain is the point, and `approvalRecords:submit`'s `validateSubmit` checks the record's actually-assigned `userId`.
- `find_pending_approval`'s `listMine` dot-path filter (`approval.collectionName`/`approval.dataKey`) works live — no client-side fallback needed.

The drafting history of the rules built on this mechanism (R12 through the PO/receiving rules) lives in `decisions.md` (D60–D62 onward) and git — not here.

## Environment

- Env name `havenbeheer`, `http://localhost:13000`. NocoBase runtime as of this retrofit: `2.1.0-beta.47` (was `2.1.0-beta.36` in the old state doc — keep current via `nb env list`, don't hardcode).
- **Canonical working tree: `~/nocobase-dev/havenbeheer`** (compose + `storage/`, containers `havenbeheer-app-1` / `havenbeheer-postgres-1`) — since the 2026-07-14 recovery (D76). **Never run a live Postgres data dir from an iCloud-synced folder** — that caused the June-25 DB revert. Only `.nbdata` logical backups may live in iCloud.
- Legacy locations (do not start containers from these): `~/nocobase` (stale June-25 copy, old `nocobase-*` containers stopped but kept ~2 weeks post-2026-07-14), iCloud `TTGA/nocobase` (the July source, kept untouched as insurance, deletable a few weeks after 2026-07-14). Snapshots: `~/nocobase-recovery/{july08-postgres,stale-june25-postgres}`.
- **After any tree recovery/relink, re-open `storage/` permissions for nginx or every storage-installed plugin bundle 403s.** The 2026-07-14 recovery left `~/nocobase-dev/havenbeheer/storage` (bind-mounted to `/app/nocobase/storage`) at mode `700`, owned by host uid 501. nginx inside `havenbeheer-app-1` runs as uid **999** and serves plugin client JS from `node_modules/@nocobase/plugin-*` symlinks that point into `storage/plugins/`. It couldn't traverse/read them → `403 Forbidden` on every storage-installed plugin's `dist/client/index.js` (built-in image plugins in `node_modules`, owned `root:root 644`, were unaffected). Symptom: app boots to "App error — Script error for @nocobase/plugin-…" (failing plugin name varies by load race), and any page using an affected plugin crashes — e.g. the **PR approval form** threw a `plugin-workflow-approval/index.js` React stack because its bundle 404-equiv'd. Discovered 2026-07-15. Fix applied (host side, other-class bits only, reversible): `chmod o+x storage` + `chmod -R o+rX storage/{uploads,plugins}` → dirs `705`, files `604`. Deliberately NOT applied to `db` (Postgres data), `backups`, `.license`, `logs` — those stay `700`. To reset: `chmod o-x storage; chmod -R o-rwx storage/{uploads,plugins}` (original other bits were all 0). No restart needed — nginx reads per request.

## Known traps (project-specific)

- **zsh word-splitting:** an unquoted shell variable holding multiple ids (e.g. `$ids`) does **not** word-split in this shell — use a `while read` (newline-delimited) loop when bulk-deleting/iterating ids via the CLI, not `for id in $ids`.
- **The mechanism traps this section used to spell out are cross-project, and their single home is `nb-bootstrap`'s `references/gotchas.md`** — read it there, not here. Deduplicated 2026-07-20 after the maintenance pass confirmed each one is in the catalogue in fuller form: nested-picker association creates silently dropping the FK when `id` is missing from the role's field whitelist; `fields: []` on an ACL row meaning *no* fields rather than all; `nb api` list queries defaulting to page-size 20 (which once produced a false "the field doesn't exist" finding, retracted in D69); workflow revisions (versioning, unfaithful copies, `--filter` key placement, post-enable sync); `templatePrint` not being workflow-triggerable; and v2 having no native table/sub-table summary footer. The *operating* rules built on top of these — "diff every revision copy", workflow-level fields included — live in this project's CLAUDE.md.
- **This project's answer to the missing footer row is `snippets/po-line-items-total.js`** — the canonical JS block for the PO line-items running total. RunJS isn't version-controlled, so that file is the source of truth for it.

## Stale IDs — removed 2026-07-20

A 40-line "DO NOT USE" list of superseded workflow versions, approval surfaces
and deleted keys lived here, frozen at 2026-06-28 and never re-verified since.
It was deleted in the maintenance pass because CLAUDE.md already rules: **never
act on an ID that wasn't just read from the live env.** That covers every id, so
naming particular forbidden ones added nothing and risked misleading — a live id
could in principle collide with the list. Query the app instead:
`nb api workflow workflows list --filter '{"current":true}'`, then check `enabled`.
Git history has the old list if it is ever wanted.
