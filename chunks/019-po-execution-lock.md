# 019 — PO is execution only: lock the approved terms, freeze line prices at issue

**Status:** drafted 2026-07-18, not built
**Depends on:** D46 (PR-copied fields locked on update), D52 (Issue-gate budget cap), D81 (line destroy blocked once issued), D82 (admin-exempt lock guards)

## The rule in plain language

A purchase order is the execution of an approved purchase request. You can only
order **what** was approved, from the **supplier** that was approved, in the
**currency** that was approved, up to the **amount** that was approved.

Two consequences:

1. The PR-copied terms — supplier, currency, total, FX rate — are set by the
   Generate PO workflow and by nobody else, at any status, including draft.
2. Once a PO is **issued**, its line quantities and prices are frozen. Issuing
   becomes a formal act: the numbers on the printed document the supplier
   receives are the numbers the system holds, permanently.

Receiving still works — `received_quantity` stays writable.

## Why

**The budget cap only runs once.** `issue_po` aggregates `Σ(line_total)` and
rejects if it exceeds the PR's `quoted_total` (D52 Part A). Today procurement
can issue a PO at $9,000 against a $10,000 PR, then edit a line's `unit_price`
up to $15,000, then print it. Nothing re-checks. The chokepoint D52 built is
only a chokepoint if the numbers can't move afterwards.

**The printed PO has left the building.** Once issued, the PDF has gone to the
supplier. If the stored line differs from the paper, receiving and invoice
matching compare against the wrong numbers and nobody can say which version is
authoritative.

**It finishes a job already two-thirds done.** Adding a line after issue is
already blocked (import button hidden on non-draft + the D47 per-line create
guards). Deleting a line after issue is already blocked (D81, guard
`v61hc3ou3pa`). Editing a line is the only one of the three still open, and it
is the largest hole of the three.

**No escape hatch, deliberately.** Alexander's call 2026-07-18. If a supplier
changes a price after issue, the answer is close the PO and generate a new one.
Admin retains the ability to fix mistakes (all lock guards exempt admin, D82).
A "Revert to Draft" button was discussed and explicitly deferred — add it only
if the freeze turns out to bite in practice.

## What changes vs. what stays

