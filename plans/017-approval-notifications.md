# Plan — chunk 017, complete approval notifications

## Context

When a purchase request or a project is finally approved or rejected, the people
who care are not told. Rejections notify **nobody** today. Approvals notify only
the submitter, via three nodes that are mislabelled as something else entirely.

017 fixes that. On every final decision, three people get an in-app message: the
submitter, the head of the submitter's department, and the head of procurement.
Two exceptions: whoever made the decision is never told (they just clicked the
button), and procurement is skipped when the request died before reaching them.
Returns stay silent — a returned request already shows up in the submitter's
to-do list.

This is the last build chunk before go-live. The spec is
[chunks/017-approval-notifications-complete.md](../chunks/017-approval-notifications-complete.md);
both of its open questions are already answered and must not be re-asked.

**Drift check: clean.** Every id, node key, node count and workflow-level field
matches what was verified on 2026-07-18. Nothing was revised in between.

## Scope

16 node touches across two new workflow revisions. No trigger changes, no ACL
changes, no collection changes — so approval routing is untouched and does not
need re-testing.

## Recipient expressions

| Recipient | Expression |
|---|---|
| Submitter | `{{$context.data.createdById}}` |
| Dept head | `{{$context.data.createdBy.mainDepartment.mainApproverId}}` |
| Proc head — PR Approval | `{{$jobsMapByNodeKey.yrl9kgkrb3x.main_approver.id}}` |
| Proc head — Project Approval | `{{$jobsMapByNodeKey.ioqkg84ju36.main_approver.id}}` |

Every node: channel `approval-todo-in-app-message`, `ignoreFail: true`,
`options: {"duration": 10, "url": "<deep link>"}`.
PR link `/admin/cuycec133qb/view/ceaecc4498c/filterbytk/{{$context.data.id}}`,
project link `/admin/71k045k77w2/view/5964407f0c9/filterbytk/{{$context.data.id}}`.

Rejection content names the stage so a reader knows where it died:
`{{{$context.data.pr_number}}} "{{$context.data.title}}" was rejected at the <stage> stage.`

---

## Phase 1 — PR Approval (`375705420496896`, key `cv237r8h7k9`)

Revise, then apply 5 edits (3 with retitles) and 5 new nodes.

```
nb api workflow workflows revision --filter '{"key":"cv237r8h7k9"}' --title "PR Approval"
```

`key` sits at the top level of `--filter`, never inside `$and`, or the call mints
a stray workflow on a brand-new lineage. Passing `--title` explicitly pre-empts
the D84 bug where the copy silently ships as "PR Approval copy".

Then re-read the new version's nodes and map key → new numeric id. Node ids are
freshly minted by the revision; **never reuse an id from the old version.**

### Edits to existing notification nodes

| Node | Change |
|---|---|
| `xtr5t4xy1gq` over budget | receivers → submitter + dept head + proc head. Keep its distinct "auto-rejected — it would exceed the project budget" wording. |
| `hy95mz4oo5f` procurement final | receivers → submitter + dept head. Retitle **Notify — PR approved (procurement final)** |
| `dproua9530i` director | already has submitter + proc head; **add dept head only**. Retitle **Notify — PR approved (director)** |
| `p53qqltz9v2` board | receivers → submitter + dept head + proc head. Retitle **Notify — PR approved (board)** |
| `fvbrc41tdl2` project drawdown | receivers → submitter + dept head |

Write each node's **full intended config**, not a patch onto whatever the
revision produced (D69/D75 — the copy has silently dropped clauses twice).

### New rejection nodes

Each is a `flow-nodes duplicate` of an existing notification node, with
`--upstream-id` set to the update node below and `--config` supplied inline, then
a `flow-nodes update --title`. All five attach to terminal update nodes with no
existing downstream, so `duplicate` appends cleanly.

| Upstream update node | Stage wording | Recipients |
|---|---|---|
| `1b06nufq3bi` Dept Head Rejected | department | submitter |
| `vhize11vzsg` Custom Approver Rejected | custom approver | submitter, dept head |
| `01vfxfgw6s3` Procurement Rejected | purchasing review | submitter, dept head |
| `t2odlgyqdra` Director Rejected | director | submitter, dept head, proc head |
| `2rd8sap9m04` Board Rejected | board | submitter, dept head, proc head |

Leave `5h232imw9ss` alone — it is the genuine reassignment notice and is
correctly titled. It shares a title with the three mislabelled nodes; do not
sweep it up with them.

### Diff before enabling

Compare the new version against the live one node by node **and at workflow
level** — `title`, `description`, `options`, `sync`, `categories`. A node-only
diff reads clean and misses the title bug. Expected `options`:
`{"timeout":0,"stackLimit":1,"deleteExecutionOnStatus":[]}`.

