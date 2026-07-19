# Plan — 020 Receiving integrity + print gating

## Context

The 2026-07-19 exploratory pilot found three defects in the PO receiving
lifecycle that the runner's rules missed, because they live in sequences
rather than single paths. The drift scout confirmed all three are still live
and unfixed. This chunk fixes them and locks each one down with a regression
rule.

Settled before planning:
- The negative-quantity block applies to **everyone, admin included** —
  matching the Receive guard's existing stance and its own description.
- Phase 2's open question is closed, but not the way the chunk assumed.
  `uiSchema['x-validator']` really is client-only — no server package reads it
  on the write path. But NocoBase 2.x has a *second*, server-side validation
  mechanism under `field.options.validation` (Joi-backed, called by
  `Repository` on create and update). The bound goes there, not in the guard.
  See the Fields section of nb-bootstrap's `references/gotchas.md`.
- The ordered-quantity field is `quantity_ordered`, not `quantity` (the chunk
  file says `quantity`; I'll correct it).

---

## Phase 1 — Receiving recompute: the fall-back to Issued

Workflow `ork27v016yo`, live version `368710576439296`, sync, collection event
on `po_lines` changed `received_quantity`. Executed → new revision required.

**The rule:** when a correction leaves no line with anything received, the
order goes back to **Issued**. Only if it is currently in a receiving state —
an order someone already completed or closed must not be dragged backwards by
a late line edit.

**The change:** attach a new update node to the false branch (`branchIndex: 0`)
of condition `7sncivamuep` ("Any receipts logged?"), which today ends in
nothing. It writes `status: "issued"` to `purchase_orders`, filtered on
`id == {{$context.data.purchase_order.id}}` **and** status in
`["partially_received", "received"]`. Putting the guard in the filter rather
than in an extra condition node keeps it atomic — no read-then-write gap.

**Same fix on the two existing writes (approved).** `913yhkkni8r` (→ Received)
and `9tot1o6z03u` (→ Partially Received) filter on `id` alone with no status
condition, so the same late-edit problem runs in the other direction: editing
a line on a **Closed** order today silently pulls it back to Received. Both get
the identical `status $in ["issued","partially_received","received"]` filter.
Note the set differs from the new node's — a fall-back to Issued only makes
sense from a receiving state, while a climb to Received/Partially Received is
valid from Issued too. This widens the chunk's scope by one bug; it gets its
own D-entry.

Revision discipline, per D69/D75/D84 and the two more misses during 017: diff
the copy node by node **and** the workflow-level fields (`title` — the revision
appends " copy" — `description`, `sync`, `options`, `categories`). Rewrite each
edited node's config in full rather than trusting the copy.

Update the description in the same session: it currently names two outcomes,
and there will be three.

## Phase 2 — Refuse a negative quantity (field validation, not the guard)

**The rule:** a received quantity below 0 is refused. Over-delivery stays
allowed and unbounded — receiving 12 against 10 ordered keeps working, on
purpose.

**The change:** a server-side validation rule on `po_lines.received_quantity`
(field key `v5fa2gvsp0j`):

```
validation: { type: "number", rules: [ { name: "min", args: { limit: 0 } } ] }
```

The Receive guard `mhfp4d15uee` is **not touched** — no revision, no new nodes.

Why the field and not the guard: the guard is a request-interception on
`po_lines:update`, so it only fires on a direct update of that resource. Field
validation runs inside the repository, so it also catches nested writes through
`purchase_orders.po_lines`, sub-table edits, imports, and workflow update
nodes — the paths the guard structurally cannot see. Fewer moving parts and
wider coverage.

The cost is the message: Joi's `"po_lines.received_quantity" must be greater
than or equal to 0` rather than something written for Pat. Accepted. A Formily
`x-validator` can go on top later purely for a nicer in-form message, but it is
never the enforcement.

The admin question is moot — repository validation applies to every caller,
which is the answer you chose anyway.

**Execute the empirical check first**, before anything else in this phase: set
the rule, then as a signed-in test user POST `-5` (expect rejection), POST `12`
against 10 ordered (expect it to save), and POST an unrelated field update with
no `received_quantity` (expect no interference). If any of that fails, fall
back to guard nodes on `mhfp4d15uee` — condition (basic engine `lt` 0) →
response-message → end `endStatus: -1`.

## Phase 3 — Print watermark

Source `templates/build_po_template.py` → `templates/purchase-order-template.docx`;
live record `printingTemplates:kkooshlz8rf`, stored as the hashed filename
`178097646034702149965747981053.docx`.

**The rule:** a printed order that hasn't been issued carries
**"DRAFT — NOT A VALID ORDER"** on the document. `draft` is the only pre-issue
status, so that's the single trigger.

**The change:** a conditional banner paragraph at the top of the template,
`{d.status.value:ifEQ('draft'):show('DRAFT — NOT A VALID ORDER'):elseShow('')}`,
styled large and red. `status` is a select field, so it arrives as
`{value,label}` — I'll drive off `.value`, which is stable, not the label.

Not a true Word watermark shape: those live in the header as drawing XML and
Carbone can't conditionally remove one. A banner renders reliably and is
readable on a printout. If you want it diagonal across the page I can do it,
but it's meaningfully more work for the same effect.

Verify with the plugin's bundled Carbone before touching the live record, then
overwrite the **hashed** file exactly — a friendly name silently looks cached.

Button visibility by stage is a linkage rule and stays yours to build, per the
test gate. I'll write the brief.

## Phase 4 — Regression rules

Draft via `nb-test`, review, then run the full suite:
- receipts corrected to zero → status returns to Issued
- a late line edit does **not** move a Closed or Completed order (covers the
  Phase 1 extra fix, if you take it)
- negative received quantity refused
- over-delivery still accepted — recorded as a rule so nobody "fixes" it later

The watermark is a rendering outcome the runner can't check; manual verification.

## Decisions to record

- Over-delivery is allowed on purpose; only negatives are refused.
- Print is gated at the document, not the action — non-CRUD plugin actions
  can't be intercepted or ACL-denied by name, so watermark plus button-hiding
  is the whole defence, accepted as such.
- Value bounds go on the field (`options.validation`), not in a guard —
  repository-level enforcement covers nested and workflow writes that a
  request-interception guard never sees. Guards stay for rules needing related
  records or role context.
- The recompute's status writes are filtered by current status, so a late line
  edit can no longer move a Completed or Closed order (widens 020 by one bug).

## Verification

Per phase, before moving on: drive the real API as a signed-in test user, not
admin — receive against a line, correct it to zero, read the header status
back; POST a negative and check for the rejection message; POST an
over-delivery and check it still saves. Then `nb-test run` green plus your
confirmation on the UI.

## Out of scope

Over-receipt tolerance/approval flow (F1); the dangling `member` scope on
`purchase_orders`/`po_lines` (`scopeId: 363334209503233` resolves to no row);
`director`'s missing field whitelist on its strategy-mode view grant.
