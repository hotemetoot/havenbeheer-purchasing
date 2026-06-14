# Manual Workflow Test Walkthrough

A click-through acceptance pass for the whole PR → PO lifecycle. Walk it top to bottom; tick each
`- [ ]` as you confirm the **Expected** result. Start from an empty data set (PRs/POs/lines are
currently 0). Cases are ordered so earlier artifacts feed later ones — don't skip the PR-approval
section if you intend to run the PO section.

- **App:** http://localhost:13000 · **Version:** NocoBase 2.1.0-beta.47
- **Drafted:** 2026-06-13 against live active workflow versions (PR Approval `369536223739904`).
- **How to switch users:** log out / log in as each test user (passwords as configured; `fiona.finance` = `Test1234!`). Roles are per-user; the role switcher in the user menu only matters where a user holds >1 role.
- **Result key:** tick the box when **Expected** is met. Write `FAIL: …` inline if not.

---

## Reference

### Test users
| User | ID | Dept | Role | Is dept main-approver? |
|---|---|---|---|---|
| alice.member | 9 | Operations | operations | no |
| oliver.owner | 10 | Operations | operations | **yes (Operations)** |
| pat.procurement | 11 | Procurement | procurement | **yes (Procurement)** |
| dana.director | 12 | Director | director | **yes (Director)** |
| simon.supervisor | 13 | Operations | operations | no |
| fiona.finance | 14 | Finance | finance | **yes (Finance)** |

### Who approves what (assignee resolution — all data-driven, D40)
| Stage | Assignee | = user |
|---|---|---|
| Dept owner | submitter's dept main-approver | Operations PR → **Oliver** |
| Custom approver | the picked user | whoever the submitter selects |
| Procurement | Procurement dept main-approver | **Pat** |
| Director | Director dept main-approver | **Dana** |
| Board | Procurement dept main-approver | **Pat** (same person as Procurement — expected) |

### Status values
`draft` → `pending_dept_approval` → `pending_purchasing_review` → `pending_director_approval` → `pending_board_approval` → `approved` / `rejected` / `info_requested`.

### Routing thresholds (USD)
- **Director required** when `is_regular != true` **OR** `quoted_total_usd ≥ 300`. (Procurement sets `is_regular` on their approval form.)
  - To approve **without** Director: must be `is_regular = true` **AND** `< 300`.
  - Sub-$300 but **not** regular ⇒ still goes to Director (D37 default flip).
- **Board required** when `quoted_total_usd ≥ 15000` (evaluated after Director approves). Board approval requires an uploaded `board_approval_document`.

### Budget zones on Send PO (PR USD = `quoted_total_usd`, PO USD = `total / fx_rate_to_usd`)
| Zone | Condition | Behaviour |
|---|---|---|
| 1 | PO USD ≤ PR USD | Sends straight through |
| 2 | PR USD < PO USD ≤ 1.1 × PR USD | Requires `budget_override_comment`, else **blocked** |
| 3 | PO USD > 1.1 × PR USD | **Blocked** outright |

### Value tip
Use **USD, fx_rate_to_usd = 1** on every PR/PO so `quoted_total_usd = quoted_total` and `total_usd = total` — keeps the threshold math trivial.

---

## Section A — PR Approval routing & assignees

> Unless stated, create PRs as **alice.member** (Operations) with `quoted_currency=USD`, `fx_rate_to_usd=1`. Title them so you can find them (e.g. "A2 normal").

### A1 — Submitter IS dept head → dept stage skipped
- [ ] As **oliver.owner** (Operations main-approver), create + submit a PR (any amount, e.g. $250, `is_regular` will be set later).
- [ ] **Expected:** status goes directly to `pending_purchasing_review` (no `pending_dept_approval`, no dept task). Oliver gets **no** dept-approval task.

