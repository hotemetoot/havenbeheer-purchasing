# 009e — PO template printing (Word → PDF)

## Goal
Procurement clicks "Generate PDF" on a PO and gets a formatted PO document built from a `.docx` template, rendered via LibreOffice.

## Scope (in)
- Enable NocoBase Template Printing plugin.
- Build the Word `.docx` template (PO header, supplier, delivery address, lines).
- LibreOffice on server for PDF output.
- Action button on PO detail: "Generate PDF".
- `supplier_note` prints; `internal_notes` does not.

## Scope (out)
- Sending the PDF by email (D19).
- Multi-language templates.

## Dependencies
- Requires 9a–9d.

## Acceptance
- P1: PDF generated matches the template.
- P2: `internal_notes` does not appear on the PDF.
- P3: Generation works against POs in any post-draft status.
- Manual verification by user.

## Phases
- **9e.1** Confirm Template Printing plugin enabled, LibreOffice installed (`nocobase-env-manage` if needed).
- **9e.2** Build `.docx` template.
- **9e.3** Wire action button.
- **9e.4** Verify P1–P3.

## Current state (verified live 2026-06-09, corrected with user — read before planning)
- **Plugin `@nocobase/plugin-action-template-print` ("Template print") is ENABLED and functioning** (confirmed via `nb plugin list`; user has tested PDF export end-to-end). This is the plugin that owns `TemplatePrintRecordActionModel` + the template-config UI.
- **Do NOT confuse with `@nocobase/plugin-action-print`** (simple "calls browser print", also enabled). That is the wrong plugin for templated Word→PDF output.
- **PDF output WORKS.** LibreOffice ships inside the NocoBase server image (the Mac-host `soffice` check was a red herring — rendering happens server-side, not on the local host). **User has verified PDF export already.** So P1/P2 stand as written (PDF). No LibreOffice install needed.
- **No letterhead/layout exists yet → build a clean default `.docx` template** in 9e.2 (no brand assets to match).
- **Existing button:** `TemplatePrintRecordActionModel` uid `c579329db0d` ("Template print") sits on the PO detail block `g9xffr68350` (PO page UID `liwmklclbnc`, table block `vldbcvf41r6`), beside Send. 9e.3 = configure/confirm its template binding (use this button; don't create a new one).
- **Fields to render** (from `purchase_orders`): `po_number`, `supplier` (name/address), `delivery_address`, `currency`, `total`, `total_usd`, `expected_delivery_date`, `supplier_note` (**prints**), `po_lines` (description, quantity_ordered, unit_of_measure). **`internal_notes` must NOT print** (P2). PR link: `purchase_request.pr_number` if a "Ref PR" line is wanted.
- **Test fixtures on hand for verification:** `PO-26-T4` (completed, has invoice) and the other staged POs T1–T3; plus real POs PO-26-0002/0005/0007. Any post-draft PO works for P3.

## Open questions to resolve at 9e.1 kickoff
- None blocking. Plugin enabled, PDF verified, clean-default template agreed. Proceed: 9e.2 build the `.docx` template → 9e.3 bind it to button `c579329db0d` → 9e.4 verify P1–P3.

## BUILT + VERIFIED 2026-06-09 (MVP9e DONE)
- **Template engine = Carbone**, data root `d`. Registry collection **`printingTemplates`**; record **`kkooshlz8rf`** (title now **"Purchase Order"**, `collectionName=purchase_orders`, `rootDataType=map`, `dataSource=main`, `filename=po-template-mvp9e.docx`). The `.docx` lives at **`/Users/alexander/nocobase/storage/print-templates/po-template-mvp9e.docx`**. Old stub file `17809643261187811286095403871.docx` kept on disk (rollback).
- **Button:** existing `TemplatePrintRecordActionModel` **`c579329db0d`** ("Print") on PO detail block `g9xffr68350`, already bound to `kkooshlz8rf` with `convertedToPDF:true`. No new button.
- **Template source-of-truth in repo:** [templates/build_po_template.py](../templates/build_po_template.py) regenerates [templates/purchase-order-template.docx](../templates/purchase-order-template.docx); logo asset `templates/main-logo.png` (from havenbeheer.com). To change the template: edit the builder → run `/tmp/po_tpl_venv/bin/python templates/build_po_template.py` (needs python-docx) → `cp` the docx over the storage file (file overwrite only, no live config write).
- **Layout (Havenbeheer-branded, modern):** letterhead (dark-green `main-logo.png` left + company name/address/phone/email/website right) over a dark-green rule; big "PURCHASE ORDER" title + prominent `{d.po_number}`; Supplier + Deliver-to panels (light-green bg); line-items table with dark-green header row; right-aligned totals with Total (USD) emphasized; conditional supplier note; per-page footer. Brand colors dark green `#004D38` + lime `#50B848`.
- **Fields rendered:** `po_number`; `supplier.name/address/email/phone`; `delivery_address.name/address`; `lines[i].description/quantity_ordered/unit_of_measure.name` (assoc is **`lines`**, not po_lines); `currency.label`; `total` (`formatN(2)`); `total_usd` (`formatN(2)`); `supplier_note` (conditional `ifNEM():showBegin … showEnd`). **`internal_notes` is NOT rendered (P2).** Per user request, **status / expected_delivery_date / purchase_request.pr_number were dropped** from the final design.
- **Gotchas (saved to auto-memory):** select fields render as `{value,label}` → use `.label` (`feedback_template_print_select_label`); Carbone `formatD` comma=patternIn + spaces stripped → use dashes (`feedback_template_print_carbone_date_format`); appends auto-derive from markers + local self-verify via bundled Carbone needing dayjs on NODE_PATH (`feedback_template_print_authoring`).
- **Verification:** markers self-verified locally via the plugin's bundled Carbone (all fields resolve, date `15-Jul-2026`, empty note hides, internal_notes absent, no `[object Object]`). **User confirmed the live server-rendered PDF on PO-26-0006 looks great** (P1 layout + supplier note prints, P2 internal note absent). P3 (any post-draft status) — `closed` PO-26-0006 already exercised; PO-26-0007 (`completed`) available as a second status.
