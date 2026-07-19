# Final build phase — chunks 019 then 017

## Context

This is the last build work before the first version goes live. Everything else
on the go-live runbook is now either done or is server-side work.

**What just got cleared** (2026-07-18, recorded in the roadmap and go-live doc):
the Complete Project button is built and PRJ-26-0079 was completed in the app;
the 014.6 projects walkthrough was done with no failures; the `member` `ui.*`
flip moves to the server, after the restore.

**What's left in the app** is these two chunks:

- **019 — PO execution lock.** A PO is the execution of an approved request, but
  its line prices can still move after it has been issued and printed. This
  freezes them.
- **017 — Complete approval notifications.** Rejections notify nobody at all
  today. A submitter whose request dies at the dept stage learns nothing. Only
  three "approved" nodes exist, and their titles are copy-paste leftovers that
  say "reassigned to custom approver".

Both chunk files are already written, approved, and were re-verified live today.

**Drift found and folded in before planning** (already committed):
- Both guard ids named in 019 were stale — the workflows were revised
  2026-07-16. Corrected to the live enabled ids.
- 019's Phase 2 risk is retired: 108 real executions show every receive
  submitting only `received_quantity`, never alongside `quantity_ordered`.
- **The Add new button on the PO table is already gone** — Alexander removed it;
  verified live, no create action for `purchase_orders` renders anywhere. The
  planned Phase 1b is dropped. (One dead `flowModels` row survives, uid
  `i2sb9sjg84d`, unparented so it cannot render. Cosmetic, not scheduled.)

### Correcting 019's stated motivation

Alexander pushed back on the chunk's "Why", and he's right — **the chunk file
overstates the hole and the correction changes what needs writing down, not what
needs building.**

`Guard: PO Line Update — budget ceiling (PR amount)` (`c9c14tyn876`) already
caps the line sum at the parent PR's `quoted_total`. Verified from its config:
it compares the **newly submitted** value, and it **never looks at PO status**,
so it fires identically on a draft and an issued PO. The chunk's example —
"issue at $9,000 against a $10,000 PR, then edit a line up to $15,000" — is
already rejected today.

What is genuinely still open, on an **issued** PO:

- Edit the lines from $9,000 to $9,999 → **allowed**. Under the ceiling, so the
  budget guard passes it. The supplier is holding paper that says $9,000.
- The same end state is reachable by import, which bypasses the per-line guards
  by design (D52) — Alexander's point.

So 019's real justification is the chunk's *second* argument, not its first:
**once issued, the printed PO has left the building, and receiving and invoice
matching then compare against numbers that no longer match the paper.** Budget
containment is already solved. Document integrity is not.

This narrows nothing in the build — the guard in 1c is unchanged — but 019's
"Why" section must be rewritten before execution, or it stands as a wrong
statement about the app in a file we rely on. First task below.
- 017's ids and all 28 node keys verified live and correct. Its build step 0 is
  answered: the projects deep link is
  `/admin/71k045k77w2/view/5964407f0c9/filterbytk/{{$context.data.id}}`.

---

## Sequencing

**019 first, then 017.** 019 is smaller, self-contained, and closes a hole where
money can move. 017 is larger (16 new nodes across two workflow revisions) and
touches the approval ladder, which is the riskiest thing in the app.

Realistically this is **two sessions**, not one. The hard checkpoint is after
019 is verified. If 017 runs long, §6 of its chunk file names the node to cut
and carry forward: the over-budget auto-rejection notification, which
linkage rules on the procurement approval form make nearly unreachable anyway.

---

## Part 1 — Chunk 019: PO execution lock

Chunk file: [chunks/019-po-execution-lock.md](chunks/019-po-execution-lock.md)

### 1a-pre. Correct the chunk file's "Why"

Rewrite 019's budget-cap paragraph per the correction above: the per-line budget
guard already caps edits at the PR total at every status, so the remaining hole
is divergence from the printed PO within that ceiling, plus the import route.
Record the Add new button as already removed by Alexander. Commit before
building.

### 1a. Close the create-whitelist gap

Remove `supplier`, `currency`, `fx_rate_to_usd`, `total`, `issued_at` from
`procurement`'s **create** field whitelist on `purchase_orders` (ACL resource
`366562898804736`).

Generate PO is a workflow create node, and workflow nodes bypass ACL entirely,
so this does not affect the only path that should be creating POs.

*Verify:* re-read the whitelist; run Generate PO on an approved PR as
procurement; confirm the draft PO still carries supplier, currency, total, FX.
*Rollback:* re-add the five names.

### 1b. ~~Remove the Add new button~~ — already done by Alexander

Verified live: no create action for `purchase_orders` renders anywhere. Nothing
to do. This also means 1a can no longer break a UI path, since the only
remaining creator of POs is the Generate PO workflow.

### 1c. New guard — freeze line quantity and price at issue

New `request-interception` workflow on `po_lines`, action `update`. Copy the
shape of `Guard: PO Line Destroy — block once PO issued` (id `375767284252672`,
key `v61hc3ou3pa`) node for node:

1. Query `users` for the caller with `roles.name $in [root, admin]` — the
   admin-exempt head (D71/D63).
2. Condition: caller lookup returned null → continue; otherwise stop.
3. Query `po_lines` by `{{$context.params.filterByTk}}`, appending
   `purchase_order`.
4. Condition: parent PO `status != "draft"` **AND**
   (`params.values.quantity_ordered != null` **OR**
   `params.values.unit_price != null`).
5. Reject branch: response-message *"Cannot change quantity or price once the
   PO has been issued."* + end node `endStatus: -1`
   (per `feedback_inline_guard_end_node` — without the end node the UI reports
   silent success).