### A2 — Normal dept approval (approve)
- [ ] As **alice**, create + submit a PR ($250).
- [ ] **Expected:** status = `pending_dept_approval`; **Oliver** has an approval task.
- [ ] As **oliver**, open the task → **Approve**.
- [ ] **Expected:** status = `pending_purchasing_review`; **Pat** now has a Procurement task.

### A3 — Custom approver (reassign dept stage + FYI to dept head)
- [ ] As **alice**, create a PR; tick **Use custom approver**; pick **simon.supervisor** (same-dept, not self). Submit.
- [ ] **Expected:** status = `pending_dept_approval`; the dept task goes to **simon** (not Oliver); **Oliver** receives an FYI in-app notification ("reassigned to custom approver").
- [ ] As **simon**, **Approve**.
- [ ] **Expected:** status = `pending_purchasing_review`; Pat has the Procurement task.
- [ ] *(Negative)* As **alice**, confirm the picker will **not** let you select yourself, and only lists Operations users.

### A4 — Regular + under $300 → approved directly (no Director)
- [ ] Use the A2 PR (now at Procurement, $250) **or** make a fresh $250 one through dept approval.
- [ ] As **pat**, open the Procurement task; tick **`is_regular`**; **Approve**.
- [ ] **Expected:** status = `approved` (no Director task, no Board). `approved_at` stamped.

### A5 — Under $300 but NOT regular → Director required (default flip, D37)
- [ ] Fresh $250 PR through dept approval to Procurement.
- [ ] As **pat**, **Approve** *without* ticking `is_regular`.
- [ ] **Expected:** status = `pending_director_approval`; **Dana** has a task. (Demonstrates sub-$300 defaults to Director.)
- [ ] As **dana**, **Approve** → **Expected:** status = `approved` (under $15k, no Board).

### A6 — Mid-value → Director, no Board
- [ ] Fresh PR **$5,000**; dept-approve (Oliver) → Procurement.
- [ ] As **pat**, **Approve** (is_regular irrelevant; ≥ $300 forces Director).
- [ ] **Expected:** `pending_director_approval`; Dana has a task.
- [ ] As **dana**, **Approve** → **Expected:** `approved` (no Board, < $15k).

### A7 — High-value → Board with required document (≥ $15k)
- [ ] Fresh PR **$20,000**; dept-approve (Oliver) → Procurement.
- [ ] As **pat**, **Approve** → **Expected:** `pending_director_approval`; Dana task.
- [ ] As **dana**, **Approve** → **Expected:** `pending_board_approval`; **Pat** now has a **Board** task.
- [ ] As **pat**, open the Board task; try **Approve with no document** → **Expected:** blocked (the `board_approval_document` field is required).
- [ ] Attach a document; **Approve** → **Expected:** status = `approved`, `approved_at` stamped, document stored.

### A8 — Return at dept stage (→ info_requested → resubmit)
- [ ] Fresh PR as **alice**; status `pending_dept_approval`.
- [ ] As **oliver**, **Return** (request info) with a comment.
- [ ] **Expected:** status = `info_requested`; the PR is editable again by **alice** (own + `info_requested` window).
- [ ] As **alice**, edit a field and re-submit.
- [ ] **Expected:** status returns to `pending_dept_approval` and the cycle resumes.

### A9 — Return at Procurement stage
- [ ] Take any PR to `pending_purchasing_review`.
- [ ] As **pat**, **Return** with a comment → **Expected:** `info_requested`, editable by submitter.

### A10 — Reject at Director
- [ ] Take a ≥ $300 PR to `pending_director_approval`.
- [ ] As **dana**, **Reject** with a reason → **Expected:** status = `rejected` (terminal); PR no longer editable by submitter (see B/immutability spirit — PR Guard A blocks edits on terminal PRs).

### A11 — Reject at Board
- [ ] Take a $20k PR to `pending_board_approval` (via A7 steps).
- [ ] As **pat**, **Reject** the Board task → **Expected:** status = `rejected`.

