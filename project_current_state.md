# Current Build State

**Last verified:** 2026-05-26 (live env queried via `nb api` — collections, workflows, approval surfaces; MVP9a fix-up pass completed).

MVPs 1–8 built. MVP7 was reduced to suppliers-only (D26). MVP8 added comments collection + 4 soft fields + UI surfaces; the comments UI block in the PR detail popup was removed by the user post-verification (data layer remains — can be re-added). **MVP9a built 2026-05-26**: PO + po_lines + lookups, Generate-PO workflow (`2izsx8uv50r` v `366595041853440`), Create-PO Guard (`vgv8hcrtjvx`), Generate-PO button on PR surfaces with procurement-only visibility. PR↔PO relation re-shaped to clean m2o + virtual hasOne. Next: **MVP9b — sending the PO + budget zones**.

This file is the **single source of truth** for the live NocoBase environment state. Update it at the end of every session that creates or modifies collections, fields, workflows, or UI surfaces. Commit changes alongside the build commits they describe.

---

## CLI environment

- **Env name:** `havenbeheer`
- **URL:** http://localhost:13000
- **NocoBase version:** 2.1.0-beta.36
- **CLI version:** 2.1.0-beta.33 (newer available — run `nb self update --yes`)
- **Auth:** OAuth token (valid, auto-refreshes)

---

## Collections

### `purchase_requests`

| Field | Interface | Notes |
|---|---|---|
| title | input | |
| description | textarea | |
| justification | vditor | rich text |
| submitter | m2o → users | |
| department | m2o → departments | |
| status | select | see values below |
| rejection_reason_category | select | |
| rejection_comment | textarea | |
| cancellation_reason | textarea | MVP2 — cancel popup only |
| cancelled_at | datetime | MVP2 — set by cancel workflow |
| quoted_total | number | MVP3 — entered by submitter or procurement |
| quoted_currency | radioGroup (USD/SRD/EUR) | MVP3 |
| fx_rate_to_usd | number | MVP3 — **entered manually** by submitter or procurement |
| quoted_total_usd | formula | MVP3 — formula.js: `{{quoted_total}} / {{fx_rate_to_usd}}`, auto-computes, read-only. **Division**: `fx_rate_to_usd` is local-per-USD (e.g. 35 SRD per 1 USD). |
| quotation_attachment | attachment (multi) | MVP3 |
| needs_director_approval | checkbox (boolean) | MVP4 — default false; set by submitter; triggers director path |
| approved_at | datetime | MVP4 — written on final approval (both paths) |
| supplier | m2o → suppliers | MVP7 — optional "Suggested supplier" |
| expenditure_type | select (capex/opex/maintenance/consumables) | MVP8 |
| is_emergency | checkbox (boolean) | MVP8 — UI flag only, no routing impact |
| needed_by | dateOnly | MVP8 |
| other_attachments | attachment (multi) | MVP8 — distinct from `quotation_attachment` |
| comments | o2m → pr_comments | MVP8 — comment thread relation; UI block removed post-verify (data layer kept) |
| purchase_order | oho (hasOne) → purchase_orders | MVP9a — virtual inverse of `purchase_orders.purchase_request`. No FK column on PR side. |

**`status` values:** `draft`, `pending_dept_approval`, `pending_purchasing_review`, `pending_director_approval`, `info_requested`, `approved`, `rejected`, `cancelled`

### `departments`

| Field | Notes |
|---|---|
| main_approver (m2o → users) | primary approval assignee |
| secondary_approver (m2o → users) | backup when main_approver is on leave |

| Department | ID | main_approver | secondary_approver |
|---|---|---|---|
| Procurement | 363554444476416 | Pat (user 11) | — |
| Director | 363554454962176 | — | — |
| Finance | 363554454962177 | — | — |
| Operations | 363554454962178 | Oliver (user 10) | — |

### `users` — extra fields
- `on_leave` (boolean, default false) — workflow uses this for fallback routing

### `suppliers` (MVP7 — built 2026-05-24)

