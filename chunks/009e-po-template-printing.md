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
