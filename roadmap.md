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
| — | supplier_issues + supplier_evaluations | deferred (D26) — see [chunks/deferred-supplier-issues-evaluations.md](chunks/deferred-supplier-issues-evaluations.md) |

Detail lives in `chunks/NNN-*.md` for pending/active MVPs and `completed/NNN-*.md` for finished ones.
