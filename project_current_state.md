# Current Build State

**Last verified:** 2026-05-30 (live env queried via `nb api` — director-approval $300 floor activated; MVP9b Send-PO + Close-PO workflows and budget zones; MVP010 skip-dept-approval).

MVPs 1–8 built. MVP7 was reduced to suppliers-only (D26). MVP8 added comments collection + 4 soft fields + UI surfaces; the comments UI block in the PR detail popup was removed by the user post-verification (data layer remains — can be re-added). **MVP9a built 2026-05-26**: PO + po_lines + lookups, Generate-PO workflow (`2izsx8uv50r` v `366595041853440`), Create-PO Guard (`vgv8hcrtjvx`), Generate-PO button on PR surfaces with procurement-only visibility. PR↔PO relation re-shaped to clean m2o + virtual hasOne. **MVP9b built 2026-05-29**: PO `draft → sent` with budget-zone guard (Send PO workflow `send_po`), PO `draft → closed` (Close PO workflow `close_po_draft`), Send + Close buttons on PO surfaces. `cancelled` collapsed into `closed` (D28). Zone-2 in-app notifications (9b.3) deferred — gated on Finance dept `main_approver` being set (still NULL). **MVP010 built + verified 2026-05-29:** optional submitter `skip_dept_approval` (D29) — field + UI toggle live; PR Approval workflow revision `367150157135872` (key `cv237r8h7k9`) activated and end-to-end verified by user. When skipped, dept head gets an in-app FYI notification and the PR routes straight to Procurement. **D30 built + verified 2026-05-30:** mandatory director approval at **`quoted_total_usd >= 300`** — PR Approval revisioned to `367158084370432` (key `cv237r8h7k9`); the director-decision condition `bizoy1sj87j` is now an OR of the manual `needs_director_approval` checkbox and the $300 USD floor. Next: **MVP9c — receiving**.

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
| skip_dept_approval | checkbox (boolean) | MVP010 — default false; submitter opts to skip dept-head approval (D29). On the create form + read-only on detail popup. Honored by active PR Approval workflow `367158084370432` (FYI-notifies dept head). |

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

Key fields: `po_number` (sequence `PO-YYYY-NNNN`), `purchase_request` (m2o → purchase_requests, FK `purchaseRequestId`), `supplier` (m2o), `delivery_address` (m2o), `status` (default `draft`), `currency`, `fx_rate_to_usd`, `total` (workflow-maintained, no formula), `total_usd` (formula.js: `{{total}} / {{fx_rate_to_usd}}` — division, local-per-USD), `payment_status`, `payment_date`, `expected_delivery_date`, `invoice` (attachment), `attachments` (attachment multi), `supplier_note`, `internal_notes`, `budget_override_comment`, `close_reason`, `close_comment`, audit timestamps (`sent_at`, `confirmed_at`, `completed_at`, `closed_at`).

