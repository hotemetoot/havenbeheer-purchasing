# PO line pricing + per-line budget hard-block

## Context

Today a PO carries a single manually-entered `total` (the supplier-invoice figure) and its
`po_lines` track only quantity/receiving — line pricing was deliberately removed in **D27**. There
is currently **no** check that a PO stays within the approved PR amount: **D46** (2026-06-14)
retired the old Send-step budget zones and replaced Send with an `issue_po` completeness gate.

The user wants to itemize the PO — each line gets a **unit price** and a **line total**, so the
**PO total is built up from its lines** — and to **hard-block** any line that would push the line
sum over the **approved PR amount, in the PR's own currency** (SRD 10000 blocks at SRD 10000, EUR
400 at EUR 400 — never USD).

### Why per-line (not issue-gate + freeze)
A check only at the Issue gate would let procurement add lines *after* issuing and print an
over-budget PO, so the lines would have to be frozen after issue — which makes legitimate
corrections (wrong item name, small price error) impossible without revert-to-draft churn.
Enforcing the ceiling at **line create/update** instead keeps the invariant
`sum(line_total) ≤ approved` true continuously, needs **no freeze**, and leaves the PO editable for
corrections (editing a name never changes the total; only an edit that actually breaches the budget
is blocked). The one thing per-line gives up — "printed == final snapshot" — is handled with a
**`needs_reprint` flag** rather than locking.

### Decisions baked in (from user)
- **Itemize:** `po_lines` get `unit_price`; a **new** PO field sums the lines. The existing `total`
  (invoice figure) is left untouched. (Reverses part of D27.)
- **Enforcement:** per-line hard block at create **and** update. (Partially reverses D46.)
- **Currency:** single PO currency; block expressed in PR currency (no USD/FX — see below).
- **Post-issue edits:** allowed, but set a **`needs_reprint`** flag so a stale printed PDF is visible.

### The currency question is already solved
PO `currency`/`fx_rate_to_usd` are copied from the PR and ACL-locked read-only (D46), so
`PO.currency == PR.quoted_currency` always. The budget check is therefore a **pure same-currency
comparison** — `sum(line_total) ≤ PR.quoted_total` — with **no FX conversion**. The ceiling is
`PR.quoted_total` (PR amount in its own currency), not `quoted_total_usd`.

## Pre-flight (read-only, do first)
Per CLAUDE.md, **re-query active workflow versions live** (`workflows` filter
`{"current":true,"enabled":true}`) before touching any workflow — the state doc lags. Confirm live
keys/versions for `issue_po`, `polncreateg1` (line-create terminal guard), `f3dkb37te22` (line
update/destroy terminal guard), `ork27v016yo` (receiving recompute). Don't use any "Stale IDs".

Also verify two NocoBase specifics that shape the build (model on the receiving recompute
`ork27v016yo`, which already aggregates across lines):
- whether `line_total` (formula) is a stored or virtual column — drives whether sums use the field
  or recompute from `quantity_ordered * unit_price` (real columns);
- that two request-interception workflows can coexist on `po_lines:create`/`:update` (existing
  terminal guard + new budget guard) and that the first to reject wins.

## Changes

### 1. Data model (`nocobase-data-modeling`)
- **`po_lines.unit_price`** — decimal, PO currency, nullable. Add to Procurement's `po_lines`
  **create + update** field whitelist.
- **`po_lines.line_total`** — formula `{{quantity_ordered}} * {{unit_price}}` (same-record, so a
  formula field works here). Read-only, display.
- **`purchase_orders.lines_total`** — **new** decimal, the sum of `quantity_ordered * unit_price`
  across the PO's lines, maintained by the recompute workflow below. Read-only, workflow-written
  (not in any role whitelist). Label e.g. "PO Total (from lines)". This is the figure the budget
  guards compare against the ceiling.
- **`purchase_orders.total`** — **unchanged**. Stays the supplier-invoice figure (prefilled from PR
  at generation, ACL-locked read-only per D46); `total_usd` and the Complete gate (`total_usd > 0`)
  keep working off it. The new `lines_total` lives alongside it — ordered-from-lines vs invoiced are
  intentionally distinct.
- **`purchase_orders.needs_reprint`** — boolean, default false, workflow-maintained (not in any
  role whitelist).

### 2. Recompute + reprint-flag workflow (`nocobase-workflow-manage`)
New **collection-event** workflow on `po_lines`, scoped to **composition changes** (create,
destroy, or update touching `quantity_ordered`/`unit_price` — **not** `received_quantity`, so it
never collides with receiving). Modelled on `ork27v016yo`:
- Recompute `purchase_orders.lines_total = Σ(quantity_ordered * unit_price)` for the parent PO.
  (Leaves the existing `total`/invoice field untouched.)
