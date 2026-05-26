# Decisions — currently effective

Design, implementation, and workaround decisions that still apply to the current build. Superseded entries live in [decisions-archive.md](decisions-archive.md).

Scope: this is not just design. Implementation choices ("we used a workflow because formulas can't aggregate", "we deferred X to MVP9d", "pattern Y was rejected because of NocoBase limitation Z") belong here. The "why" matters more than the "what" — future-you reads these to understand constraints, not to discover features.

When adding new entries, list affected downstream MVPs by number so step 3 of the session workflow catches forward references.

---

## D1 — Procurement cannot cancel stalled PRs
Only the original submitter can cancel a PR. Simpler Guard C. **Affects:** MVP2.

## D2 — Procurement-originated PRs always go to director
No threshold check on this path. **Affects:** MVP6 (moot under D25 — kept for historical context).

## D5 — Projects + project-budget bypass removed from v1
No `projects` collection, no `charge_to` field, no Guards B/D, no project-budget routing. Every PR follows the same flow. Deferred to v2. **Affects:** all MVPs.

## D6 — Supplier `current_rating` is manually maintained
Procurement edits on the supplier record. No computation. **Affects:** MVP7.

## D7 — Supplier scoring scale is 1–5 (5 best)
On `supplier_evaluations.score`. **Affects:** MVP7.