Collection key `a4ogom91smz`. Fields:

| Field | Interface | Notes |
|---|---|---|
| name | input | required, title field |
| display_name | input | |
| tax_id | input | |
| email | email | |
| phone | input | |
| address | textarea | |
| country | select | |
| default_currency | select (USD/SRD/EUR) | |
| payment_terms | select (Net30/Net60/Net90/COD/Prepayment) | per D17 |
| status | select (active/inactive/blocked) | default `active` |
| current_rating | number (1–5) | manual per D6 |
| notes | textarea | |

### Collections NOT built (postponed — D26)
- `supplier_issues` — postponed from MVP7
- `supplier_evaluations` — postponed from MVP7

### `pr_comments` (MVP8 — built 2026-05-26)

Comment-template collection (`@nocobase/plugin-comments`). Baseline fields only: `id`, `content` (vditor, long text, not deletable), `createdAt`, `createdBy`, `updatedAt`, `updatedBy`. Linked to `purchase_requests` via the `purchase_requests.comments` o2m relation.

### `purchase_orders` (MVP9a — built 2026-05-26)

Header collection for purchase orders. Created via Generate-PO workflow from approved PRs (one PR → one PO per D9).

Key fields: `po_number` (sequence `PO-YYYY-NNNN`), `purchase_request` (m2o → purchase_requests, FK `purchaseRequestId`), `supplier` (m2o), `delivery_address` (m2o), `status` (default `draft`), `currency`, `fx_rate_to_usd`, `total` (workflow-maintained, no formula), `total_usd` (formula.js: `{{total}} / {{fx_rate_to_usd}}` — division, local-per-USD), `payment_status`, `payment_date`, `expected_delivery_date`, `invoice` (attachment), `attachments` (attachment multi), `supplier_note`, `internal_notes`, `budget_override_comment`, `close_reason`, `close_comment`, audit timestamps (`sent_at`, `confirmed_at`, `completed_at`, `closed_at`, `cancelled_at` — populated by later MVPs).

### `po_lines` (MVP9a — built 2026-05-26)

Line items for purchase orders — **pricing was descoped 2026-05-26 (D27)**. Lines now track quantity + receiving only; financial values stay at PO level (manually entered from supplier invoice). Fields: `purchase_order` (m2o), `product` (m2o optional), `description` (textarea, required), `unit_of_measure` (m2o), `quantity_ordered`, `received_quantity`, `line_status` (default `pending`). Previously had `unit_price`, `line_total` (formula), `line_total_usd` (formula); all three deleted. The planned 9a.4 Total-maintenance workflow is **cancelled** — PO `total` is no longer derived from lines.

### `delivery_addresses`, `units_of_measure`, `products` (MVP9a — built 2026-05-26)

Lookup collections. `delivery_addresses` has `name` (title), `address`, `is_default`, `status`. `units_of_measure` has `name` (title, **unique**), `abbreviation`, `status`. `products` (v1 stub) has `name` (title, **unique**), `description`, `default_uom` (m2o → units_of_measure), `status`.

### Deleted collections
- `fx_rates` — deleted 2026-05-24 (MVP3 simplification under D22)

---

## Active workflows

