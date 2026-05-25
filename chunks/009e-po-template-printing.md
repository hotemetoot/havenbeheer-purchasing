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