### A12 — PR immutability when terminal (Guard A)
- [ ] On a `rejected` or `approved` PR, as the submitter try to edit any field and save.
- [ ] **Expected:** blocked with the immutability message (single-record edit). *(Known D24 gap: bulk-update is not intercepted — single-record only.)*

---

## Section B — Purchase Order lifecycle

> PO work is done as **pat.procurement**. You need at least one `approved` PR with a known
> `quoted_total_usd` to generate a PO. Reuse A6's approved $5,000 PR (PR USD = 5000) for the
> Send-zone math below, or approve a fresh one.

### B1 — Generate PO (number derivation)
- [ ] As **pat**, open an `approved` PR (e.g. PR-26-00xx) → click **Generate PO**.
- [ ] **Expected:** a new PO is created in `draft`; its `po_number` mirrors the PR number with `PR-`→`PO-` (e.g. PR-26-0001 → PO-26-0001). The PR's Generate-PO button disappears (already has a PO).

### B2 — Create-PO guard (non-approved PR blocked)
- [ ] Find a PR that is **not** `approved` (e.g. one in `pending_*`). The Generate-PO button should be hidden for non-approved / non-Procurement.
- [ ] *(Server stop)* If you can trigger a PO create against a non-approved PR, **Expected:** blocked by the Create-PO guard with a message. (Button visibility already prevents the normal path.)

### B3 — Send PO, Zone 1 (≤ PR USD)
- [ ] On the B1 draft PO, as **pat** set `fx_rate_to_usd = 1` and `total = 5000` (= PR USD). Save.
- [ ] Click **Send PO**.
- [ ] **Expected:** status = `sent`, `sent_at` stamped (Zone 1, no comment needed).

### B4 — Send PO, Zone 2 without comment → blocked
- [ ] New approved PR with PR USD = 1000 → Generate PO. Set `total = 1050`, `fx_rate_to_usd = 1` (PO USD 1050; 1000 < 1050 ≤ 1100 → Zone 2). Leave `budget_override_comment` empty.
- [ ] Click **Send PO** → **Expected:** blocked, message asks for an override comment; status stays `draft`.

### B5 — Send PO, Zone 2 with comment → sent
- [ ] On the same PO, fill `budget_override_comment`. **Send PO**.
- [ ] **Expected:** status = `sent`.

### B6 — Send PO, Zone 3 (> 110%) → blocked
- [ ] New approved PR with PR USD = 1000 → Generate PO. Set `total = 1200`, `fx_rate_to_usd = 1` (PO USD 1200 > 1100). **Send PO**.
- [ ] **Expected:** blocked (Zone 3) regardless of comment; status stays `draft`.

### B7 — Receiving, partial
- [ ] On a `sent` PO with at least one line (add a line via the Line Items tab if needed: description + quantity_ordered, e.g. qty 10), as **pat** set `received_quantity = 4` on the line.
- [ ] **Expected:** line `line_status = partially_received`; PO `status = partially_received`.

### B8 — Receiving, full → received + notify
- [ ] Set `received_quantity = 10` (= ordered) on every line.
- [ ] **Expected:** each line `line_status = received`; PO `status = received`; **Pat** gets an in-app "ready to complete" notification.

### B9 — Complete PO (happy path)
- [ ] On the `received` PO, attach an **invoice** and set a positive `total_usd` (ensure `total` + `fx_rate_to_usd` give `total_usd > 0`).
- [ ] Click **Complete** → **Expected:** status = `completed`, `completed_at` stamped.

### B10 — Complete blocked: no invoice
- [ ] Take another PO to `received` with **no invoice** attached. The Complete button should be hidden; if forced, **Expected:** server guard rejects with "invoice required".

### B11 — Complete blocked: not received / zero USD total
- [ ] On a `sent` (not received) PO, attempt Complete → **Expected:** blocked ("only for a fully-received PO with an invoice total").
- [ ] On a `received` PO with `total_usd = 0`, attempt Complete → **Expected:** blocked by the server guard (`> 0`).