## D8 — No supplier onboarding workflow
Procurement creates suppliers directly; immediately usable. ACL gate (Guard #9) is sufficient. **Affects:** MVP7.

## D9 — One PR → exactly one PO
Simpler than original "1 PR → many POs". `closed_for_new_pos` field on PR is moot under this model and is not built. **Affects:** MVP9a–e.

## D10 — PO generation is manual ("Generate PO" button)
Procurement clicks on the approved PR. No auto-creation. PO opens in `draft` pre-filled from the PR. **Affects:** MVP9a.

## D11 — Keep `po_lines`
Procurement may split the PR description into structured lines (UoM, qty, unit price) on the PO. **Affects:** MVP9a, 9c.

## D12 — PO budget-overrun zones
Keep 110% tolerance + zone 1/2/3 logic. Procurement may adjust line prices between PR and PO; overrun guard fires at `draft → sent`. Director + Finance head notified for zone 2; zone 3 blocked. **Affects:** MVP9b.

## D13 — Per-line `received_quantity`
Receiving model uses `po_lines.received_quantity` (fractional supported). **Affects:** MVP9c.

## D14 — Currencies at launch
USD, SRD, EUR. **Affects:** MVP3.

## D15 — `quotation_attachment` is multi-file
Future-proofs for multi-quote later. **Affects:** MVP3.

## D16 — Edit permission for approvers
Dept head can edit PR content while in their queue. Procurement and Director are read-only on PR content (procurement only fills its own quote fields). **Affects:** MVP1, ongoing ACL.

## D17 — Supplier `payment_terms` shape
Single-select from fixed list: Net30 / Net60 / Net90 / COD / Prepayment. **Affects:** MVP7.

## D18 — `resubmitted_from` field dropped
Rejected PRs do not formally link to a successor. Submitter creates a fresh PR.

## D19 — Notifications: in-app only
NocoBase native (workflow tasks + notification icon). No email/SMTP in v1. **Affects:** MVP9b.

## D20 — Director self-PRs deferred to v2
In v1 an assistant submits on Dana's behalf.

## D21 — Dept routing via `main_approver` + `secondary_approver`
Explicit `main_approver` (m2o → users) and `secondary_approver` (m2o → users) on `departments`. `users.on_leave` (boolean) controls fallback. Names are role-neutral ("approver", not "manager"). Replaced the unreliable `department.owners[]` array approach. **Affects:** MVP1 routing, all downstream.

**Why:** `department.owners[]` could be empty, multi-valued, or accidentally broken; the array shape made workflow filters fragile.

**How to apply:** Use `main_approver` for routing; check `on_leave` and fall back to `secondary_approver` if needed. Never reference `department.owners` in workflows.

## D22 — Manual FX rate entry on PR
User enters `fx_rate_to_usd` manually on the PR. `quoted_total_usd` is a formula field (`{{quoted_total}} * {{fx_rate_to_usd}}`, formula.js, read-only). No `fx_rates` collection. **Supersedes** the original design's FX-lookup workflow + `fx_rates` collection. **Affects:** MVP3, MVP4 (Guard E validates `fx_rate_to_usd IS NOT NULL` instead of doing a rate lookup).

**Why:** The original design had `fx_rates` collection + workflow nodes to look up rates at submit time. Built then deleted on 2026-05-24 — the lookup added complexity for no clear payoff. Manual entry gives procurement the rate they want without a separate maintenance burden.

**How to apply:** `fx_rate_to_usd` is just a number field. Guard E checks it is not null. `quoted_total_usd` requires no workflow writes.

## D23 — Manual `needs_director_approval` checkbox (instead of automatic threshold)
Submitter checks `needs_director_approval` on the PR form. Workflow conditions on the field. **Supersedes** D4 (USD director threshold $1,500) — the `approval_limits` collection was never built. Linkage rule on create form makes `justification` required when the checkbox is checked. **Affects:** MVP4.

**Why:** Routing rules weren't clear enough to automate ("is this above $1,500?" missed nuance like emergency procurement, capex vs opex). Manual checkbox shifts judgement to the submitter, which is where it belonged anyway.

**How to apply:** Workflow Procurement Approve branch conditions on this field — true → director path, false → approved immediately.

## D24 — Guard A bulk-update limitation (deferred)
Guard A does NOT intercept bulk update. Bulk-update requests send target IDs in `$context.params.filter.$and[0].id.$in`, not `$context.params.filterByTk`. Guard A's Query node looks up by `filterByTk` only, so bulk-update requests pass through. Fix requires a Script/JSON-query node to extract IDs from `$context.params.filter`, or a dedicated bulk-update workflow. **Deferred post-MVP5.** **Affects:** future hardening.

**Why:** Caught at MVP5 verification; not blocking single-record protection which is the main risk surface.

**How to apply:** If hardening bulk-update is requested, build either a Script node that reads from `$context.params.filter.$and[0].id.$in` or a separate request-interception workflow targeting `action=update` with the bulk shape.

## D26 — MVP7 descoped to suppliers only
`supplier_issues` and `supplier_evaluations` were postponed during MVP7. Only the `suppliers` collection + the optional `supplier` m2o field on `purchase_requests` were built. **Affects:** MVP7 scope; original MVP7 scenarios S3 and S4 are not applicable.

**Why:** Not blocking the PR/PO flow. Procurement can manually edit `suppliers.current_rating` and `suppliers.notes` as a placeholder (per D6). Bring issue logging + evaluations back when there's real demand.

**How to apply:** Treat `supplier_issues` and `supplier_evaluations` as not-built. Do not assume them as dependencies for MVP8 or MVP9*. Revival sketch lives in [chunks/deferred-supplier-issues-evaluations.md](chunks/deferred-supplier-issues-evaluations.md).

## D25 — Procurement staff are excluded from initiating PRs
Policy/ACL, not workflow logic. The "submitter's dept = Procurement → skip to director" routing variant is moot. The dept-owner skip (submitter IS dept approver → skip dept) was already implemented in MVP1 (condition `5hed96jh1u7`). **Supersedes** the original MVP6 scope. **Affects:** MVP6 (complete with no new build).

**Why:** Cleaner separation of duties — procurement reviews PRs, doesn't author them.

**How to apply:** ACL: `member` role used for submitting PRs; procurement-only roles do not get create-PR. No workflow change.

---

## D27 — po_lines pricing descoped
Line items track quantity + receiving only. `unit_price`, `line_total`, and `line_total_usd` are removed from `po_lines`. PO `total` is manually entered from the supplier invoice (no derivation from lines). **Affects:** MVP9a (this revision — Generate-PO workflow no longer writes `unit_price` on the default line; planned 9a.4 Total-maintenance workflow is cancelled); MVP9c (receiving) — only `received_quantity` and `line_status` change; no $-math on lines. MVP9d, MVP9e unaffected.

**Why:** Formula fields can only reference same-collection scalars (see `feedback_formula_field_scope`), so `line_total_usd` cannot traverse to `purchase_order.fx_rate_to_usd`. The denormalize-fx alternative would add a sync-workflow per PO update for a value not currently needed at line level. Pricing decisions in this domain happen at the PO header (supplier invoice = source of truth for $$), and line items are quantity-tracking artifacts. Simpler model overall.

**How to apply:** Don't restore the deleted fields. If a future MVP needs line-level USD reporting, denormalize `fx_rate_to_usd` onto `po_lines` and recompute line USD via a workflow update — don't try to formula-traverse the relation.

---

## Living register

New entries go below in numeric order. When superseding a prior decision, mark the prior entry as superseded in [decisions-archive.md](decisions-archive.md) and add a `**Supersedes:** D#` line on the new entry.
