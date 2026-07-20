# 017 — Complete approval notifications (PR + Project)

**Status:** **COMPLETE 2026-07-19.** Built + live, suite green; the §1.2b walkthrough was executed the same day via API on Alexander's delegation (D92) — 9 scenarios driven as the real approver users (all five PR rejection stages, project rejection at dept + director stage, both approved-to-final paths), recipients read back from `notificationInAppMessages`, exact match with the §3/§4 matrix in all 9. As-built: PR Approval `376242882347008` (47 nodes), Project Approval `376252879470592` (28 nodes); predecessors `375705420496896` / `373589018214400` disabled. Decision entry: **D88**. Scoped 2026-07-18 from a live read of both approval workflows; a fresh drift check on 2026-07-19 found zero drift, so every id and node key below held.
**Built to plan, with no scope changes.** The only surprises were in the revision mechanism, not the design — see "What actually happened" below.
**Session history:** [plans/017-handoff.md](../plans/017-handoff.md) (written at the end of 019) and [plans/017-approval-notifications.md](../plans/017-approval-notifications.md) (the executed plan).
**Extends:** MVP 015 / D50 (which only covered "PR approved", requester + procurement head on the director path).
**Supersedes:** D50's recipient rule. D50 stays historically valid; this chunk replaces the recipient matrix it defined.

---

## 1. The rule in plain language

When a purchase request or a project reaches a **final** decision — approved or rejected — three people are told, in-app:

1. the **submitter** (whoever created the record),
2. the **head of the submitter's department** (that department's main approver),
3. the **head of procurement**.

With two exceptions:

- **The person who made the decision is not notified.** They just clicked the button; telling them what they did is noise. This applies to whoever acted — dept head, custom approver, procurement, director, or board.
- **Procurement is not notified about a record that never reached them.** If a dept head or custom approver rejects, the request dies before procurement ever sees it, so procurement hears nothing.

Not covered, deliberately: **"Returned — Info Requested" sends no notification.** A returned request already appears in the submitter's to-do list automatically. Confirmed with Alexander 2026-07-18.

### Why the exceptions are cheap to build

Each terminal node sits on exactly one approver's branch, so "who acted" is known from the node's *position* in the graph — no runtime role check, no extra condition nodes. The recipient list is hardcoded per node. This is the reason the whole chunk is just notification nodes and nothing else.

### Story check

> Olga (Operations) submits a $500 request. Her dept head Oscar approves it. Procurement approves it. It's over $300 and not a regular purchase, so it goes to Director Dana, who rejects it.
> **Notified:** Olga, Oscar, and the procurement head. Not Dana — she rejected it.

> Olga submits a $200 request. Oscar rejects it at the dept stage.
> **Notified:** Olga only. Not Oscar (he rejected it), not procurement (they never saw it).

---

## 2. Recipient variables

| Recipient | Expression |
|---|---|
| Submitter | `{{$context.data.createdById}}` |
| Dept head | `{{$context.data.createdBy.mainDepartment.mainApproverId}}` |
| Procurement head — **PR Approval** | `{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}` |
| Procurement head — **Project Approval** | `{{$jobsMapByNodeKey.ioqkg84ju36.main_approver.id}}` |

**Verified reachable.** Both triggers already append `createdBy`, `createdBy.mainDepartment`, and `createdBy.mainDepartment.main_approver`, so the dept head resolves everywhere. The "Query Procurement Dept" node runs **first** in both workflows — before any approval node — so its result is in scope at every terminal node, including the early dept-stage rejections. **No trigger changes are needed**, which means approval routing is untouched and does not need re-testing.

Channel for every node: `approval-todo-in-app-message`. `ignoreFail: true` on every node (matches existing).

---

## 3. PR Approval — workflow `375705420496896`, lineage key `cv237r8h7k9`

10 terminal outcomes. 5 nodes exist and need edits; 5 are new.

| # | Terminal node (key) | Who acted | Reached proc? | Submitter | Dept head | Proc head | Work |
|---|---|---|---|:--:|:--:|:--:|---|
| 1 | Dept Head Rejected `1b06nufq3bi` | dept head | no | ✓ | — | — | **NEW** |
| 2 | Custom Approver Rejected `vhize11vzsg` | custom approver | no | ✓ | ✓ | — | **NEW** |
| 3 | Procurement Rejected `01vfxfgw6s3` | procurement | yes | ✓ | ✓ | — | **NEW** |
| 4 | Director Rejected `t2odlgyqdra` | director | yes | ✓ | ✓ | ✓ | **NEW** |
| 5 | Board Rejected `2rd8sap9m04` | board | yes | ✓ | ✓ | ✓ | **NEW** |
| 6 | Over budget → Rejected `3o2q8urkutu` | system | yes | ✓ | ✓ | ✓ | **EDIT** `xtr5t4xy1gq` — see open question |
| 7 | Procurement Approved (No Director) `jy1365pvsce` | procurement | yes | ✓ | ✓ | — | **EDIT** `hy95mz4oo5f` + retitle |
| 8 | Director Approved `kj1zcmujub8` | director | yes | ✓ | ✓ | ✓ | **EDIT** `dproua9530i` + retitle |
| 9 | Board Approved `8gqeq6djrfj` | board | yes | ✓ | ✓ | ✓ | **EDIT** `p53qqltz9v2` + retitle |
| 10 | Project drawdown → Approved `47fd05ite4i` | procurement | yes | ✓ | ✓ | — | **EDIT** `fvbrc41tdl2` |

