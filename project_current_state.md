# Current Build State

**Last verified:** 2026-05-24 (migrated from auto-memory 2026-05-25; live-env spot-check pending — see notes at bottom)

MVPs 1–7 fully built; MVP7 was the most recent and added the supplier field to the three approval surfaces. Next: **MVP8 — comments + attachments + soft fields**.

This file is the **single source of truth** for the live NocoBase environment state. Update it at the end of every session that creates or modifies collections, fields, workflows, or UI surfaces. Commit changes alongside the build commits they describe.

---

## CLI environment

- **Env name:** `havenbeheer` (not `havenbeheer-dev`)
- **URL:** http://localhost:13000
- **NocoBase version:** 2.1.0-beta.36
- **Auth:** OAuth token (valid, auto-refreshes)

---

## Collections

### `purchase_requests`

| Field | Interface | Notes |
|---|---|---|
| title | input | |
| description | textarea | |
| justification | textarea | |
| submitter | m2o → users | |
| department | m2o → departments | |
| status | select | see values below |
| rejection_reason_category | select | |
| rejection_comment | textarea | |
| cancellation_reason | textarea | MVP2 — cancel popup only |
| cancelled_at | datetime | MVP2 — set by cancel workflow |
| quoted_total | number | MVP3 — entered by submitter or procurement |
| quoted_currency | select (USD/SRD/EUR) | MVP3 |
| fx_rate_to_usd | number | MVP3 — **entered manually** by submitter or procurement |
| quoted_total_usd | formula | MVP3 — formula.js: `{{quoted_total}} * {{fx_rate_to_usd}}`, always auto-computes, read-only |
| quotation_attachment | attachment (multi) | MVP3 |
| needs_director_approval | checkbox (boolean) | MVP4 — default false; set by submitter; triggers director path |
| approved_at | datetime | MVP4 — written on final approval (both no-director and director paths) |
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

### `suppliers`, `supplier_issues`, `supplier_evaluations` (MVP7)
Built per design doc. See [Planning and Design/havenbeheer purchasing — design validation.md](Planning%20and%20Design/havenbeheer%20purchasing%20—%20design%20validation.md) §11 for full field lists. Key facts:
- `suppliers.payment_terms`: single-select (Net30/Net60/Net90/COD/Prepayment) per D17
- `suppliers.current_rating`: manual integer 1–5, maintained by procurement (D6)
- `supplier_evaluations.score`: 1–5 (5 best) per D7

### Deleted collections
- `fx_rates` — deleted 2026-05-24 (MVP3 simplification under D22; no longer needed)

---

## Active workflows

### PR Approval workflow
- **Key:** `cv237r8h7k9`
- **Active version ID:** `366232953880576` (enabled=true, current=true) — MVP7 revision; old version `366087730298880` disabled
- **Type:** approval, collection `purchase_requests`
- **Trigger appends:** `createdBy`, `createdBy.mainDepartment`, `createdBy.mainDepartment.main_approver`, `createdBy.mainDepartment.secondary_approver`
- **Trigger approvalUid:** `2zmok19gb2c`; taskCardUid `exgm0gh0mru`
- **18 nodes** (current as of MVP4 restructure):
  - Root update `1f6a1h52l9u` — sets status=pending_dept_approval
  - Query `yrl9kgkrb3x` (qProc) — fetches Procurement dept with `main_approver` appended
  - Condition `5hed96jh1u7` — submitter IS dept approver → skip dept
    - br=1 (true): Update `nkbguc8uo7z` → status=pending_purchasing_review
    - br=0 (false): Approval#1 `cfg687cye3n` Dept Owner Approval
  - Approval#2 `ec2h8cqal32` Procurement Approval → main downstream: **null** (MVP4 change)
    - br=2 (approve): Condition `bizoy1sj87j` — `needs_director_approval == true?`
      - br=1 (true): Update `eg86l2ilhmk` → status=pending_director_approval → Approval#3 `sxvxwl498xg`
      - br=0 (false): Update `jy1365pvsce` → status=approved, approved_at=now
    - br=1 (return): Update `pket0lgmjyk` → status=info_requested
    - br=-1 (reject): Update `01vfxfgw6s3` → status=rejected
  - Approval#3 `sxvxwl498xg` Director Approval → hardcoded [12] (Dana) — nested in condition br=1
    - br=2 (approve): Update `kj1zcmujub8` → status=approved, approved_at=now
    - br=1 (return): Update `z1x6ghkmr2t` → status=info_requested
    - br=-1 (reject): Update `t2odlgyqdra` → status=rejected
- **Approval surfaces (version 366232953880576 — MVP7):**
  - Dept approver (`cfg687cye3n`): approvalUid `7xwj8l0sjqp`, taskCardUid `5l5vdolh5su`
  - Procurement (`ec2h8cqal32`): approvalUid `knwxauc0yoz`, taskCardUid `ivg75pqfe6b`
  - Director (`sxvxwl498xg`): approvalUid `lav2su037qi`, taskCardUid `arpce782zod`
  - All three forms show supplier field at position [2] (after description); director is readPretty

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
- **PR view popup** (DetailsBlockModel `2b367dbd157`): shows all fields including quoted_total, quoted_currency, fx_rate_to_usd, quoted_total_usd, quotation_attachment, needs_director_approval, supplier
- **Procurement approval form** (ProcessFormModel `ti4uf7gwhpu`): includes quoted_total (editable), quoted_currency (editable), fx_rate_to_usd (editable), quotation_attachment (editable), quoted_total_usd (readPretty), supplier (editable)
- **PR create form** (CreateFormModel `e76c40c8c79`, template `n9f8v5vnhhc`): includes needs_director_approval checkbox (after justification); linkage rule makes justification required when checkbox is checked

---

## Stale IDs (DO NOT USE)
- Old workflow key `p4n6dffjcgq` / version `364960795000832` — does not exist
- Old workflow key `p1tnx6nb5r9` / version `364995697901568` — disabled (user's rebuild from between sessions)
- All revisions of `cv237r8h7k9` before `366232953880576` — disabled
- Approval surfaces `5sewfvayoc4`, `ylccjkdatwa`, `wa1guuahjjo`, `4ceoua2g0ij` — belong to disabled versions, do not use
- Old approval surfaces `klak6hh6vu0`, `qswcu5p6ihj`, `42ay2w0j69v` — belong to disabled version `366087730298880`

---

## Notes for the next session

- **Live-env spot-check pending.** This file was migrated from auto-memory on 2026-05-25 without re-verifying IDs against the live NocoBase. Before acting on any specific ID for an irreversible change, verify it with `nb` against the env. The IDs were correct as of 2026-05-24 per the previous session.
- **MVP7 verification status.** MVP7 (suppliers + supplier_issues + supplier_evaluations + supplier field on PR) was built. Whether scenarios S1–S5 were user-verified is unclear from the migrated memory — confirm with user at start of MVP8.
