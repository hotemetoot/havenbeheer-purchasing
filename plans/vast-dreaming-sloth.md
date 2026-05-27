# MVP9b — Send PO + budget zones + zone 2/3 notifications

## Context

MVP9a built PO creation (Generate-PO from approved PR, default draft state). MVP9b wires up the **send transition** on a PO: procurement reviews the PO total against the PR's approved budget and either sends it, sends it with an override comment, or is blocked. This is the first PO status transition we build, and it carries the budget-overrun policy (PO design §5, D12). We also add a `Close PO` transition while we're here.

**Simplification vs. PO design doc** (new D-entry at session end): collapse `cancelled` into `closed`. Two terminal states only — `completed` (happy path) and `closed` (everything else, with a reason). The former `draft → cancelled` action becomes `draft → closed` with `close_reason = "no_longer_required"` (or similar). `close_at`/`cancelled_at` collapse to `closed_at`. This change carries into 9d (close-from-non-draft) and 9a's collection definition (drop `cancelled` from the status enum, drop `cancelled_at`, add a `no_longer_required` value to `close_reason`).

PO `total` is now manually entered per D27 (no derivation from lines); `total_usd = total / fx_rate_to_usd` via existing formula. The zone evaluation compares `po.total_usd` against `purchase_request.quoted_total_usd` directly — no intermediate variable.

## Scope

In: `draft → sent` workflow (zone 1/2/3 logic), `draft → closed` workflow (formerly cancel), Send-PO & Close-PO buttons on PO surfaces, in-app notifications to Director + Finance head on zone 2, status-enum cleanup (drop `cancelled`, drop `cancelled_at`, add `no_longer_required` to `close_reason`), manual user verification of Z1/Z2/Z3 + close-from-draft.

Out: PO immutability when terminal (9d), receiving (9c), close-from-non-draft (9d), completion (9d), email notifications (D19).

## Pre-flight checks (read-only)

1. Confirm `purchase_orders.status` enum includes `sent`, `closed`, `completed` (built in 9a). Remove `cancelled` from the enum if present (no live POs in `cancelled` state yet — verify; if any exist, migrate them to `closed` with `close_reason = "no_longer_required"` before dropping the value).
2. Confirm `purchase_orders.sent_at` and `closed_at` datetime fields exist (per current_state line 102 — yes). Drop `cancelled_at` (verify no rows have it set first).
3. Confirm `budget_override_comment` textarea exists (yes, line 102). Confirm `close_reason` select and add `no_longer_required` to its options.
4. **Finance dept `main_approver` is currently NULL** (queried live). The user must set this on the Finance department record before zone 2 notifications can target anyone — pause and ask before building 9b.3 if still null.
5. Confirm in-app notification channel exists: yes, `approval-todo-in-app-message` (notificationType `in-app-message`). Workflow node type `notification` should support it; if the available node types do not include `notification`, fall back to creating a NocoBase "task"/message record directly via a create node on the notifications collection.

## Build phases

### 9b.1 — Send-PO workflow

- **Type:** custom-action, sync, collection `purchase_orders`, appends `["purchase_request"]`.
- **Key:** new, captured at build time.
- **Node chain (all sync):**
  1. Guard condition — `status == "draft"` AND `total IS NOT NULL` AND `fx_rate_to_usd IS NOT NULL`.
     - false branch → response-message ("PO must be in draft with total and FX rate set.") → end-process (`endStatus: -1`). Pattern per [`feedback_inline_guard_end_node`](../../../.claude/projects/-Users-alexander-Documents-Claude-Projects-Havenbeheer-Purchasing/memory/feedback_inline_guard_end_node.md).
  2. Zone-3 condition — `(total / fx_rate_to_usd) > (purchase_request.quoted_total_usd * 1.1)`.
     - true branch → response-message ("Zone 3: PO total exceeds 110% of PR budget. A new PR is required.") → end-process (`endStatus: -1`).
  3. Zone-2 condition — `(total / fx_rate_to_usd) > purchase_request.quoted_total_usd`.
     - true branch:
       - sub-condition: `budget_override_comment` empty → response-message ("Zone 2: budget_override_comment is required to send this PO.") → end-process (`endStatus: -1`).
       - else → Update PO → `status=sent`, `sent_at={{$system.now}}` → notification fan-out (9b.3).
     - false branch (zone 1) → Update PO → `status=sent`, `sent_at={{$system.now}}`.

### 9b.2 — Close-PO-from-draft (edit form + collection-trigger workflow)