**`status` values (post-9b):** `draft`, `sent`, `confirmed`, `partially_received`, `received`, `completed`, `closed`. `cancelled` was removed in MVP9b (D28 — collapsed into `closed`). Two terminal states: `completed` (happy path) and `closed` (everything else, with a `close_reason`).
**`close_reason` values:** `no_longer_required`, `supplier_unable_to_fulfill`, `partial_fulfillment_accepted`, `duplicate`, `replaced_by_new_po`, `other`.
**Note:** the `cancelled_at` datetime field still physically exists (the drop was blocked by the irreversible-action guard in MVP9b) — it is unused and no workflow writes it. Safe to drop later with explicit user OK.

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
- **Active version ID:** `367158084370432` (enabled=true, current=true) — **D30 revision: director-approval $300 floor, activated + verified 2026-05-30**. Revision of `367150157135872` (MVP010 lineage); the only change is condition `bizoy1sj87j` (see below). All prior versions disabled — see "Stale IDs".
- **Prior version ID:** `367150157135872` (now disabled) — MVP010 revision (skip_dept_approval branch, D29), activated + verified 2026-05-29.
- **Type:** approval, collection `purchase_requests`
- **Trigger appends:** `createdBy`, `createdBy.mainDepartment`, `createdBy.mainDepartment.main_approver`, `createdBy.mainDepartment.secondary_approver`
- **Trigger approvalUid:** `eau2jcelpdt`; **taskCardUid:** `samikialtou`
- **Nodes** (active version `367158084370432`; 21 nodes; node keys preserved across revisions):
  - Root update `1f6a1h52l9u` — sets status=pending_dept_approval
  - Query `yrl9kgkrb3x` (qProc) — fetches Procurement dept with `main_approver` appended
  - Condition `5hed96jh1u7` — submitter IS dept main_approver → skip dept (no notify)
    - br=1 (true): Update `nkbguc8uo7z` → status=pending_purchasing_review
    - br=0 (false): Condition `eafkgfa3axi` — `skip_dept_approval == true?` (MVP010, basic engine)
      - br=1 (true): Notification `5h232imw9ss` (FYI to dept head) → Update `budfy1scwbw` → status=pending_purchasing_review
      - br=0 (false): Approval#1 `cfg687cye3n` Dept Owner Approval
        - br=2 (approve): Update `xqlzgk0326f` → status=pending_purchasing_review
        - br=1 (return): Update `bm50djboga3` → status=info_requested
        - br=-1 (reject): Update `1b06nufq3bi` → status=rejected
  - Approval#2 `ec2h8cqal32` Procurement Approval
    - br=2 (approve): Condition `bizoy1sj87j` — **OR group (D30, basic engine):** `needs_director_approval == true` **OR** `quoted_total_usd >= 300`. (Reads both operands from `{{$jobsMapByNodeKey.ec2h8cqal32.data.*}}`. `quoted_total_usd` is the stored formula field; computes to 0 when no quote, so a missing quote never trips the floor.)
      - br=1 (true): Update `eg86l2ilhmk` → status=pending_director_approval → Approval#3 `sxvxwl498xg`
      - br=0 (false): Update `jy1365pvsce` → status=approved, approved_at=now
    - br=1 (return): Update `pket0lgmjyk` → status=info_requested
    - br=-1 (reject): Update `01vfxfgw6s3` → status=rejected
  - Approval#3 `sxvxwl498xg` Director Approval → hardcoded [12] (Dana) — nested in condition br=1
    - br=2 (approve): Update `kj1zcmujub8` → status=approved, approved_at=now
    - br=1 (return): Update `z1x6ghkmr2t` → status=info_requested
    - br=-1 (reject): Update `t2odlgyqdra` → status=rejected
- **MVP010 notification node** `5h232imw9ss`: channel `approval-todo-in-app-message` (existing in-app channel), receivers `["{{$context.data.createdBy.mainDepartment.mainApproverId}}"]`, `ignoreFail=true` (FYI must not block flow). on_leave→secondary fallback NOT implemented (main-only, v1 per D29).
- **Approval surfaces (active version 367158084370432, D30 revision):**
  - Trigger: approvalUid `oudb91ahp0g`, taskCardUid `84gqev1gycl`
  - Dept approver (`cfg687cye3n`): approvalUid `x1v8vfcjrnv`, taskCardUid `g93one3xwn9`
  - Procurement (`ec2h8cqal32`): approvalUid `1zfnz7s6in2`, taskCardUid `zbx9zt781mg` — procurement ProcessForm local to this revision lineage (detached from shared template `k60b738pjy0` in MVP8).
  - Director (`sxvxwl498xg`): approvalUid `04fmmdcx1p9`, taskCardUid `j5uzaf7vnnn`

The four MVP8 fields (`expenditure_type`, `is_emergency`, `needed_by`, `other_attachments`) are present on all three approval forms: editable on dept, read-only (`pattern: readPretty`) on procurement and director.

**Note:** Filter by key `cv237r8h7k9` + enabled=true to get current version.
**Revision how-to (CLI bug workaround):** `nb api workflow workflows revision` mints a NEW key (stray copy). To get a same-key revision, pass the key via raw `--body`: `revision --filter-by-tk <srcVersionId> --body '{"key":"cv237r8h7k9","enabled":false,"current":false}'`. See auto-memory `feedback_workflow_revision_key_bug`.

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

