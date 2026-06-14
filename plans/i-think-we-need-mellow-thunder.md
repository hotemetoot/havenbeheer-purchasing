# Plan — PO workflow rework: Issue-gated, draft → issued → received → completed

## Context

The PO process is changing. The PO already copies supplier / price / currency / fx-rate / total
from the approved PR via the **Generate-PO workflow** (`2izsx8uv50r`). Going forward:

- **Procurement no longer edits the PR-copied fields** (supplier, price, currency, fx-rate, total).
  They only add **PO lines, supplier note, delivery address, internal notes**.
- **The "Send PO" action is removed** — sending happens outside the system (procurement downloads the
  PDF and emails it). The budget-overrun zone checks (`send_po` workflow) go away with it.
- **Issuing becomes the pivotal action.** A new **"Issue PO"** button validates the PO is complete
  (≥ 1 line, delivery address, supplier, currency, total) and advances `draft → issued`. The **Print**
  button (download) only appears once the PO is `issued`, so an incomplete PO can never be printed.
- **New status lifecycle:** `draft → issued → (partially_received) → received → completed`; **close is
  possible from `draft`, `issued`, or `partially_received`** (not once fully received). The `printed`
  status was rejected by the user in favour of `issued`.

### Split of responsibilities (confirmed with the user)

| Done by the **user** themselves | Built in **this plan** |
|---|---|
| Make the PR-copied PO fields **read-only on the form** (display layer) | **ACL**: remove the PR-copied fields (supplier, total, currency, fx_rate_to_usd) from procurement's PO **update** whitelist — hard server lock |
| Remove the Send action **button** from the PO surface | New **"Issue PO"** custom-action button + guarded workflow (completeness check → `draft → issued`); replaces Send |
| | **Status lifecycle** rewire: add `issued` status, allow receiving from `issued`, set close to `{draft, issued, partially_received}`; gate the Print button to `issued`+ |
| | Decommission the orphaned `send_po` workflow |

### SPIKE RESULT (2026-06-14) — templatePrint cannot be workflow-triggered or guarded

Read the trigger plugins in the container (`/app/nocobase/node_modules/@nocobase/...`):

- **Post-action (`plugin-workflow-action-trigger`)** middleware hard-stops on non-CRUD:
  `if (!["create","update"].includes(actionName)) return;`. So a post-action workflow **never fires**
  on `templatePrint`. → step 2 "advance on print via post-action" is **impossible**.
- **Request-interception (`plugin-workflow-request-interceptor`)**: global-mode config validates
  `actions` to `CREATE/UPDATE/UPSERT/DESTROY` only (joi `.valid`); local-mode requires the request to
  carry `triggerWorkflows`, which the Print button does not send. → step 3 "hard guard on templatePrint"
  is **not cleanly available**.
- **Confirmed:** PO id is at `params.values.queryParams.filterByTk` (client `runAction("templatePrint",
  {data:{queryParams:{filterByTk:...}}})`, `blockName:"details"`); custom-action "Trigger workflow"
  buttons fire fine and **can reject + message** (proven: Send `send_po`, Complete `qh7b3hc5q1r`).

**Resolution → use the plan's pre-approved fallback (an "Issue PO" custom-action button):** the hard
completeness gate and the `draft → printed` advance both live in a **custom-action workflow** behind an
"Issue PO" button (this button *replaces* Send). The **Print button** stays a pure download, made
visible only once status is `printed`+. Because a PO can only reach `printed` by passing the Issue
guard (which can reject), "you cannot print an incomplete PO" becomes a **hard** guarantee, achieved
indirectly. See revised steps 2/3/5 below.

### Key technical finding (drives the design)

The `@nocobase/plugin-action-template-print` render action (`templatePrint`, v2.1.0-beta.47) **only
streams the rendered PDF back to the browser** (`ctx.body = renderResult`, `Content-Disposition:
attachment`). It has **no ability to save the file to a record or attachment field**. That is why the
user chose "gate the existing Print button" over an auto-attach build — auto-attach would require
custom plugin/JS code for no data-integrity benefit. Procurement downloads and (optionally) drags the
PDF into the PO's `attachments` field manually.

The render action is a resource action registered on every collection (`<collection>:templatePrint`),
ACL `allow("*","templatePrint","loggedIn")`, with the record id at
`ctx.action.params.values.queryParams.filterByTk` (note the **non-standard nested path** — not the
usual top-level `filterByTk`). This shape must be honored by any guard/trigger that targets it.

---

## Build plan

### 1. Data model — `purchase_orders.status` + stamp

- **Add status value `issued`** to the `purchase_orders.status` enum (between `draft` and the
  receiving states). Keep `sent`/`confirmed` enum values for historical safety (parallel to retained
  `cancelled`) — they simply stop being produced. (User rejected `printed` in favour of `issued`.)