- If parent `status != draft` (i.e. already issued), set `needs_reprint = true`.

### 3. Per-line budget guards (`nocobase-workflow-manage`)
Two dedicated **request-interception** workflows (sync, global). Keep the existing terminal guards
(`polncreateg1`, `f3dkb37te22`) **as-is** — they still block edits on `completed`/`closed`; these
new guards add the budget concern only.

**Create guard — `po_lines:create`:**
- Parent FK from `{{$context.params.values.purchase_order}}` (already injected via the add-line
  form Submit's assign-field-values, D45 — covers both create routes).
- Query PO (+ `purchase_request`) → `quoted_total`, `quoted_currency`.
- `existing_sum` = Σ over the PO's current lines of `quantity_ordered * unit_price`
  (query lines + math.js sum; arithmetic in its own calc node — condition nodes can't do math).
- `new_total = existing_sum + (values.quantity_ordered * values.unit_price)`.
- Condition `new_total > quoted_total` → response-message in PR currency (e.g. "Line would bring
  the PO to {new_total} {currency}, over the approved {quoted_total} {currency}.") → end-process
  `endStatus:-1`. Keep `failOnEmpty:false`/`rejectOnFalse:false` so a missing FK fails open.

**Update guard — `po_lines:update`:**
- **Skip** when the update carries neither `quantity_ordered` nor `unit_price` (received_quantity /
  line_status writes pass straight through — receiving unaffected).
- Read the edited line via `{{$context.params.filterByTk}}` → stored qty/price + parent FK.
- `existing_sum_excl_self` = Σ qty*price over the PO's **other** lines (id != this line).
- Coalesce: `eff_qty = values.quantity_ordered ?? stored`, `eff_price = values.unit_price ?? stored`.
- `new_total = existing_sum_excl_self + eff_qty * eff_price`; block if `> quoted_total`.
- **This is the fiddly node chain** (exclude-self + coalesce partial updates) — test thoroughly.

> Destroy needs no budget guard (sum only decreases); the existing terminal guard still covers
> completed/closed.

### 4. Issue gate (`issue_po`) — minor (`nocobase-workflow-manage`)
Revise (new same-lineage revision; never edit in place). Keep all completeness checks; **add**
"every line priced" (`unit_price > 0`) so an unpriced line can't slip through as 0. On successful
issue, set `needs_reprint = false`. No budget check needed here (per-line guards already guarantee
the ceiling) — optionally add a cheap `Σ ≤ quoted_total` backstop.

### 5. Reprint affordance (`nocobase-ui-builder`)
- Surface `needs_reprint` on the PO detail (a "Reprint needed — lines changed since issue"
  indicator), shown via linkage when `needs_reprint == true`.
- Add a small **"Mark reprinted"** custom-action button (visible only when `needs_reprint == true`)
  that sets `needs_reprint = false`. (Template-print is non-CRUD and can't be workflow-hooked or
  write to the record — per `feedback_noncrud_action_workflow_triggers` — so the clear is a manual
  acknowledgement after reprinting.)
- Print PDF template: add line `unit_price` + `line_total` columns and the PO `total`.

## Verification (end-to-end, live)
1. Add `unit_price` to lines → `line_total` and PO `lines_total` update; existing `total`/`total_usd`
   (invoice) untouched.
2. Create a line within budget → allowed; one that breaches → blocked with the **PR-currency**
   message (test an SRD PO and a EUR PO; confirm amounts are never USD-converted).
3. Edit a line: price up within budget → allowed; up beyond → blocked; price down → allowed; edit
   description/name only → allowed (total unchanged).
4. Post a `received_quantity` → not blocked by the budget guard; receiving recompute `ork27v016yo`
   still advances status.
5. Issue with an unpriced line → blocked; all priced & within budget → issued, `needs_reprint=false`.
6. After issue, edit a line → `needs_reprint` flips true and the indicator shows; "Mark reprinted"
   clears it.
7. Confirm the terminal guards still fire (edit on completed/closed blocked) alongside the budget
   guard — i.e. interception stacking works.

`flow-nodes test` only validates calculation/condition nodes; verify query/aggregate nodes via live
data readback. `issue_po` (custom-action) can't be `workflows execute`d (no user) — drive the real
Issue button.

## Session-end bookkeeping
- New **D-entry** in `decisions.md`: re-introduce `po_lines` pricing (reverses D27) and a **per-line**
  budget hard-block in PR currency at create/update (partially reverses D46), with `needs_reprint`
  in place of freezing. Record the rationale (correctability over snapshot-lock). Affected
  downstream: PO printing (price columns + reprint indicator), Payment MVP, MVP9b notes.
- Update `project_current_state.md`: new fields, recompute/reprint workflow, the two budget guards,
  revised `issue_po` version.
- Commit after each verified phase.