New nodes attach directly beneath the status-update node named in each row.

**Not notified (intermediate stage advances, unchanged):** Dept Head Approved `xqlzgk0326f`, Custom Approver Approved `r8f85w1w1ze`, Skip Dept `nkbguc8uo7z`, Procurement Approved → Director `eg86l2ilhmk`, Board required `fm6kvldiduk`. These move the request along; they are not decisions.

**Left exactly as-is:** the reassignment notice `5h232imw9ss` (tells the dept head their PR went to a submitter-chosen approver). Correct today, correctly titled today.

### Title fix

Three nodes are titled "Notify dept head — PR reassigned to custom approver" but actually send "PR approved" to the requester — copy-paste leftovers from duplicating `5h232imw9ss`. Retitle:

| Key | New title |
|---|---|
| `hy95mz4oo5f` | Notify — PR approved (procurement final) |
| `dproua9530i` | Notify — PR approved (director) |
| `p53qqltz9v2` | Notify — PR approved (board) |

---

## 4. Project Approval — workflow `373589018214400`

Currently **zero** notification nodes. 6 terminal outcomes, all new.

| # | Terminal node (key) | Who acted | Reached proc? | Submitter | Dept head | Proc head |
|---|---|---|---|:--:|:--:|:--:|
| 1 | Dept Rejected `ftt0dnnq8iw` | dept head | no | ✓ | — | — |
| 2 | Procurement Rejected `8wywlcbea89` | procurement | yes | ✓ | ✓ | — |
| 3 | Director Rejected `5j5hyd0piqi` | director | yes | ✓ | ✓ | ✓ |
| 4 | Board Rejected `22e5jxvgd90` | board | yes | ✓ | ✓ | ✓ |
| 5 | Director Approved `yhc99ooprj8` | director | yes | ✓ | ✓ | ✓ |
| 6 | Board Approved `8fyj9j9tw2r` | board | yes | ✓ | ✓ | ✓ |

**Not notified:** Dept Approved `mtugzs9s6yq`, Skip Dept `oklnh22f6n4`, Procurement Approved → Director `s8k21sgph93`, Board required `7rkl02hfzej`.

Note there is no "procurement is final" path for projects — procurement approval always advances to the director — so the procurement-approves exception never arises here.

---

## 5. Message copy

`projects` has `title` and `project_number`, mirroring `purchase_requests` (`title`, `pr_number`). Titles use the same shape.

**Approved:**
- Title: `PR approved: {{$context.data.title}}` / `Project approved: {{$context.data.title}}`
- Content: `{{{$context.data.pr_number}}} "{{$context.data.title}}" has been approved.`

**Rejected** — name the stage, so a recipient can tell where it died without opening the record:
- Title: `PR rejected: {{$context.data.title}}` / `Project rejected: {{$context.data.title}}`
- Content: `{{{$context.data.pr_number}}} "{{$context.data.title}}" was rejected at the <stage> stage.`
  where `<stage>` is literal per node: department, custom approver, purchasing review, director, or board.

Over-budget auto-rejection keeps its existing distinct wording ("was auto-rejected — it would exceed the project budget").

**Options block** (matches existing nodes):
```
"options": { "duration": 10, "url": "<deep link>" }
```
- PR deep link (known good): `/admin/cuycec133qb/view/ceaecc4498c/filterbytk/{{$context.data.id}}`
- Project deep link — **RESOLVED 2026-07-18, build step 0 is done:**
  `/admin/71k045k77w2/view/5964407f0c9/filterbytk/{{$context.data.id}}`
  (Projects page routeId `372377246040064`, view action uid `5964407f0c9`,
  `filterByTk: {{ ctx.record.id }}`, collection `projects`.)

---

## 6. Open question — RESOLVED 2026-07-18

**Node 6, over-budget auto-rejection: does the procurement head get told?**

This is the one case where no person made the decision. Procurement *approved* the request, and the system then overturned that on the project budget ceiling. The matrix above provisionally says yes, all three, on the reasoning that procurement should know their approval was overridden. The competing reading is that procurement acted, so the actor-exception applies and they're excluded.

**Alexander's answer: notify all three — the table stands as written.**

He added a fact worth recording: **in practice this path is close to unreachable.** The procurement approval form carries linkage rules that hide the Approve button when the request's USD amount exceeds the project's remaining USD. So procurement cannot normally approve an over-budget request in the first place, and the auto-rejection only fires if something slips past the form — a concurrent approval eating the remaining budget, an API-level approve, or an admin acting outside the form.

Consequence for building: node 6 is real and must be correct, but it is the lowest-value node in this chunk. If the build runs long, it is the one to cut and carry forward, not one of the five rejection nodes.

---

## 7. Build steps

