# Permissions

**Reference.** Authoritative source: [havenbeheer PR — permissions and guards.md](../Planning%20and%20Design/havenbeheer%20PR%20—%20permissions%20and%20guards.md).

## Guards in effect

| Guard | What it does | Where built | Status |
|---|---|---|---|
| Guard A | PR immutability when terminal | MVP5 (workflow key `496ookqmg01`) | active; bulk-update limitation per D24 |
| Guard C | Cancel: only submitter, only draft | MVP2 (workflows `59ezifdoqvj` + `8yngslauuj4`) | active |
| Guard E | Procurement finalisation (quote fields not null) | **Not built.** Original plan was MVP4; superseded by D23. Could be revived for MVP8+ if needed. |
| Guard #9 | Only procurement creates/edits suppliers | MVP7 (ACL) | active |

## Roles

See [users-and-roles.md](users-and-roles.md).

## Field-level ACL highlights

- Submitter + dept owner can edit PR content during their stages (D16).
- Procurement is read-only on PR content except for quote fields (`quoted_total`, `quoted_currency`, `fx_rate_to_usd`, `quotation_attachment`) which they fill in.
- Director is read-only on the whole PR.
- All members get base view of PRs they're involved with via standard NocoBase ACL — do not add redundant view grants per the auto-memory feedback note on `member` being the base role.
- **Reassigned-PR view access (D36, was D29).** When a submitter reassigns the dept stage via `custom_approver`, the dept head gets no approval task but must still be able to *open* the PR they're FYI-notified about. The dept-owner (`main_approver`) view scope must therefore cover department PRs independent of task assignment — verify the MVP1 scope already does this; widen only if it's effectively task-driven. (Same requirement as the retired D29 skip; the chosen custom approver gets the actual approval task via the workflow assignee.)