- **Add `issued_at` (datetime)** stamp, mirroring `sent_at`/`confirmed_at`/`completed_at`.
- CLI category: `nocobase-data-modeling`. UI result: a new "Issued" status option + an `issued_at`
  field on the PO.

### 2. "Issue PO" custom-action button + guarded workflow (replaces Send)

- **New workflow** (`plugin-workflow-custom-action-trigger`, **custom-action, sync**) on
  `purchase_orders` — same trigger type as Send (`send_po`) / Complete (`qh7b3hc5q1r`). Appends
  `[lines]` (or `[po_lines]` — confirm the o2m field name; markers use `lines`) so the guard can count.
  Node chain (mirrors Send's inline-guard shape, `feedback_inline_guard_end_node`):
  - `issue_count` (calculation, **math.js**): `count({{$context.data.lines}})` (basic engine can't
    count arrays — Complete-guard precedent `inv_count`).
  - `issue_guard` (condition): PO is **complete** AND `status == "draft"` — all of:
    `status == "draft"`, `issue_count >= 1`, `delivery_address` id not null, `supplier` id not null,
    `currency` not null, `total > 0`. Split engines if needed (basic for null/string/`> 0`, math.js
    for the count compare — see D34 engine split).
    - br=0 (false) → `issue_fail_msg` (response-message, e.g. "Cannot issue: the PO needs at least one
      line, a delivery address, supplier, currency, and a total.") → `issue_fail_end` (end, `-1`).
    - br=1 (true) → `issue_update` (update `purchase_orders` where id=`{{$context.data.id}}`,
      `status = issued`, `issued_at = now`).
- **Button** `RecordTriggerWorkflowActionModel` "Issue PO" on the PO detail block `g9xffr68350` (beside
  Print), bound by workflow key. Linkage: visible only when `status == "draft"` and procurement-only
  (`ctx.role $notIncludes "Procurement"`) — mirrors the Send button `slybgc23q1i` it replaces.
- This is the **hard completeness gate**: a PO can only reach `issued` by passing this guard, and Print
  (step 5) is hidden until `issued` — so an incomplete PO can never be printed.
- CLI categories: `nocobase-workflow-manage` (workflow), `nocobase-ui-builder` (button). The button is
  built through flow-surfaces authoring, not raw `flowModels` create (D33 / `feedback_flowmodels_raw_create_no_render`).

### 3. (folded into step 2)

The hard print gate is delivered indirectly via step 2 (Issue guard) + step 5 (Print visible only when
`issued`+). No `templatePrint` guard is built — the spike showed it isn't cleanly possible, and it is
unnecessary given the status gate.

### 4. Receiving + close — adjust the status sets

- **Receive Guard** `mhfp4d15uee` (active `368072131870720`): **add `issued`** to the receivable
  status set (currently `{sent, confirmed, partially_received, received}`) so receiving works from
  `issued`. Revision the workflow (it has executed — needs a same-key revision, never in-place; see
  `feedback_workflow_versioning`).
- **PO Receiving recompute** `ork27v016yo` (active `368710576439296`): no logic change needed (it sets
  `received`/`partially_received` from quantities regardless of prior status). Re-confirm live active
  version first.
- **Close PO** `f8gpu17s6hq` (post-action, active `368791950131200`) + **Close Guard** `b6brl8r9c58`
  (active `368982201729024`): set the closeable set to **`{draft, issued, partially_received}`**
  (currently `{draft, sent, confirmed, partially_received}` — swap `sent`→`issued`, drop `confirmed`,
  keep `partially_received`). Revision both. A PO can still be closed mid-receiving; only a **fully
  `received`** PO is no longer closeable (it completes).

### 5. UI — gate the Print button to issued+ (this IS the print gate)

- **Print button** `c579329db0d` (`TemplatePrintRecordActionModel` on PO detail block `g9xffr68350`):
  add a **linkage rule** hiding it unless `status ∈ {issued, partially_received, received, completed}`
  (i.e. issued onward — not `draft`, not `closed`) and procurement-only (`ctx.role $notIncludes
  "Procurement"`). Pattern: the Send/Complete button linkage (`$ne`/`$notIncludes` items).
  - Because `issued` is only reachable through the Issue guard (step 2), gating Print on status is the
    **effective hard gate** on "only print a complete PO" — no field-level `$empty` checks needed here.
- CLI category: `nocobase-ui-builder` (flow-surfaces). Reuse the linkage authoring path used for the
  Send/Complete buttons.

### 6. Decommission `send_po`

- The user removes the Send **button**; the **`send_po` workflow** (active `367086330314752`) is then
  orphaned. **Disable it** (with explicit user OK — reversible). Budget-zone overrun checks are retired
  with it; surface this consequence to the user explicitly. Do **not** delete versions without OK.

### 7. ACL — lock the PR-copied PO fields (server side)

- Read procurement's live `purchase_orders` **update** field whitelist (currently 16 fields, already
  excludes status/po_number/stamps/total_usd/purchase_request-relink — D38). **Remove** the PR-copied
  fields from it: `supplier`, `total`, `currency`, `fx_rate_to_usd`. Net editable on update =
  lines-adjacent + `delivery_address`, `supplier_note`, `internal_notes` (+ whatever else was already
  whitelisted minus the four).
- The user separately sets these fields `readPretty` on the form (display layer); the ACL whitelist is
  the hard server lock, consistent with D38 ("ACL field whitelists, not form readPretty only").
- Honor `feedback_acl_nested_association_id_whitelist`: do **not** strip `id` from any nested-picker
  target's whitelist while editing — only remove the four header scalars from `purchase_orders.update`.
- CLI category: `nocobase-acl-manage`. UI result: procurement can no longer save changes to
  supplier/total/currency/fx-rate on a PO (403 / silently dropped); lines/address/notes still editable.

---

## Critical files / entities

- State + IDs: [project_current_state.md](../project_current_state.md) (PO collection, Print button
  `c579329db0d`, PO detail block `g9xffr68350`, guards `mhfp4d15uee`/`b6brl8r9c58`/`xvcsdv07c5j`,
  workflows `send_po`/`f8gpu17s6hq`/`ork27v016yo`).
- Plugin source (read-only, for the action shape): `/Users/alexander/nocobase/storage/plugins/@nocobase/plugin-action-template-print/dist/server/actions/render.js`.
- Memory to honor: `feedback_workflow_versioning`, `feedback_workflow_revision_key_bug`,
  `feedback_prefer_mathjs_engine`, `feedback_inline_guard_end_node`, `feedback_request_interception_scope`,
  `feedback_template_print_*`.

## Build sequence

1. **Spike first (read-only / throwaway):** verify a workflow trigger (post-action **and**
   request-interception) can target `purchase_orders:templatePrint` and that the PO id resolves from
   `params.values.queryParams.filterByTk`. This decides steps 2 & 3 vs. their fallbacks. **Show the
   result to the user before building** — it determines the final shape.
2. Data model (step 1) — add `issued` status + `issued_at`.
3. "Issue PO" workflow + button (step 2).
4. Receive Guard + Close (Guard + workflow) status-set revisions (step 4).
5. Print button linkage → visible at `issued`+ (step 5).
6. ACL whitelist trim (step 7).
7. Disable `send_po` (step 6, explicit OK).

Each live change follows the CLAUDE.md protocol (show intended change + CLI category + expected UI
result; wait for approval; irreversible/revision steps get explicit confirmation). Always re-query
active workflow versions live before revisioning (the doc lags).

## Verification (end-to-end)

- **Re-query live active versions** of every workflow before touching it.
- **Issue gate (negative):** an incomplete PO (missing a line / address / supplier / currency / total)
  → "Issue PO" → rejected with the guard message; status stays `draft`; Print button hidden.
- **Issue gate (positive):** complete the PO → "Issue PO" → status `draft → issued`, `issued_at`
  stamped → Print button now appears → click Print → PDF downloads.
- **Receiving:** receive lines on an `issued` PO → not blocked; recompute drives
  `partially_received`/`received` as before.
- **Complete:** `received` PO with invoice + USD total → `completed` (unchanged path).
- **Close:** close allowed on `draft`, `issued`, and `partially_received`; close attempt on a fully
  `received` PO → blocked + messaged by the Close Guard.
- **ACL lock:** as procurement, editing a PO's supplier/total/currency/fx-rate → rejected/dropped;
  editing lines/delivery_address/supplier_note/internal_notes → still works.
- **Send gone:** Send button absent; `send_po` disabled; no budget-zone path reachable.
- Drive the real buttons as the appropriate user (custom-action/post-action can't be `workflows
  execute`'d without a user — `feedback_custom_action_execute_no_user`). Use throwaway fixtures, then
  clean up (guards temporarily disabled then re-verified, per the established cleanup ritual).

## Session-end bookkeeping

- New **D-entry** in [decisions.md](../decisions.md): the Issue-gated lifecycle
  (`draft → issued → received → completed`, close from `{draft, issued, partially_received}`), the
  "Issue PO" button replacing Send, Send/budget-zone retirement, the ACL field-lock, and the two spike
  findings (template-print is stream-only/no-attach; `templatePrint` can't be workflow-triggered —
  post-action is create/update-only, interception global is CRUD-only). List affected MVPs (9b Send, 9c
  receiving, 9d close, 9e print).
- Update [project_current_state.md](../project_current_state.md): new status value + `issued_at`, the
  new Issue-PO workflow + button, the revised receive/close guards, the Print button linkage,
  `send_po` disabled, the PO update ACL trim.
- Save a `feedback_*` memory for the reusable gotcha: **`templatePrint` (and other non-CRUD custom
  resource actions) cannot be targeted by post-action events (create/update only) or global
  request-interception (CRUD-only); gate via a status-advancing custom-action button instead.**