Create with `deleteExecutionOnStatus: []` (D79 — sync guards keep history or
the dispatcher race returns 500s). Set `description` and the Guards category on
the workflow record itself (D84).

**This becomes the fourth interception guard on `po_lines` update.** The overlaps
are intentional, and none of the three existing guards is made redundant:

| Guard | What it blocks | Status-aware? |
|---|---|---|
| `c9c14tyn876` budget ceiling | line sum exceeding the PR's approved total | no — fires at every status |
| `f3dkb37te22` immutability | *every* field, once Completed or Closed | yes |
| `mhfp4d15uee` receive guard | receiving on a non-receivable PO | yes |
| **new** | quantity and price only, from Issued onward | yes |

The new guard is the only one that says "these numbers are final now". Whichever
rejects first wins.

*Rollback:* disable the workflow. Nothing else is touched.

### 1d. Tests and docs

- `tests/plan.yaml`: draft-line edit succeeds; issued-line quantity/price edit
  rejected; `received_quantity` on an issued line still succeeds.
- Extend the PO-create ACL rule to assert the five removed fields are rejected.
- `docs/user-guide.md` — the Issue step gains a line. Labels via `nb-ui-labels`.
- D-entry in decisions.md.

**The likely overrun.** These cases need an **issued**-PO fixture, which
requires driving the Issue PO custom action with supplier and delivery address
set. R18/R22 and the R21 delete-deny have been waiting on that same fixture
since D61. Building it is worth doing once and unblocks four rules — but if it
turns into a session of its own, I'll stop, report, and we decide whether to
ship 019 on manual verification alone and land the fixture separately.

---

## Part 2 — Chunk 017: Complete approval notifications

Chunk file: [chunks/017-approval-notifications-complete.md](chunks/017-approval-notifications-complete.md)

Both workflows have executed, so both need a **new revision** — no in-place
edits.

### 2a. PR Approval — `375705420496896`, key `cv237r8h7k9`

Revise, then apply: **5 node edits, 3 retitles, 5 new nodes.** The full matrix
of which of the three recipients each of the 10 terminal outcomes gets is §3 of
the chunk file; it doesn't need restating here.

Two things worth calling out:

- **The recipient list is hardcoded per node, with no runtime role check.** Each
  terminal node sits on exactly one approver's branch, so "who acted" is known
  from the node's position in the graph. That's why this chunk is only
  notification nodes and nothing else.
- **The three retitles are cosmetic but matter for the next person.**
  `hy95mz4oo5f`, `dproua9530i` and `p53qqltz9v2` are all labelled "Notify dept
  head — PR reassigned to custom approver" while actually sending "PR approved"
  to the requester. Their *content* is correct and live; only the label lies.

### 2b. Project Approval — `373589018214400`, key `hzykothf9cx`

Revise, then add **6 new notification nodes** (§4). This workflow has zero
notification nodes today. Deep link as resolved above.

Note its `options` is only `{"timeout":0}` — no `stackLimit` or
`deleteExecutionOnStatus` keys, unlike PR Approval. Preserve that as-is through
the revision rather than "fixing" it; it's async, so D79 doesn't apply.

### 2c. Diff both revisions before enabling

Non-negotiable, and the step most likely to catch a real problem. The revision
copy has silently dropped condition clauses twice (D69, D75) and silently
appended " copy" to a workflow title once (D84, hit this week). Diff **node
configs and the workflow-level fields** — `title`, `description`, `options`,
`sync`, `categories`. A node-only diff reads clean and misses the title bug.

Where a node is being edited anyway, write its full intended config rather than
trusting the copy.

### 2d. Enable, then descriptions

Enable new versions, disable predecessors. Then re-read both workflow
descriptions and update them in the same session — per D84 a revision that
leaves a stale description is not finished. Describe statuses by their
on-screen labels.

### 2e. Tests and docs

- `nb-test run` green.
- D85 in decisions.md; mark D50's recipient rule superseded.
- `workflows-explained.md` — approval ladder sections.
- `docs/user-guide.md` — notification behaviour is user-visible. Labels via
  `nb-ui-labels`.
- Roadmap: 017 done, 015 superseded in part.

---

## Verification

Backend green is not enough for either chunk — the test gate needs your verbal
confirmation from the UI. The checks are already written into
[docs/go-live.md §1.2b](docs/go-live.md) so they land on the go-live checklist:

**019, as Pat:**
- On an **issued** PO, edit a line's Quantity → rejected with the message. Same
  for Unit Price. On a **draft** PO the same edit still saves.
- Enter a Received Quantity on an issued PO's line → still saves. *(This is the
  one that would break receiving if the guard were wrong.)*
- Generate PO on an approved PR still produces a draft PO with supplier,
  currency, total and FX rate filled in.

**017, driving real approver users rather than admin:**
- Reject a PR at each of the five stages. Each time: the submitter, their dept
  head, and — only where the PR actually reached them — the procurement head get
  a message naming the stage. The person who rejected gets nothing.
- The same for a rejected project.
- Approve a PR through to final; the three notification titles now read
  correctly.

---

## Per-phase stops

Per CLAUDE.md I pause after each phase with a summary and a preview of the next.
Explicit stop-and-confirm, regardless of phase boundary, before **2d** —
disabling the predecessor versions on both approval workflows. Nothing else in
this plan is destructive; the Add new deletion that would have been is already
done.

## Closing out

After 019 and after 017, separately: `nb backup create` to the iCloud
Havenbeheer backups folder, then commit and push.