Two pieces, mirroring the MVP2 Cancel-PR pattern but with a collection-trigger workflow instead of custom-action (user decision: a custom-action button can't open a fresh input form).

**Edit popup**, opened by the Close PO button (9b.4):
- `UpdateRecordActionModel` configured to show only `close_reason` (select, required, includes new `no_longer_required` option) and `close_comment` (textarea, required).
- `status` is NOT exposed in the form — the workflow promotes it.
- Form-level required rules enforce both fields before Save (guard #6).

**Workflow:** collection trigger on `purchase_orders`, **mode: update**, async is fine (the user just sees the record after save; we don't need to block).
- **Filter:** `close_reason` is not empty AND `status == "draft"` AND `closed_at` is empty (the last predicate prevents re-firing if anything ever re-saves the same record).
- **Node chain (single node):** Update PO → `status=closed`, `closed_at={{$system.now}}`.

This pattern means a user with direct PO update permission could in theory set `close_reason` via API while in any non-draft state — but the workflow filter pins it to draft, so other states won't flip via this path. Full close-from-non-draft (with its own button/form) is 9d.

### 9b.3 — Zone 2 in-app notifications

- Two notification nodes (or one with a multi-receiver config) inside the zone-2 success branch from 9b.1.
- **Receivers:**
  - Director — hardcoded user 12 (Dana), same convention as the PR director-approval node.
  - Finance head — `departments` record id `363554454962177` → `main_approver` (currently null; **gate this phase on the user setting it**).
- **Channel:** `approval-todo-in-app-message` (only existing in-app channel).
- **Message:** "PO {{po_number}} sent in zone 2 ({{total}}/{{fx_rate_to_usd}} USD vs PR budget {{purchase_request.quoted_total_usd}} USD). Override comment: {{budget_override_comment}}."
- If NocoBase 2.1 workflows lack a usable `notification` node type here, fall back to two `create` nodes against the in-app `messages` collection (the same one approval tasks land in). Decide during build after listing available node types.

### 9b.4 — UI buttons

- **Send PO** button on PO detail popup and PO table row popup (whichever pages already exist post-9a — locate during build):
  - `RecordTriggerWorkflowActionModel`, workflowKey = 9b.1 workflow key (set via `nb api resource update --resource flowModels`, per CLAUDE.md gotcha — `flow-surfaces configure` does not handle `workflowKey`).
  - Linkage rules: hide when `record.status != "draft"`; hide when `ctx.user.roles.title` does not include `"Procurement"` (same procurement-only pattern as Generate-PO).
- **Close PO** button — same surfaces, type `UpdateRecordActionModel` (not a workflow-trigger button). Opens an edit popup scoped to `close_reason` + `close_comment` (both required); Save commits these to the PO, which then fires the 9b.2 collection-trigger workflow. Linkage rules on the button: hide when `record.status != "draft"` (9d will broaden this); procurement-only.

### 9b.5 — Verify Z1/Z2/Z3 (manual, with user)

- Z1: PO total ≤ PR `quoted_total_usd` (e.g. equal). Click Send → status flips to `sent`, `sent_at` populated, no notification.
- Z2 (without comment): PO total between 100% and 110% of PR, `budget_override_comment` empty → Send blocked with the override-required message.
- Z2 (with comment): same total, comment filled → Send succeeds; Dana and the Finance main_approver receive an in-app notification.
- Z3: PO total > 110% → Send blocked with zone-3 message; nothing changes.
- Close-from-draft: draft PO + Close (reason=no_longer_required, comment filled) → status flips to `closed`, `closed_at` populated. Non-draft PO → Close button hidden (will be re-enabled by 9d).

## Critical files / surfaces to touch

- Live NocoBase env (no repo file edits): workflows under `flow_engine/workflows`, surfaces under `flowModels` on PO detail page (UID captured during build), `departments` row id `363554454962177`.
- After successful verification, update [project_current_state.md](../project_current_state.md): two new workflow keys + version IDs, button UIDs, status-enum change (removed `cancelled`), `close_reason` new option, dropped `cancelled_at` field.
- Append a D-entry to [decisions.md](decisions.md) capturing the **cancel-into-close collapse** (affects 9b, 9a definitions, 9d scope; supersedes PO design doc §3 + §8 guard #8). Add a second D-entry only if the build deviates further from this plan.

## Risks / open items

- **Finance main_approver is null** — blocking for 9b.3. User must set this first.
- **Existing POs in `cancelled` state** — verify count at build time; migrate any to `closed` before dropping the enum value.
- **Inline arithmetic in condition nodes** — NocoBase condition nodes accept handlebars expressions but division/multiplication inside `{{...}}` may need formula.js or a calculation node depending on this version. If the inline form doesn't evaluate, fall back to a single calculation node producing `po_total_usd` and `cap_usd` and branch on those.
- **Notification node availability** — if the workflow editor lacks a `notification` node in this NocoBase version, fall back to direct creates on the in-app messages collection.
- **No request-interception guard for status mutation in this MVP.** Direct status updates via bulk-edit or API still bypass these workflows. That belongs to the 9d immutability MVP; flag it but don't build it here.

## Verification

End-to-end runs in the live env at http://localhost:13000 against a fresh approved PR → Generate-PO → manually set PO `total` + `fx_rate_to_usd` to land in each zone → click Send / Cancel and observe status, audit timestamps, and notification icon for Dana + Finance head. No automated tests.
