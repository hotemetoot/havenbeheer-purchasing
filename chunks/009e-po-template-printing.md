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

## Current state (verified live 2026-06-09 — read before planning)
- **Plugin `@nocobase/plugin-action-template-print` ("Template print") is DISABLED.** Must enable in 9e.1 (`nb plugin enable @nocobase/plugin-action-template-print`). This is the plugin that owns `TemplatePrintRecordActionModel` + the template-config UI.
- **Do NOT confuse with `@nocobase/plugin-action-print`** (simple "calls browser print", already enabled). That is the wrong plugin for templated Word→PDF output.
- **LibreOffice / `soffice` is NOT installed on this host** (no `soffice`/`libreoffice` on PATH, no `/Applications/LibreOffice.app`). The plugin renders PDF server-side via LibreOffice; without it, output is `.docx` only. **Open decision (ask user in 9e.1):** install LibreOffice on the NocoBase server host (server is local `localhost:13000`), or ship `.docx`-only and drop the PDF acceptance (P1/P2 reword). Resolve before 9e.2.
- **Existing bare button:** `TemplatePrintRecordActionModel` uid `c579329db0d` ("Template print") already sits on the PO detail block `g9xffr68350` (PO page UID `liwmklclbnc`, table block `vldbcvf41r6`), added by the user beside Send. No template configured → currently inert (and inert anyway while the plugin is disabled). 9e.3 = configure its template binding rather than create a new button (verify it survives the plugin enable; recreate if needed).
- **Fields to render** (from `purchase_orders`): `po_number`, `supplier` (name/address), `delivery_address`, `currency`, `total`, `total_usd`, `expected_delivery_date`, `supplier_note` (**prints**), `po_lines` (description, quantity_ordered, unit_of_measure). **`internal_notes` must NOT print** (P2). PR link: `purchase_request.pr_number` if a "Ref PR" line is wanted.
- **Test fixtures on hand for verification:** `PO-26-T4` (completed, has invoice) and the other staged POs T1–T3; plus real POs PO-26-0002/0005/0007. Any post-draft PO works for P3.

## Open questions to resolve at 9e.1 kickoff
1. **PDF vs DOCX:** install LibreOffice on the server, or accept `.docx`-only? (Blocks P1/P2 wording.)
2. **Template look:** does the user have an existing PO letterhead / layout to match, or build a clean default?
