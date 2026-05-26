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
| 009a | PO collection + po_lines + Generate-PO button | pending |
| 009b | PO send + budget zones (110%) + zone 2/3 notifications | pending |
| 009c | PO receiving (per-line `received_quantity`) | pending |
| 009d | PO completion / closing / cancellation + immutability | pending |
| 009e | PO template printing (Word → PDF) | pending |
| — | supplier_issues + supplier_evaluations | deferred (D26) — see [chunks/deferred-supplier-issues-evaluations.md](chunks/deferred-supplier-issues-evaluations.md) |

Detail lives in `chunks/NNN-*.md` for pending/active MVPs and `completed/NNN-*.md` for finished ones.
