# 008 — Comments + attachments + soft fields

## Goal
After this MVP, any user on a PR can leave comments that persist across approval stages, and the PR captures expenditure type, emergency flag, needed-by date, and additional attachments beyond the quotation.

## Scope (in)
- Enable NocoBase native **Comment Collection** plugin on `purchase_requests`.
- Add 4 fields to `purchase_requests`:
  - `expenditure_type` — single-select (capex / opex / maintenance / consumables)
  - `is_emergency` — boolean (UI flag only, no routing change)
  - `needed_by` — date
  - `other_attachments` — attachment (multi)
- Update PR table, detail popup, and forms (create + approval forms) to surface these.

## Scope (out)
- Email notifications on comment (D19 — in-app only).
- Comment threading beyond NocoBase native.
- Any routing change driven by `is_emergency` (UI flag only).

## Dependencies
- Requires MVPs 1–7 complete.
- No dependency on MVP9*.

## Acceptance
- All four new fields save and display correctly across create form, detail popup, approval forms, and table.
- Comments persist on a PR across approval stages (visible to all approvers).
- ACL on the new fields matches existing PR field-level rules (submitter + dept head can edit at appropriate stages; procurement/director read-only on these particular fields unless otherwise specified).
- Manual verification by user before marking complete.

## Phases
- **8.1** Enable Comment Collection plugin (`nocobase-plugin-manage`) on `purchase_requests`.
- **8.2** Add the 4 new fields (`nocobase-data-modeling`).
- **8.3** Update create form, detail popup, table columns, dept/procurement/director approval forms (`nocobase-ui-builder`).
  - Approval forms: workflow revision required if the active version has been executed — see [decisions.md](../decisions.md) D21/D24 prep notes and the workflow-versioning gotcha.
- **8.4** Verify the acceptance criteria with the user.

## Open questions
- Should `is_emergency` be visible/settable by dept head and procurement, or submitter only?
- Should `other_attachments` be addable post-submission by anyone in the approval chain?
