# MVP9e — PO template printing (Word → PDF)

## Context
The PO detail block already has a `TemplatePrintRecordActionModel` "Print" button (uid `c579329db0d`,
on block `g9xffr68350`, PO page `liwmklclbnc`). It is fully wired: bound to template `kkooshlz8rf`
with `convertedToPDF: true`, and the user has already verified the PDF pipeline end-to-end
(LibreOffice renders server-side inside the NocoBase image). **But the bound template is a throwaway
stub** — its `.docx` only contains `PO: {d.po_number}`, `Status: {d.status.label}`, and a `{d.lines[i]...}`
loop. MVP9e replaces that stub with a real, clean PO document that renders the proper fields, and
crucially must **omit `internal_notes`** (P2). No brand assets exist → clean default layout (decided
in the chunk, 2026-06-09).

So 9e.1 (plugin enabled) and 9e.3 (button bound) are effectively already done. The real work is 9e.2
(build the template) plus 9e.4 (verify P1–P3).

## Syntax confirmed against official docs (docs.nocobase.com/template-print)
- Data root is **`d`**; nested via dot notation `{d.supplier.address}`. ✓
- **Loops**: first row `{d.lines[i].field}` is the repeated template; a `{d.lines[i+1].field}` marker
  defines the loop end. ✓
- **Date**: `{d.expected_delivery_date:formatD(MMM D, YYYY)}` — pattern is **unquoted** (corrected from
  my earlier `'...'` form).
- **Conditionals**: `{d.field:ifNEM():showBegin} ... {d.field:showEnd}` (show when NOT empty) /
  `ifEM()` / inline `{d.field:ifEM():show(x):elseShow(y)}`. Used below to hide empty optional blocks.
- **Selects**: docs basic-usage shows no label-vs-value syntax, and the record serializes `status`/
  `currency` as plain strings already → raw `{d.status}` / `{d.currency}` is correct.
- `formatN(2)` (number, 2 decimals) is standard Carbone; will be confirmed in the local self-test and
  swapped for raw `{d.total}` if it errors.

## Key facts established from the live env
- Plugin: `@nocobase/plugin-action-template-print` (ENABLED). Engine: **Carbone** (bundled at
  `/Users/alexander/nocobase/storage/plugins/@nocobase/plugin-action-template-print/dist/node_modules/carbone`).
- Template collection: **`printingTemplates`**. The one record `kkooshlz8rf` →
  `{ title:"Test Template", collectionName:"purchase_orders", rootDataType:"map", dataSource:"main",
  filename:"17809643261187811286095403871.docx" }`.
- Template `.docx` files live on disk at **`/Users/alexander/nocobase/storage/print-templates/`**.
- **Appends are auto-derived from the template markers** at render time
  (`generateTemplateAssociationAppends`) — no manual append config needed. Whatever associations the
  template references get loaded.
- `purchase_orders` relation field names (verified): `supplier` (m2o), `delivery_address` (m2o →
  delivery_addresses), **`lines`** (hasMany → po_lines, NOT `po_lines`), `purchase_request` (m2o),
  `invoice`/`attachments` (belongsToMany). On `po_lines`: `unit_of_measure` (m2o → units_of_measure),
  `description`, `quantity_ordered`, `received_quantity`, `line_status`.
