# MVP Roadmap

| MVP | Scope | Status |
|---|---|---|
| 001 | 3-stage approval (dept → procurement → director), approve/return/reject | ✓ complete |
| 002 | Cancel by submitter (draft only) | ✓ complete |
| 003 | Quotation fields + currency + manual FX rate (D22) + formula USD total | ✓ complete |
| 004 | Manual `needs_director_approval` checkbox (D23) + routing | ✓ complete |
| 005 | Guard A — PR immutability when terminal (bulk-update limitation deferred, D24) | ✓ complete |
| 006 | Submitter-role routing variants (resolved via ACL under D25, no new build) | ✓ complete |
| 007 | Suppliers collection + supplier on PR (issues/evaluations descoped, D26) | ✓ built |
| 008 | Comments + attachments + soft fields | ✓ built (comments UI block removed post-verify; data layer kept) |
| 009a | PO collection + po_lines + Generate-PO button | ✓ built (D27 descoped po_lines pricing; planned 9a.4 total-maintenance cancelled) |
| 009b | PO send + budget zones (110%) + zone 2/3 notifications | ✓ built (D28 cancel→close collapse; zone-2 verified; zone-2 in-app notifications deferred — gated on Finance `main_approver`) |
| 009c | PO receiving (per-line `received_quantity`) | ✓ built + verified 2026-06-07 (Receive Guard `mhfp4d15uee` + Receiving recompute `ork27v016yo`; receiving UI user-built; R1–R4 passed) |
| 009d | PO completion / closing + immutability (no cancel — D28/D33) | ✓ built + verified 2026-06-09 (Complete `qh7b3hc5q1r` w/ D34 invoice+USD gate, broadened Close `f8gpu17s6hq`, D35 Close Guard `b6brl8r9c58`, PO/line immutability guards; C1–C5 + D34a/b + D35 all passed via API-staged fixtures) |
| 009e | PO template printing (Word → PDF) | ✓ built + verified 2026-06-09 (Carbone template `printingTemplates:kkooshlz8rf` → `po-template-mvp9e.docx`, Havenbeheer-branded; Print button `c579329db0d`; P1/P2 confirmed on PO-26-0006; source in `templates/`) |
| 010 | Optional submitter-chosen skip of dept-head approval (FYI notify + view access, D29) | ⊘ superseded by 012 (D36) — skip retired |
| 011 | Mandatory board approval at ≥ $15k USD after director — `pending_board_approval` + required signed-doc upload (D32) | ✓ built + verified |
| 012 | Submitter-selectable dept-stage approver (reassign to dept member, FYI-notify dept head; retires skip, D36) | ✓ built + verified 2026-06-09 (A1–A7 passed) |
| 013 | Regular-purchase flag — procurement-set `is_regular` bypasses director below $300; sub-$300 default flips to director; retires `needs_director_approval` routing (D37) | ✓ built + verified 2026-06-09 (workflow `cv237r8h7k9` rev `369161752084480` active; condition `bizoy1sj87j` swapped; is_regular editable on procurement form + read-only on popup; A1–A7 passed) |
| 014 | Projects & budget drawdown — USD budget envelope approved via its own ladder; project-linked PRs skip director+board (Procurement final) but keep dept-owner approval and are hard-blocked from exceeding `budget_usd` (D49, reverses D5) | ◑ logic complete 2026-06-27, **pending user E2E** — built+CLI-verified: `projects` collection, `purchase_requests.project` m2o, committed_usd recompute A/B, PR budget guards; **014.4 drawdown branch** on PR Approval (rev `372368060514304`, +cond `492iwdlv0mr`/update `48myq8dpqza`/notif `kykl9gnqj9h`); **014.2b/c** Project Approval `hzykothf9cx` **ENABLED** w/ 4 approver surfaces + initiator (centralized) + ACL (operations/procurement/director). Pending: 014.5 UI (Projects page/detail/Close button + PR `project` picker + PR field whitelists; board `approval_document` required), 014.6 user E2E (A1–F2). See [chunks/014-projects-and-budget-drawdown.md](chunks/014-projects-and-budget-drawdown.md) |
| 015 | "PR approved" notifications — on final approval, in-app notify the requester always + head of procurement only on the director path (not when Procurement is final, not on board path) (D50) | ✓ built + verified 2026-06-24 — workflow `cv237r8h7k9` rev `371864957943808` active; 3 notification nodes (`hy95mz4oo5f`/`dproua9530i`/`p53qqltz9v2`); A1–A5 passed. See [chunks/015-pr-approved-notifications.md](chunks/015-pr-approved-notifications.md) |
| 016 | Budget-safe PO line-item import — bulk-import PO lines; budget cap enforced at the Issue gate (Σ line_total ≤ PR.quoted_total) since import bypasses the D47 per-line guards; import button hidden unless PO is `draft` (D52) | ◑ Part A built + user-verified 2026-06-27 — `issue_po` rev `372351365087232` (+4 nodes `kkk684uupcd`/`hksnw304p3b`/`0udjhd90ljj`/`3ba6bu5e6un`); import action + hide rule user-built in UI. **Parked:** import doesn't recompute `lines_total` (collection event fires before FK lands — cap unaffected). See [chunks/016-po-line-import-budget-safe.md](chunks/016-po-line-import-budget-safe.md) |
| — | supplier_issues + supplier_evaluations | deferred (D26) — see [chunks/deferred-supplier-issues-evaluations.md](chunks/deferred-supplier-issues-evaluations.md) |

Detail lives in `chunks/NNN-*.md` for pending/active MVPs and `completed/NNN-*.md` for finished ones.
