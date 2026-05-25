# 003 — Quotation, currency, FX rate, USD total ✓

**Verified:** 2026-05-24 by user. **Design change:** D22.

## Goal
Capture quotation amount, currency, FX rate, and a computed USD total on the PR. Allow procurement to fill these in during their approval step.

## What was built
- New fields on `purchase_requests`:
  - `quoted_total` (decimal)
  - `quoted_currency` (single-select USD/SRD/EUR per D14)
  - `fx_rate_to_usd` (decimal, **user-entered** per D22)
  - `quoted_total_usd` (formula.js: `{{quoted_total}} * {{fx_rate_to_usd}}`, auto-computes, read-only)
  - `quotation_attachment` (attachment, multi per D15)
- Procurement approval form: `quoted_total`, `quoted_currency`, `fx_rate_to_usd`, `quotation_attachment` editable; `quoted_total_usd` readPretty.
- PR table: `quoted_total`, `quoted_currency` columns added.
- PR detail popup: all 5 quote fields visible (read-only display).
- Approval workflow remains the MVP1 shape (no FX-lookup nodes).

## Design change (D22)
The original design had an `fx_rates` collection + workflow FX-lookup nodes at submit time. Built then deleted on 2026-05-24. Replaced with manual `fx_rate_to_usd` entry + formula USD field. See [decisions.md](../decisions.md) D22 for rationale.
