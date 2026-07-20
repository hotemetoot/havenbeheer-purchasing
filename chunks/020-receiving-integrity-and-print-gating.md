# 020 — Receiving integrity + print gating

Fixes the three defects the 2026-07-19 exploratory pilot found in the PO
receiving lifecycle, plus the unguarded print path. All four were confirmed
live against the API as real signed-in users; the area's runner rules were
green throughout, because they test paths and these bugs live in sequences.

Source: `tests/reports/2026-07-19-exploratory-pilot.md` (untracked/disposable)
and the violation markers in `tests/invariants.md` (I15, I16, I17).

---

## The rules, in plain language

### Rule 1 — An order that has nothing received is not "partially received"

Today: Pat receives all 10 cleats, the order reads **Received**. She realises
the delivery note was wrong and corrects the received quantity back to 0. The
order falls to **Partially Received** — and stays there forever, showing
zero received on every line. There is no way back to **Issued**.

After: when no line has anything received, the order returns to **Issued**.
Received → Partially Received → Issued follows the receipts up *and* down.

Why it matters beyond the wrong label: the close guard's own message tells
users to "correct a received line down to revert it" — advice that currently
only works while some other line still holds a receipt.

### Rule 2 — A received quantity cannot be negative

Today: Pat can enter **-5 received**. It saves. The line displays Pending,
so the negative sits in the data silently, and any sum over received
quantities is wrong.

After: a received quantity below 0 is refused with a clear message.

**Over-delivery stays allowed** — deliberately. Suppliers do ship more than
ordered, so receiving 12 against 10 ordered must keep working. No upper
bound is added. (This is a decision, not an oversight: see the D-entry.)

**Same floor for the other money-bearing numbers** (added 2026-07-19 —
none of these is enforced today, all checked clean in live data):

- `purchase_requests.fx_rate_to_usd` — must be **above 0 when present**.
  USD totals divide by this rate; a saved 0 makes the USD total
  infinite/garbage. Empty stays allowed — one live PR has no rate, and a
  USD request doesn't need one.
- `po_lines.quantity_ordered` — above 0. A zero-quantity line is nonsense.
- `po_lines.unit_price` — 0 or more. A negative price would silently lower
  the lines total that the budget ceiling checks.
- `purchase_requests.quoted_total` — 0 or more.
- `projects.budget_usd` — above 0. A zero-budget envelope can never take a
  PR anyway; refusing it at save gives a clear message instead of a
  confusing block later.

### Rule 3 — A draft order cannot be printed as if it were real

Today: nothing server-side stops anyone with view access from printing a
purchase order at any stage, **draft included** — an order nobody has
approved for issue. Confirmed live: a plain operations user can read a PO
through the API.

After: a printed order that is not Issued (or beyond) carries a clear
**"DRAFT — NOT A VALID ORDER"** watermark on the document itself.

Why the document and not the button: printing is a non-CRUD plugin action, so
no guard can intercept it and no ACL action name exists to deny — that path
is closed to us. Hiding the button stops accidents but not a determined user.
Watermarking the artifact means that even if someone extracts a draft, the
paper cannot be passed off as a real order. **Hide the button by stage as
well** — the two do different jobs.

---

## What changes vs. what stays

| Changes | Stays |
|---|---|
| Receiving recompute gains a "nothing received" branch → status back to Issued | Received/Partially Received logic unchanged |
| Field validation refuses negative received quantities — plus floors on quantity, price, totals, fx rate, and project budget | Over-delivery still allowed, unbounded; empty fx rate still allowed |
| Print template watermarks non-issued orders; print button hidden off-issue | Anyone with view can still print an issued order |
| — | Issue freeze and budget ceiling untouched (both probed clean, 5/5 each) |

Expected UI result: correcting all receipts to zero puts the order back to
**Issued** and it behaves as a fresh issued order. Typing a negative received
quantity shows a rejection message instead of saving. Printing a draft order
produces a watermarked document.

---

## Phases

### Phase 1 — Receiving recompute: the missing branch (Rule 1)

`ork27v016yo` (PO Receiving: recompute line + header status), sync,
collection event on `po_lines` changed `received_quantity`.

Its condition chain today: "all lines received?" → Received; else "any
receipts logged?" → Partially Received; else **nothing**. The else-branch is
the bug — add the write to `issued` there.

Guard against a wrong fix: only orders currently in a receiving state should
fall back. An order that is completed or closed must not be dragged back to
Issued by a late line edit — check the parent status before writing.

Workflow has executed → new revision required. Diff the copy node by node
**and** the workflow-level fields (the revision has silently dropped clauses
three times on this project: D69, D75, D84 — and twice more during 017).
Update the workflow description in the same session; it currently describes
only two outcomes.