**Changes:**
- Procurement can no longer set `supplier`, `currency`, `total`,
  `fx_rate_to_usd`, or `issued_at` when *creating* a `purchase_orders` record.
  (They already can't on update — D46.)
- Procurement can no longer change a PO line's `quantity_ordered` or
  `unit_price` once the parent PO has left `draft`.

**Stays:**
- Generate PO keeps working untouched. Workflow create nodes bypass ACL, so
  removing those five fields from procurement's create whitelist does not
  affect the workflow that actually creates POs.
- Receiving keeps working — `received_quantity` is not covered by the freeze.
- Procurement still edits `delivery_address`, `supplier_note`,
  `internal_notes`, invoice and payment fields on an issued PO.
- Lines remain fully editable while the PO is `draft`.
- Admin bypasses the new guard, as with every lock guard (D82).

## Expected UI result

- On a **draft** PO, the Line Items sub-table behaves exactly as today.
- On an **issued** (or later) PO, editing a line's Quantity or Unit Price and
  saving shows a rejection: *"Cannot change quantity or price once the PO has
  been issued."* The line is not saved.
- Entering a received quantity on the same line still saves normally.

## Verified live state (2026-07-18, before any change)

| Fact | Value |
|---|---|
| `procurement` / `purchase_orders`, `usingActionsConfig` | `true` — whitelists are real, not strategy mode |
| update whitelist | `attachments, close_comment, close_reason, delivery_address, expected_delivery_date, internal_notes, invoice, lines, payment_date, payment_status, supplier_note` — D46 confirmed applied |
| create whitelist | **still contains** `supplier`, `currency`, `fx_rate_to_usd`, `total`, `issued_at` — this is the gap |
| ACL resource record | data-source-resources id `366562898804736` |
| Generate PO | id `368786562547712`, key `2izsx8uv50r`, create node `ubg9mju1tjm` |
| Generate PO copies | `supplier` ← PR `supplier.id`; `currency` ← PR `quoted_currency`; `total` ← PR `quoted_total`; `fx_rate_to_usd` ← PR `fx_rate_to_usd` |
| Existing destroy guard | `Guard: PO Line Destroy — block once PO issued`, id `375767284252672`, key `v61hc3ou3pa` — the shape to copy |
| Existing update guard | `Guard: PO Line Immutability`, id `375761900863488`, key `f3dkb37te22` — bites only on `completed`/`closed`; stays as-is |
| PO create guard | `Guard: Create PO (PR must be approved)`, id `366562380808192`, key `vgv8hcrtjvx` — blocks a create whose PR is missing or unapproved, or which already has a PO |
| `purchase_orders.status` enum | `draft` Draft, `issued` Issued, `partially_received` Partially Received, `received` Received, `completed` Completed, `closed` Closed |

## Re-verified live 2026-07-18 (second drift pass, before building)

Three corrections to the table above, all found by `nb-drift-scout`:

1. **The two guard ids were stale.** Both workflows were revised on 2026-07-16;
   the ids originally written here (`373256900640768`, `368747750555648`) are
   now disabled predecessors. Corrected above. The node *shapes* are unchanged,
   so the pattern this chunk copies is still accurate.

2. **The Phase 1 prerequisite FAILED — a direct-create surface exists.** The
   Purchase Orders page (route `366560025706496`) has a hidden tab "All POs"
   (route `366560025706497`) holding a `purchase_orders` table (uid
   `vldbcvf41r6`) with an **Add new** button (uid `2t0335tmfkf`, popup template
   `n0hoz6l1jzf`). No hide rule; procurement can reach the route.

   The hole is narrower than it first looked, because `vgv8hcrtjvx` already
   blocks a create with no PR or an unapproved PR — verified empirically, not
   just by reading the condition. What is **not** blocked: pick a genuinely
   approved PR, then type your own supplier, currency, total and FX rate. The
   guard passes it (PR approved, no PO yet) and the record consumes that PR's
   one-and-only PO slot. That is exactly the hole Phase 1 closes.

   The popup form shows `purchase_request` (not a required field — the guard is
   the only enforcement) and does **not** show `po_number`, so a manual PO would
   have no number at all.

   **Alexander's call 2026-07-18: remove the Add new button.** POs come from the
   Generate PO button on an approved PR and nowhere else. Added as Phase 1b.

3. **Phase 2's stated risk does not exist.** Execution history across
   `mhfp4d15uee` (37 runs) and `c9c14tyn876` (71 runs), spanning 2026-07-03 to
   2026-07-18, shows every real receive submitting exactly one key:
   `{"received_quantity": N}`. `quantity_ordered` never co-occurs with
   `received_quantity` in any payload; line edits are always separate requests.
   A presence-based condition is therefore safe and the fallback design
   (compare submitted-vs-stored) is not needed.

## Phases

### Phase 1 — Close the create-whitelist gap
Remove `supplier`, `currency`, `fx_rate_to_usd`, `total`, `issued_at` from
`procurement`'s **create** field whitelist on `purchase_orders`.

**Prerequisite check: DONE, and it failed** — a direct-create surface exists.
See correction 2 above. Handled by Phase 1b rather than by re-scoping.

**Verify:** re-read the whitelist; then run Generate PO on an approved PR as
procurement and confirm the resulting draft PO still carries supplier,
currency, total and FX rate.

**Rollback:** re-add the five field names. Trivially reversible.

### Phase 1b — Remove the Add new button on the PO table
Delete the `AddNewActionModel` (uid `2t0335tmfkf`) from the "All POs" table
block (uid `vldbcvf41r6`) on route `366560025706497`.

Without this, Phase 1 leaves a button that can still create a blank, numberless
PO which permanently consumes an approved PR's one PO slot — a worse failure
than the one being fixed, because it is silent.

**Rollback:** rebuild the button in the UI (it is a stock Add new action; the
popup template `n0hoz6l1jzf` is a separate record and is not deleted here, so
the form layout survives). Record the full action config before deleting.

### Phase 2 — New guard: freeze line quantity and price at issue
New `request-interception` workflow on `po_lines`, action `update`.

Node chain, following the D81 destroy-guard shape:
1. **Admin-exempt head** (2 nodes, D71/D63 pattern) — look up the caller's
   roles; run the rest only if not root/admin.
2. **Query parent PO** by the line's `filterByTk`, appending `purchase_order`.
3. **Condition** — reject when the parent PO's `status != "draft"` **AND** the
   payload touches a frozen field: `params.values.quantity_ordered != null`
   **OR** `params.values.unit_price != null`.
4. **Reject branch** — response-message + end-process `endStatus: -1`
   (per `feedback_inline_guard_end_node`; without it the UI reports silent
   success).

Create it with `deleteExecutionOnStatus: []` (D79 — sync guards keep history or
the dispatcher race returns 500s).

Set the workflow `description` and `category` (Guards) on the record itself,
per D84.

**The risk to test first:** if the receiving form submits the whole line row
rather than just `received_quantity`, `params.values.quantity_ordered` will be
non-null on every receive and the guard will block receiving. Check the actual
receive payload before enabling. If it does submit the whole row, the condition
must compare submitted-vs-stored values instead of testing for presence.

**Rollback:** disable the workflow. Nothing else is touched.

### Phase 3 — Tests and docs
- `tests/plan.yaml`: new rule — procurement may edit a draft PO line's quantity
  and price; the same edit on an issued PO is rejected; a `received_quantity`
  update on an issued PO still succeeds. Needs the issued-PO fixture (the same
  one R18/R22/R21-delete-deny have been waiting on since D61 — build it here).
- Extend the existing PO-create ACL rule to assert the five removed fields are
  rejected on create.
- `docs/user-guide.md`: the Issue step gains a line — after issuing, line
  quantities and prices can no longer be changed. Get exact labels via
  `nb-ui-labels`.
- D-entry in `decisions.md`.

## Out of scope / open

- **`purchase_orders.fx_rate_to_usd` — RESOLVED 2026-07-18: keep it.**
  Alexander's call: probably nobody uses "Invoice Total (USD)" (`total_usd`,
  key `mtlqz3a1zks`, `{{total}} /{{fx_rate_to_usd}}`), but neither field costs
  anything to carry and both may be wanted later. No change. The rate stays in
  the create whitelist removal (Phase 1) regardless — it is copied by Generate
  PO, so procurement never needs to type it.
  The drift risk originally raised — PR rate changing after the PO copies it —
  **does not exist**: Guard A locks an approved PR against every edit, and a PO
  can only be generated from an approved PR.
- **Revert-to-Draft button.** Deferred by decision, not oversight.
- **PO header edits at non-terminal status** (D69) stay as they are; the
  D46 whitelist already covers the PR-derived terms.