### PR Approval workflow
- **Key:** `cv237r8h7k9`
- **Active version ID:** `366549533655040` (enabled=true, current=true) — built MVP8 (revision of 366234405109760, with user follow-up edits creating this final version). All prior versions of this key are disabled — see "Stale IDs".
- **Type:** approval, collection `purchase_requests`
- **Trigger appends:** `createdBy`, `createdBy.mainDepartment`, `createdBy.mainDepartment.main_approver`, `createdBy.mainDepartment.secondary_approver`
- **Trigger approvalUid:** `1yw73plyqsf`; **taskCardUid:** `e6edajqk51d`
- **Nodes** (active version `366549533655040`; same 18-node structure as prior, node keys preserved across revisions):
  - Root update `1f6a1h52l9u` — sets status=pending_dept_approval
  - Query `yrl9kgkrb3x` (qProc) — fetches Procurement dept with `main_approver` appended
  - Condition `5hed96jh1u7` — submitter IS dept main_approver → skip dept
    - br=1 (true): Update `nkbguc8uo7z` → status=pending_purchasing_review
    - br=0 (false): Approval#1 `cfg687cye3n` Dept Owner Approval
      - br=2 (approve): Update `xqlzgk0326f` → status=pending_purchasing_review
      - br=1 (return): Update `bm50djboga3` → status=info_requested
      - br=-1 (reject): Update `1b06nufq3bi` → status=rejected
  - Approval#2 `ec2h8cqal32` Procurement Approval
    - br=2 (approve): Condition `bizoy1sj87j` — `needs_director_approval == true?`
      - br=1 (true): Update `eg86l2ilhmk` → status=pending_director_approval → Approval#3 `sxvxwl498xg`
      - br=0 (false): Update `jy1365pvsce` → status=approved, approved_at=now
    - br=1 (return): Update `pket0lgmjyk` → status=info_requested
    - br=-1 (reject): Update `01vfxfgw6s3` → status=rejected
  - Approval#3 `sxvxwl498xg` Director Approval → hardcoded [12] (Dana) — nested in condition br=1
    - br=2 (approve): Update `kj1zcmujub8` → status=approved, approved_at=now
    - br=1 (return): Update `z1x6ghkmr2t` → status=info_requested
    - br=-1 (reject): Update `t2odlgyqdra` → status=rejected
- **Approval surfaces (version 366549533655040):**
  - Dept approver (`cfg687cye3n`): approvalUid `0qljvpsiceo`, taskCardUid `pdbm4aixrc9`
  - Procurement (`ec2h8cqal32`): approvalUid `z01rza37pod`, taskCardUid `bvlz1vbvi7t` — procurement ProcessForm detached from shared template `k60b738pjy0` during MVP8 to scope field additions; now local to this revision lineage.
  - Director (`sxvxwl498xg`): approvalUid `6x42w7n9h4g`, taskCardUid `aahsde3cnie`

The four MVP8 fields (`expenditure_type`, `is_emergency`, `needed_by`, `other_attachments`) are present on all three approval forms: editable on dept, read-only (`pattern: readPretty`) on procurement and director.

**Note:** Filter by key `cv237r8h7k9` + enabled=true to get current version.

### Cancel Purchase Request workflow
- **Key:** `59ezifdoqvj`
- **Active version ID:** `364980262862848` (enabled=true)
- **Type:** custom-action, sync=true, collection=purchase_requests, appends=["submitter"]
- **Guard C (embedded):** condition node `kj9d7bnvw02` — AND: user.id==submitter.id AND status=="draft", rejectOnFalse=false
- **Update node:** `5pl72u5ktdm` (branch=1) — sets status=cancelled, cancelled_at={{$system.now}}, cancellation_reason from form

### Cancel PR Guard (request-interception)
- **Key:** `8yngslauuj4`
- **Active version ID:** `364984924831744` (enabled=true)
- **Type:** request-interception — server-side guard on cancel attempts

### Guard A — PR immutability (MVP5)
- **Key:** `496ookqmg01`
- **Active version ID:** `366217145548800` (enabled=true)
- **Type:** request-interception, global, sync; actions: update + destroy on `purchase_requests`
- **Node chain:** Query (`q33wtlxitr1`) → Condition OR status∈{approved,rejected,cancelled} (`nbs3zmsr60x`) → branch 1: response-message + end(endStatus:-1)
- **Known limitation (D24):** does NOT intercept bulk update. See [decisions.md](decisions.md).

