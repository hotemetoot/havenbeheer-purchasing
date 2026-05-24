# Handoff — 2026-05-24 — Start MVP7

Read the memory file first, then this document. Do NOT read the whole v3 plan — just the MVP7 section.

---

## Where we stopped

MVPs 1–6 are fully built and verified. The session ended after:
- MVP5: Guard A (immutability) — request-interception workflow blocking update/destroy on terminal-status PRs
- MVP6: Complete by design change D25 — no new build needed

**The next thing to build is MVP7.**

---

## Design changes recorded this session

**D24 — Guard A bulk update limitation (known, deferred)**
Guard A does NOT intercept the table's bulk update action. Bulk update sends IDs via `$context.params.filter.$and[0].id.$in`, not `$context.params.filterByTk`. The guard's Query node returns nothing for a null `filterByTk` → condition false → passes through. Deferred post-MVP5.

**D25 — MVP6 Procurement submitter routing (no build)**
Original MVP6 included routing for "submitter's dept = Procurement → skip to director." Decision: Procurement staff cannot initiate PRs at all (ACL/policy). Dept-owner skip (submitter IS dept approver → skip dept) was already implemented in MVP1 (condition `5hed96jh1u7`). No workflow restructuring needed.

---

## Active runtime state

### Workflows
| Workflow | Key | Active version ID | Notes |
|---|---|---|---|
| PR Approval | `cv237r8h7k9` | `366087730298880` | enabled, 18 nodes |
| Cancel PR | `59ezifdoqvj` | `364980262862848` | enabled |
| Cancel PR Guard | `8yngslauuj4` | `364984924831744` | enabled, request-interception |
| Guard A | `496ookqmg01` | `366217145548800` | enabled, request-interception, global update+destroy |

### Guard A node chain
| Node | Key | Type | Notes |
|---|---|---|---|
| Fetch current record | `q33wtlxitr1` | query | purchase_requests by filterByTk |
| Status is terminal? | `nbs3zmsr60x` | condition | OR: approved/rejected/cancelled; rejectOnFalse:false |
| Lock message | `oevaqo6q5im` | response-message | branch 1; "This record is locked…" |
| End (block) | `n89dufkutuu` | end | endStatus:-1 |

### UI
- **Purchase Requests page:** `cuycec133qb`
- **PR detail popup:** `2b367dbd157`
- **Create form:** template `n9f8v5vnhhc`, target `e76c40c8c79`

---

## MVP7 build plan

### One-line scope
Build the `suppliers`, `supplier_issues`, and `supplier_evaluations` collections, add an optional `supplier` field to `purchase_requests`, configure ACL, and build list/detail pages.

### Design decisions that govern MVP7

| Decision | What it means for build |
|---|---|
| D6 | `supplier.current_rating` is manually maintained by procurement — plain number field, no computation |
| D7 | `supplier_evaluations.score` scale: 1–5 (5 = best) |
| D8 | No onboarding workflow — procurement creates suppliers directly, immediately usable |
| D17 | `suppliers.payment_terms` is a **single-select**: Net30 / Net60 / Net90 / COD / Prepayment |
| D25 | Procurement staff cannot initiate PRs — ACL guard on create in MVP7 |

### Collection schemas

#### `suppliers`
| Field | Type | Values / notes |
|---|---|---|
| `name` | text | Legal name |
| `display_name` | text | Short UI name |
| `tax_id` | text | VAT / KvK / equivalent |
| `country` | single select | (country list) |
| `default_currency` | single select | USD / SRD / EUR (same as PR) |
| `payment_terms` | single select | Net30 / Net60 / Net90 / COD / Prepayment (D17) |
| `status` | single select | active / inactive / blocked |
| `notes` | textarea | |
| `current_rating` | number (decimal) | Manual, maintained by procurement (D6) |

**Not in MVP7:** `address` (textarea) — deferred to MVP9a when PO delivery address is needed.

#### `supplier_issues`
| Field | Type | Notes |
|---|---|---|
| `supplier` | m2o → suppliers | Required |
| `purchase_request` | m2o → purchase_requests | Optional |
| `issue_type` | single select | quality / delivery / price / communication / compliance / other |
| `severity` | single select | minor / moderate / major / critical |
| `description` | textarea | Required |
| `reported_by` | m2o → users | Auto-set (createdBy) |
| `reported_at` | datetime | Auto-set (createdAt) |
| `status` | single select | open / under_review / resolved / closed |
| `resolution` | textarea | |
| `resolved_at` | datetime | |

#### `supplier_evaluations`
| Field | Type | Notes |
|---|---|---|
| `supplier` | m2o → suppliers | Required |
| `evaluator` | m2o → users | Auto-set (createdBy) |
| `evaluation_date` | date | |
| `score` | number (integer) | 1–5; 5 = best (D7) |
| `evaluation_type` | single select | per_transaction / periodic_review |
| `purchase_request` | m2o → purchase_requests | Optional; for per-transaction reviews |
| `comments` | textarea | |

#### `purchase_requests` — new field
| Field | Type | Notes |
|---|---|---|
| `supplier` | m2o → suppliers | Optional; "Suggested supplier" label |

### ACL
- `suppliers`: Procurement role can create/edit; all roles can view (Guard #9, D8)
- `supplier_issues`: all roles can create; procurement can edit/resolve
- `supplier_evaluations`: all roles can create; procurement can edit
- `purchase_requests.supplier`: submitter and procurement can set; not editable after `pending_purchasing_review` (enforcement deferred to MVP9a when procurement review finalises)

### Phases

**7.1** Create `suppliers` collection with fields above.

**7.2** Create `supplier_issues` collection with fields above.

**7.3** Create `supplier_evaluations` collection with fields above.

**7.4** Add optional `supplier` (m2o → suppliers, label "Suggested supplier") field to `purchase_requests`.

**7.5** Configure ACL — procurement creates/edits suppliers; all view.

**7.6** Build pages:
- Suppliers: list page + detail popup (name, display_name, payment_terms, status, current_rating, notes)
- Supplier issues: sub-table or related block (per supplier and per PR where applicable)
- Supplier evaluations: sub-table or related block per supplier

**7.7** Add `supplier` field to PR create form, detail popup, and procurement approval form (all optional/read-pretty as appropriate).

### Verification

| # | Test | Expected |
|---|---|---|
| S1 | Pat (procurement) adds a supplier | Succeeds |
| S2 | Alice (member) tries to add a supplier | Blocked |
| S3 | Anyone logs a supplier issue | Succeeds |
| S4 | Procurement edits/resolves an issue | Succeeds |
| S5 | PR submitted with a supplier set | Succeeds; supplier shows in detail |
| S6 | PR submitted without supplier | Succeeds (field is optional) |

---

## Environment
- Env: `havenbeheer`, http://localhost:13000
- CLI: `nb` with OAuth auto-refresh
- UI page: `cuycec133qb` (Purchase Requests)

---

## MVP8 preview (after MVP7 verified)

Comments + attachments + soft fields:
- Enable native Comment Collection plugin on `purchase_requests`
- Add `expenditure_type` (capex/opex/maintenance/consumables), `is_emergency` (boolean), `needed_by` (date), `other_attachments` (attachment multi)
- Update PR table, detail, forms

See v3 plan §MVP8.
