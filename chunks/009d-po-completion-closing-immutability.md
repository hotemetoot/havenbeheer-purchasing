# 009d — PO completion / closing + immutability

> **Reconciled to D28 (2026-06-07):** `cancelled` was collapsed into `closed`, so there is
> **no cancel action and no `cancelled` status**. "Cancel a draft" = close-with-reason, already
> built in 9b. The original "cancel" item below was removed.

## Goal
Procurement can complete a received PO or close a non-terminal one with a reason. Terminal POs
(and their lines) are immutable (same pattern as PR Guard A).

## Scope (in)
- **Complete action:** status `received → completed` (manual procurement action). Sets `completed_at`.
  - **D34 (2026-06-09):** Complete additionally requires an **attached invoice** (`invoice` non-empty)
    AND a **positive invoice total in USD** (`total_usd > 0`). Enforced in the workflow guard
    (server, hard stop) and mirrored on the Complete button linkage (UX hide). See decisions D34.
- **Close action (broadened):** status `draft / sent / confirmed / partially_received → closed`.
  Requires `close_reason` (single-select) + `close_comment` (textarea). Broadens the 9b draft-only
  Close (same `close_po_draft` workflow; guard edited in place). Sets `closed_at`.
  - `received` is **not** closeable — a received PO completes; to bail, correct a line down first
    (reverts to `partially_received`), then close. (User-confirmed.)
  - **D35 (2026-06-09):** because the Close workflow is a post-action event (can't reject/message),
    a Close attempt on a non-closeable PO (notably `received`) was silently ignored. Added a
    request-interception **Close Guard** (`b6brl8r9c58`) that rejects with a message. See decisions D35.
- **PO immutability guard** when status ∈ {completed, closed} — request-interception on
  `purchase_orders` (update + destroy), mirroring PR Guard A. D24 bulk-update limitation applies.
- **PO line immutability guard** when the parent PO is terminal — request-interception on
  `po_lines` (update + destroy). (Header + lines, user-confirmed.)

## Scope (out)
- Template printing (9e).
- Reopening closed/completed POs.
- Any cancel/`cancelled` path (removed — D28).
- Payment-field exemption on terminal POs (no payment UI/workflow exists yet; deferred to a
  future payment MVP — see D33).

## Dependencies
- Requires 9a, 9b, 9c.

## Acceptance
- C1: complete from `received` → `completed`, `completed_at` set; Complete hidden on non-received.
- C2: close from `sent` (and `partially_received`) → `closed`, reason + comment required,
  `closed_at` set; Close blocked/hidden on `received` and on terminal POs.
- C3: draft close still works (9b regression) → `closed`.
- C4: any header edit OR line edit/delete on a terminal PO → blocked; non-terminal still editable.
- C5: D24-style bulk-update limitation acknowledged; documented and deferred.
- Manual verification by user.

## Phases (as built)
- **9d.1** Complete PO workflow (`qh7b3hc5q1r`) + Complete button (**button built by user**).
- **9d.2** Close as a **post-action event** (`action`, local mode, key `f8gpu17s6hq`), bound to the Close EditForm Submit — captures `close_reason`/`close_comment`. (The first attempt used a `custom-action` workflow, which can't bind to a form Submit; deprecated.)
- **9d.3** Guard: PO Immutability (`xvcsdv07c5j`).
- **9d.4** Guard: PO Line Immutability (`f3dkb37te22`).
- **9d.5** Verify C1–C5 (pending user UI wiring).

See [decisions.md](../decisions.md) D33 and `project_current_state.md` for live IDs and node keys.
