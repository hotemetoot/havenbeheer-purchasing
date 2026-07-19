# Invariants — what must never be true, whatever path got you there

Draft 2026-07-19 (exploratory-testing pilot). This file is the contract that
exploratory sessions and scripted journeys check against. It complements
`plan.yaml`: a rule there tests one mechanism on one path; an invariant here
must hold after **every** action sequence, including ones nobody enumerated.
Where a runner rule already guards an invariant on some path, it's cited as
R#; "no runner coverage" marks the gaps exploration must probe.

Statuses are written as stored values here (this is a test doc, not a user
doc).

## Purchase requests

- **I1 — Status moves only through the flow.** No business role can write
  `status` (or `approved_at`, `submitterId`, stamped routing fields) directly,
  at any stage — not even the owner on their own `info_requested` PR. Only the
  approval workflow (and admin) moves it. *No direct runner coverage of the
  field-whitelist edge on the owner-update path.*
- **I2 — Terminal is forever.** `approved` / `rejected` PRs accept no edit and
  no delete from any business role, whatever the payload shape. (R43,
  Guard A.) Admin-only edits deliberately bypass — and then `committed_usd`
  does NOT follow (§3.5 of workflows-explained.md).
- **I3 — Routing matches the ladder.** Regular AND < 300 USD → no director;
  otherwise director; ≥ 15000 USD → board after director; approved-project
  link → procurement is final, no director/board regardless of amount.
  (R35, R36, R30.)
- **I4 — Only the assigned approver can act.** Submitting approve/reject on a
  pending approval record works only for the user the task is assigned to —
  not for another user of the same role, not for the submitter. *No runner
  coverage.*

## Projects and budget

- **I5 — Reserve on submit.** A new PR (create or re-link/amount edit) must
  fit: sum of the project's non-rejected PRs ≤ `budget_usd`, whatever payload
  shape carries the project id. (R28, guard; shapes per D70.)
- **I6 — Committed = sum of approved.** Immediately after every PR approval
  and every approved-PR delete, `committed_usd` equals the sum of
  `quoted_total_usd` over that project's approved PRs, and `remaining_usd` =
  `budget_usd − committed_usd`. (R29.)
- **I7 — Over-budget approval is impossible.** Procurement approving a
  project-linked PR that would push committed past budget auto-rejects it
  (strict >: exactly on budget passes). (R29.)
- **I8 — Only approved projects take PRs.** Draft, mid-ladder,
  info_requested, rejected, completed → link blocked. (R28.)
- **I9 — Projects are locked outside draft/info_requested** except through
  their flow and the Complete action (procurement + approved only). (R26,
  R27.)

## Purchase orders

- **I10 — PO only from an approved PR, one PO per PR.** (R15/R16.)
- **I11 — A PO never exceeds its PR.** Sum of line totals stays ≤ the source
  PR's approved `quoted_total`; the ceiling holds at every status and for
  every route a line can change (create, update, any payload shape). (R21,
  guard c9c14tyn876.) *Runner covers create; update/shape routes unproven.*
- **I12 — Lines total is honest.** `lines_total` on the PO converges to the
  sum of its lines' `line_total` after any line create/update (async, short
  lag) and immediately on delete. (R42.)
- **I13 — Issue freezes the paper.** Once a PO leaves draft, its lines accept
  only pure receiving entries — quantity/price edits, blanked values, or
  mixed receiving+edit payloads are refused; line deletes refused. (R44,
  R45, D87.)
- **I14 — Terminal PO is forever.** `completed` / `closed`: no updates by
  any business role. (R18.)
- **I15 — Status tells the receiving truth.** The PO's
  issued / partially_received / received status always matches its lines'
  received quantities — including after a received quantity is *reduced*.
  **VIOLATED — see F3 (2026-07-19 pilot):** reducing the last remaining
  receipt to zero leaves the order stuck at Partially Received with nothing
  received; the recompute has no "no receipts at all" branch.
- **I16 — Receiving is bounded.** `received_quantity` writable only in
  issued / partially_received / received, only by procurement (R22 — holds),
  and must be **between 0 and quantity_ordered**. **VIOLATED — see F1/F2:**
  over-receipt (999 against 10 ordered) and negative receipts are both
  accepted; nothing checks the value at all.
- **I17 — Print only in allowed stages.** **VIOLATED — see F4:** no
  server-side stage gate exists; `view` on the record is the only gate, and
  a plain member can read a draft PO. Print is a non-CRUD plugin action, so
  a workflow guard is not available — any fix is ACL- or UI-shaped.

## Cross-cutting

- **I18 — Hidden is not forbidden.** Every rule above must hold via the raw
  API; a linkage rule that hides a button is UI convenience, not enforcement.
- **I19 — Guards judge every payload shape.** `assoc: 5`, `assocId: 5`,
  `assoc: {id: 5}`, string ids — one rule, all shapes. (D70.)
- **I20 — Admin bypass is the only bypass.** Lock guards exempt admin/root
  (cleanup); rule-checking guards (budget, receive, create-PO, complete)
  exempt nobody, admin included.
