# Notes

Non-queryable context: traps, reasons behind manual changes, and environment facts that `nb api` can't surface on its own. Queryable facts (current collections, fields, roles, workflow state) live only in the running app — query it, don't look here. Decisions with lasting rationale live in `decisions.md`.

Migrated 2026-07-02 from the retired `project_current_state.md` (see D-entries in `decisions.md` for anything decision-shaped — most of that file's content was already captured there).

---

## Before go-live

- **`member` role's `ui.*` snippet is intentionally un-negated** (should be `!ui.*` per vanilla defaults in `role-acl-guidelines.md` §3). Alexander uses this deliberately during development so any test user can enter UI edit mode without switching to admin. Because `systemSettings.roleMode` is `only-use-union` (D54), this grants **every user in the app** UI-edit access right now, not just a convenience toggle. **Must be reverted (re-negated) before real end users get accounts.**

## Test/demo user personas (NOT the automated suite's fixtures)

`alice.member`, `oliver.owner`, `pat.procurement`, `dana.director`, `simon.supervisor`, `fiona.finance` are long-lived, manually-created personas used for UI walkthroughs and demos — not the `nocobase-test` runner's ephemeral `test_<name>@test.local` fixtures. The test suite must not assume these users, touch their data, or clean them up; if suite fixtures are needed, seed separate `test_*` accounts.

## Environment

- Env name `havenbeheer`, `http://localhost:13000`. NocoBase runtime as of this retrofit: `2.1.0-beta.47` (was `2.1.0-beta.36` in the old state doc — keep current via `nb env list`, don't hardcode).

## Known traps (project-specific)

- **zsh word-splitting:** an unquoted shell variable holding multiple ids (e.g. `$ids`) does **not** word-split in this shell — use a `while read` (newline-delimited) loop when bulk-deleting/iterating ids via the CLI, not `for id in $ids`.
- **Nested-picker association creates silently drop the FK unless the picker's field is in the target role's field whitelist.** NocoBase's `checkChangesWithAssociation` middleware prunes a nested object (e.g. `{project: {id: 7}}`) down to the acting role's whitelist for that collection; if `id` isn't in the whitelist, the id is stripped and the nested object is treated as a brand-new record to create — silently produces a **draft duplicate** instead of linking to the intended record. Always include `id` in create **and** update whitelists for any collection that's ever set via a nested picker. A CLI `resource create --role <x>` run as the root token does **not** reproduce this (root bypasses the association middleware) — only a real non-root user session hits it. See auto-memory `feedback_acl_nested_association_id_whitelist`.
- **`fields: []` on an ACL resource-permission row means NO fields, not all fields.** Always resolve and write the full field list explicitly.
- **Workflow revisions:** once a workflow has executed, it can't be edited in place — node edits 400 with "Nodes in executed workflow could not be reconfigured." Create a new same-key revision, edit while disabled, enable, disable the predecessor.
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