### B12 — Close PO from a non-terminal state
- [ ] On a `sent` (or `draft`/`confirmed`/`partially_received`) PO, click **Close**, fill `close_reason` (+ comment), Submit.
- [ ] **Expected:** status = `closed`, `closed_at` stamped.

### B13 — Close guard: blocked on `received`
- [ ] On a `received` PO, click **Close**, fill `close_reason`, Submit.
- [ ] **Expected:** blocked with a message (the Close Guard); `close_reason` is **not** persisted, status stays `received`. *(To bail a received PO, revert a line down to `partially_received` first.)*

### B14 — Immutability: header edit on a terminal PO
- [ ] On a `completed` (B9) or `closed` (B12) PO, edit any header field and save.
- [ ] **Expected:** blocked ("This PO is finalized and can no longer be edited").

### B15 — Immutability: line edit on a terminal PO
- [ ] On a `completed`/`closed` PO, try to edit or delete a line.
- [ ] **Expected:** blocked ("Lines of a finalized PO can no longer be edited").

### B16 — Immutability: add a NEW line to a terminal PO (D45)
- [ ] On a `completed`/`closed` PO, try to **add** a new line item.
- [ ] **Expected (UI):** the add-line form is hidden on terminal POs (frontend control).
- [ ] **Expected (server, direct API):** a direct `po_lines:create` naming a finalized PO is rejected — "Cannot add a line to a finalized (completed or closed) PO" (guard `polncreateg1`). *Note: the association add-line route is covered by the hidden form, not the guard — see D45.*

---

## Section C — ACL / permissions

### C1 — member is view-only
- [ ] As **alice** but **switch to the bare `member` role** (if available in the switcher), confirm you can view but not create/edit PRs or POs.
- [ ] **Expected:** no New/Edit actions where `member` has only `view`.

### C2 — operations create + edit-own window
- [ ] As **alice** (operations), confirm you **can** create a PR and edit your **own** PR while `draft`/`info_requested`.
- [ ] **Expected:** you **cannot** edit a PR once it's `pending_*`/`approved`/`rejected`, and cannot edit someone else's PR.

### C3 — procurement cannot create a PR
- [ ] As **pat**, go to Purchase Requests.
- [ ] **Expected:** no "New PR" create action (D25 — procurement create/import removed). Pat can still view all PRs and act on Procurement tasks.

### C4 — workflow-managed fields are read-only
- [ ] As any non-admin, confirm `status`, `po_number`, `approved_at`, stamps, `line_status` are **not** user-editable on forms (and a direct API PATCH of `status` is rejected by the field whitelist).
- [ ] **Expected:** these columns are display-only; status only changes via the workflows.

### C5 — director / finance see approvals and the form renders
- [ ] As **dana** (director) confirm the Director approval ProcessForm **renders fully** (not blank) when a task is open.
- [ ] As **fiona** (finance) confirm desktop routes are present and PRs are viewable (no finance approval stage exists yet — view + render-enabler only).

---

## Appendix — reset between runs

The walkthrough leaves PRs/POs behind. To return to a clean slate, ask Claude to wipe
transactional data (PRs / POs / po_lines + cascaded approval records) — the same "fresh-slate"
operation used on 2026-06-13. Workflows, roles, templates, and lookups (suppliers, products,
UoM, delivery addresses) are untouched by that wipe.

> Coverage map: A1–A12 = PR Approval `369536223739904` (skip / custom-approver / regular-flag /
> $300 floor / $15k board / return / reject / immutability). B1–B15 = Generate PO `2izsx8uv50r`,
> Create-PO guard `vgv8hcrtjvx`, Send PO `send_po`, Receiving `ork27v016yo` + Receive guard
> `mhfp4d15uee`, Complete `qh7b3hc5q1r`, Close `f8gpu17s6hq` + Close guard `b6brl8r9c58`,
> immutability guards `xvcsdv07c5j` / `f3dkb37te22` / line-create `polncreateg1` (D45).
> C1–C5 = role hardening (D38–D40).
