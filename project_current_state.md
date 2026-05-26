# Current Build State

**Last verified:** 2026-05-25 (live env queried via `nb api` — collections, workflows, approval surfaces).

MVPs 1–7 built; MVP7 reduced to suppliers-only (`supplier_issues` and `supplier_evaluations` postponed — see [decisions.md](decisions.md) D26). Next: **MVP8 — comments + attachments + soft fields**.

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
| quoted_total_usd | formula | MVP3 — formula.js: `{{quoted_total}} * {{fx_rate_to_usd}}`, auto-computes, read-only |
| quotation_attachment | attachment (multi) | MVP3 |
| needs_director_approval | checkbox (boolean) | MVP4 — default false; set by submitter; triggers director path |
| approved_at | datetime | MVP4 — written on final approval (both paths) |
| supplier | m2o → suppliers | MVP7 — optional "Suggested supplier" |

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

### Deleted collections
- `fx_rates` — deleted 2026-05-24 (MVP3 simplification under D22)

---

## Active workflows

### PR Approval workflow
- **Key:** `cv237r8h7k9`
- **Active version ID:** `366234405109760` (enabled=true, current=true). All prior versions of this key are disabled — see "Stale IDs".
- **Type:** approval, collection `purchase_requests`
- **Trigger appends:** `createdBy`, `createdBy.mainDepartment`, `createdBy.mainDepartment.main_approver`, `createdBy.mainDepartment.secondary_approver`
- **Trigger approvalUid:** `no4q0qifkv2`; **taskCardUid:** `fc8790fw6pd`
- **Nodes** (active version `366234405109760`):
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
- **Approval surfaces (version 366234405109760):**
  - Dept approver (`cfg687cye3n`): approvalUid `0x4yjm74y0o`, taskCardUid `jmy6o8nkdld`
  - Procurement (`ec2h8cqal32`): approvalUid `zbvpqgod2bs`, taskCardUid `39ynx9u1zlh`
  - Director (`sxvxwl498xg`): approvalUid `nnzr393hos1`, taskCardUid `wet1jqjv8t2`

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
- **Table block:** `l1e2iwdwau9` — columns include title, status, quoted_total, quoted_currency (+ more)
- **PR view popup** (DetailsBlockModel `2b367dbd157`): shows all PR fields incl. quote fields, `needs_director_approval`, `supplier`
- **Procurement approval form** (ProcessFormModel `ti4uf7gwhpu`): quoted_total, quoted_currency, fx_rate_to_usd, quotation_attachment editable; quoted_total_usd readPretty; supplier editable
- **PR create form** (CreateFormModel `e76c40c8c79`, template `n9f8v5vnhhc`): includes `needs_director_approval` checkbox after justification; linkage rule makes justification required when checkbox is checked

Approval form surface IDs on the active version: see "Approval surfaces" above.

---

## Stale IDs (DO NOT USE)

### Workflow versions of `cv237r8h7k9` (all disabled before `366234405109760`):
- `366232953880576` (was active during MVP7 build, now disabled)
- `366207890817024`
- `366087730298880`
- `366086440550400`
- `366059727028224`
- `366057076228096`
- `366053490098176`
- `365711034417152`
- `365001941123072`

### Approval surfaces from disabled workflow versions:
- Trigger surfaces from version `366232953880576`: approvalUid `2zmok19gb2c`, taskCardUid `exgm0gh0mru`
- Dept surfaces from version `366232953880576`: approvalUid `7xwj8l0sjqp`, taskCardUid `5l5vdolh5su`
- Procurement surfaces from version `366232953880576`: approvalUid `knwxauc0yoz`, taskCardUid `ivg75pqfe6b`
- Director surfaces from version `366232953880576`: approvalUid `lav2su037qi`, taskCardUid `arpce782zod`
- Older disabled-version surfaces: `5sewfvayoc4`, `ylccjkdatwa`, `wa1guuahjjo`, `4ceoua2g0ij`, `klak6hh6vu0`, `qswcu5p6ihj`, `42ay2w0j69v`, `apz6gdy0z6z`, `n7n6x0xg3t0`, `wdty2zx7de7`, `8yyu6ofo1ww`, `rgcyt60s8pg`, `yyptfj0azru`, `o4jc2ghrs4q`, `8x5ktd74gwx`, `o1n99mp7sn7`

### Stale workflow keys:
- `p4n6dffjcgq` / version `364960795000832` — does not exist
- `p1tnx6nb5r9` / version `364995697901568` — disabled rebuild from between sessions
- `idezsq1k1ts` / `363982109736960` — original v3-plan MVP1 key, superseded

---

## Notes for the next session

- **MVP7 was descoped.** Only `suppliers` was built; `supplier_issues` and `supplier_evaluations` are postponed (D26). Don't assume they exist.
- **Supplier UI:** if a suppliers list/detail page was built during MVP7, its page UID isn't recorded here yet — capture it the next time it's touched.