- Scalar serialization (verified on PO-26-0002): `status` and `currency` serialize as **plain strings**
  ("completed", "USD") in the record data — so use raw `{d.status}` / `{d.currency}`, NOT `.label`
  (the stub's `.label` likely rendered empty). `total` is a number; `total_usd` is a formula (number);
  `expected_delivery_date` is dateOnly; `supplier_note`/`internal_notes` are text.

## Plan

### 9e.2 — Build the PO `.docx` template (clean default)
Generate `purchase-order-template.docx` with python-docx (install into a scratch venv if needed —
build tooling only, not a project dep). Layout, all Carbone `{d....}` markers:

- **Title:** `PURCHASE ORDER`
- **Header (2-col key/value):**
  - PO Number: `{d.po_number}`
  - Status: `{d.status}`
  - Ref PR (only if present): `{d.purchase_request.pr_number:ifNEM():showBegin}Ref PR: {d.purchase_request.pr_number}{d.purchase_request.pr_number:showEnd}`
  - Expected delivery: `{d.expected_delivery_date:formatD(MMM D, YYYY)}`
- **Supplier block:** `{d.supplier.name}` / `{d.supplier.address}` / `{d.supplier.email}` / `{d.supplier.phone}`
- **Deliver to:** `{d.delivery_address.name}` / `{d.delivery_address.address}`
- **Line items table** (header row + one body row repeated by Carbone):
  `#` `{d.lines[i].description}` `{d.lines[i].quantity_ordered}` `{d.lines[i].unit_of_measure.name}`
- **Totals:** Currency `{d.currency}`, Total `{d.total:formatN(2)}`, Total (USD) `{d.total_usd:formatN(2)}`
- **Supplier note** (whole line hidden when empty, via conditional):
  `{d.supplier_note:ifNEM():showBegin}Note to supplier: {d.supplier_note}{d.supplier_note:showEnd}`  ← prints
- **`internal_notes` appears NOWHERE** (P2).

### Self-verify the markers locally (before touching the live record)
Write a throwaway Node script that `require`s the plugin's bundled Carbone and renders the new `.docx`
against a representative sample PO object (po_number, status, supplier, delivery_address, two lines,
totals, supplier_note, and an `internal_notes` sentinel like `"SECRET-INTERNAL"`). Then unzip the
output `.docx` and assert: all the real field values appear, and `SECRET-INTERNAL` does **not**. This
proves P1/P2 at the marker level without needing the server or auth. (PDF conversion stays a server
concern, already proven.)

### 9e.3 — Point the existing template record at the new file
Reuse the existing record + button (chunk: "use this button; don't create a new one"). Minimal churn:
1. Copy the new `.docx` into `/Users/alexander/nocobase/storage/print-templates/` under a fresh
   filename (keep the old stub file on disk for rollback).
2. `nb api resource update --resource printingTemplates --filter-by-tk kkooshlz8rf` setting
   `filename` → new file and `title` → `"Purchase Order"`. Leave `collectionName`/`rootDataType`/
   `dataSource` unchanged. The button already references `kkooshlz8rf`, so no button edit needed.

### 9e.4 — Verify P1–P3 (user-driven, as with prior MVP9 UI steps)
Render is a UI/ACL action (`printingTemplates:render`) not callable via the CRUD CLI, so the live
PDF check is user-driven — consistent with how 9c/9d were verified.
- **Prep (agent, before handoff):** pick a **non-terminal** PO (e.g. a `sent`/`confirmed` one — a
  terminal PO can't be edited due to the PO immutability guard) and set `supplier_note="Thank you"`
  and `internal_notes="DO NOT PRINT — internal only"` so P2 is a real test. Ensure it has ≥1 line.
- **P1:** User clicks **Print** on that PO → PDF downloads and matches the template (header, supplier,
  delivery, line table, totals, supplier note).
- **P2:** The internal-notes sentinel does **not** appear in the PDF.
- **P3:** Repeat Print on a PO in a different post-draft status (e.g. `completed` PO-26-0002) → still
  renders.

## Files / entities touched
- New: `purchase-order-template.docx` (build artifact; the canonical source copy can live in the repo,
  e.g. `templates/purchase-order-template.docx`, for future edits — optional, confirm in execution).
- New file in `storage/print-templates/` (outside the repo).
- Updated live record: `printingTemplates:kkooshlz8rf` (`filename`, `title`).
- No workflow, ACL, collection, or button changes.

## Rollback
The old stub file stays on disk; revert by pointing `kkooshlz8rf.filename` back to
`17809643261187811286095403871.docx`. Fully reversible.

## Doc updates at session end
- `chunks/009e-po-template-printing.md`: mark phases done, record final template filename + field list.
- `project_current_state.md`: record the `printingTemplates` collection, record `kkooshlz8rf` (now
  "Purchase Order"), the storage path, and the Print button `c579329db0d` binding; move MVP9e to built.
- `roadmap.md`: 009e → built/verified.
- Commit after the template is verified; commit the state-doc update at session end.
- If a NocoBase-general gotcha surfaces (e.g. auto-append-from-markers, raw-string vs `.label` for
  selects), save a `feedback_template_print_*` auto-memory.
