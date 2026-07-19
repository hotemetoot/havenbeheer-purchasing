# Notes

Non-queryable context: traps, reasons behind manual changes, and environment facts that `nb api` can't surface on its own. Queryable facts (current collections, fields, roles, workflow state) live only in the running app — query it, don't look here. Decisions with lasting rationale live in `decisions.md`.

Migrated 2026-07-02 from the retired `project_current_state.md` (see D-entries in `decisions.md` for anything decision-shaped — most of that file's content was already captured there).

---

## How to write for Alexander

See auto-memory `feedback_plain_language_concrete_examples` (the single home): plain language, every rule/test as a concrete story with a named person, explain unavoidable technical terms on first use. Non-negotiable in everything he reads.

## Drift / open issues

- **OPEN — manual check owed: R42's bulk-import claim has no automated case (2026-07-18, D84).** R42 says the PO's Lines Total catches up "no matter how the line arrived — typed by hand, written by a workflow, or bulk-imported". The first two are covered by runner cases; **bulk-imported is not**, because import is a UI action `runner.py` cannot drive. That clause currently rests on D83's one-off manual verification. It is the exact scenario the async reload was built for (on import-created rows the trigger payload's PO link is empty), so it is the clause most worth re-checking and the one least likely to be noticed if it breaks. **To check:** import PO lines via the UI onto a draft PO, then confirm the PO's Lines Total equals the sum of the imported lines' totals. Belongs with D83's parked 016 B-cases — do both in one pass.

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
- **Nested-picker association creates silently drop the FK unless the picker's field is in the target role's field whitelist.** NocoBase's `checkChangesWithAssociation` middleware prunes a nested object (e.g. `{project: {id: 7}}`) down to the acting role's whitelist for that collection; if `id` isn't in the whitelist, the id is stripped and the nested object is treated as a brand-new record to create — silently produces a **draft duplicate** instead of linking to the intended record. Always include `id` in create **and** update whitelists for any collection that's ever set via a nested picker. A CLI `resource create --role <x>` run as the root token does **not** reproduce this (root bypasses the association middleware) — only a real non-root user session hits it. See auto-memory `feedback_acl_nested_association_id_whitelist`.
- **`fields: []` on an ACL resource-permission row means NO fields, not all fields.** Always resolve and write the full field list explicitly.
- **`nb api` list/field queries default to page-size 20 — pass `--page-size 100` before concluding anything is missing.** `data-modeling collections fields list` on `purchase_orders` (30 fields) returned only 20 without `--page-size`, and `completed_at`/`closed_at` were on the cut-off page. Led to a false "the field doesn't exist" finding (retracted in D69). Same risk on any `resource list` / `workflows list` used to prove absence.
- **Workflow revisions** (versioning, unfaithful copies, the `--filter` key placement, post-enable sync): cross-project traps, single home `nb-bootstrap`'s `references/gotchas.md` §Workflows. The operating rules ("diff every revision copy", workflow-level fields included) are in this project's CLAUDE.md.
- **`templatePrint` (Carbone PDF print) cannot be workflow-triggered** — post-action events fire only on create/update, and global request-interception is CRUD-only. A status-advancing custom-action button is the only way to gate "must be complete before printable." It also streams the PDF to the browser only (no save-to-record/attach) — there's no automatic "attach the PDF to the record" path.
- **No native table summary/footer row in NocoBase v2** — a running total at the bottom of a sub-table (e.g. PO line items) needs a JS block reading the association's `MultiRecordResource`, wired to refresh on the relevant forms' Submit. See `snippets/po-line-items-total.js` for the canonical pattern here.

## Stale IDs (DO NOT USE) — carried over verbatim from `project_current_state.md`, frozen at 2026-06-28

