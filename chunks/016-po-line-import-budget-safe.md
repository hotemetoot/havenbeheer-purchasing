# 016 — PO line-item import (budget-safe)

Status: Part A built + user-verified 2026-06-27; Part B (import action + hide rule) user-built in UI; import→lines_total recompute FIXED 2026-07-18 (D83 — new async workflow `1ugka88lngm` reloads the line post-commit; old sync `5ukanitoy74` disabled). Remaining: UI import re-test (B-cases) by the user. D52, D83.

> **Lets Procurement bulk-import PO line items (useful for large orders) without opening the budget
> hole that import creates.** Import bypasses *all* `po_lines` request-interception guards — the D47
> per-line budget block **and** the D45/D46 terminal guards — so imported lines can silently push
> `Σ(line_total)` over the approved PR amount. Two complementary controls close this:
> (1) move/duplicate the budget check onto the **Issue PO gate** (the chokepoint every PO must pass to
> become printable), and (2) **hide the Import button unless the PO is `draft`**, so lines can't be
> added after issue. See decision D52.

## Background — why the existing guard isn't enough

The current budget invariant `Σ(line_total) ≤ PR.quoted_total` (same currency, PO is PR-locked) is
enforced **per line at create/update** by the D47 request-interception guards (`8u81nd3vxhc` create,
`c9c14tyn876` update). D47 deliberately chose per-line enforcement *over* an Issue-gate check
specifically to avoid having to freeze lines after issue (D47 §"Why per-line"). That reasoning assumed
**every** line-creation path passes through request-interception. **Import doesn't** — neither base
`@nocobase/plugin-action-import` nor Import Pro fire pre-action interception. So import is a new
line-creation path that escapes D47. This chunk supplements D47 (it does **not** reverse it): the
per-line guard stays for manual entry; the Issue gate becomes the net for imported lines; and the
hide-button handles the "lines added after issue" case D47 worried about.

## Goal
- A PO whose line total exceeds the approved PR amount **cannot be issued** (and therefore cannot be
  printed — Print is gated on `status ∈ {issued,…}`, D46). The Issue PO button rejects with a message.
- The **Import** button on the PO's Line Items tab is **only visible while the PO is `draft`** (and only
  to Procurement), so no lines can be imported onto an already-issued/terminal PO.

## Scope (in)

### A. Modify the `issue_po` workflow — add the budget check
- **Same-key revision** of `issue_po` (live active **`370047775735808`**, title "Issue PO copy",
  `current+enabled`; doc recorded `370019772465152` — **stale**). Force key `issue_po`; build the new
  version disabled, then enable.
- **Trigger appends:** add `purchase_request` (currently `[lines]`) so the check can read
  `{{$context.data.purchase_request.quoted_total}}`.
- **New nodes**, inserted on the all-priced **pass** branch (`x01errm96yk` br=1), *before* `issue_update`:
  - `issue_sum_lines` (aggregate **sum** `line_total` where `purchase_order.id == {{$context.data.id}}`) —
    mirrors the D47 guard's `sum_lines`.
  - `issue_over` (condition, **math.js**): `{{$jobsMapByNodeKey.issue_sum_lines}} > {{$context.data.purchase_request.quoted_total}}`
    (mirrors D47 `cond_over`).
    - br=1 (over) → `issue_over_msg` (response-message, dynamic, echoing the line total + `quoted_currency`
      and the PR ceiling) → `issue_over_end` (end, `endStatus: -1`).
    - br=0 (within budget) → `issue_update` (unchanged — `status=issued`, `issued_at=now`, `needs_reprint=false`).
  - **Rewire:** `x01errm96yk` br=1 downstream `issue_update` → `issue_sum_lines`.
- Because `issue_sum_lines` aggregates lines **live**, the check is correct regardless of whether the
  stale `lines_total` header was recomputed after an import.

### B. Add the Import action + hide rule
- Add an **Import** action to the PO popup's **Line Items** sub-table block (association
  `purchase_orders.lines`), so imported rows attach to the parent PO via the association source-id.
- **Field mapping:** `description`, `quantity_ordered`, `unit_price` (+ any other procurement-editable
  line fields). `line_total` is a formula field — do **not** import it (computes from qty×price).
- **Enable Import Pro's per-row "trigger workflow" option** on this import action (user has enabled the
  `@nocobase/plugin-action-import-pro` plugin). This fires the **collection-event** workflows per imported
  row — **Recompute A** `5ukanitoy74` (po_lines create/qty/price) refreshes `lines_total` (and would set
  `needs_reprint`, but the hide rule keeps imports on `draft` POs, where it stays false). **It does NOT
  fire request-interception** (the D47 budget guards / terminal guards never run on import), so this is
  for recompute + observability, **not** budget enforcement — control A is the enforcement.
