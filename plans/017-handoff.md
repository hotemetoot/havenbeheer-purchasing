# Handoff — chunk 017, approval notifications

**Written 2026-07-18** at the end of the session that built 019. Start here, then
read [chunks/017-approval-notifications-complete.md](../chunks/017-approval-notifications-complete.md),
which is the actual spec and is accurate — every id and node key in it was
verified live on 2026-07-18 and none needs re-checking unless something else
revised those workflows in between.

## Where the project stands

This is the **last build chunk before go-live**. Everything else on the runbook
is done or is server-side work.

- **019 shipped** the same day (D87) — PO create-whitelist trimmed, and a new
  guard freezing PO lines at issue. Suite **94/94**. Alexander confirmed
  Generate PO still works, tested as Pat.
- **014 is complete**, 016 is done bar one import re-test.
- After 017 the remaining work is: Alexander's UI spot-checks
  ([docs/go-live.md](../docs/go-live.md) §1.2 and §1.2b), then Parts 2–4 of the
  runbook (VPS rebuild, migration, backups).
- The `member` `ui.*` flip **moved to the server** (§3.2). Do not do it locally.

## What 017 is

When a purchase request or a project reaches a **final** decision — approved or
rejected — notify three people in-app: the submitter, the head of the
submitter's department, and the head of procurement. Two exceptions: the person
who made the decision is never notified, and procurement is skipped when the
record never reached them. Returns stay silent.

Today rejections notify **nobody**, and only three "approved" nodes exist.

Scope: **16 nodes across two workflow revisions** — 5 edits, 3 retitles and 5
new nodes on PR Approval; 6 new nodes on Project Approval.

## Both open questions are already answered

Do not re-ask these.

1. **Over-budget auto-rejection notifies all three.** Alexander added that
   linkage rules on the procurement approval form hide the Approve button when
   the amount exceeds the project's remaining budget, so that path is nearly
   unreachable. If the build runs long, **that node is the one to cut and carry
   forward** — not one of the five rejection nodes.
2. **The projects deep link** (chunk build step 0) resolved to
   `/admin/71k045k77w2/view/5964407f0c9/filterbytk/{{$context.data.id}}`.

## Live state, verified 2026-07-18

| Object | Value |
|---|---|
| PR Approval (live) | `375705420496896`, key `cv237r8h7k9` — 42 nodes |
| Project Approval (live) | `373589018214400`, key `hzykothf9cx` — 22 nodes, **zero** notification nodes |
| Notification channel | `approval-todo-in-app-message` |
| Workflow category "Approval" | `373613569572864` |
| PR deep link | `/admin/cuycec133qb/view/ceaecc4498c/filterbytk/{{$context.data.id}}` |

All 28 node keys named in the chunk file exist on the live versions with the
expected types. Both triggers already append
`createdBy.mainDepartment.main_approver`, so **no trigger changes are needed**
and approval routing does not need re-testing.

Two cosmetic drift notes: the query node in both workflows is titled "Query
Procurement Dept **(for assignees)**", and `hy95mz4oo5f` / `dproua9530i` /
`p53qqltz9v2` are mislabelled "Notify dept head — PR reassigned to custom
approver" while actually sending "PR approved". Their *content* is correct; only
the labels lie. Retitling them is part of the chunk.

Project Approval's `options` is only `{"timeout":0}` — no `stackLimit` or
`deleteExecutionOnStatus`, unlike PR Approval. **Preserve that through the
revision rather than "fixing" it**; it's async, so D79 doesn't apply.

## Sequence

1. Drift-check both workflows (`nb-drift-scout`) — they may have been revised.
2. Revise PR Approval → apply 5 edits + 3 retitles + 5 new nodes.
3. Revise Project Approval → add 6 new nodes.
4. **Diff both revision copies before enabling** — see the trap below.
5. **STOP and get Alexander's explicit go before disabling the predecessors.**
6. Update both workflow descriptions in the same session (D84).
7. Suite green, then D88 in decisions.md marking D50's recipient rule
   superseded. Update `workflows-explained.md`, `docs/user-guide.md` (labels via
   `nb-ui-labels`), roadmap.
8. Backup to iCloud, commit, push.

## Traps that actually bit this week

- **The revision copy is not always faithful.** It has silently dropped
  condition clauses twice (D69, D75) and silently appended " copy" to a workflow
  title once (D84, hit 2026-07-18 and shipped live for ~40 minutes). Diff
  **workflow-level fields too** — `title`, `description`, `options`, `sync`,
  `categories` — because a node-only diff reads clean and misses the title bug.
  In 019's revision the copy *was* faithful, but check anyway.
- **`workflows revision` needs `key` at the top level of `--filter`**, not
  wrapped in `$and`, or it mints a stray workflow with a brand-new key.
  `--filter '{"key":"cv237r8h7k9"}'`.
- **A guard testing `values.X != null` to mean "is X being changed" is blind to
  a blanking** — an absent field and an emptied one render identically. This
  cost a rebuild in 019 (D87). Not directly relevant to 017's notification
  nodes, but it is the live lesson about trusting a condition's shape.
- **After enabling a revision, run
  `nb api workflow workflows sync --filter '{"enabled": true}'`** or
  `?triggerWorkflows=`-bound actions can 500.
- **`nb api workflow workflows update` has no `--values`** — use the named flags
  (`--enabled` / `--no-enabled`, `--title`, `--description`).
- **D-numbers: next free is D88.** D85, D86 and D87 are all taken. The chunk
  file's "append D85" instruction is stale.
- **YAML in `tests/plan.yaml`:** a rule sentence containing a colon must be
  quoted, or the runner dies with a scanner error.

## Running the suite

```
python3 /Users/alexander/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

Currently **94/94**. `tests/.env.test` exists and is filled in — never write it.
`check` does hygiene only; `acl` runs config checks in seconds.

## Verification 017 needs

Backend green is not enough — the test gate needs Alexander's verbal
confirmation from the UI. The checks are already written into
[docs/go-live.md](../docs/go-live.md) §1.2b:

- Reject a PR at each of the five stages. Each time the submitter, their dept
  head, and — only where the PR actually reached them — the procurement head get
  a message naming the stage. The person who rejected gets nothing.
- The same for a rejected project.
- Approve a PR to final; the three notification titles now read correctly.

Drive real approver users, not admin.

## Known gap, out of scope

Project Approval's Board Approval node `vwuxv7zih9f` has no "Returned" branch —
only reject and approve — unlike every other approval node in both workflows.
Flagged in the chunk file as a possible later chunk. Do not fix it here.
