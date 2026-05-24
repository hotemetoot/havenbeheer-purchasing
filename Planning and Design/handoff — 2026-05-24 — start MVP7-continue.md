# Handoff — 2026-05-24 — MVP7 Continue (Approval Forms)

Read the memory file first (`project_current_state.md`), then this document.

---

## What was completed this session

### MVP7 data model ✓
- `suppliers` collection created: name (unique, required), display_name, tax_id, email, phone, address, country, default_currency, payment_terms, status (default: active), current_rating (decimal, min=1 max=5 validated), notes
- `suppliers.titleField` = `name`
- `supplier` m2o field added to `purchase_requests` (label: "Suggested Supplier", optional)

### ACL ✓
- `procurement`: create + view + update on suppliers (scope=all, all fields)
- `member`: view only (overrides their broad global strategy)
- `director` and `finance`: independent config removed — they inherit view through member base role
- **Memory saved**: every user has `member` as base role; do NOT add redundant view ACL to other roles

### Suppliers page ✓
- New page under Purchasing group (`pageSchemaUid: gbg516xq3ie`, routeId: `366222348582912`)
- Table: name, display_name, payment_terms, status, current_rating, country
- Filter action + Add action (ACL blocks non-procurement)
- View + Edit record actions
- Detail popup with fieldGroups: Basic Info / Contact / Commercial / Notes / Record Info

### PR form surfaces ✓ (supplier field added)
- PR detail popup (`2b367dbd157`): supplier display field added
- PR create form (`e76c40c8c79`): supplier picker added
- Procurement approval form (`ti4uf7gwhpu`): supplier picker added, positioned after description

---

## What still needs to be done

### Approval workflow forms — supplier field NOT properly applied

**Problem**: The `add-field` calls targeted `ProcessFormModel` UIDs that appear to be template-backed surfaces. The fields were added to the schema shell but not to the template source the approval workflow actually renders. The user confirmed changes are not visible in the workflow.

**The correct procedure** (per user): "create a copy and then adjust the forms"

This means: before editing an approval form, you must first detach it from its template (create an independent copy), then add fields to the local copy.

**Three approval forms need the supplier field:**

| Approval Step | Form UID | Field mode |
|---|---|---|
| Dept Owner Approval | `ProcessFormModel uid=070d0efb9bb` (approvalUid `klak6hh6vu0`) | editable picker, after description |
| Procurement Approval | `ProcessFormModel uid=ti4uf7gwhpu` (approvalUid `qswcu5p6ihj`) | editable picker, after description |
| Director Approval | `ProcessFormModel uid=qcwkfuffa9g` (approvalUid `42ay2w0j69v`) | **display-only** (readPretty), after description |

**Current state of each form** (field order currently stored, may or may not be visible):
- Dept (`070d0efb9bb`): title → description → supplier (editable) → quoted_total → ...
- Procurement (`ti4uf7gwhpu`): title → description → supplier (editable) → justification → ...
- Director (`qcwkfuffa9g`): title → description → supplier (readPretty) → justification → ...

**What to ask the user at start of session**: Confirm the exact procedure for "create a copy" — is this the `flow-surfaces` `copy` mode on the popup template, a workflow node form reset, or a UI operation? Then apply correctly to all 3 forms.

**Task card UIDs** (read-only view side, for reference):
- Dept: taskCardUid `92sgwoqox8y`
- Procurement: taskCardUid `koo33nxd7gg`
- Director: taskCardUid `j0ikk0gww0m`

---

## Known deferred items

- D24: Guard A bulk-update limitation (post-MVP5, still deferred)
- `display_name` field: user questioned its purpose — confirm keep/remove
- `supplier_issues` and `supplier_evaluations`: deferred pending team discussion
- `address` field on suppliers was added (previously deferred to MVP9a — now included per user feedback)

---

## ACL rule to remember

Every user has `member` as base role. When setting up ACL for a new collection:
- `member` = view only (covers all users who just need to read)
- `procurement` = create + edit + view
- Do NOT add separate view grants to `director`, `finance`, `dept_head` etc. unless they need MORE than member already provides

---

## Environment
- Env: `havenbeheer`, http://localhost:13000
- CLI: `nb` with OAuth auto-refresh
- PR Approval workflow key: `cv237r8h7k9`, active version `366087730298880`
