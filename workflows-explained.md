# How the approval workflows actually work — plain-English reference

Written 2026-07-16 from the live app (enabled revisions read node by node, every
threshold quoted from the actual condition — not from memory or old plans).
Companion to `role-acl-guidelines.md` (who may click what) — this file covers
what happens *after* the click. Update it when a workflow changes; the D-entry
that changes a workflow should also touch this file.

Verified against: PR Approval revision `376242882347008`, Project Approval
`376252879470592` (both current since 2026-07-19, D88), and the guard/recompute
revisions current on 2026-07-19 (PO side: D87 line freeze, D89 payload-shape
hardening, the receiving roll-up correction — see footnote 4).

---

## 1. The big picture

Three kinds of records move money:

- A **purchase request (PR)** — "I need to buy cables for $1,000." It must be
  approved by people before anything is ordered.
- A **project** — a pre-approved budget envelope, e.g. "Pier B upgrade,
  $10,000." PRs can draw against it.
- A **purchase order (PO)** — the actual order sent to a supplier, generated
  from an approved PR. (PO lifecycle has its own guards; out of scope here,
  listed briefly at the end.)

Two mechanisms enforce the rules:

- **Approval workflows** — the routing ladders. They decide *who must say yes*
  and move the record's status along.
- **Guards** — safety nets that inspect a save/delete request *before* it
  touches the database and block it with an error message if it breaks a rule.
  (Technical name: "request-interception workflow" — it intercepts the HTTP
  request.) The **lock** guards exempt admin so cleanup stays possible; the
  **rule-checking** guards bind everyone, admin included (§4).

---

## 2. A purchase request's journey

Olga from Operations submits a PR: "Replacement mooring cleats, $1,000."
Here is every fork in the road, in order, with the real numbers.

### Stage 1 — the department stage

The moment the PR enters the flow, it gets status **Pending Dept Approval**,
and the workflow stamps who submitted it and their department onto the record.

Three ways this stage can go:

- **Normal case:** the approval task lands with the **main approver of Olga's
  own department**. If Oscar is Operations' main approver, Oscar gets the task.
- **Head-skip:** if the submitter *is* their own department's main approver
  (Oscar submits his own PR), the dept stage is skipped entirely — nobody
  reviews their own request at their own stage. Status jumps straight to
  Pending Purchasing Review.