This list was accurate as of the old state doc's last edit. It has **not** been re-verified against the live app during this retrofit and workflow revisions have continued since (see `decisions.md` D53 onward) — treat every id below as "known-stale as of 2026-06-28," not as a complete current list. For the live active version of any workflow, query `nb api workflow workflows:list --filter '{"current":true}'` and check `enabled`.

### Workflow versions of `cv237r8h7k9` (PR Approval) — all disabled before whatever is currently active:
`369536223739904`(*), `369495666917376`, `369166026080256`, `369161752084480`, `369154168193024`, `369076269481984`, `368983543906304`, `368641179582464`, `367885604880384`, `367158084370432`, `367150157135872`, `366549533655040`, `366523411529728`, `366523398946816`, `366234405109760`, `366232953880576`, `366207890817024`, `366087730298880`, `366086440550400`, `366059727028224`, `366057076228096`, `366053490098176`, `365711034417152`, `365001941123072`.
(*`369536223739904` was itself the active version as of 2026-06-13 doc-lag correction — by 2026-06-28 it too is superseded; see decisions.md D48 onward for the chain.)

### Approval surfaces from disabled workflow versions (all stale, kept only in case an old deep-link surfaces):
`no4q0qifkv2`/`fc8790fw6pd`, `0x4yjm74y0o`/`jmy6o8nkdld`, `zbvpqgod2bs`/`39ynx9u1zlh`, `nnzr393hos1`/`wet1jqjv8t2`, `svezxiek2gk`/`ndpn7l9cnif`, `wankth4i85p`/`iwqxqf5j5p6`, `4qbsr41frsw`/`jwwayk35jmg`, `mcmyxnng8q7`/`pa83sj9uoke`, `2zmok19gb2c`, `7xwj8l0sjqp`, `knwxauc0yoz`, `lav2su037qi`, `exgm0gh0mru`, `5l5vdolh5su`, `ivg75pqfe6b`, `arpce782zod`, and older: `5sewfvayoc4`, `ylccjkdatwa`, `wa1guuahjjo`, `4ceoua2g0ij`, `klak6hh6vu0`, `qswcu5p6ihj`, `42ay2w0j69v`, `apz6gdy0z6z`, `n7n6x0xg3t0`, `wdty2zx7de7`, `8yyu6ofo1ww`, `rgcyt60s8pg`, `yyptfj0azru`, `o4jc2ghrs4q`, `8x5ktd74gwx`, `o1n99mp7sn7`.

### Stale/nonexistent workflow keys:
- `p4n6dffjcgq` / `364960795000832` — does not exist.
- `p1tnx6nb5r9` / `364995697901568` — disabled rebuild from between sessions.
- `idezsq1k1ts` / `363982109736960` — original v3-plan MVP1 key, superseded.
- `1r4vyfbnie8` — hardcoded on the Generate-PO button before the workflow was built; no workflow with this key ever existed.

### Stale Generate-PO (`2izsx8uv50r`) versions, pre-2026-06-28:
`367255610327040`, `366569458696192`, `366595041853440`, `366602797121536`, `366608098721792`, `366623370182656`, `366623590383616`, `366626266349568`, `366626572533760`.

### Stale Send-PO (`send_po`) versions — note the whole key is now retired (D46), not just individual revisions:
`366981771362304`, `366776493735936`, `366882024521728`, `366883251355648`, `366883769352192`, `366980364173312`. (`366980536139776`/key `s6m4i5hrmzs` "Send PO copy" was deleted 2026-06-11.)

### Stale Complete-PO (`qh7b3hc5q1r`) version:
`368746204954624` (superseded 2026-06-09 by the D34 invoice-gate revision).

### Deleted workflows (gone, not just disabled):
`jsgbxph9444` ("PO Total: Lines Added/Updated"), `s4syz7vom4n` ("PO Total: Line Deleted") — cancelled per D27, deleted 2026-06-11. `59ezifdoqvj` + `8yngslauuj4` (Cancel PR workflow, both keys, all versions) — retired per D42, deleted 2026-06-12.
