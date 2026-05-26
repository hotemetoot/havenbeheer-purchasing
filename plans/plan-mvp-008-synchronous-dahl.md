# Plan — MVP 008: Comments + attachments + soft fields

## Context

PR records today carry approval data (status, quote, currency, FX, supplier, `needs_director_approval`) but no narrative trail between stages and no soft business metadata. Approvers can't comment on a PR as it moves through dept → procurement → director, and submitters can't capture expenditure category, urgency, target date, or supplementary documents (anything beyond the single `quotation_attachment`).

MVP8 closes this gap by:

1. Wiring NocoBase's native **Comments** plugin to `purchase_requests` so comments persist across stages.
2. Adding four soft fields: `expenditure_type`, `is_emergency`, `needed_by`, `other_attachments`.
3. Surfacing the fields on the table, the detail popup, the create form, and the three approval form surfaces (dept / procurement / director).

No routing logic changes — `is_emergency` is a flag only (per chunk scope-out). No email — comments are in-app only (D19).

## Decisions taken (open questions in chunk → resolved)

- **`is_emergency` edit**: submitter + dept approver. Locked for procurement/director.
- **`other_attachments` edit**: submitter + dept approver. Locked for procurement/director. Procurement keeps using `quotation_attachment` for its own files.
- **Approval forms**: revise workflow `cv237r8h7k9` to add fields to the three approval form surfaces (read-only there, since per D16 procurement/director are read-only on PR content other than quote fields). Dept approval form gets the new fields **editable** for dept approver.

## Pre-flight findings

- `@nocobase/plugin-comments` is already enabled (verified via `nb plugin list`). No install step needed.
- Current active workflow version of `cv237r8h7k9` is `366234405109760`. It has been executed, so per the workflow-versioning rule it cannot be edited in place — revise → modify surfaces → enable.
- Approval form surfaces on the active version are recorded in [project_current_state.md](../project_current_state.md): dept `jmy6o8nkdld`, procurement `39ynx9u1zlh`, director `wet1jqjv8t2`.

## Phases

### 8.1 — Wire Comments on `purchase_requests`

- Use `nocobase-plugin-manage` / `nocobase-data-modeling` to attach the comments collection template to `purchase_requests` (one-to-many comments association).
- Verify a comment block can be added to the PR detail popup (done in 8.3.b).
- ACL: rely on Comments plugin defaults — any role that can view a PR can read+create comments. No per-stage gating in this MVP.

### 8.2 — Add four fields to `purchase_requests`

Skill: `nocobase-data-modeling`.

| Field | Interface | Notes |
|---|---|---|
| `expenditure_type` | select | options: `capex`, `opex`, `maintenance`, `consumables` |
| `is_emergency` | checkbox (boolean) | default false; UI flag only — no workflow conditions reference it |
| `needed_by` | date | optional |
| `other_attachments` | attachment (multi) | distinct from `quotation_attachment` |

Field-level ACL (set via `nocobase-acl-manage`):
- `expenditure_type`, `needed_by`: submitter editable at create, dept approver editable in dept stage, read-only thereafter.
- `is_emergency`, `other_attachments`: same — submitter + dept approver editable, others read-only.

(Matches D16. The "submitter editable during draft only" rule is enforced by existing Guard A once status is terminal; per-stage edit windows for the active approval stage are governed by the standard PR-content edit model already in place for `title`/`description`/`justification`.)

### 8.3 — UI surfaces

Skill: `nocobase-ui-builder`. Live-app authoring (not DSL).

a. **Create form** (`e76c40c8c79`, template `n9f8v5vnhhc`): add the four new fields after `justification` / `needs_director_approval`. Suggested order: `expenditure_type`, `needed_by`, `is_emergency`, `other_attachments`.

b. **Detail popup** (`2b367dbd157`): add the four fields. Append a **Comments block** bound to `purchase_requests.comments`.

c. **Table block** (`l1e2iwdwau9`): add `expenditure_type`, `is_emergency`, `needed_by` columns. Skip `other_attachments` (attachment lists are noisy in tables).

d. **Approval forms** — see 8.4 (workflow revision).

### 8.4 — Workflow revision for approval form surfaces

Skill: `nocobase-workflow-manage` for revision, `nocobase-ui-builder` for surface edits.

1. Revise workflow `cv237r8h7k9` (current active version `366234405109760` → new version).
2. **Verify node count and branch integrity post-revision** before touching surfaces (gotcha in CLAUDE.md: condition-branch nodes can drop). Expected: same node set as listed in [project_current_state.md](../project_current_state.md) under PR Approval workflow.
3. Edit the three approval form surfaces on the new version:
   - **Dept** (current `jmy6o8nkdld`): add the four fields, **editable** (matches D16 — dept head can edit PR content).
   - **Procurement** (current `39ynx9u1zlh`): add the four fields, **read-only**.
   - **Director** (current `wet1jqjv8t2`): add the four fields, **read-only**.
4. Enable the new version (auto-disables the prior).
5. Capture new surface UIDs and new workflow version ID for state file.

**Pause before enabling** the new version — show the user the revised node list + new surface UIDs and get verification before flipping `enabled=true`.

### 8.5 — Verification

Manual run-through with the user (test users from state file):

1. **alice.member** creates a PR — fills new fields including `is_emergency=true`, attaches a file to `other_attachments`, picks `expenditure_type=opex`, `needed_by=<future date>`. Submit.
2. **oliver.owner** opens dept approval task — sees new fields editable; corrects `expenditure_type` to `maintenance`; adds a comment "approving for emergency repair"; approve.
3. **pat.procurement** opens procurement task — sees new fields read-only; sees Alice's PR data + Oliver's comment in the comment thread; adds own comment; fills quote fields; approve.
4. **dana.director** (if `needs_director_approval=true`): sees fields read-only; sees full comment thread.
5. Reach `approved` — confirm Guard A still blocks edits on the new fields.

If anything in 8.4 dropped branch nodes or broke routing, recreate before re-enabling.

### 8.6 — Close-out

- Update [project_current_state.md](../project_current_state.md): new fields, new workflow version ID under PR Approval workflow, new approval surface UIDs, move prior surface UIDs to "Stale IDs", note the Comments association.
- Commit per CLAUDE.md commit rules (after chunk completion + state-file update).
- If anything in the plan changed during execution, edit `chunks/008-comments-attachments-soft-fields.md` in place and append a D-entry to `decisions.md`.

## Files to touch

- Live NocoBase env only (no source-tree code changes for this MVP). Build state captured in:
  - [project_current_state.md](../project_current_state.md)
  - [chunks/008-comments-attachments-soft-fields.md](../chunks/008-comments-attachments-soft-fields.md) (in place if scope shifts)
  - [decisions.md](../decisions.md) (only if a new decision is taken)