**Do not enable yet.**

---

## Phase 2 — Project Approval (`373589018214400`, key `hzykothf9cx`)

Six new nodes, all rejection/approval terminals. Zero notification nodes exist
today.

```
nb api workflow workflows revision --filter '{"key":"hzykothf9cx"}' --title "Project Approval"
```

**Preserve `options` as exactly `{"timeout":0}`.** It has no `stackLimit` or
`deleteExecutionOnStatus`, unlike PR Approval. That is correct — the workflow is
async, so D79 does not apply. Do not "fix" it.

### The seeding problem

`flow-nodes duplicate` works within one workflow only, and Project Approval has
no notification node to copy. So the first node must be created raw:

```
nb api resource create --resource flow_nodes --values '{"workflowId":…,"type":"notification","key":…,"title":…,"upstreamId":…,"config":{…}}'
```

**Risk:** raw create does not go through the plugin's re-link logic, so the
upstream node's `downstreamId` may not be written. `duplicate` and `move` both
re-link automatically; raw create likely does not. After the first create, read
back both the new node and its upstream and confirm the chain is bidirectional —
`upstream.downstreamId` must point at the new node. If it doesn't, set it by
hand before continuing.

Once one node is verified, build the remaining five with `flow-nodes duplicate`
off it, which handles linking properly. This confines hand-linking to a single
node that gets checked before the pattern repeats.

| Upstream update node | Message | Recipients |
|---|---|---|
| `ftt0dnnq8iw` Dept Rejected | rejected, department | submitter |
| `8wywlcbea89` Procurement Rejected | rejected, purchasing review | submitter, dept head |
| `5j5hyd0piqi` Director Rejected | rejected, director | submitter, dept head, proc head |
| `22e5jxvgd90` Board Rejected | rejected, board | submitter, dept head, proc head |
| `yhc99ooprj8` Director Approved | approved | submitter, dept head, proc head |
| `8fyj9j9tw2r` Board Approved | approved | submitter, dept head, proc head |

Project copy uses `project_number` and the project deep link. There is no
"procurement is final" path for projects, so the procurement-acted exception
never arises here.

Diff as in Phase 1. **Do not enable yet.**

---

## Phase 3 — Go live (explicit stop)

Both revisions sit built and diffed but disabled. **Stop here and get
Alexander's explicit go before disabling the predecessors.**

On approval:

1. Enable both new versions, disable both predecessors.
2. `nb api workflow workflows sync --filter '{"enabled": true}'` — without it,
   `?triggerWorkflows=`-bound actions can return 500.

Rollback is the reverse: re-enable the predecessors, disable the new versions,
sync again. The old versions are untouched throughout.

---

## Phase 4 — Finish

1. **Update both workflow descriptions** in the same session. Per D84 a revision
   that leaves a stale description is not finished. Both current descriptions
   describe routing only and say nothing about notifications.
   `workflows update` has no `--values` — use `--title` / `--description` /
   `--enabled`.
2. Run the suite; currently 94/94:
   `python3 /Users/alexander/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .`
   Add regression cases for the new recipient matrix. Any rule sentence with a
   colon must be quoted or the YAML scanner dies. Never write `tests/.env.test`.
3. Append **D88** to decisions.md marking D50's recipient rule superseded.
   D85–D87 are taken; the chunk file's "D85" is stale.
4. Update `workflows-explained.md`, `docs/user-guide.md` (labels via
   `nb-ui-labels`), roadmap.md.
5. Backup to iCloud, commit, push.

## Verification

Backend green is not enough — the test gate needs Alexander's verbal
confirmation from the UI. Checks are already written into
[docs/go-live.md](../docs/go-live.md) §1.2b:

- Reject a PR at each of the five stages. Each time the submitter, their dept
  head, and — only where the PR actually reached them — the procurement head get
  a message naming that stage. Whoever rejected gets nothing.
- The same for a rejected project.
- Approve a PR through to final; the three notification titles now read
  correctly instead of claiming a reassignment.

Drive real approver users, not admin.

## Out of scope

- Project Approval's Board Approval node `vwuxv7zih9f` has no "Returned" branch,
  unlike every other approval node in both workflows. Flagged for a later chunk.
  Do not fix it here.
- Email notification. Both mail plugins are enabled and unused; it needs SMTP
  config and a template pass of its own.
- Duplicate messages on the "Skip Dept" path, where submitter and dept head are
  the same person and both slots resolve to one user. Alexander accepted this.

## If the build runs long

Cut the over-budget node (`xtr5t4xy1gq`) and carry it forward — linkage rules on
the procurement form hide Approve when the amount exceeds remaining budget, so
that path is close to unreachable. Never cut one of the five rejection nodes.