### Phase 2 — Value bounds via field validation, not the guard (Rule 2)

The open question is settled (see the plan and gotchas' Fields section):
NocoBase has server-side field validation in `field.options.validation` —
Joi-backed, run by the repository on create and update. It catches paths a
guard structurally can't see (nested sub-table writes, imports, workflow
update nodes), applies to everyone including admin, and needs no revision
discipline. The Receive guard `mhfp4d15uee` is **not touched**.

Set the bounds listed under Rule 2: `received_quantity` ≥ 0,
`quantity_ordered` > 0, `unit_price` ≥ 0, `quoted_total` ≥ 0,
`fx_rate_to_usd` > 0 when present, `budget_usd` > 0.

**Empirical check first, before trusting any of it:** as a signed-in test
user, write an out-of-bound value (expect rejection), an in-bound value
(expect save), an unrelated-field update (expect no interference), and —
for the fx rate — a PR with **no rate at all** (must still save; one live
PR legitimately has none). If nulls are rejected, drop the fx-rate bound
rather than break USD requests. Fallback if validation misbehaves: guard
nodes, as originally drafted.

The cost is Joi's error message ("must be greater than or equal to 0")
instead of a friendly one. Accepted; a form-side validator can be layered
on later purely for wording — it is never the enforcement.

### Phase 3 — Print watermark + button visibility (Rule 3)

Template source lives in `templates/` (`build_po_template.py`); the live
record is `printingTemplates:kkooshlz8rf`. Carbone conditional content drives
the watermark off the order's status.

Two traps already known and both project-recorded: the live file is stored
under a **hashed** filename that must be overwritten exactly, and select
fields arrive as `{value,label}` objects. Self-verify with the plugin's
bundled Carbone before touching the live record.

Button visibility by stage is a linkage rule — Alexander's build, per the
test gate.

### Phase 4 — Regression rules

Every fix becomes an `nb-test` rule so the runner holds the line: status
returns to Issued when receipts drop to zero; negative received quantity
refused; over-delivery still accepted (the deliberate allow, so nobody
"fixes" it later). Draft via `nb-test`, review, then run the full suite.

The watermark is a document-rendering outcome — not runner-checkable; it
needs a manual check.

---

## Decisions to record

- **Over-delivery is allowed on purpose.** Received may exceed ordered
  without limit; only negatives are refused. Suppliers over-ship, and
  blocking it would stop legitimate receiving. Affects: any future
  receiving work, and R22's rule text.
- **Print is gated at the document, not the action.** Non-CRUD plugin
  actions can't be guarded or ACL-denied by name, so the watermark plus
  button-hiding is the whole defence, and it is accepted as such.
- **Value bounds live on the field, not in a guard.** Record-local bounds
  go in `field.options.validation` (repository-level, covers nested and
  workflow writes, admin included); guards stay reserved for rules that
  need related records, status, aggregates, or role context. Affects: any
  future rule of the "field X can't be negative/zero" shape.

## Status — built 2026-07-19 (D91)

- **Phase 1 done**: recompute `ork27v016yo` version `376327812808704` rolls an
  emptied order back to Issued, never moves a Completed/Closed order.
- **Phase 2 done**: all six bounds live in `field.options.validation`.
  Drift found on arrival: `quoted_total` already carried "greater than 0" and
  `fx_rate_to_usd` a "minimum 1", both UI-set around May. The quoted_total
  rule was kept (stricter than the drafted ≥ 0, and right). The minimum-1
  rate rule would have refused the first euro request (~0.92 per USD under
  the local-per-USD convention) — replaced with "greater than 0" per
  Alexander. Empirical probes all passed, including the empty-rate save; the
  refusal messages turn out to use the on-screen labels ("Purchase Requests:
  FX Rate to USD must be greater than 0"), so the feared ugly-Joi-message
  cost didn't materialize.
- **Phase 3 done**: watermark confirmed by Alexander on a printed draft
  order ("DRAFT — NOT A VALID ORDER"). Button visibility by stage is his
  linkage-rule build; the watermark holds either way.
- **Phase 4 done**: R46/R48/R49 (earlier session) + R51 (the sweep, 7 cases).
  Suite green **116/116** 2026-07-19.

## Out of scope

- Over-receipt tolerance/approval flow (F1 — left open by decision).
- The dangling `member` scope on `purchase_orders`/`po_lines`
  (`scopeId: 363334209503233` resolves to no row) — real, unrelated to
  receiving, worth its own look.
- `director`'s strategy-mode view grant having no field whitelist, so any
  new PO field is automatically director-visible.