0. **Find the projects view-popup uid** for the deep link (page schemaUid `71k045k77w2`). If it can't be resolved cleanly, fall back to linking the Projects page without `filterbytk` rather than shipping a broken link.
1. Confirm the §6 open question.
2. Revise **PR Approval** (`375705420496896`). Both workflows have executed, so in-place editing is impossible — new revision required.
3. **Diff the revision copy node by node before enabling** (D69/D75 — the copy has silently dropped condition clauses twice). Where a node is being edited anyway, write its full intended config rather than patching the copy.
4. Apply the 5 edits + 3 retitles + 5 new nodes from §3.
5. Repeat 2–4 for **Project Approval** (`373589018214400`): 6 new nodes.
6. Enable new versions, disable predecessors (rollback = reverse this).
7. Update each workflow's **description** in the same session — per D84 a revision that leaves a stale description is not finished.
8. Live-verify: drive each terminal path and read the resulting in-app messages. Prefer real approver users over admin.
9. `nb-test run` green, then Alexander's manual confirmation.
10. Append **D88** to decisions.md (D85/D86/D87 are taken); mark D50's recipient rule superseded.
11. Update `workflows-explained.md` (approval ladder sections) and `docs/user-guide.md` (notification behaviour is user-visible — get exact labels via `nb-ui-labels`).
12. Roadmap: add 017; note 015 superseded-in-part.
13. Backup, commit, push.

---

## 8. Notes and things spotted en route

- **Duplicate messages are accepted.** On the "Skip Dept" path the submitter *is* the department main approver, so both recipient slots resolve to one user and they get two identical in-app messages. NocoBase won't dedupe. Alexander accepted this 2026-07-18 rather than pay for the extra branching; revisit only if it annoys anyone in practice.
- **Email is deliberately out of scope.** `@nocobase/plugin-notification-email` and `@nocobase/plugin-workflow-mailer` are both enabled and unused. Everything here is in-app only, so a user who isn't logged in learns nothing. Email is its own chunk — it needs SMTP config and a template pass.
- **`projects` has its own `department` field**, separate from the submitter's department. This chunk uses `createdBy.mainDepartment.main_approver` per Alexander's explicit instruction ("same as for the PR workflow"). If a project is ever submitted on behalf of another department, these two diverge and the rule should be revisited.
- **`projects` also has a `submitter` field** distinct from `createdBy`. This chunk uses `createdById` for consistency with PR Approval. Worth confirming the two never diverge in practice.
- **Project Approval's Board Approval node `vwuxv7zih9f` has no "Returned" branch** (only reject `b-1` and approve `b2`), unlike every other approval node in both workflows. Not in scope here — flagged as a possible gap for a later chunk.

---

## 9. What actually happened (2026-07-19)

Everything in §1–§5 was built exactly as specified. Nothing in the design changed,
both §6 answers held, and the suite went green at 94/94 with no new cases — in-app
notification content stays walkthrough-only per `tests/plan.yaml` line 71.

The cost of this chunk was entirely in the **revision copies, which were unfaithful
both times**, in three ways the handoff's warning did not cover:

1. **A whole node disappeared.** PR Approval's revision came back with 41 nodes, not
   42. The missing one was `x8s6jal11h9`, "Write committed_usd to project" — the node
   that books an approved PR against its project's budget. The copy quietly re-linked
   `Project drawdown → Approved` straight to the notification node. Recreated by raw
   `resource create` and re-linked by hand. Proven repaired by the suite's own case
   ("project committed_usd written at approval"), which passes against the new version
   and would have caught the drop independently.
2. **Both `description` fields came back `null`.** Rewritten in the same session per D84.
3. **Three Project Approval nodes came back with rewritten logic.** Director Approval
   lost `returnTo: 'ik1ixug5rrs'` — the pointer that sends a director's Return back to
   Procurement. The Return button survived; only its destination was blanked, so
   nothing would have errored. Both approval nodes also had their `actions` arrays
   rewritten (Procurement 9 → 6, Director 5 → 3), and `amc633b85wx` had its department
   expression silently swapped to a different variable. All three restored verbatim
   from the live version, keeping only the newly minted `approvalUid`/`taskCardUid`.
   The duplicated entries in those `actions` arrays look like accumulated cruft, but
   normalising them is a separate decision and was deliberately not folded in here.

**The lesson, now standing practice (D88):** diff a revision by full node config and
node count, not by the node keys the chunk happens to name. A diff scoped to the nodes
you intend to edit reads perfectly clean and misses all three of the above.

Two mechanical facts worth keeping:

- **Raw `resource create` on `flow_nodes` does not re-link neighbours.** The new node
  knows its upstream and downstream; neither neighbour points back. Both must be
  patched by hand. `flow-nodes duplicate` links correctly but only works within a
  single workflow — which is why Project Approval's first node had to be created raw
  and the other five duplicated off it.
- **`workflows revision` accepts `--title`**, which pre-empts D84's " copy" bug at the
  source instead of catching it in the diff.

One correction to a mid-session reading: `categories` is **not** lost by a revision.
`nb api workflow workflows get` simply never returns that key, for old and new
workflows alike.