### Send PO workflow (MVP9b) — `draft → sent` + budget zones
- **Key:** `send_po`
- **Active version ID:** `366981771362304` (enabled=true, current=true)
- **Type:** custom-action, sync, collection `purchase_orders`; appends `[purchase_request, supplier]` (supplier appended now for future supplier-email step).
- **15-node chain** (node keys, branch structure):
  - `g_send_guard` (condition, basic) — AND status==draft, total≠null, fx_rate_to_usd≠null.
    - br=0 (false) → `g_send_fail_msg` (response-message) → `g_send_fail_end` (end, -1).
    - br=1 (true) → `calc_po_usd`.
  - `calc_po_usd` (calculation, **math.js**): `{{$context.data.total}} / {{$context.data.fx_rate_to_usd}}` → `c2dibomnrby`.
  - `c2dibomnrby` (calculation, formula.js): `{{$context.data.purchase_request.quoted_total}}/{{$context.data.purchase_request.fx_rate_to_usd}}` (PR total in USD) → `calc_cap_usd`.
  - `calc_cap_usd` (calculation, **math.js**): `{{$jobsMapByNodeKey.c2dibomnrby}} * 1.1` (110% cap) → `z3_check`.
  - `z3_check` (condition, basic `gt`): `calc_po_usd.result > calc_cap_usd.result`.
    - br=1 (true, zone 3) → `z3_msg` (response-message) → `z3_end` (end, -1).
    - br=0 (false) → `z2_check`.
  - `z2_check` (condition, **math.js**): `{{$jobsMapByNodeKey.calc_po_usd}}>{{$jobsMapByNodeKey.c2dibomnrby}}` (zone 2 = PO USD over PR USD).
    - br=1 (true, zone 2) → `oc_check`.
    - br=0 (false, zone 1) → `z1_update` (update status=sent, sent_at=now).
  - `oc_check` (condition, basic) — OR budget_override_comment==null | =="".
    - br=1 (true, comment missing) → `oc_msg` (response-message) → `oc_end` (end, -1).
    - br=0 (false, comment present) → `z2_update` (update status=sent, sent_at=now).
- **Bound to button:** `slybgc23q1i` (Send PO, `RecordTriggerWorkflowActionModel`) on PO surfaces.
- **Engine note:** `z2_check` originally used the basic `gt` calculator and never fired (every PO fell to zone 1); switching the node to math.js fixed it. See auto-memory `feedback_prefer_mathjs_engine`. **Zone 2 verified 2026-05-29** (exec `366982002049024`: PO 2.8 USD vs PR 2.667 USD, cap 2.933 → zone 2, missing comment → rejected). Zone-2 in-app notifications (9b.3) are **not yet built** — gated on Finance `main_approver`.

### Close PO workflow (MVP9b) — `draft → closed`
- **Key:** `close_po_draft`
- **Active version ID:** `366780629319680` (enabled=true, current=true)
- **Type:** custom-action, sync, collection `purchase_orders`. Triggered by the Close PO popup form's Submit (popup-form-with-submit-trigger pattern — see auto-memory `feedback_workflow_form_button_pattern`).
- Stamps `status=closed`, `closed_at={{$system.now}}` from the submitted `close_reason` + `close_comment`.

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
- **PR create form** (CreateFormModel `e76c40c8c79`, template `n9f8v5vnhhc`): includes `needs_director_approval` checkbox after justification; linkage rule makes justification required when checkbox is checked. MVP8 added `expenditure_type`, `needed_by`, `is_emergency`, `other_attachments` after `needs_director_approval`. **MVP010** added `skip_dept_approval` (CheckboxFieldModel, wrapper `830iodzmcjo`, appended to grid `5c325101ecc`).
- **PR detail popup** (`2b367dbd157`): MVP010 added `skip_dept_approval` read-only (DisplayCheckboxFieldModel, wrapper `in24ndj91et`).
- **Generate PO button** (`28jh1q2camo`, MVP9a): `RecordTriggerWorkflowActionModel` on PR table row popup and PR detail popup. Bound to workflow key `2izsx8uv50r`. Two linkage rules:
  - Hide when `record.status != "approved"` OR `record.purchase_order is not empty`.
  - Hide when `ctx.user.roles.title` does not include `"Procurement"` (procurement-only visibility; see [feedback_linkage_rules_user_roles](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_linkage_rules_user_roles.md) in auto-memory for the pattern).