### Generate PO workflow (MVP9a)
- **Key:** `2izsx8uv50r`
- **Active version ID:** `366623590383616` (enabled=true) — user-revisioned 2026-05-27 to add a `response-message` + `end-process(-1)` pair on the inline guard's false branch, per [`feedback_inline_guard_end_node`](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_inline_guard_end_node.md). Earlier round-3 (`366608098721792`) had the guard but no end-process node, which left the UI without a clear rejection signal.
- **Type:** custom-action, sync, collection `purchase_requests`; appends `[supplier, purchase_order]`.
- **Node chain:** Guard condition (`uufqoeb8xyz`, AND of `status==approved` + `purchase_order==null`):
  - branch 1 (true) → Query default delivery address (`ay8dlnys4ef`) → Create purchase_orders (`ubg9mju1tjm`, sets `createdById={{$context.user.id}}`) → Create po_lines default line (`4p3q7oq3co5`, writes only `purchase_order`/`description`/`quantity_ordered=1`)
  - branch 0 (false) → Response message (`ylrivonemrq`) → End process (`gviz4zia0ha`, endStatus: -1)
- **Bound to button:** `28jh1q2camo` (Generate PO button, visible on PR table block `l1e2iwdwau9` and PR detail popup `2b367dbd157`).

### Create-PO Guard (MVP9a)
- **Key:** `vgv8hcrtjvx`
- **Active version ID:** `366562380808192` (enabled=true)
- **Type:** request-interception, global, sync; actions: `create` on `purchase_orders`
- **Node chain:** Query referenced PR (`ww4mxz67ge8`, appends `purchase_order`) → Condition OR pr.status≠approved | pr.purchase_order≠null (`dba34lyg168`) → branch 1: response-message (`7fp12f2018u`) + end (`j57v75y2cky`, endStatus:-1).

---

## Test users

| Username | ID | Main dept |
|---|---|---|
| alice.member | 9 | Operations (363554454962178) |
| oliver.owner | 10 | Operations (363554454962178) |
| pat.procurement | 11 | Procurement (363554444476416) |
| dana.director | 12 | Director (363554454962176) |

---

## UI

- **Purchase Requests page UID:** `cuycec133qb`
- **Table block:** `l1e2iwdwau9` — columns include title, status, quoted_total, quoted_currency, `expenditure_type`, `is_emergency`, `needed_by` (MVP8)
- **PR view popup** (DetailsBlockModel `2b367dbd157`): shows all PR fields incl. quote fields, `needs_director_approval`, `supplier`, and the four MVP8 fields. The popup grid `5fb7b74fa30` contained an MVP8 Comments block `52t8wtbzni4` bound to `purchase_requests.comments`; the user removed it post-verification. Re-add via `nb api flow-surfaces add-block` with type `comments` and resource `{binding:"associatedRecords", associationField:"comments"}` targeting the grid.
- **Procurement approval form** (now per-revision, detached from template `k60b738pjy0`): current ProcessFormModel uid varies per workflow revision. MVP8 read-only fields applied.
- **PR create form** (CreateFormModel `e76c40c8c79`, template `n9f8v5vnhhc`): includes `needs_director_approval` checkbox after justification; linkage rule makes justification required when checkbox is checked. MVP8 added `expenditure_type`, `needed_by`, `is_emergency`, `other_attachments` after `needs_director_approval`.
- **Generate PO button** (`28jh1q2camo`, MVP9a): `RecordTriggerWorkflowActionModel` on PR table row popup and PR detail popup. Bound to workflow key `2izsx8uv50r`. Two linkage rules:
  - Hide when `record.status != "approved"` OR `record.purchase_order is not empty`.
  - Hide when `ctx.user.roles.title` does not include `"Procurement"` (procurement-only visibility; see [feedback_linkage_rules_user_roles](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_linkage_rules_user_roles.md) in auto-memory for the pattern).

Approval form surface IDs on the active version: see "Approval surfaces" above.

---

## Stale IDs (DO NOT USE)

