# Decisions Archive — full D1–D25 history

Verbatim from v3 plan §3, with superseded items flagged. This is the historical record. The currently effective subset lives in [decisions.md](decisions.md).

---

| # | Topic | Decision | Status |
|---|---|---|---|
| D1 | Procurement cancel of stalled PRs | **No.** Only the original submitter can cancel. Simpler Guard C. | active |
| D2 | Procurement-originated PRs → director | **Always to director**, regardless of amount. No threshold check on this path. | active (moot under D25) |
| D3 | ~~Stale FX rate threshold~~ | ~~Only warn when no rate exists at all. Any FX rate ≤ today is acceptable. No age check in Guard E.~~ | **superseded by D22** (no rate lookup exists) |
| D4 | ~~USD director threshold~~ | ~~**$1,500 USD.** Single row in `approval_limits` (applies_to = global).~~ | **superseded by D23** (manual checkbox; `approval_limits` never built) |
| D5 | Projects + project-budget bypass | **Removed from v1 scope.** No `projects` collection, no `charge_to` field, no `project` field, no Guards B/D, no project-budget routing. Every PR follows the same flow. Defer to v2. | active |
| D6 | Supplier `current_rating` | **Manually maintained** by procurement on the supplier record. No computation. | active |
| D7 | Supplier scoring scale | **1–5** (5 best). On `supplier_evaluations.score`. | active |
| D8 | New supplier onboarding workflow | **No.** Procurement creates suppliers directly; immediately usable. Permission gate (Guard #9) is sufficient. | active |
| D9 | PR → PO cardinality | **One PR → exactly one PO.** Simpler model than the original PO design's "1 PR → many POs". | active |
| D10 | PO generation trigger | **Procurement clicks "Generate PO" on the approved PR.** No auto-creation on approval. The PO opens in `draft` pre-filled from the PR. | active |
| D11 | PO line items | **Keep `po_lines`.** Procurement may split the PR description into structured lines (UoM, qty, unit price) when generating the PO. | active |
| D12 | PO budget-overrun zones | **Keep the original 110% tolerance + zone 1/2/3 logic.** Procurement can adjust line prices between PR and PO; the overrun guard fires at `draft → sent`. Director + head of Finance notified for zone 2; blocked for zone 3. | active |
| D13 | Receiving model | **Per-line `received_quantity`** on `po_lines`. Matches the original PO design. | active |
| D14 | Currencies at launch | **USD, SRD, EUR.** | active |
| D15 | Quotation attachment | **Multi-file.** Future-proofs for multi-quote later. | active |
| D16 | Edit permission for approvers | **Dept head can edit PR content while in their queue.** Procurement and Director are read-only on PR content (procurement only fills its own quote fields). | active |
| D17 | Supplier `payment_terms` shape | **Single-select** from fixed list: Net 30 / Net 60 / Net 90 / COD / Prepayment. | active |
| D18 | `resubmitted_from` field | **Dropped.** Rejected PRs do not formally link to a successor. Submitter creates a fresh PR. | active |
| D19 | Notifications | **In-app only** (NocoBase native — workflow tasks + notification icon). No email/SMTP. | active |
| D20 | Director self-PRs | **Deferred to v2.** Director cannot submit their own PR in v1. If they need to, an assistant submits on their behalf. | active |
| D21 | Dept approval routing model | **Explicit `main_approver` + `secondary_approver` fields on `departments` (m2o → users).** `users.on_leave` (boolean) controls fallback. Replaced the `department.owners[]` array approach. | active |
| D22 | FX rate entry in MVP3 | **User enters `fx_rate_to_usd` manually on the PR.** `quoted_total_usd` is a formula field. No `fx_rates` collection. | active — supersedes D3 |
| D23 | MVP4 director routing | **Manual `needs_director_approval` checkbox instead of automatic `approval_limits` threshold.** `approval_limits` collection never built. | active — supersedes D4 |
| D24 | Guard A bulk update | **Guard A does not intercept bulk update (known limitation, deferred).** Fix requires extracting IDs from `$context.params.filter`, or a dedicated bulk-update workflow. Deferred post-MVP5. | active limitation |
| D25 | MVP6 Procurement submitter routing | **Procurement staff cannot initiate purchase requests.** Excluded by policy/ACL. The dept-owner skip already implemented in MVP1 is sufficient. | active — supersedes original MVP6 scope |

---

## Discrepancies resolved during v3

- **`closed_for_new_pos` field.** Moot under the new 1 PR → 1 PO model (D9). Once procurement generates the PO from a PR, the PR is "consumed". No expiry workflow needed, no flag on the PR. The PR permissions doc was right to remove it; the PO design doc's references to it are obsolete.

## Items deferred to v2 (do not implement in v1)

- Director-submitted PRs (D20)
- Recurring / blanket PRs
- SLA / overdue tracking and alerts
- Multi-approver committees for very-high-value PRs
- PR templates
- Compliance review checkpoint
- Linked / parent-child PRs
- Approval workflow versioning (as a user-facing feature)
- Multi-quote requirement above some threshold
- Projects + project budget tracking (D5)
- Email notifications via SMTP

## Operational ownership (handled by runtime ACL, not by build decisions)

- FX rate updates → Finance role members
- `approval_limits` changes (moot under D23) → admin only if ever revived
- Supplier records → any procurement role member
