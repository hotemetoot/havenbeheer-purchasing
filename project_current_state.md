# Current Build State

**Last verified:** 2026-06-11 evening (**ROLE HARDENING Phase 2 DONE — data-driven approvers (D40); user round-trip test PENDING.** New test user **fiona.finance (14)**, Finance dept, member base + dept-inherited `finance` role, password `Test1234!`. `departments.main_approver` now fully populated: Director → Dana (12), Finance → fiona (14) (Procurement → Pat 11, Operations → Oliver 10 already set). `finance` role got the D38 render-enabler treatment: independent `purchase_requests` row (view all 37 fields + update 2 rejection fields @ scopeId 10) + member's 11 desktop routes (was zero). **PR Approval revisioned `369166026080256` → active `369495666917376`** (same key via raw `--body`; 31 nodes): new query node `ld6gei5ybc5` "Query Director Dept (for assignee)" inserted between `eg86l2ilhmk` and the Director approval node; Director assignees `[12]` → `{{$jobsMapByNodeKey.ld6gei5ybc5.main_approver.id}}` (filter-block form); Board assignees `[11]` → `{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}` (existing qProc). All 5 approval surfaces regenerated, all 10 referenced CommentFormModels verified to exist. Note: `flow-nodes test` is NOT implemented for `query` nodes — verified instead by live data readback + identical config shape to the proven qProc node. New surface uids: trigger `a88dhcc6p8k`/`yuli5bfnwfu`, Procurement `fjrw5u3cxxg`/`n7bjt8nz4uy`, Dept `h84ic5epwko`/`mjy73tr4cid`, Director `7qnayjp9lzl`/`k7ynav1jxw4`, Custom `wc4et0bt8si`/`qld8db015tw`, Board `r3w4l3ibkui`/`z1o8zfquxgn`. Board surface still Approve-only (pre-existing — confirm with user). Phases 3–4 remain in [HANDOFF.md](HANDOFF.md).)

**Prior (2026-06-11):** (**ROLE HARDENING phases 0–1 DONE + user-verified** — see the new "Roles & ACL" section: member/director strategies now view-only, member snippets reverted to vanilla, new dept-bound `operations` role (PR create/update + routes), procurement trimmed (no PR create/importXlsx, whitelisted updates), director render-enabler grant. D38. **Remaining phases 2–4 are specced in [HANDOFF.md](HANDOFF.md).** Also this session: doc-lag corrected — **PR Approval active is `369166026080256`** (user revision; doc said `369161752084480`), **Generate PO active is `368786562547712`** (6 nodes — the user *manually removed* the default-line create node; NOT the branch-drop bug). Four stray disabled workflows deleted (`close_po_draft` deprecated custom-action, `s6m4i5hrmzs` "Send PO copy", `jsgbxph9444`, `s4syz7vom4n`). **User flow change (D39): PR `draft` stage removed from the flow — users submit directly.** The status enum + `defaultValue: 'draft'` still exist on the field; the change is at form/flow level. Implications (cancel workflow guard checks `status=="draft"`; scope 2 references draft) tracked in HANDOFF.md.)

**Prior (2026-06-09):** (**MVP013 DONE + VERIFIED (A1–A7 passed)** — D37 regular-purchase flag: below $300 now defaults to Director, with a new Procurement-set `is_regular` checkbox as the opt-out (regular + <$300 → approved directly). `needs_director_approval` retired from routing (column kept, unused). New field `is_regular` (`fw0rz4we4bw`, boolean default false). **PR Approval `cv237r8h7k9` revisioned `369154168193024`→active `369161752084480`** (30 nodes): condition `bizoy1sj87j` is now basic-OR `is_regular != true` OR `quoted_total_usd >= 300` (the `needs_director_approval` leaf removed). Procurement ProcessForm grid `03uy1easu6l` gained editable `is_regular` (wrapper `dcbp2xasi5f`); detail popup grid `16975baef39` gained read-only `is_regular` (wrapper `6q8zzia1bt7`). flow-nodes test passed all 6 quadrants incl null-safety. **Doc-lag corrected:** the active version before MVP013 was a user revision `369154168193024`, NOT the doc-recorded `369076269481984` — both now stale. See D37. Prior: **MVP012 DONE + VERIFIED** — A1–A7 all passed via test users; user set the picker data scope (same-dept + exclude-self) in the form UI. Submitter-selectable dept-stage approver, retires the MVP010 skip (D36, supersedes D29). Two new `purchase_requests` fields: `use_custom_approver` (boolean), `custom_approver` (m2o → users, FK `customApproverId`). **PR Approval workflow `cv237r8h7k9` revisioned to active `369076269481984`** (30 nodes) — the skip branch was repurposed into a custom-approver branch: condition `eafkgfa3axi` retitled "Custom approver chosen?" = AND(`use_custom_approver==true`, `custom_approver.id != null`, `custom_approver.id != createdById` self-exclusion); br=1 → reused notify `5h232imw9ss` (FYI dept head) → new approval node `fifkfnqn9pm` "Custom Approver Approval" (assignee `{{$context.data.custom_approver.id}}`, approvalUid `1a1zhqfmpdl`/taskCardUid `369lxzap6i2`, duplicated from Dept Owner node so form+comment models identical) → outcome updates `r8f85w1w1ze`/`8loza7mypxd`/`vhize11vzsg`; br=0 → unchanged Dept Owner Approval `cfg687cye3n`. `custom_approver` added to trigger appends. Auto-skip `5hed96jh1u7` (submitter IS dept head) unchanged + still first. **Doc-lag corrected:** active PR-Approval before this was `368983543906304` (NOT `368641179582464` as previously recorded) — both now stale. **UI:** create form `e76c40c8c79` got checkbox `r9iu06my5ot` + picker `gfozpat06nw` + show/require linkage; detail popup `2b367dbd157` got both fields read-only (`7jjizc66ex2`/`9tpfw54yy1e`) and the skip read-only `in24ndj91et` was removed. **`skip_dept_approval` column RETAINED but dead** (no workflow reads/writes it; off both forms). Picker data scope (same-dept + exclude-self) was set by the user via the form "Set data scope" UI (public CLI can't author it); self-approval is also hard-blocked server-side. **Only remaining (low priority):** drop the dead `skip_dept_approval` column with explicit OK. See D36. Earlier same day: **MVP9e DONE + VERIFIED** — PO template printing: Carbone template `printingTemplates:kkooshlz8rf` → `storage/print-templates/po-template-mvp9e.docx` (Havenbeheer-branded), Print button `c579329db0d`; user confirmed live PDF on PO-26-0006, P2 internal_notes-not-printed holds. See the `printingTemplates` collection + MVP9e note in "Notes for the next session". Earlier same day: **MVP9d fully VERIFIED end-to-end** — all 8 cases C1/C2/C3/C4/C5 + D34a/D34b/D35 passed via Pat-driven UI clicks against API-staged fixtures; see "Notes for the next session". D34 — Complete PO requires an attached invoice + positive `total_usd`; guard revisioned `368746204954624`→`368971625791488`, Complete button `e60dce0bb2d` linkage extended. D35 — Close Guard request-interception `b6brl8r9c58` rejects + messages a Close attempt on a non-closeable (e.g. `received`) PO, which the post-action Close workflow couldn't.** See Complete/Close workflow sections + decisions D34/D35. Prior baseline below from 2026-06-07.) Earlier: live env queried via `nb api` — **MVP9d backend built (Complete workflow + broadened Close + PO/line immutability guards); UI buttons + end-to-end C1–C5 verification PENDING (user wires the buttons)**; MVP9c PO-receiving verified; D32/MVP011 board-approval ≥ $15k; PR/PO numbering D31; director-approval $300 floor D30; MVP9b Send-PO + Close-PO; MVP010 skip-dept-approval). Next: **MVP9d verification, then MVP9e — PO template printing (not started; a bare "Template print" button exists on the PO detail block but no template is configured or tested)**.

**MVP9d backend built 2026-06-07 (PO completion / closing / immutability) — UI + verification pending.** Scope aligned to **D28** (no `cancel` action, no `cancelled` status — "cancel a draft" is just close-with-reason, already in 9b). Four workflow changes: (1) **Complete PO** (custom-action, sync, key `qh7b3hc5q1r`, ver `368746204954624`): guard `complete_guard` (status==received) → true: `complete_update` status=completed + completed_at; false: reject msg + end(-1). (2) **Close PO** rebuilt as a **post-action event** (`action` type, sync, local mode, key `f8gpu17s6hq`, ver `368791950131200`): guard `close2_guard` (status ∈ {draft,sent,confirmed,partially_received}) → `close2_update` (status=closed, closed_at=now). **Correction:** the original 9d build wrongly made Close a `custom-action` (`close_po_draft`) — a form Submit can only bind pre/post-action/approval, so custom-action couldn't bind; the old one is disabled + renamed "(deprecated custom-action)". The user binds `f8gpu17s6hq` to the Close EditForm's Submit (local mode). (3) **Guard: PO Immutability** (request-interception, global, sync, key `xvcsdv07c5j`, ver `368747670863872`; actions update+destroy on `purchase_orders`): query target PO → condition OR status∈{completed,closed} → reject msg + end(-1). (4) **Guard: PO Line Immutability** (request-interception, global, sync, key `f3dkb37te22`, ver `368747750555648`; actions update+destroy on `po_lines`): query line (appends purchase_order) → condition OR purchase_order.status∈{completed,closed} → reject msg + end(-1). No new fields (completed_at/closed_at/close_reason/close_comment + status enum all pre-existed). **UI:** the user builds the Complete + Close buttons themselves (as with the 9c receiving UI); the doc-recorded Close button `lylrxwl1b3g` was **removed by the user** and is gone from the surface. **Caveat:** the PO immutability guard locks ALL updates on terminal POs, including payment fields — fine now (no Finance payment UI/workflow built, finance role strategy = null), but a future payment MVP will need a carve-out (cf. the `closed_for_new_pos` exemption pattern). See D33.

**Doc-lag corrected 2026-06-07 (live `nb api` re-query):** active versions had drifted from the doc — **Send PO** active is `367086330314752` (was recorded `366981771362304`); **PR Approval** active is `368641179582464` (was `367885604880384`); **PO Receiving recompute** active is `368710576439296` (was `368072534523904`). Sections below updated. A stray disabled PR-Approval ver `368062113775616` may also exist (not re-confirmed this session).

**MVP9c built + verified 2026-06-07 (PO receiving).** Receiving UI built by the user; R1–R4 passed (partial→partially_received; full→received + Pat notified; correct-down reverts received→partially_received; receiving on non-sent PO blocked). Two workflows: (1) **Guard: Receive** (request-interception, key `mhfp4d15uee`, ver `368072131870720`) blocks a `received_quantity` change on a PO not in `sent`/`confirmed`/`partially_received`/`received`; (2) **PO Receiving recompute** (collection trigger, key `ork27v016yo`, ver `368072534523904`) derives `po_lines.line_status` + PO header status on `received_quantity` change, and notifies Procurement (Pat) when fully received. Pricing untouched (D27 — no PO-total recompute). No new fields (received_quantity/line_status already existed from 9a; Record History already on via collection-level `logging:true`). No plan changes during build → no D-entry.

**D32 built + verified 2026-06-02 (MVP011):** mandatory board approval at `quoted_total_usd >= 15000`, *after* the director. New status `pending_board_approval`, new multi-attachment field `board_approval_document`. PR Approval revisioned `367158084370432` → **`367885604880384`** (key `cv237r8h7k9`); board branch hangs off the director-approve branch via condition `fro4hak78r9`, routing ≥ $15k to a 4th approval node **Board Approval** (`01upqmcb1qy`, assignee Pat) whose ProcessForm requires the signed-doc upload. Two follow-on fixes were needed to make a fresh approval form usable by a non-admin approver: (1) granted Procurement `create` on `attachments` (independent resource perm) so Pat can upload; (2) pre-created the per-action `CommentFormModel`s the blueprint omits (else approver 403 on `flowModels:save`). See decisions D32 and auto-memory `feedback_approver_attachment_upload_acl` + `feedback_approval_blueprint_comment_models`.

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
| pr_number | sequence | **D31** — auto `PR-YY-NNNN` (2-digit year, 4-digit yearly-cycling counter, e.g. `PR-26-0004`); field key `jo6vvssc0i5`, `inputable: false`. Assigned at PR creation. PO derives its number from this (see Generate-PO workflow). **Counter note:** `PR-26-0001` was consumed by a since-deleted verification PR; deleting records does not roll back a sequence counter, so the next new PR will be **`PR-26-0002`**. |
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
| needs_director_approval | checkbox (boolean) | MVP4 — **RETIRED FROM ROUTING (D37/MVP013)**; column kept but no longer read by any workflow and off the create form; read-only display remains on the detail popup. Was: submitter-set director escalation. |
| is_regular | checkbox (boolean) | **D37 (MVP013)** — default false (real boolean); set by **Procurement** on their approval form. Below $300, `is_regular==true` → approved directly; else → director. Field key `fw0rz4we4bw`. Read by condition `bizoy1sj87j` via `{{$jobsMapByNodeKey.ec2h8cqal32.data.is_regular}}`. Editable on procurement ProcessForm, read-only on detail popup. |
| approved_at | datetime | MVP4 — written on final approval (both paths) |
| supplier | m2o → suppliers | MVP7 — optional "Suggested supplier" |
| expenditure_type | select (capex/opex/maintenance/consumables) | MVP8 |
| is_emergency | checkbox (boolean) | MVP8 — UI flag only, no routing impact |
| needed_by | dateOnly | MVP8 |
| other_attachments | attachment (multi) | MVP8 — distinct from `quotation_attachment` |
| comments | o2m → pr_comments | MVP8 — comment thread relation; UI block removed post-verify (data layer kept) |
| purchase_order | oho (hasOne) → purchase_orders | MVP9a — virtual inverse of `purchase_orders.purchase_request`. No FK column on PR side. |
| skip_dept_approval | checkbox (boolean) | MVP010 — default false; submitter opts to skip dept-head approval (D29). On the create form + read-only on detail popup. Honored by active PR Approval workflow (FYI-notifies dept head). |
| use_custom_approver | checkbox (boolean) | **D36 (MVP012)** — default false; submitter opts to reassign the dept-approval stage. On the create form; read-only on detail popup. |
| custom_approver | m2o → users | **D36 (MVP012)** — FK `customApproverId`; the chosen dept-stage approver. Create-form picker (required when `use_custom_approver` on; data scope = same dept + exclude self, set via form UI). Read by the workflow's "Custom approver chosen?" branch. |
| board_approval_document | attachment (multi) | **D32 (MVP011)** — field key `ingr48ghuzj`, type belongsToMany → attachments. Editable+**required** on the Board Approval ProcessForm; read-only display on the PR detail popup. Holds the board's signed hard-copy scan. |

**`status` values:** `draft`, `pending_dept_approval`, `pending_purchasing_review`, `pending_director_approval`, `pending_board_approval` (**D32** — purple, after director), `info_requested`, `approved`, `rejected`, `cancelled`

### `departments`

| Field | Notes |
|---|---|
| main_approver (m2o → users) | primary approval assignee |
| secondary_approver (m2o → users) | backup when main_approver is on leave |

| Department | ID | main_approver | secondary_approver |
|---|---|---|---|
| Procurement | 363554444476416 | Pat (user 11) | — |
| Director | 363554454962176 | Dana (user 12) — **D40** | — |
| Finance | 363554454962177 | Fiona (user 14) — **D40** | — |
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

Key fields: `po_number` (**D31** — plain `string`/`input` field, key `esjop6vlpp9`; the old auto-`sequence` field was deleted by the user and replaced. Written by the Generate-PO workflow as the PR's `pr_number` with the `PR-` prefix swapped to `PO-`, e.g. `PO-26-0004`), `purchase_request` (m2o → purchase_requests, FK `purchaseRequestId`), `supplier` (m2o), `delivery_address` (m2o), `status` (default `draft`), `currency`, `fx_rate_to_usd`, `total` (workflow-maintained, no formula), `total_usd` (formula.js: `{{total}} / {{fx_rate_to_usd}}` — division, local-per-USD), `payment_status`, `payment_date`, `expected_delivery_date`, `invoice` (attachment), `attachments` (attachment multi), `supplier_note`, `internal_notes`, `budget_override_comment`, `close_reason`, `close_comment`, audit timestamps (`sent_at`, `confirmed_at`, `completed_at`, `closed_at`).

**`status` values (post-9b):** `draft`, `sent`, `confirmed`, `partially_received`, `received`, `completed`, `closed`. `cancelled` was removed in MVP9b (D28 — collapsed into `closed`). Two terminal states: `completed` (happy path) and `closed` (everything else, with a `close_reason`).
**`close_reason` values:** `no_longer_required`, `supplier_unable_to_fulfill`, `partial_fulfillment_accepted`, `duplicate`, `replaced_by_new_po`, `other`.
**Note:** the `cancelled_at` datetime field still physically exists (the drop was blocked by the irreversible-action guard in MVP9b) — it is unused and no workflow writes it. Safe to drop later with explicit user OK.

### `po_lines` (MVP9a — built 2026-05-26)

Line items for purchase orders — **pricing was descoped 2026-05-26 (D27)**. Lines now track quantity + receiving only; financial values stay at PO level (manually entered from supplier invoice). Fields: `purchase_order` (m2o), `product` (m2o optional), `description` (textarea, required), `unit_of_measure` (m2o), `quantity_ordered`, `received_quantity`, `line_status` (default `pending`). Previously had `unit_price`, `line_total` (formula), `line_total_usd` (formula); all three deleted. The planned 9a.4 Total-maintenance workflow is **cancelled** — PO `total` is no longer derived from lines.

### `delivery_addresses`, `units_of_measure`, `products` (MVP9a — built 2026-05-26)

Lookup collections. `delivery_addresses` has `name` (title), `address`, `is_default`, `status`. `units_of_measure` has `name` (title, **unique**), `abbreviation`, `status`. `products` (v1 stub) has `name` (title, **unique**), `description`, `default_uom` (m2o → units_of_measure), `status`.

### `printingTemplates` (MVP9e — template-print registry)

Owned by `@nocobase/plugin-action-template-print`. One record per print template. Fields: `name` (the `templateName` the Print button references), `title`, `collectionName`, `rootDataType`, `dataSource`, `filename`.

| Record `name` | title | collectionName | filename | Notes |
|---|---|---|---|---|
| `kkooshlz8rf` | Purchase Order | purchase_orders | `po-template-mvp9e.docx` | MVP9e PO template (Carbone). Bound to Print button `c579329db0d`. Old stub `17809643261187811286095403871.docx` kept on disk for rollback. |

The `.docx` files live on disk at **`/Users/alexander/nocobase/storage/print-templates/`** (not in attachments). Repo source-of-truth: `templates/build_po_template.py` → `templates/purchase-order-template.docx` (+ `templates/main-logo.png`). To change: edit builder → run it → `cp` docx over the storage file (file overwrite, no live config write). Carbone markers: data root `d`; **select fields use `.label`**; assoc to po_lines is **`lines`**; **`internal_notes` is NOT rendered** (P2). See auto-memory `feedback_template_print_*`.

### Deleted collections
- `fx_rates` — deleted 2026-05-24 (MVP3 simplification under D22)

---

## Active workflows

### PR Approval workflow
- **Key:** `cv237r8h7k9`
- **Active version ID:** `369495666917376` (enabled=true, current=true) — **D40 data-driven approvers, built 2026-06-11 (Phase 2); user round-trip PENDING.** 31 nodes: same-key revision of `369166026080256` + new query node **`ld6gei5ybc5`** "Query Director Dept (for assignee)" (filter id `363554454962176`, appends `main_approver`) inserted between `eg86l2ilhmk` and Director approval `sxvxwl498xg`. Director assignees = `{{$jobsMapByNodeKey.ld6gei5ybc5.main_approver.id}}`, Board (`01upqmcb1qy`) assignees = `{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}` (both filter-block form per `feedback_approval_assignee_from_variable`). Approval surfaces on THIS version (all regenerated, comment models verified): trigger `a88dhcc6p8k`/`yuli5bfnwfu`, Procurement `fjrw5u3cxxg`/`n7bjt8nz4uy`, Dept `h84ic5epwko`/`mjy73tr4cid`, Director `7qnayjp9lzl`/`k7ynav1jxw4`, Custom `wc4et0bt8si`/`qld8db015tw`, Board `r3w4l3ibkui`/`z1o8zfquxgn`. **Board surface has only an Approve action (no Reject/Return buttons)** though the workflow has board reject/return outcome nodes — confirm with user whether intentional.
- **Prior active (now stale):** `369166026080256` — a user revision found live 2026-06-11 (audit re-query); 30 nodes, hardcoded assignees Director [12] / Board [11]. Superseded by the D40 revision above. Its surfaces (Procurement `su56vx8p048`, Dept `nwjvklrknlf`, Director `7kuv49goy4o`, Custom `h2sh3r9monu`, Board `xwd019rr78k`) are stale. Disabled.
- **Prior active (now stale):** `369161752084480` — **D37/MVP013, built 2026-06-09**: the director-decision condition `bizoy1sj87j` (id `369161754181632`, retitled "Director required? (>= $300 OR not regular)") now reads the new `is_regular` flag. Basic-engine OR: `notEqual {{$jobsMapByNodeKey.ec2h8cqal32.data.is_regular}} != true` **OR** `gte {{$jobsMapByNodeKey.ec2h8cqal32.data.quoted_total_usd}} >= 300` (the `needs_director_approval == true` leaf was removed/retired). true→Director (`eg86l2ilhmk`), false→approved (`jy1365pvsce`). 30 nodes (no branches dropped). Revision of `369154168193024` (forced same key). **New Procurement approval surface uid (regenerated by this revision):** approvalUid `otlzkklrg0n`, taskCardUid `bhx9rxilzwm`; its ProcessForm grid `03uy1easu6l` gained editable `is_regular` (CheckboxFieldModel wrapper `dcbp2xasi5f`). All other MVP012 custom-approver nodes/surfaces unchanged (keys preserved). flow-nodes test passed; A1–A7 user verification pending.
- **Prior active (now stale):** `369154168193024` (a **user revision** discovered this session — the doc had wrongly listed `369076269481984` as active; `369076269481984` and all earlier are disabled). The MVP012 custom-approver node keys below (condition `eafkgfa3axi`, notify `5h232imw9ss`, approval `fifkfnqn9pm`, outcomes `r8f85w1w1ze`/`8loza7mypxd`/`vhize11vzsg`) are preserved across the MVP013 revision; surface IDs from earlier revisions are stale — refresh when next touched.
- **Prior active (now stale):** `368983543906304` (pre-MVP012). `368641179582464` was also superseded. Both disabled.
- **(Pre-MVP012 line, retained for history) was-recorded Active version ID:** `368641179582464` — **doc-lag corrected 2026-06-07** (was recorded `367885604880384`; a later user revision is now active — its node/surface IDs were NOT re-inspected this session, so the node/surface tables below describe the `367885604880384` D32 revision and may lag). The D32 board-approval ≥ $15k branch was activated + verified 2026-06-02 (16,000 USD PR) on this lineage. All prior versions disabled — see "Stale IDs".
- **Prior version ID:** `367158084370432` (now disabled) — D30 revision (director $300 floor), was active 2026-05-30 → 2026-06-02.
- **Type:** approval, collection `purchase_requests`
- **Trigger appends:** `createdBy`, `createdBy.mainDepartment`, `createdBy.mainDepartment.main_approver`, `createdBy.mainDepartment.secondary_approver`
- **Trigger approvalUid:** `2xxjrbc0b36`; **taskCardUid:** `1yj5xm96k3p` (regenerated by the D32 revision)
- **Nodes** (active version `367885604880384`; 27 nodes; node keys preserved across revisions):
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
    - br=2 (approve): Condition `bizoy1sj87j` — **OR group (D37/MVP013, basic engine):** `is_regular != true` (notEqual) **OR** `quoted_total_usd >= 300` (gte). (Reads both operands from `{{$jobsMapByNodeKey.ec2h8cqal32.data.*}}`. `is_regular` set by Procurement on their form; `!= true` so null→Director (null-safe). `quoted_total_usd` computes to 0 when no quote → missing quote never trips the floor. **D37 replaced the old D30 `needs_director_approval == true` leaf with the `is_regular != true` leaf** — `needs_director_approval` is retired from routing.)
      - br=1 (true): Update `eg86l2ilhmk` → status=pending_director_approval → Approval#3 `sxvxwl498xg`
      - br=0 (false): Update `jy1365pvsce` → status=approved, approved_at=now
    - br=1 (return): Update `pket0lgmjyk` → status=info_requested
    - br=-1 (reject): Update `01vfxfgw6s3` → status=rejected
  - Approval#3 `sxvxwl498xg` Director Approval → hardcoded [12] (Dana) — nested in condition br=1
    - br=2 (approve): Condition `fro4hak78r9` — **board floor (D32, basic engine, `gte`):** `quoted_total_usd >= 15000`, reading `{{$jobsMapByNodeKey.ec2h8cqal32.data.quoted_total_usd}}` (same proven reference as D30).
      - br=0 (false, < $15k): Update `kj1zcmujub8` → status=approved, approved_at=now
      - br=1 (true, ≥ $15k): Update `fm6kvldiduk` → status=pending_board_approval → Approval#4 `01upqmcb1qy` **Board Approval** → hardcoded [11] (Pat)
        - br=2 (approve): Update `8gqeq6djrfj` → status=approved, approved_at=now
        - br=1 (return): Update `s1tignlqc54` → status=info_requested
        - br=-1 (reject): Update `2rd8sap9m04` → status=rejected
    - br=1 (return): Update `z1x6ghkmr2t` → status=info_requested
    - br=-1 (reject): Update `t2odlgyqdra` → status=rejected
- **MVP010 notification node** `5h232imw9ss`: channel `approval-todo-in-app-message` (existing in-app channel), receivers `["{{$context.data.createdBy.mainDepartment.mainApproverId}}"]`, `ignoreFail=true` (FYI must not block flow). on_leave→secondary fallback NOT implemented (main-only, v1 per D29).
- **Approval surfaces (active version 367885604880384, D32 revision — all regenerated by the revision):**
  - Trigger: approvalUid `2xxjrbc0b36`, taskCardUid `1yj5xm96k3p`
  - Dept approver (`cfg687cye3n`): approvalUid `kf4c07ogog3`, taskCardUid `039itexge7o`
  - Procurement (`ec2h8cqal32`): approvalUid `96s75dc8gh4`, taskCardUid `d9evoyo0fns`
  - Director (`sxvxwl498xg`): approvalUid `cgctmkrd7c5`, taskCardUid `wlibpupq7mx`
  - **Board (`01upqmcb1qy`, D32 — built via `applyApprovalBlueprint`, NOT cloned):** approvalUid `4eydmvrzsxs`, taskCardUid `gurwtm8po6b`. ProcessForm `he7olrujn6w` with **editable+required** `board_approval_document` (wrapper `y07ibxtl4i9`, `editItemSettings.required.required=true`) + a read-only `approvalInformation` block (`x3c2i31k26v`, 7 PR fields). Actions: Approve `0nxvt0eutij` / Reject `urne0a35pt9` / Return `ai7gyigfny1`.
- **Board comment models (D32):** the blueprint did NOT create the per-action `CommentFormModel`, causing approver `flowModels:save` 403 ("Failed to load or create comment model"). Pre-created `bcmt_approve` / `bcmt_reject` / `bcmt_return` (standalone `CommentFormModel` flowModels) and set each board action's `commentFormUid` to match a working node. See auto-memory `feedback_approval_blueprint_comment_models`.

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

### Generate PO workflow (MVP9a; D31 PO-number derivation)
- **Key:** `2izsx8uv50r`
- **Active version ID:** `368786562547712` (enabled=true, current=true) — **user revision, 6 nodes: the default-line create node (`4p3q7oq3co5`) was removed manually by the user** (confirmed 2026-06-11 — intentional, not the suspected revision branch-drop bug). The node chain below otherwise holds (guard → query address → calc number → create PO → false-branch message+end).
- **Prior active (now stale):** `367255610327040` — **D31 revision: derive `po_number` from PR's `pr_number`, built + verified 2026-05-30.** Revision of `366626572533760` (which itself was a user revision after the doc previously recorded `366623590383616` as active — that and the other intermediate versions are now stale; see Stale IDs).
- **Type:** custom-action, sync, collection `purchase_requests`; appends `[supplier, purchase_order]`.
- **Node chain (7 nodes):** Guard condition (`uufqoeb8xyz`, AND of `status==approved` + `purchase_order==null`):
  - branch 1 (true) → Query default delivery address (`ay8dlnys4ef`) → **Calculation `umk9xiw5aio` (D31, formula.js): `SUBSTITUTE({{$context.data.pr_number}}, "PR-", "PO-")`** → Create purchase_orders (`ubg9mju1tjm`, sets `po_number={{$jobsMapByNodeKey.umk9xiw5aio}}`, `createdById={{$context.user.id}}`) → Create po_lines default line (`4p3q7oq3co5`, writes only `purchase_order`/`description`/`quantity_ordered=1`)
  - branch 0 (false) → Response message (`ylrivonemrq`) → End process (`gviz4zia0ha`, endStatus: -1)
- The `response-message` + `end-process(-1)` pair on the false branch (per [`feedback_inline_guard_end_node`](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_inline_guard_end_node.md)) is preserved across the D31 revision.
- **Bound to button:** `28jh1q2camo` (Generate PO button, visible on PR table block `l1e2iwdwau9` and PR detail popup `2b367dbd157`). Binding is by key, unaffected by the revision.

### Create-PO Guard (MVP9a)
- **Key:** `vgv8hcrtjvx`
- **Active version ID:** `366562380808192` (enabled=true)
- **Type:** request-interception, global, sync; actions: `create` on `purchase_orders`
- **Node chain:** Query referenced PR (`ww4mxz67ge8`, appends `purchase_order`) → Condition OR pr.status≠approved | pr.purchase_order≠null (`dba34lyg168`) → branch 1: response-message (`7fp12f2018u`) + end (`j57v75y2cky`, endStatus:-1).

### Send PO workflow (MVP9b) — `draft → sent` + budget zones
- **Key:** `send_po`
- **Active version ID:** `367086330314752` (enabled=true, current=true) — **doc-lag corrected 2026-06-07** (was recorded `366981771362304`, which is now a disabled prior version). Node keys/structure unchanged from the description below; the math.js zone-2 fix is carried.
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

### Close PO workflow (MVP9d, **post-action event**) — `draft/sent/confirmed/partially_received → closed`
- **Key:** `f8gpu17s6hq` · title "Close PO"
- **Active version ID:** `368791950131200` (enabled=true, current=true) — built 2026-06-07.
- **Type:** **`action` (Post-action event), sync, local mode** (`global:false`), collection `purchase_orders`. Bound by the user to the Close popup EditForm's **Submit** under **Bind workflows → post-action event (local mode)**. (A form Submit can ONLY bind pre-action/post-action/approval — **not** custom-action; the old custom-action close was the wrong type. See auto-memory `feedback_workflow_form_button_pattern` — corrected.)
- **Nodes (2):** `close2_guard` (condition, basic, OR of `equal {{$context.data.status}}` against `draft`/`sent`/`confirmed`/`partially_received`, rejectOnFalse=false) → br=1 (true): `close2_update` (update `purchase_orders` where id=`{{$context.data.id}}`, status=closed, closed_at=now). No false-branch nodes — **a post-action event runs AFTER the update and cannot reject or surface a message** (confirmed via the trigger reference: `type:"action"` = Post-action Event). So this workflow just skips stamping when not closeable; the user-facing rejection is now done by the **Close Guard** request-interception workflow below (D35).
- Flow: the EditForm Submit saves `close_reason` + `close_comment` (its own update), then this post-action workflow stamps `status=closed`, `closed_at`. **Note:** `received` is intentionally NOT closeable (a received PO completes; to bail, correct a line down to revert to `partially_received` first — D33).
- **Deprecated predecessor:** `close_po_draft` (`366780629319680`, custom-action) — **DELETED 2026-06-11** (with user OK, role-hardening session) along with strays `s6m4i5hrmzs` ("Send PO copy"), `jsgbxph9444`, `s4syz7vom4n`.

### Close Guard (D35, 2026-06-09) — reject + message when closing a non-closeable PO
- **Key:** `b6brl8r9c58` · title "Close Guard — block close on non-closeable PO"
- **Active version ID:** `368982201729024` (enabled=true, current=true).
- **Why:** the Close PO workflow is a **post-action** event and can't show a failure message; a Close attempt on a `received` PO previously saved `close_reason`/`close_comment` and silently did nothing (no message). The PO immutability guard `xvcsdv07c5j` only covers `completed`/`closed`, leaving `received` as a silent gap. This guard fills it.
- **Type:** request-interception (Pre-action Event), global, sync; actions: `update` on `purchase_orders`.
- **Nodes (4):** `close_guard_query` (query purchase_orders, multiple=false, filter id=`{{$context.params.filterByTk}}`, failOnEmpty=false) → `close_guard_cond` (condition, basic, **AND**, rejectOnFalse=false) of: `notEqual {{$context.params.values.close_reason}} != null` (a close attempt — same `values.<field>` pattern as the Receive guard, so it does NOT fire on a normal edit that omits `close_reason`) **AND** `{{$jobsMapByNodeKey.close_guard_query.status}}` ≠ each of `draft`/`sent`/`confirmed`/`partially_received` (i.e. status NOT in the closeable set) → br=1 (true=block): `close_guard_msg` (response-message) → `close_guard_end` (end, -1).
- **Logic verified** via `flow-nodes test`: close attempt on `received`/`completed` → block; close attempt on `sent`/`draft` → allowed; normal edit (no `close_reason`) on `received` → allowed (no false-block). **D24 bulk-update limitation applies** (relies on `filterByTk`). For `completed`/`closed` this guard and `xvcsdv07c5j` both fire (redundant, harmless).
- **Caveat:** detection keys on `close_reason` being present in the submitted values. If a future PO **edit** form includes a non-empty `close_reason` field on a `received` PO, it would be blocked — keep `close_reason`/`close_comment` out of the normal edit form (they belong to the Close popup only).

### Complete PO workflow (MVP9d; D34 invoice gate) — `received → completed`
- **Key:** `qh7b3hc5q1r`
- **Active version ID:** `368971625791488` (enabled=true, current=true) — **D34 revision built 2026-06-09: Complete now also requires an attached invoice AND a positive invoice total (USD).** Revision of `368746204954624` (now disabled — see Stale IDs). The predecessor's recorded `executed:0` was stale; `versionStats.executed` was 3 (user's C1 runs completed PO-26-0002/0005), so the change required a same-key revision, not an in-place edit.
- **Type:** custom-action, sync, collection `purchase_orders`. **Trigger appends:** `["invoice"]` (D34 — so the guard can see the attachment; `invoice` is a `belongsToMany` to `attachments`, loads as `[]` when empty).
- **Nodes (8):**
  - `complete_guard` (root; condition, **basic**, AND of `equal {{$context.data.status}} == "received"` **and** `gt {{$context.data.total_usd}} > 0`, rejectOnFalse=false). Basic engine chosen for these two because it returns `false` (not an error) when `total_usd` is null — math.js throws on `null > 0`.
    - br=0 (false) → `complete_fail_msg` (response-message, "Complete is only available for a fully-received PO with an invoice total (USD).") → `complete_fail_end` (end, -1).
    - br=1 (true) → `inv_count`.
  - `inv_count` (calculation, **math.js**): `count({{$context.data.invoice}})` → number of attached invoice files (`[]`→0).
  - `complete_invoice_guard` (condition, **math.js**, `{{$jobsMapByNodeKey.inv_count}} >= 1`, rejectOnFalse=false). math.js used because the basic engine has **no array-emptiness calculator** (`empty`/`notEmpty` are unregistered) and math.js resolves `{{$jobsMapByNodeKey.<key>}}` without `.result`.
    - br=0 (false) → `complete_inv_msg` (response-message, "An invoice attachment is required to complete this PO.") → `complete_inv_end` (end, -1).
    - br=1 (true) → `complete_update` (update `purchase_orders` where id=`{{$context.data.id}}`, status=completed, completed_at=now).
- **Engine split rationale (verified via `flow-nodes test`):** basic has no empty-check + can't count arrays; math.js can't string-compare (`"a"=="b"` → "Cannot convert to number") and errors on `null > 0`. So: string/scalar/null-safe checks (status, total_usd) → basic; array count → math.js. `count()` parses object-array literals fine.
- **Button (BUILT by user — `e60dce0bb2d`):** `RecordTriggerWorkflowActionModel` on the PO detail block `g9xffr68350`, bound to key `qh7b3hc5q1r`. **Linkage rule `us98o7djgw0`** (single `$or`, action=hidden) — hides the button unless completable: hidden when `ctx.record.status $ne "received"` OR `ctx.role $notIncludes "Procurement"` OR `ctx.record.invoice $empty` OR `ctx.record.total_usd $empty` (D34 added the last two; block renders `invoice`/`total_usd` so `ctx.record` carries them). The guard is the hard stop; the button just mirrors it. **Note:** linkage `$empty` won't catch `total_usd == 0` (a value); the server guard's `> 0` does.
- **Verification:** node logic validated via `flow-nodes test`; **end-to-end C1 re-verification PENDING** (user drives the Complete button — custom-action can't be `workflows execute`'d without a user, per `feedback_custom_action_execute_no_user`).

### Guard: PO Immutability (MVP9d) — lock terminal PO header
- **Key:** `xvcsdv07c5j`
- **Active version ID:** `368747670863872` (enabled=true, current=true) — built 2026-06-07, verification pending.
- **Type:** request-interception, global, sync; actions: `update` + `destroy` on `purchase_orders`. Mirrors PR Guard A.
- **Nodes (4):** `po_imm_query` (query purchase_orders, multiple=false, filter id=`{{$context.params.filterByTk}}`, failOnEmpty=false) → `po_imm_cond` (condition, basic, OR `equal {{$jobsMapByNodeKey.po_imm_query.status}}` against `completed`/`closed`, rejectOnFalse=false) → br=1: `po_imm_msg` (response-message, "This PO is finalized and can no longer be edited.") → `po_imm_end` (end, -1).
- **D24 bulk-update limitation applies** (relies on `filterByTk`; bulk update via `filter.$and[0].id.$in` bypasses it) — documented, not fixed (C5). **Payment caveat:** see D33.

### Guard: PO Line Immutability (MVP9d) — lock lines of a terminal PO
- **Key:** `f3dkb37te22`
- **Active version ID:** `368747750555648` (enabled=true, current=true) — built 2026-06-07, verification pending.
- **Type:** request-interception, global, sync; actions: `update` + `destroy` on `po_lines`. Separate from the 9c Receive Guard (`mhfp4d15uee`, which only blocks `received_quantity` on non-receivable POs).
- **Nodes (4):** `line_imm_query` (query po_lines, multiple=false, filter id=`{{$context.params.filterByTk}}`, **appends `[purchase_order]`**, failOnEmpty=false) → `line_imm_cond` (condition, basic, OR `equal {{$jobsMapByNodeKey.line_imm_query.purchase_order.status}}` against `completed`/`closed`, rejectOnFalse=false) → br=1: `line_imm_msg` (response-message, "Lines of a finalized PO can no longer be edited.") → `line_imm_end` (end, -1).
- Workflow-internal updates (9c receiving recompute) bypass request-interception (`feedback_request_interception_scope`), so receiving is unaffected.

### Receive Guard (MVP9c) — block receiving against a non-receivable PO
- **Key:** `mhfp4d15uee`
- **Active version ID:** `368072131870720` (enabled=true, current=true) — built + verified 2026-06-07 (R4 passed).
- **Type:** request-interception, global, sync; actions: `update` on `po_lines`.
- **Node chain (4 nodes):** Query line+parent PO (`567k7v8jzsi`, filter id=`{{$context.params.filterByTk}}`, appends `[purchase_order]`) → Condition (`74kymxgok4k`, basic, **AND** of 5 `notEqual` leaves: `received_quantity` present (`{{$context.params.values.received_quantity}} != null`) AND PO.status ≠ each of sent/confirmed/partially_received/received) → br=1 (true=block): response-message (`9c4j0rzf24t`) → end (`03fvl5yb4vy`, endStatus −1).
- **Design note:** blocks only when the submitted values carry a non-null `received_quantity` AND the PO isn't receivable — so editing a `draft` PO's lines stays allowed *provided `received_quantity` is empty on that form*. Bulk-update caveat (D24) applies. Workflow-internal update nodes bypass this guard (`feedback_request_interception_scope`).

### PO Receiving recompute workflow (MVP9c) — derive line_status + PO header
- **Key:** `ork27v016yo`
- **Active version ID:** `368710576439296` (enabled=true, current=true) — **doc-lag corrected 2026-06-07** (was recorded `368072534523904`; a later user revision is now active). R1–R3 verified on the lineage.
- **Type:** collection event, **sync**, collection `po_lines`; **mode=2 (update), `changed:["received_quantity"]`** (loop guard — the workflow's own line_status/header writes don't re-fire), appends `[purchase_order]`.
- **Node chain (10 nodes):**
  - `nys8gwon5ic` (calculation, **formula.js**) → `line_status` = `IFS(AND(quantity_ordered>0, received_quantity>=quantity_ordered),"received", received_quantity>0,"partially_received", true,"pending")` (reads `{{$context.data.*}}`).
  - `dbaahktlgww` (update po_lines, batch/`individualHooks:false`) → write `line_status={{$jobsMapByNodeKey.nys8gwon5ic}}` to the trigger line (`id={{$context.data.id}}`).
  - `b8bd5brza19` (aggregate count, **A**) → po_lines where `purchase_order.id=<PO>` AND `line_status != received`.
  - `jsj8bqoihag` (aggregate count, **B**) → po_lines where `purchase_order.id=<PO>` AND `received_quantity > 0`.
  - `y7lkvu5cxkx` (condition, **math.js**, rejectOnFalse=false) `{{$jobsMapByNodeKey.b8bd5brza19}} == 0` (all received?):
    - br=1 (true): `913yhkkni8r` Update PO `status=received` → `9wr1evj9pjj` Query Procurement dept (id `363554444476416`, appends `[main_approver]`) → `7421bepct6m` Notification (channel `approval-todo-in-app-message`, receivers `["{{$jobsMapByNodeKey.9wr1evj9pjj.main_approver.id}}"]`=Pat, `ignoreFail:true`, "PO {{po_number}} is fully received and ready to complete.").
    - br=0 (false): `7sncivamuep` (condition, **math.js**) `{{$jobsMapByNodeKey.jsj8bqoihag}} > 0` (any receipts?):
      - br=1 (true): `9tot1o6z03u` Update PO `status=partially_received` (covers R1 + R3 reverse).
      - br=0 (false): no node — header unchanged.
- **Verification status:** line_status formula + both math.js conditions validated via `nb api workflow flow-nodes test`; full R1–R4 passed end-to-end via the user-built receiving UI 2026-06-07.

---

## Test users

| Username | ID | Main dept | Roles (besides member) |
|---|---|---|---|
| alice.member | 9 | Operations (363554454962178) | operations (via dept) |
| oliver.owner | 10 | Operations (363554454962178) | operations (via dept) |
| pat.procurement | 11 | Procurement (363554444476416) | procurement |
| dana.director | 12 | Director (363554454962176) | director |
| simon.supervisor | 13 | Operations (363554454962178) | operations (via dept; not shown in users.roles append — dept-inherited at runtime) |

| fiona.finance | 14 | Finance (363554454962177) | finance (via dept; not in users.roles append — dept-inherited at runtime). Created Phase 2 (D40), password `Test1234!` |

---

## Roles & ACL (hardened 2026-06-11, phases 0–1 — D38)

- **roleMode:** `allow-use-union` (each session still runs on ONE selected role; union is an option in the user-menu role switcher).
- **member** (base, default): snippets `["!pm","!pm.*","!ui.*"]` (vanilla, `ui.*` workaround reverted), strategy `{"actions":["view"]}` — view-only everywhere.
- **director**: strategy `{"actions":["view"]}` + independent `purchase_requests` row: view (all 37 fields) + **render-enabler** update (2 fields: `rejection_reason_category`,`rejection_comment`; scopeId 10 "PR — director stage"). Needed so the approval ProcessForm renders (see CLAUDE.md rule / auto-memory).
- **operations** (NEW, bound to Operations dept `363554454962178` via `departments.roles`): no strategy; independent rows: `purchase_requests` view(37) / create(19) / update(19, scopeId 2 "PR — own and editable"); `attachments` view+create. Desktop routes: same 11 as member. Create/update field list = the 18 submitter fields + `quoted_total_usd` (display in forms; server recomputes).
- **procurement**: strategy `view/trigger/update` (unchanged); independent rows rewritten: `purchase_requests` view(37)/update(22, excludes status+stamps)/trigger/triggerNew/export(37) — **create + importXlsx REMOVED (D25 now enforced)**; `purchase_orders` view(31)/create(16)/update(16, excludes status/po_number/stamps/total_usd/purchase_request-relink)/destroy/trigger; `po_lines` view(12)/create(5)/update(5, excludes line_status)/destroy; `attachments` + `suppliers` rows untouched (pre-existing, working — note their scopeId `363334209503233` is a dangling reference that behaves as all-rows).
- **finance** (**Phase 2 / D40, 2026-06-11**): `null` strategy; independent `purchase_requests` row: view (all 37 fields) + **render-enabler** update (2 fields: `rejection_reason_category`,`rejection_comment`; scopeId 10) — mirror of director's row. Desktop routes: same 11 as member (was zero). User: fiona.finance (14, via Finance dept binding). No finance approval stage exists yet — groundwork for the payment MVP.
- **Scopes** (`rolesResourcesScopes`): 2 "PR — own and editable" (**fixed 2026-06-11**: `submitter_id`→`submitterId`; filter: status ∈ {draft,info_requested} AND (createdById|submitterId = $user.id)); 10 "PR — director stage" (NEW: status ∈ {pending_director_approval,pending_board_approval}); **3, 6–9 still contain snake_case FK columns and will 400 if bound — fix before first use.**
- **Workflow-managed columns** (`status`, `approved_at`, `cancelled_at`, PO stamps, `po_number`, `line_status`) are now enforced read-only via ACL field whitelists per user preference (D38) — no longer reliant on form `readPretty` only. Strategy-view roles can read but not write them.

---

## UI

- **Purchase Requests page UID:** `cuycec133qb`
- **Table block:** `l1e2iwdwau9` — columns include title, status, quoted_total, quoted_currency, `expenditure_type`, `is_emergency`, `needed_by` (MVP8), `pr_number` (D31 — column wrapper `05rzpmr4pxk`, DisplayTextFieldModel)
- **PR view popup** (DetailsBlockModel `2b367dbd157`): shows all PR fields incl. quote fields, `needs_director_approval`, `supplier`, and the four MVP8 fields. The popup grid `5fb7b74fa30` contained an MVP8 Comments block `52t8wtbzni4` bound to `purchase_requests.comments`; the user removed it post-verification. Re-add via `nb api flow-surfaces add-block` with type `comments` and resource `{binding:"associatedRecords", associationField:"comments"}` targeting the grid.
- **Procurement approval form** (now per-revision, detached from template `k60b738pjy0`): current ProcessFormModel uid varies per workflow revision. MVP8 read-only fields applied. **D37/MVP013:** on the active revision `369161752084480` the ProcessForm grid is `03uy1easu6l` — gained **editable** `is_regular` (CheckboxFieldModel, wrapper `dcbp2xasi5f`, inner `w5v1zvd8t00`, tooltip on the regular-purchase rule). (Procurement sets `is_regular` here; the condition reads it.)
- **PR create form** (CreateFormModel `e76c40c8c79`, template `n9f8v5vnhhc`): includes `needs_director_approval` checkbox after justification; linkage rule makes justification required when checkbox is checked. MVP8 added `expenditure_type`, `needed_by`, `is_emergency`, `other_attachments` after `needs_director_approval`. **MVP010** added `skip_dept_approval` (CheckboxFieldModel, wrapper `830iodzmcjo`) — **GONE: user rebuilt the create form and dropped both `skip_dept_approval` and `needs_director_approval` from it** (discovered MVP012; the recorded wrapper IDs are stale). **D36/MVP012** added `use_custom_approver` checkbox (wrapper `r9iu06my5ot`) + `custom_approver` picker (wrapper `gfozpat06nw`, inner `RecordPickerFieldModel mu4s7d3w0h2`, selector `TableSelectModel ueeb9ybhmuc`) to grid `5c325101ecc`, with field-linkage rules (fingerprint-based) that show+require `custom_approver` when `use_custom_approver` is on and hide it otherwise. **Picker data scope (same-dept + exclude-self) is NOT set via CLI** — public authoring exposes no data scope on the record picker; set it via the form's "Set data scope" UI setting (manual). Self-approval is independently blocked in the workflow condition.
- **PR detail popup** (`2b367dbd157`): MVP010 added `skip_dept_approval` read-only (DisplayCheckboxFieldModel, wrapper `in24ndj91et`) — **removed in MVP012**. **D36/MVP012** added `use_custom_approver` (wrapper `7jjizc66ex2`) + `custom_approver` (wrapper `9tpfw54yy1e`) read-only. **D31** added `pr_number` read-only (DisplayTextFieldModel, wrapper `24fsysz731w`). **D32** added `board_approval_document` read-only on grid `16975baef39` (DisplayPreviewFieldModel, wrapper `ive719bxqm2`). **D37/MVP013** added `is_regular` read-only on grid `16975baef39` (DisplayCheckboxFieldModel, wrapper `6q8zzia1bt7`, inner `n6l48asyh9p`). The retired `needs_director_approval` read-only display (DisplayCheckboxFieldModel, wrapper `p9acb4e35of`) remains (harmless/historical).
- **Generate PO button** (`28jh1q2camo`, MVP9a): `RecordTriggerWorkflowActionModel` on PR table row popup and PR detail popup. Bound to workflow key `2izsx8uv50r`. Two linkage rules:
  - Hide when `record.status != "approved"` OR `record.purchase_order is not empty`.
  - Hide when `ctx.user.roles.title` does not include `"Procurement"` (procurement-only visibility; see [feedback_linkage_rules_user_roles](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_linkage_rules_user_roles.md) in auto-memory for the pattern).

Approval form surface IDs on the active version: see "Approval surfaces" above.

### Purchase Orders page (MVP9a/9b)
- **Page UID:** `liwmklclbnc`
- **Table block:** `vldbcvf41r6`
- **PO detail popup (DetailsBlockModel):** `g9xffr68350`; row-popup template `wp2s32qgfeg`.
- **Send PO button** (`slybgc23q1i`, MVP9b): `RecordTriggerWorkflowActionModel`, bound to workflow key `send_po` (set via `nb api resource update --resource flowModels`). Linkage: hide when `record.status != "draft"`; procurement-only (`ctx.user.roles.title` not-includes `"Procurement"`).
- **Print button** (`c579329db0d`, MVP9e): `TemplatePrintRecordActionModel` on PO detail block `g9xffr68350`, beside Send. Bound to template `kkooshlz8rf` (`props.templateName`), `convertedToPDF:true`. Renders the branded PO PDF via Carbone+LibreOffice (server-side). No linkage rules (visible to all PO viewers). See the `printingTemplates` collection + MVP9e notes below.
- **Close PO button** (`lylrxwl1b3g`, MVP9b): `PopupCollectionActionModel` — opens a popup with an EditForm bound to the current record. Form fields: `close_reason` (`qou6ge8axe5`, required) + `close_comment` (`h5872h3mc8r`, required). Submit action `5ove3dxktz9` triggers workflow key `close_po_draft`. Same draft + procurement-only linkage as Send. (Close-from-non-draft broadens this in 9d.)

---

## Stale IDs (DO NOT USE)

### Workflow versions of `cv237r8h7k9` (all disabled before the active `369495666917376`):
- `369166026080256` — user revision (hardcoded Director [12] / Board [11] assignees), superseded by the D40 data-driven revision `369495666917376` (2026-06-11). Disabled.
- `369161752084480` — the D37/MVP013 `is_regular` revision, superseded by a user revision `369166026080256` (found live 2026-06-11). Disabled.
- `369154168193024` — a **user revision** that was active immediately before MVP013 (the doc had wrongly listed `369076269481984` as active); 30 nodes. Superseded by the D37 `is_regular` revision `369161752084480`. Disabled.
- `369076269481984` — the D36/MVP012 custom-approver revision (doc-recorded active, but actually superseded by the user revision above). Disabled.
- `368983543906304` — active immediately before MVP012 (2026-06-09); 27 nodes (still had the skip branch). Superseded by the D36 custom-approver revision `369076269481984`. Disabled.
- `368641179582464` — previously (wrongly) recorded as active; superseded. Disabled.
- `367885604880384` — was the D32 board-approval active version (2026-06-02 → sometime before 2026-06-07); superseded by a later user revision `368641179582464` (current). Its approval-surface IDs (recorded in the PR Approval section above) may now be stale; not re-inspected this session.
- `367158084370432` (was active D30 $300-floor, replaced by D32 board-approval revision 2026-06-02). Its approval surfaces are now stale: trigger approvalUid `oudb91ahp0g`/taskCardUid `84gqev1gycl`; dept `x1v8vfcjrnv`/`g93one3xwn9`; procurement `1zfnz7s6in2`/`zbx9zt781mg`; director `04fmmdcx1p9`/`j5uzaf7vnnn`.
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

### Stale Generate-PO (`2izsx8uv50r`) versions (all disabled before the active `368786562547712`):
- `367255610327040` — the D31 revision (7 nodes incl. default-line create); superseded by the user's 6-node revision `368786562547712` (default-line create removed on purpose). Disabled.
- `366569458696192` — initial build with JSON-filter embedded guard.
- `366595041853440` — round-2 revision that wrongly removed the inline guard.
- `366602797121536` — interim revision.
- `366608098721792` — round-3 revision: restored guard but missed the end-process node on the false branch.
- `366623370182656` — interim user revision.
- `366623590383616` — was recorded as active through the $300-floor session; superseded by user revisions.
- `366626266349568`, `366626572533760` — later user revisions; `366626572533760` was the live active version (executed=9) immediately before the D31 revision.
- All superseded 2026-05-30 by `367255610327040` (current, D31).

### Stale Send-PO (`send_po`) versions (all disabled before `367086330314752`):
- `366981771362304` — was recorded as active through MVP9c; superseded by a later user revision `367086330314752` (current). Earlier disabled versions below.
- `366776493735936`, `366882024521728`, `366883251355648` — early build iterations.
- `366883769352192` — had the zone-2 bug (basic-engine `gt` condition that never fired).
- `366980364173312` — a revision where the agent patched the zone-2 condition with `.result` (wrong theory); superseded by the user's math.js fix in `366981771362304`.
- `366980536139776` (**key `s6m4i5hrmzs`**, title "Send PO copy") — stray duplicate; **DELETED 2026-06-11** (user OK).

### Stale Complete-PO (`qh7b3hc5q1r`) versions (disabled before `368971625791488`):
- `368746204954624` — original MVP9d build (status==received only, no invoice gate). Executed 3× (user C1 runs). Disabled 2026-06-09 by the D34 invoice-gate revision `368971625791488` (current).

### Disabled po_lines collection workflows (cancelled per D27):
- `jsgbxph9444` ("PO Total: Lines Added/Updated") and `s4syz7vom4n` ("PO Total: Line Deleted") — **DELETED 2026-06-11** (user OK, role-hardening session).

---

## Notes for the next session

- **MVP9d — DONE + VERIFIED 2026-06-09.** Complete workflow (`qh7b3hc5q1r`, D34 active ver `368971625791488`), broadened Close (`f8gpu17s6hq`), Close Guard (`b6brl8r9c58`), and the two immutability guards (`xvcsdv07c5j` PO header, `f3dkb37te22` po_lines) are live + enabled. **Complete button** `e60dce0bb2d` on PO detail block `g9xffr68350`. **End-to-end verification passed 2026-06-09** — all 8 cases green: C1 (received+invoice+USD→completed), C2 (Complete button hidden on non-received), D34a (received, no invoice→blocked/hidden), D34b (received, invoice, total_usd=0→server guard rejects), D35 (Close Guard blocks Close on `received`, close_reason never persists), C3 (Close on `sent`→closed), C4 (header edit on completed PO blocked), C5 (line edit on completed PO blocked). Verified by Pat-driven UI clicks against **API-staged throwaway fixtures** PR-26-0008..0011 / PO-26-T1..T4 (see cleanup note below). MVP9d milestone committed.
- **Test-fixture cleanup PENDING (low priority):** verification used throwaway records — PRs `PR-26-0008/0009/0010/0011` (ids 368984082874368, …874369, …874370, 368984084971520) and POs `PO-26-T1/T2/T3/T4` (ids 368984504401923, 368984531664899, 368984533762051, 368984533762055). **They can't be deleted normally** — the very guards we verified block it: PR Guard A blocks destroy on `approved` PRs; PO immutability blocks destroy on T1(closed)/T4(completed). T2/T3 (received) are deletable. To purge fully, temporarily disable Guard A + PO immutability, delete, re-enable. Left in place for now (harmless test noise).
- **MVP9e — DONE + VERIFIED 2026-06-09.** PO template printing: Carbone template record `printingTemplates:kkooshlz8rf` ("Purchase Order") → `storage/print-templates/po-template-mvp9e.docx`, Havenbeheer-branded (logo + contact letterhead, green theme). Print button **`c579329db0d`** on PO detail block `g9xffr68350` bound to it (`convertedToPDF:true`). Repo source: `templates/build_po_template.py` + `purchase-order-template.docx` + `main-logo.png`. User confirmed the live PDF (PO-26-0006) looks great; P2 (internal_notes never prints) holds. Status / expected_delivery / ref-PR were dropped from the final design per user. Gotchas saved to auto-memory `feedback_template_print_{authoring,select_label,carbone_date_format}`. The PO detail block's Close button `lylrxwl1b3g` is gone (user removed it earlier on purpose).
- **PO surface drift (FYI):** the user rebuilt the PO detail block — the doc's Close button `lylrxwl1b3g` is gone (removed on purpose). (MVP9e Print button is now configured — see above.)
- **Doc-lag corrected this session:** Send-PO active `367086330314752`, PR-Approval active `368641179582464`, Receiving-recompute active `368710576439296` (see sections + Stale IDs). The PR-Approval node/surface tables still describe `367885604880384` and were not re-inspected — refresh them next time that workflow is touched. Stray disabled PR-Approval ver `368062113775616` not re-confirmed.
- **MVP7 was descoped.** Only `suppliers` was built; `supplier_issues` and `supplier_evaluations` are postponed (D26). Don't assume they exist.
- **Supplier UI:** if a suppliers list/detail page was built during MVP7, its page UID isn't recorded here yet — capture it the next time it's touched.
- **MVP8 ACL note — SUPERSEDED 2026-06-11 (D38):** field gating is now enforced via ACL whitelists, not just form `readPretty`. See the "Roles & ACL" section above (authoritative); the old strategy table (member/director `view/update/create`) no longer applies.
- **Role hardening remaining work:** Phase 2 (data-driven approvers, D40) **built 2026-06-11 — user round-trip test PENDING** (Dana on a ≥$300 PR via the new query-node assignee; Pat on a ≥$15k board PR). Phases 3–4 + low-priority items remain specced in [HANDOFF.md](HANDOFF.md) — Phase 3 cleanup steps each need explicit user OK.