- **Custom approver:** if the submitter ticked "Choose a custom approver" and
  picked someone (who isn't themselves), that person replaces the dept head
  for this stage. The dept head gets an FYI notification ("this PR was routed
  to a submitter-chosen approver instead of you") but no task.

Whoever holds the task can **Approve** (→ Pending Purchasing Review),
**Return** (→ Info Requested — the submitter fixes it and resubmits), or
**Reject** (→ Rejected, flow over, their comment is stored as the rejection
comment).

### Stage 2 — procurement review

The task goes to the **Procurement department's main approver** (currently
Pat). This is where the quote gets entered/checked (amount, currency,
supplier, quotation attachment). Same three buttons: Approve / Return /
Reject.

Procurement's **Approve** is the big fork. The workflow asks, in this order:

### Fork A — is this a project drawdown?

**Condition (verbatim): the PR has a project linked AND that project's status
is `approved`.**

If yes, the PR takes the project branch — **skipping the director and board
entirely.** Procurement is the final human step for project-linked PRs (that's
deliberate: the envelope was already approved by the director when the project
itself went through its ladder). What happens on this branch is in §3.

If no project is linked, continue to Fork B.

### Fork B — is the director required?

**Condition (verbatim): director required if `is_regular != true` OR
`quoted_total_usd >= 300`.**

In words: the director sees everything except *regular* purchases under $300.

- Regular purchase, $250 → **approved right here**, no director. The submitter
  and their dept head get an "approved" notification; procurement doesn't,
  because procurement is the one who just approved it.
- Regular purchase, exactly $300 → director required (the 300 is inclusive).
- Non-regular purchase, even $100 → director required. ("Regular" is a
  procurement-set flag meaning routine/recurring; anything not flagged goes
  up.)

The director (Director department's main approver — Dana) can Approve /
Return / Reject. Return sends it back to Info Requested (the director's return
targets the procurement stage — procurement's task re-opens after resubmit).

### Fork C — is the board required?

After the director approves:

**Condition (verbatim): `quoted_total_usd >= 15000`.**

- $14,999 → the director's approve is final → **Approved**.
- $15,000 exactly → one more stage: **Pending Board Approval**.

The board stage's approve makes it Approved; reject ends it.

> **Quirk to know:** the board stage's task is assigned to the **Procurement
> main approver**, not a separate board person. That is intentional (D63): the
> real board approves on paper, and procurement uploads the board's signed
> document as the approval artifact. Don't "fix" this without a decision.

Every terminal Approve on any branch stamps `approved_at`.

### Who gets told when it ends (D88, 2026-07-19)

The moment a PR is **Approved or Rejected**, three people get an in-app
message: the **submitter**, the **head of the submitter's department**, and the
**head of Procurement**. Two exceptions:

- **Whoever made the decision is never notified.** They just clicked the
  button. So a dept-head rejection tells the submitter and nobody else; a
  director rejection tells the submitter, the dept head, and Procurement — but
  not the director.
- **Procurement is skipped when the request never reached them.** A rejection
  at the department or custom-approver stage dies before Procurement ever sees
  it, so they hear nothing about it.

Rejection messages name the stage — "was rejected at the director stage" — so a
reader knows where it died without opening the record. **Returned — Info
Requested sends nothing**, deliberately: a returned PR already shows up in the
submitter's to-do list.

The same rule runs on the project ladder (§3.1), with one difference: projects
have no "Procurement is final" path, so that exception never arises there.

How it works, in case you ever move a node: the recipient list is hardcoded per
node rather than worked out at runtime. Each terminal node sits on exactly one
approver's branch, so "who acted" is known from *where the node is* in the
graph. Move a terminal node to a different branch and its recipient list
becomes wrong with nothing to warn you.

---

## 3. Projects: the budget envelope system

### 3.1 Getting an envelope approved

A project ("Pier B upgrade, budget $10,000, justification …") goes through its
own ladder, very similar to the PR one:

1. **Dept stage** — same head-skip rule as PRs.
2. **Procurement review.**
3. **Director — always.** Unlike PRs, there is no $300 shortcut: every budget
   envelope is reviewed by the director regardless of size.
4. **Board — only if `budget_usd >= 15000`** (the project's own budget field,
   same inclusive threshold, same procurement-holds-the-board-task quirk).

Until it reaches **approved**, the project is just a request; nothing can draw
against it.

When the project finally lands on **Approved or Rejected**, the same
notification rule as the PR ladder applies (§2, "Who gets told when it ends") —
submitter, dept head, head of Procurement, minus whoever made the decision, and
minus Procurement when a dept-stage rejection killed it before they saw it.

### 3.2 Linking a PR to a project

When Olga creates a PR and picks a project, a guard checks **at save time**:

- **The project must be status `approved`.** Linking to a draft, mid-ladder,
  rejected, or completed project is blocked with an error.
- **The money must fit.** The guard sums up what the project's other PRs
  already claim and checks the new PR wouldn't push past `budget_usd`.

The create-time guard counts **every child PR that isn't rejected or
cancelled** — including ones still mid-approval. (The filter still names
`cancelled`; that status no longer exists on PRs, so the clause is a harmless
no-op — D84.) That's "reserve on submit"
(D49): if two people each submit a $6,000 PR against a $10,000 project, the
second one is blocked at submit, not at approval. First come, first reserved.

The same checks run when someone *edits* a PR's amount, exchange rate, or
project link (with one difference — see §3.5).

### 3.3 The drawdown decision at approval time

When Pat approves a project-linked PR (Fork A in §2), the workflow does the
authoritative money check:

1. **Add it up** (aggregate node "Project committed"): the sum of
   `quoted_total_usd` over the project's PRs that are **already approved, plus
   this PR itself** — the one being approved right now, explicitly included by
   its id.
2. **Compare** (condition "Over project budget?", verbatim):
   `that sum > budget_usd` — strict greater-than, so landing exactly on budget
   still passes. Budget $5,000, approved siblings $4,000, this PR $1,000 →
   total $5,000 → **approved**.
3. **Over budget** → the PR is auto-**rejected** with a comment that names the
   numbers ("would bring committed to 14,500 USD, over its 5,000 USD budget"),
   and the submitter, their dept head, and the head of Procurement are all
   notified (D88 — Procurement is told here precisely because the system just
   overturned an approval they had given). This is the backstop for anything that
   slipped past the submit-time guard (D53: the approval form's own writes
   bypass guards, so the check must live inside the workflow).
4. **Within budget** → status becomes **approved**, and then —

### 3.4 Writing the committed amount (D78, 2026-07-16)

— the very next node, **"Write committed_usd to project"**, writes that same
sum onto the project's `committed_usd` field. The project card immediately
shows: Budget 5,000 / Committed 5,000 / Remaining 0.

Why inside the workflow? Because this is the only place that *knows* the
approval just happened. The old design (a separate "recompute" workflow that
listened for PR changes) never heard about approvals — the approval's own
status write is a silent batch write (see §5) — so Committed lagged one
approval behind, showing 0 when it should have shown 1,000. That standalone
create/update recompute is now **disabled**. Don't re-enable it: if both
mechanisms ran, the old one could overwrite the correct number with a stale
one.

`remaining_usd` is a **formula field** — `budget_usd - committed_usd`,
recomputed whenever the project record is saved *with events firing* (again
§5). It is never written directly by anyone.

### 3.5 When committed goes *down*

Only one normal path decreases commitment: **deleting an approved PR**. A
small dedicated workflow ("Project Commit: recompute (delete)") hears the
delete, re-sums the remaining approved siblings, and writes the new total.
Delete a $1,500 approved PR → committed drops by 1,500, remaining rises.

There's no other decrease path, and that is safe because approved PRs are
locked (§4, Guard A): nobody but admin can cancel one, change its amount, or
flip its status. If an admin edits an approved PR's numbers by hand anyway,
committed will NOT update — admin bypasses everything, on purpose.

Note the deliberate asymmetry with §3.2: the **submit-time** guard counts all
non-rejected PRs (reservations), but **committed_usd** counts
only *approved* PRs (real commitments). A project can therefore have
"remaining" room on its card while the submit guard still blocks a new PR,
because pending PRs hold reservations that aren't committed yet.

### 3.6 Closing a project

"Complete Project" is a button (not an automatic rule). Its workflow checks
two things and refuses otherwise: the caller must hold the procurement role,
and the project must be `approved`. It then sets status `completed` and stamps
`completed_at`. Completed projects can't take new PRs (§3.2 blocks — not
approved anymore).

---

## 4. The guards, one by one

"Guard" = a workflow that runs synchronously inside the save/delete request,
and either lets it through or cancels it with an error message. Admin (and
root) are exempt from every **lock** guard — the ones that freeze finished
records (PR Immutability, Project Immutability, the PO-side locks — PO
Immutability, PO Line Immutability, PO Line Destroy (D82) — and the PO Line
Freeze guard, D87).
That keeps cleanup possible without disabling guards. The **rule-checking**
guards (Create PO, budget ceilings, Close, Receive, line-create) apply to
everyone, admin included. UI-side you find them in the workflow list as type
"Pre-action event".

| Guard | Watches | Rule in one line |
|---|---|---|
| **Guard A — PR Immutability** | PR edits + deletes | If the PR's status is `approved` or `rejected` → "This record is locked and cannot be modified." Nothing terminal changes, ever, except by admin. (Until 2026-07-18 the condition also tested `cancelled`; that status was removed from PRs, so the clause was dropped — see D84.) |
| **PR Budget (create)** | New PRs | Project must be approved; new PR's USD amount + all non-rejected siblings must fit the budget (reserve-on-submit, §3.2). Handles every payload shape for the project id — `project: 5`, `projectId: 5`, `project: {id: 5}` — so it can't be dodged by formatting (D70 lesson). |
| **PR Budget (update)** | PR edits | Same checks, but only when the edit touches amount, fx rate, or project link; sums approved siblings only, excluding the PR being edited. |
| **Project Immutability** | Project edits + deletes | Everything except `draft` and `info_requested` is locked. Once submitted, a project changes only through its approval flow or the Complete button. |
| **Create PO (PR must be approved)** | New POs | The source PR must be `approved` and must not already have a PO → otherwise "Cannot create PO: purchase request must be approved and must not already have a PO." Handles every payload shape for the PR id — `purchase_request: 5`, `purchaseRequestId: 5`, `purchase_request: {id: 5}` — and refuses outright, with "Cannot determine which purchase request this PO is for.", when none of them names a request (021, same fix as the PR Budget guards). |
| **Complete Project** (button guard) | The Complete button | Procurement role only; approved projects only. |
| **Generate PO** (button guard) | The Generate PO button | PR must be `approved` and must not already have a PO (PR→PO is 1:1). Then it creates the draft PO, copying supplier/currency/amount, deriving PO-26-xxxx from the PR number. |

Concrete example of the layering: Pat wants to fix a typo in an approved PR's
description. ACL says procurement *may* update PRs (the permission is broad).
Guard A says **no — it's approved, it's locked.** The layers are independent:
permissions decide who may try; guards decide what states allow it. That's
also why the immutability guarantee (and with it §3.5) depends on Guard A
staying **enabled** — the ACL alone would let procurement edit approved PRs.

---

## 5. Batch vs. one-by-one updates (the `individualHooks` thing)

Every "Update record" node inside any workflow has an **Update mode** setting,
visible in the node's edit form in the workflow designer:

- **Batch update** (the default): writes the rows in one database statement.
  Fast — but **silent**: no save-events fire. Formula fields on that record do
  NOT recalculate, and no other workflow that "listens for changes" on that
  collection will hear it.
- **Update one by one**: loads each row, saves it properly, and each save
  fires the normal events — formulas recalculate, listening workflows trigger.

Neither is "right" — they're a deliberate choice per node:

- The PR Approval workflow flips PR statuses with **batch** writes on purpose.
  If those fired events, every collection-event workflow watching
  `purchase_requests` would run on each status hop — that's exactly the noise
  we don't want (and, historically, exactly why the old recompute never heard
  approvals — batch writes are inaudible).
- The two nodes that write `committed_usd` onto **projects** ("Write
  committed_usd to project" in PR Approval; "Write committed_usd" in the
  delete recompute) use **one-by-one** on purpose: `remaining_usd` is a
  formula and only recalculates on an event-firing save. Verified before
  choosing this: **nothing listens for `projects` changes today**, so the only
  side effect is the wanted formula refresh. No loops: those writes target
  `projects`, and the workflows that listen listen on `purchase_requests`.

**Rules of thumb for future workflow design:**

1. Writing a plain field, want no side effects → **batch** (default).
2. The target record has a **formula field** that must stay correct → **one
   by one**, and first check what else listens on that collection
   (workflow list → filter by collection, trigger type "Collection event").
3. Adding a **collection-event workflow** on a collection? Grep the existing
   workflows for update nodes that write to it in batch mode — those writes
   will be invisible to your new workflow. That invisibility is the root
   cause of the original committed_usd bug (D78).
4. Record every choice like this in the D-entry so the next reader knows it
   was a decision, not an accident.

These are all normal per-node settings you can inspect and change in the
workflow designer UI — nothing here lives outside it. (One workflow-level
setting from D79, also UI-visible under the workflow's own settings: sync
guards keep their execution history — "delete executions on success" is off.
Leave it off; see D79 for the race it prevents.)

---

## 6. Honest footnotes (real quirks, verified live)

1. **Board tasks go to procurement's main approver** in both ladders —
   intentional (D63), the board signs on paper. See §2 Fork C.
2. **Three different "committed total" formulas exist** and they are *meant*
   to differ: submit guard = all non-rejected (reservations, D49);
   approval-time aggregate = approved + this PR (the commit moment, D53/D78);
   delete recompute = approved only (what remains). If you change one, decide
   explicitly whether the others should follow — and there's a test rule per
   boundary (tests/plan.yaml R28/R29).
3. ~~Some notification nodes carry stale display titles.~~ **Fixed 2026-07-19
   (D88).** The three PR Approval nodes *titled* "Notify dept head — PR
   reassigned…" that actually sent "PR approved" were renamed during 017's
   revision. One node still legitimately carries that title — `5h232imw9ss`,
   which really is the reassignment notice. Don't "fix" that one.
4. **PO lifecycle** (not covered in the same depth): Create-PO guard,
   PO/PO-line immutability guards, per-line budget ceiling at the approved PR
   amount (D47), and Issue/Receive/Complete/Close actions with their own
   guards. Since 2026-07-19 also: **lines freeze at issue** — once a PO
   leaves Draft, the only line change allowed is a plain receiving entry
   (D87); the lines-total recompute runs **in the background and reloads the
   line first**, so import-created rows are counted even though their PO link
   is empty at trigger time (D83); the receiving roll-up walks an order
   **back to Issued** when a correction leaves no line with anything received
   (chunk 020); and the two line-create guards **resolve the parent order id
   themselves** at the head of the chain, refusing when they can't tell which
   order the line belongs to, instead of trusting the submitted association
   shape (D89 — a nested `{id: …}` payload used to crash them into an HTTP
   500). Same guard concepts as §4 throughout.

---

*Sources: live node reads 2026-07-16 and live workflow descriptions re-read
2026-07-19, decisions.md D37/D47/D49/D53/D63/D70/D78/D79/D82–D89,
tests/plan.yaml R25–R39.*
