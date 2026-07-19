# 018 — Stranded project commitment when a PO is closed

**Status:** planned, not built. **Low priority** — rare in practice, no data loss, no wrong money leaves the building. Scoped 2026-07-18 from PO-26-0468.
**Relates to:** D78 (committed_usd written at approval), D49 (reserve on submit), MVP 014.
**Deliberately rejects:** automatic release of commitment on PO close. See §3 — it opens a fraud path.

---

## 1. The problem

Close a PO and the money stays committed on the project forever. There is no way to get it back short of deleting the approved purchase request.

### The live case

**PRJ-26-0123** "small project" — budget $5,000, committed $4,900, remaining $100.

Of that $4,900, **$4,500 is PR-26-0468**. Its purchase order, **PO-26-0468**, was closed on 18 July with reason "No longer required". The supplier never delivered, nothing was invoiced, nothing will be paid. The project still shows only $100 of room.

### Why it happens

`committed_usd` counts purchase requests with status **Approved**, and nothing else. The PR status list ends at Approved — there is no state after it. Closing a purchase order writes nothing back to its purchase request, and no workflow listens for a PO close to recompute the project. Meanwhile "Guard A — PR Immutability Guard" locks approved PRs, so nobody but admin can change one.

Per §3.5 of [workflows-explained.md](../workflows-explained.md), the only path that decreases commitment is **deleting** the approved PR. Deleting the record to free the budget destroys the audit trail of a purchase that genuinely happened and was genuinely cancelled. That is not an acceptable fix.

### The same gap, two more ways

Worth knowing, both out of scope here:

- A PO **completed for less than the PR quoted** — $3,000 delivered against a $4,500 request — still commits the full $4,500.
- A PO issued at a different exchange rate than its PR does the same.

All three share one root cause: commitment is measured off the *request* and never re-measured against what actually happened.

---

## 2. The solution

**The director raises the project's budget.** There is no release mechanism.

When a project-linked PO is cancelled and the department genuinely needs to re-spend that money, the director increases `budget_usd`. Committed stays where it is; remaining goes up because `remaining_usd` is the formula `budget_usd - committed_usd`.

So for PRJ-26-0123: the director raises the budget from $5,000 to $9,500. Committed stays $4,900, remaining becomes $4,600, and the department can raise a replacement request.

### Why this and not a release

Three reasons, in order of weight:

1. **It puts the decision with the only person who has authority over the envelope.** Project-linked PRs skip the director entirely (Fork A) — the envelope *is* the director's control, and the sole one. Giving budget room back is therefore a director-level act by definition.
2. **It leaves an honest audit trail.** "The director increased this project's budget on 18 July" is a true and readable statement. A silent reset to a lower committed figure is not — it makes the money look unspent when it was spent and cancelled.
3. **It costs almost nothing.** Cancelled project POs are rare. A click per occurrence is cheaper than any mechanism, and cheaper than the risk in §3.

### Story check

> Olga's $4,500 order for PRJ-26-0123 is cancelled — the supplier can't get the parts. She still needs them, from someone else. Pat (procurement) can't approve a new $4,500 request: the project shows $100 remaining and the submit guard blocks her at save time. Dana (director) opens PRJ-26-0123, raises the budget to $9,500 with the reason "PO-26-0468 cancelled, supplier unable to fulfil, re-sourcing", and Olga's replacement request goes through.

> Same cancellation, but the parts are no longer needed. Nobody does anything. The project keeps showing committed $4,900 of a $5,000 budget, which is what actually happened: the money was committed, then the order was cancelled. The project is closed with $100 unspent on paper.

---

## 3. Why NOT auto-release on PO close

Recorded so a later session doesn't "fix" §1 the obvious way.

Releasing commitment automatically when a PO closes hands the release lever to **procurement — the same role that approves project-linked purchase requests**. That is a closed loop with no outside observer:

> Approve PR → issue PO → receive the goods → close the PO → commitment released → approve the next PR against the freed room.

Ten cycles against one director-approved $5,000 envelope spends $50,000, and the director's view still reads "budget 5,000, committed 4,500". He approved the envelope once and never sees it again.

The close guard is a speed bump, not a wall. Only **Draft**, **Issued**, and **Partially Received** POs can be closed — a Received or Completed PO is refused. But the guard's own rejection message spells out the way around it: *"to bail out, correct a received line down to revert it to partially-received first."* Receive the goods, walk the quantity back down, close, release.

Auto-release with a director approval task on each release would restore the oversight, but it costs a director task per cancellation to buy back a control we can keep for free by simply not building the release.

### Separate finding, not part of this chunk

**A Received PO can be walked backwards to Partially Received by correcting a line down.** Checked against the live app 2026-07-18 and closed: reaching Received has no side effects beyond the status field and a notification, so there is nothing to reverse. Receipt accuracy is a physical control, not a software one. See D85.

---

## 4. What needs building

The mechanism is free — raising `budget_usd` already flows through `remaining_usd` and the submit-time guard with no code. The work is permission and audit.

**The blocker:** per D49/R26, an **approved project is fully locked** — no role can edit `budget_usd` once it reaches Approved. The director cannot currently do the one thing this chunk depends on.

Sketch, to be re-derived against the live app at build time (never act on IDs read here):

1. **Verify the lock.** Read the live project guard and the director's ACL on `projects` — confirm exactly what blocks a budget edit on an approved project, and whether it's the guard, the ACL whitelist, or both.
2. **Allow a director-only budget increase on an approved project.** Increase only — a decrease could push `remaining_usd` negative and strand it below already-committed money. Not editable by operations, procurement, or the submitter. Not editable at any other status by this path.
3. **Require a reason.** A budget change with no stated cause is the thing an auditor cannot evaluate.
4. **Record it as history, not just a new value.** Preferred: a small child collection (`project_budget_revisions` — old value, new value, reason, who, when), shown on the project detail page. Fallback if that's too heavy: a reason field plus `updatedBy`/`updatedAt`, which loses the history across repeat raises.
5. **Notify** the project submitter and the head of procurement that the envelope changed.
6. **Tests** in `tests/plan.yaml`: director can raise an approved project's budget; procurement and operations cannot; a decrease is refused; the raise updates `remaining_usd`; a replacement PR that was blocked before the raise passes after it.
7. **User guide** — a short section under Projects on what to do when a project PO is cancelled.

### Open questions for build time

- **Should a budget increase need board approval above some size?** Projects already go to the board at `budget_usd >= 15,000` on their initial ladder. A director raising a $14,000 project to $20,000 would sidestep that. Probably the raise should re-check the board threshold — needs a decision.
- **Does the reason need to name the cancelled PO?** A free-text reason is simpler; a link to the PO is auditable. Lean free-text unless Alexander wants the link.

### Not doing

- No one-off correction to PRJ-26-0123's `committed_usd`. Under this design its $4,900 is **correct** — that money was committed and the order was cancelled. If the department wants to re-spend it, the director raises the budget, which is exactly the intended path.
- No change to the underspend and FX cases in §1. Same root cause, different chunk.