### Workflow versions of `cv237r8h7k9` (all disabled before `366549533655040`):
- `366523411529728` (MVP8 intermediate revision, superseded by user's follow-up edits → `366549533655040`)
- `366523398946816` (MVP8 duplicate revision created accidentally, never enabled — destroying it needs explicit user OK per CLAUDE.md irreversible-action rule)
- `366234405109760` (was active up to MVP8, replaced 2026-05-26)
- `366232953880576`
- `366207890817024`
- `366087730298880`
- `366086440550400`
- `366059727028224`
- `366057076228096`
- `366053490098176`
- `365711034417152`
- `365001941123072`

### Approval surfaces from disabled workflow versions:
- From version `366234405109760` (prior active): trigger approvalUid `no4q0qifkv2` / taskCardUid `fc8790fw6pd`; dept `0x4yjm74y0o` / `jmy6o8nkdld`; procurement `zbvpqgod2bs` / `39ynx9u1zlh`; director `nnzr393hos1` / `wet1jqjv8t2`.
- From version `366523411529728` (MVP8 intermediate): trigger approvalUid `svezxiek2gk` / taskCardUid `ndpn7l9cnif`; dept `wankth4i85p` / `iwqxqf5j5p6`; procurement `4qbsr41frsw` / `jwwayk35jmg`; director `mcmyxnng8q7` / `pa83sj9uoke`.
- From version `366232953880576`: approvalUids `2zmok19gb2c`, `7xwj8l0sjqp`, `knwxauc0yoz`, `lav2su037qi`; taskCardUids `exgm0gh0mru`, `5l5vdolh5su`, `ivg75pqfe6b`, `arpce782zod`.
- Older disabled-version surfaces: `5sewfvayoc4`, `ylccjkdatwa`, `wa1guuahjjo`, `4ceoua2g0ij`, `klak6hh6vu0`, `qswcu5p6ihj`, `42ay2w0j69v`, `apz6gdy0z6z`, `n7n6x0xg3t0`, `wdty2zx7de7`, `8yyu6ofo1ww`, `rgcyt60s8pg`, `yyptfj0azru`, `o4jc2ghrs4q`, `8x5ktd74gwx`, `o1n99mp7sn7`

### Stale workflow keys:
- `p4n6dffjcgq` / version `364960795000832` — does not exist
- `p1tnx6nb5r9` / version `364995697901568` — disabled rebuild from between sessions
- `idezsq1k1ts` / `363982109736960` — original v3-plan MVP1 key, superseded
- `1r4vyfbnie8` — hardcoded on the Generate-PO button before workflow build; no workflow with this key ever existed.

### Stale Generate-PO (`2izsx8uv50r`) versions:
- `366569458696192` — initial build with JSON-filter embedded guard.
- `366595041853440` — round-2 revision that wrongly removed the inline guard.
- `366602797121536` — interim revision.
- `366608098721792` — round-3 revision: restored guard but missed the end-process node on the false branch.
- `366623370182656` — interim user revision.
- All superseded 2026-05-27 by `366623590383616` (current).

### Disabled po_lines collection workflows (cancelled per D27):
- `jsgbxph9444` ("PO Total: Lines Added/Updated", id `366562246590464`) — was a sync collection trigger on po_lines create/update that aggregated `line_total`. Disabled 2026-05-27 because the field no longer exists; the sync failure was silently rolling back po_line creates from the Generate-PO workflow. Keep disabled.
- `s4syz7vom4n` ("PO Total: Line Deleted", id `366562257076224`) — sibling delete trigger for the same total-maintenance scheme. Also disabled.

---

## Notes for the next session

- **MVP7 was descoped.** Only `suppliers` was built; `supplier_issues` and `supplier_evaluations` are postponed (D26). Don't assume they exist.
- **Supplier UI:** if a suppliers list/detail page was built during MVP7, its page UID isn't recorded here yet — capture it the next time it's touched.
- **MVP8 ACL note:** Field-level edit gating for procurement/director on PR content stays enforced via form-pattern (`readPretty`) only, not strict ACL. Procurement+director roles still technically have those fields in their `update` whitelist via strategy-based ACL (`usingActionsConfig=false`). Tightening to independent permissions is a future hardening MVP. The four MVP8 fields inherit this same posture.