- **Linkage rule on the Import button** (hide): visible only when **parent PO `status == draft`** AND
  role **Procurement**; hidden otherwise. Parent status read via `ctx.popup.record.status` (the same
  popup-record context the add-line Submit uses for `ctx.popup.record.id`, D45). Mirror the
  Procurement-only gating used on the Issue/Complete buttons (`ctx.role $notIncludes "Procurement"`).

## Scope (out)
- **Relying on the triggered workflow for the budget cap** — it can't enforce it (collection-event, fires
  *after* the row is written, and import never hits request-interception). The cap is control A. The
  triggered workflow only recomputes `lines_total`/`needs_reprint` and lets the user observe import
  behavior.
- **Removing the D47 per-line guards** — kept; they give instant feedback on manual entry and cover the
  manual path.
- **Revert-to-draft-on-import via collection events** — rejected in favour of the hide-button (simpler, no
  dependency on import firing collection events, which base import doesn't).
- **API/bulk hardening** — a direct API import bypasses a hidden button (same D24 bulk caveat as every
  existing request-interception guard). UI-threat-model only; not a server guarantee. The Issue gate (A)
  *is* a server guarantee and catches over-budget lines however they arrived.
- Any change to receiving, close, complete, or the PR side.

## Dependencies
- `issue_po` live active **`370047775735808`** at session start (re-verify before revisioning).
- D47 line model: `po_lines.line_total` (persisted formula), `purchase_orders.lines_total`,
  `needs_reprint`; PR-locked PO currency (D46) → same-currency compare, no USD/FX.
- Base import `@nocobase/plugin-action-import` **enabled**; `@nocobase/plugin-action-import-pro`
  **enabled** (user, this session) — needed for the per-row "trigger workflow" option.
- Collection-event recompute workflows: **Recompute A** `5ukanitoy74` (create/qty/price), **Recompute B**
  `pnvp0dtitum` (delete) — fired per row when import-trigger is on.

## Acceptance
- **B1 (manual regression):** adding a manual line that breaches the ceiling is still blocked per-line by
  D47 — unchanged.
- **B2 (import over budget → blocked at issue):** import lines onto a **draft** PO so
  `Σ(line_total) > PR.quoted_total`. Import succeeds (no per-line guard), but **Issue PO is rejected**
  with the over-budget message; PO stays `draft`; Print stays hidden.
- **B3 (import within budget → issuable):** import lines with `Σ(line_total) ≤ PR.quoted_total` → Issue PO
  succeeds → `issued` + `issued_at`; Print appears.
- **B4 (no import after issue):** on any non-`draft` PO the Import button is **hidden** in Line Items.
- **B5 (role):** Import button hidden for non-Procurement roles.
- **B6 (FK + formula):** imported rows attach to the correct parent PO (`purchase_order` set) and
  `line_total` computes from qty×price.
- **B8 (triggered recompute):** with import-trigger on, importing lines fires Recompute A per row →
  `lines_total` reflects the imported lines (no manual touch needed). Confirm it does **not** advance/alter
  PO status on a draft PO (`needs_reprint` stays false on draft).
- **B7 (issue regression):** a within-budget, all-priced, ≥1-line draft still issues; incomplete (missing
  supplier/address/currency/total≤0) and any unpriced line still reject with their existing messages.

## Phases
- **016.1** Same-key revision of `issue_po` (force key via raw `--body`; new version disabled); add
  `purchase_request` to trigger appends.
- **016.2** Insert `issue_sum_lines` (aggregate) + `issue_over` (math.js condition) + `issue_over_msg` +
  `issue_over_end`; rewire `x01errm96yk` br=1 → `issue_sum_lines`; `issue_over` br=0 → `issue_update`.
- **016.3** Verify wiring (downstream/upstream + branchIndex) and the condition via `flow-nodes test`
  (aggregate isn't test-coverable — verify via live data readback); enable new version (auto-disables
  predecessor).
- **016.4** Add the Import action to the PO popup Line Items sub-table; map fields; **enable the per-row
  "trigger workflow" option**; confirm imported rows attach to the parent PO, `line_total` computes, and
  Recompute A fires (lines_total refreshes).
- **016.5** Add the linkage hide rule (status==draft + Procurement) to the Import button.
- **016.6** User live walkthrough B1–B7 (custom-action + import can't be driven headless).
- **016.7** Docs: D52, roadmap row, `project_current_state.md` (new `issue_po` version + node keys, import
  button + linkage), this As-built.

## Risks / known traps
- **Workflow versioning** — `issue_po` has executed (D46 verified live); revision required, never edit in
  place. Force same key via raw `--body` (`feedback_workflow_revision_key_bug`); edit while disabled, then
  enable. **Rollback:** re-enable predecessor `370047775735808`
  (`resource update --values '{"enabled":true,"current":true}'`).
- **Node insertion mechanics** — generic `flow_nodes:create` does **not** auto-maintain `downstreamId`
  (D46 build note); set it explicitly on the new sequential nodes; the branch reject head uses
  `upstreamId`+`branchIndex`.
- **math.js null-safety** — if `PR.quoted_total` or the aggregate can be null/empty, math.js throws on
  `null > …`. Lines are guaranteed ≥1 and all-priced by the upstream guards, so the sum is a number; if
  `quoted_total` can be null on an edge PO, interpose an `N()` coalesce calc node (D47 precedent) or guard
  it first.
- **Import FK attachment (verify)** — confirm rows imported through the association sub-table get
  `purchase_order` set automatically from the popup record. If base import doesn't auto-set the FK, either
  require a `purchase_order` column in the template or revisit Import Pro. **Critical** — without the FK
  the rows orphan and the issue-gate aggregate misses them.
- **Linkage parent-record reference (verify)** — confirm the import button's linkage can read
  `ctx.popup.record.status`. The add-line Submit proved `ctx.popup.record.id` resolves in this popup
  context (D45). If a block-level sub-table action exposes a different context, fall back accordingly.
- **Import bypasses every `po_lines` guard** — D47 budget (`8u81nd3vxhc`/`c9c14tyn876`) **and** terminal
  guards (`polncreateg1` create, `f3dkb37te22` update/destroy). So the Issue gate (A) + hide-button (B)
  are the *only* nets for imported lines. Hiding the button on every non-`draft` status (incl.
  completed/closed) is also what keeps imports off terminal POs.
- **Per-row workflow on large imports** — with the import-trigger on, Recompute A runs once per imported
  row, which the Import Pro docs flag as added processing time / resource use on large files (and the
  recompute writes the same `lines_total` repeatedly — harmless, idempotent). Acceptable for testing; if a
  very large import drags, the trigger can be turned off and `lines_total` refreshed on the next manual
  line touch or at issue. The budget check (control A) aggregates lines live and is unaffected either way.
- **Verification is UI-only** — `issue_po` is a custom-action (no headless user,
  `feedback_custom_action_execute_no_user`) and import is UI-driven; B1–B7 need a user walkthrough.

## As built (2026-06-27)

**Part A — `issue_po` budget check (built + user-verified live):**
- Same-key revision **`370047775735808` → `372351365087232`** (enabled+current; predecessor disabled = rollback). Added `purchase_request` to trigger appends.
- 4 nodes inserted on the all-priced (`x01errm96yk` br=1) branch, before `issue_update`:
  - `kkk684uupcd` — aggregate sum `line_total` where `purchase_order.id == {{$context.data.id}}` (precision 2).
  - `hksnw304p3b` — condition math.js `{{$jobsMapByNodeKey.kkk684uupcd}} > {{$context.data.purchase_request.quoted_total}}` (rejectOnFalse false).
    - br=1 (over) → `0udjhd90ljj` (response-message, echoes total + ceiling + `currency`) → `3ba6bu5e6un` (end −1).
    - br=0 (within, ≤, empty) → converges → `issue_update`.
- Strict `>` verified via `flow-nodes test`: `10400>10000` block, `9000>10000` allow, `10000>10000` allow (== passes). User confirmed live: over-budget Issue rejected, within-budget issues.

**Part B — import action + hide rule (user-built in UI):**
- Import action on the PO popup Line Items sub-table; hidden unless PO `status==draft` + Procurement. Import Pro enabled, per-row "trigger workflow" on. `purchase_order` confirmed in Procurement's `po_lines` create whitelist.
- Imported lines attach to the correct PO (no orphans) → Part A's live aggregate counts them.

**~~PARKED follow-up~~ FIXED 2026-07-18 (D83):** import fires the `po_lines` create collection event before the association FK lands on the snapshot, so the old sync Recompute A (`5ukanitoy74`) read `$context.data.purchaseOrderId = null` and never recomputed. Fix as planned (re-query by `{{$context.data.id}}` + async), but shipped as a **new workflow** `1ugka88lngm` (id `376139238998016`) because `sync` is immutable — the server silently keeps `sync:true` on update and on revision, so the old lineage couldn't be flipped. Old workflow disabled as rollback. Live-verified via API fixture (create → 200, quantity edit → 300, execution jobs show the reloaded FK); suite 77/77 green. **Remaining:** one real UI import by the user to confirm `lines_total` updates per imported row (rolls into the B-case walkthrough).

**Decision:** D52.
