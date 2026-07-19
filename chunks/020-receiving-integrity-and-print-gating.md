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
| Receiving guard refuses negative quantities | Over-delivery still allowed, unbounded |
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

### Phase 2 — Receiving guard: the lower bound (Rule 2)

`mhfp4d15uee` (Guard: Receive), sync request-interception on `po_lines`.

**Open question to settle first:** whether a field-level validator would
enforce this server-side at all. NocoBase `uiSchema` validators are Formily,
i.e. client-side — a negative sent straight to the API would very likely sail
past one. Verify before choosing; if confirmed client-side only, put the
bound in the guard, which already fetches the line and its parent order and
so has the ordered quantity in hand. A validator may still be worth adding on
top for the nicer in-form message, but it is not the enforcement.

New revision, same diff discipline.

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

## Out of scope

- Over-receipt tolerance/approval flow (F1 — left open by decision).
- The dangling `member` scope on `purchase_orders`/`po_lines`
  (`scopeId: 363334209503233` resolves to no row) — real, unrelated to
  receiving, worth its own look.
- `director`'s strategy-mode view grant having no field whitelist, so any
  new PO field is automatically director-visible.