Approval form surface IDs on the active version: see "Approval surfaces" above.

### Purchase Orders page (MVP9a/9b)
- **Page UID:** `liwmklclbnc`
- **Table block:** `vldbcvf41r6`
- **PO detail popup (DetailsBlockModel):** `g9xffr68350`; row-popup template `wp2s32qgfeg`.
- **Send PO button** (`slybgc23q1i`, MVP9b): `RecordTriggerWorkflowActionModel`, bound to workflow key `send_po` (set via `nb api resource update --resource flowModels`). Linkage: hide when `record.status != "draft"`; procurement-only (`ctx.user.roles.title` not-includes `"Procurement"`).
- **Close PO button** (`lylrxwl1b3g`, MVP9b): `PopupCollectionActionModel` — opens a popup with an EditForm bound to the current record. Form fields: `close_reason` (`qou6ge8axe5`, required) + `close_comment` (`h5872h3mc8r`, required). Submit action `5ove3dxktz9` triggers workflow key `close_po_draft`. Same draft + procurement-only linkage as Send. (Close-from-non-draft broadens this in 9d.)

---

## Stale IDs (DO NOT USE)

### Workflow versions of `cv237r8h7k9` (all disabled before `367158084370432`):
- `367150157135872` (was active MVP010, replaced by D30 $300-floor revision 2026-05-30). Its approval surfaces are now stale: trigger approvalUid `eau2jcelpdt`/taskCardUid `samikialtou`; dept `qvig0h56ixs`/`2570ru6tzn4`; procurement `bix5r31hbtr`/`82brq5d17mn`; director `44zwoatqddy`/`ftbqbeatyo5`.
- `366549533655040` (was active MVP8→MVP9b, replaced by MVP010 revision 2026-05-29). Its approval surfaces are now stale: trigger approvalUid `1yw73plyqsf`/taskCardUid `e6edajqk51d`; dept `0qljvpsiceo`/`pdbm4aixrc9`; procurement `z01rza37pod`/`bvlz1vbvi7t`; director `6x42w7n9h4g`/`aahsde3cnie`.
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

### Stale Send-PO (`send_po`) versions (all disabled before `366981771362304`):
- `366776493735936`, `366882024521728`, `366883251355648` — early build iterations.
- `366883769352192` — had the zone-2 bug (basic-engine `gt` condition that never fired).
- `366980364173312` — a revision where the agent patched the zone-2 condition with `.result` (wrong theory); superseded by the user's math.js fix in `366981771362304`.
- `366980536139776` (**key `s6m4i5hrmzs`**, title "Send PO copy") — a stray *duplicate* (new key, not in the `send_po` lineage) created by the CLI `workflow workflows revision` command, which duplicates rather than versions. Disabled, unreferenced; left in place (deletion needs explicit user OK).

### Disabled po_lines collection workflows (cancelled per D27):
- `jsgbxph9444` ("PO Total: Lines Added/Updated", id `366562246590464`) — was a sync collection trigger on po_lines create/update that aggregated `line_total`. Disabled 2026-05-27 because the field no longer exists; the sync failure was silently rolling back po_line creates from the Generate-PO workflow. Keep disabled.
- `s4syz7vom4n` ("PO Total: Line Deleted", id `366562257076224`) — sibling delete trigger for the same total-maintenance scheme. Also disabled.

---

## Notes for the next session

- **MVP7 was descoped.** Only `suppliers` was built; `supplier_issues` and `supplier_evaluations` are postponed (D26). Don't assume they exist.
- **Supplier UI:** if a suppliers list/detail page was built during MVP7, its page UID isn't recorded here yet — capture it the next time it's touched.
- **MVP8 ACL note:** Field-level edit gating for procurement/director on PR content stays enforced via form-pattern (`readPretty`) only, not strict ACL. Procurement+director roles still technically have those fields in their `update` whitelist via strategy-based ACL (`usingActionsConfig=false`). Tightening to independent permissions is a future hardening MVP. The four MVP8 fields inherit this same posture.
