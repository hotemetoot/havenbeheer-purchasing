# HANDOFF — havenbeheer retrofit, Step 6 (updated 2026-07-05, eighteenth session)

**Read this first, then:** `~/.claude/skills/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D63–D70. `notes.md` holds non-queryable traps and the go-live checklist (and, top of file, **how to write for Alexander** — plain language, concrete examples; non-negotiable). Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` if you touch `runner.py`.

## What landed 2026-07-05 (eighteenth session — SUITE FULLY GREEN, 58/58)

1. **R26 case rework finished, reviewed, approved.** The seventeenth session's draft was completed with one new test: procurement tries a direct edit at its own review stage — permission says yes, the safety-net workflow says no. That's the only test that isolates the projects guard (every other deny is stopped by a permission scope first). New fixture `proj_purchasing` (one dept approve, parks at `pending_purchasing_review`). Alexander approved the group; R26's `# TODO verify` is cleared.
2. **First full projects run** → found 3 failures → **D70**: the PR-to-project link guards only saw the UI's payload format. Plain `project: 5` / `projectId: 5` / string ids bypassed the "project must be approved" block AND the budget block; the update-side guard checked the old link, not the new one, and skipped pure re-link edits entirely. Fixed via new revisions of `lylobzvlh5p` (create) and `ebq41ibq60r` (update) — payload-id normalizer node first, all checks read it; update guard now loads the project being SET and fires on project edits too. All bypass shapes retested by hand: blocked. Predecessors disabled as rollback. Full detail in D70.
3. **Smuggle case rewritten** (runner lesson): the runner verifies an allowed update by checking every sent field got saved, so a deliberately-ignored field must be expressed as a deny-style case ("value must NOT get saved"). Plan is now 24 rules / **58** cases.
4. **Suite green 58/58** after the guard fix — first fully green run including all projects rules, the `pr_draft_a` return-for-info seeding, and the `proj_purchasing` seeding.
5. **Writing rule saved everywhere** (Alexander, this session): plain language, concrete examples, no jargon — see `notes.md` top, auto-memory `feedback_plain_language_concrete_examples`, and the nb-test SKILL.md review section.

> **Concurrency note:** on 2026-07-04 Alexander committed D68 from a second terminal *during* the prior session. Before any write-heavy step, make sure no other session is open on this repo.

Per-session narrative lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). Steps 0–5 done. **Step 6** (extend `tests/plan.yaml` with a full ACL/workflow audit, reviewed in workflow/mechanism groups, verified live) is in progress. PR / PO / po_lines and the projects rules R25–R30 are reviewed; `suppliers` and `departments` still have no audit.

## What landed 2026-07-05 (sixteenth session — D67 rename built + live-verified)

**D67 is done.** Full detail in `decisions.md` D67 Status; short version:
- `projects.status`: `closed` → `completed` (label "Completed"); no rows held `closed`, zero migration.
- `completed_at` created, `closed_at` dropped (all null); role whitelists auto-swapped both ways (D64 auto-append behavior, confirmed also on removal).
- Same-key revisions built, diffed clean, **activated**: Complete Project `373721283493888` (`px2xvjaxoqf`), guard `373721390448640` (`2h75zryz3cb`). Predecessors `373522687393792` / `373520806248448` disabled as rollback.
- Smoke-tested 5/5 with real signed-in users (Pat) via the real `projects:trigger` verb: reject-draft message, complete-approved (status+`completed_at`), guard-deny on completed, re-complete deny, admin teardown. Throwaway project deleted; live data untouched (the 2 real projects, both `approved`).
- `plan.yaml` vocabulary renamed throughout the projects sections (fixture `proj_approved_2` comments/values, R26/R27/R28 case names, status matches, order-sensitivity comments). PO `closed` untouched — still a legitimate PO status. Validates 24 rules / 55 cases. R27 downgraded to `# TODO verify`.
- **New CLI trap** recorded (auto-memory `reference_nb_workflow_revision_gotchas`): top-level `executed`/`allExecuted` on `workflows list/get` read 0 even for executed workflows — read `versionStats.executed` via `--appends stats,versionStats`. Both D67 workflows showed `executed: 0` but were frozen (6 and 20).

## What landed 2026-07-04 (fourteenth — review + one live ACL trim, no runner execution)

Backlog word-review, one rule at a time, each claim re-verified against live state. Two commits, **working tree clean**:
- `9fbb03f` — R2 rewrite + `pr_draft_a` fixture rework (D68).
- `54aa7d5` — R4, R5, R12, R13, R14, R16 verified + cleared.

| Rule | Outcome |
|---|---|
| R2 | **Rewritten** to info_requested-only (D68 retired `draft`); ownership = createdById or submitterId. **Live ACL trimmed:** operations update scope dropped its dead `draft` clause → now `status == info_requested AND own`. Fixture `pr_draft_a` reworked (see below). |
| R4 | Verified — only procurement holds `purchase_orders:create`; director has no entry + view-only role strategy |
| R5 | Verified — same for `po_lines:create` |
| R12 | Verified — director update scope `status $eq pending_director_approval`; fields exactly the 3 render-enablers, no project/projectId (D58) |
| R13 | Verified — same scope proves the deny outside that stage; case wording draft→info_requested |
| R14 | Verified — director PR grant is view+update only, no create; case dropped invalid `status: draft` |
| R16 | Verified — "Guard: Create PO (PR must be approved)" blocks PO create from a not-approved PR |

**D68 reconcile done** for every rule touched: no `status: draft` literal remains anywhere in `plan.yaml` (grep clean). R1 create case, R14 case, R13 wording all fixed. Header Guard-A note corrected.

**`pr_draft_a` is now Option-A seeded** (Alexander picked A): it is created **into** the PR Approval flow (`trigger_workflow: cv237r8h7k9`), lands at the procurement stage (test users carry no department, so the dept stage is skipped), then `fixtures.approvals` has **procurement RETURN it for info** → `status: info_requested`. Verified live: the Procurement Approval node's return branch (branchIndex 1) is wired to "Procurement Returned → Info Requested" (node 373617786945546), which sets `status: info_requested`; a plain return needs no `returnToNodeKey` (node `returnTo: null`). This is the only way to reach the one operations-editable status after D68 — operations cannot write `status` directly. **This fixture path has NOT been executed yet** (review-only session).

## Current state

**Suite fully green: 58/58 (2026-07-05, eighteenth session).** `plan.yaml` = **24 rules / 58 cases**. Run with:

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`). Bare `python3` non-deterministically resolves to system 3.9.6 without deps.

**Rule C revision (D65) ACTIVATED 2026-07-05 (seventeenth session)** — `373589018214400` enabled+current. Predecessor `372552255471616` still enabled (not current) as rollback; disabling it awaits Alexander's explicit word.

**D66 done and green** — ACL + guard live (see D66 Status), R26 cases reworked, reviewed, approved, and passing. Dept-head editable fields on the Dept Owner Approval approver interface: Alexander's UI, no runner case until built.

**D70 guard fix live** — both PR-to-project link guards revised (payload-shape bypass closed); predecessors `372589928710144` / `372610438856704` disabled as rollback.

## Next session starts here

1. **Finish the Step 6 audit surface**: `suppliers` and `departments` still have no rules at all. Draft from live inspection, present as one review group (plain language, concrete examples — see notes.md top), run.
2. Then Step 7 (user-guide backfill for MVPs 1–16) / Step 8 (pilot-outcome report into `nb-project-suite`'s HANDOFF, retire `myNocobase-project-workflow`).

State at close of eighteenth session: suite green 58/58, all 24 rules reviewed and approved, no `# TODO` markers anywhere in plan.yaml, working tree clean.

## Standing review gate — `# TODO verify`

Tracks Alexander's word-by-word review, NOT test-pass; he clears it.
- **Carrying:** none — the PR/PO/po_lines backlog word-review finished 2026-07-05 (fifteenth session). All of R1–R25, R28–R30 are cleared. Stale `# TODO verify` markers on R19/R23 (verified earlier, marker removal missed) were also removed.
- **Nothing marked.** R27 cleared 2026-07-05 (eighteenth session, Alexander's explicit word after the mechanism re-check); R26 cleared same day. **Every rule in plan.yaml is now reviewed and approved, and the suite is green** — the review backlog for PR / PO / po_lines / projects is fully closed.
- **Review protocol changed 2026-07-05 (Alexander):** reviews are now short verdicts — verify the cited mechanism (guard enabled+condition, grant+scope), state holds/doesn't, stop. Coverage is one case per mechanism, not per role; never flag missing role×action matrix combinations. Codified in the nb-test SKILL.md "Coverage scope" section and auto-memory `feedback_test_coverage_lean.md`. Existing fanned-out green cases (e.g. R20/R24) stay as-is — no churn.

## Live-state cleanups flagged, not done (Alexander's call — live writes)

- **Guard A (PR Immutability, id 366217145548800) still carries a dead `cancelled` clause** in its "Status is terminal?" condition (approved OR rejected OR cancelled). Harmless — no PR reaches `cancelled` after D68 — but out of sync. Trimming is a live workflow edit (needs version/revision care). *(The parallel dead `draft` clause on the operations update ACL scope WAS trimmed live this session.)*
- ~~Project guard's reject message stale~~ **FIXED 2026-07-05** (same session, Alexander's go-ahead): new revision `373836840763392` of `2h75zryz3cb` — "or rejected" removed from the message. Also fixed the Receive guard's message (said "sent", a D69-retired status; now "issued") via revision `373836909969408` of `mhfp4d15uee`. Message-only changes, copies diffed identical first; suite re-ran green 58/58 after.
- **Trap hit while re-running:** right after enabling a revision, `triggerWorkflows`-bound actions can 500 with "Workflow on your action hangs" (no execution row). `nb api workflow workflows sync --filter '{"enabled": true}'` fixes it. Recorded in auto-memory (`reference_nb_workflow_revision_gotchas` #4).
- **Predecessor housekeeping**: Rule C's old revision `372552255471616` still enabled-not-current (D65 rollback); D70's two guard predecessors + the two message-fix predecessors (`373789698883584`, `373672421949440`) disabled as rollback. Alexander says leave them for now (2026-07-05).

## Fixture design notes (carry over)

- `operations_proj` is the ONLY dept-bearing test user. **Do not add departments to the existing seeded PR users** — it would change the already-green PR approval chains (and is why PR fixtures skip the dept stage and stop at procurement).
- `pr_draft_a` is shared by R2 (owner edit at info_requested), R13 (not-director-stage deny), R16 (not-approved PO-create deny). All three hold at `info_requested`.
- Chains: projects need 3 steps (Pat dept → Pat procurement → Dana director; budgets 5000 < 15k board threshold). Drawdown PRs need 1 step each (Pat; drawdown branch replaces director/board — R30).
- **Teardown:** project fixtures delete cleanly (guard exempts admin). The two terminal drawdown PRs do NOT (Guard A) — debris grows by 2 labeled PRs per full run, on top of the 4-PR/PO/line set (D60/D62 policy).
- Case order in the file is load-bearing: R28's link-allow and the R29/R30 state cases sit BEFORE the R27 block, whose allow case completes `proj_approved`.
- When reworking R26 cases: the new model needs owner-scoped edit allow, cross-operations edit deny, dept-head stage edit, `remaining_usd` write deny, and rejected-locked deny.

## Before go-live (detail in `notes.md`)

- Re-negate `member`'s `ui.*` snippet (dev convenience; grants UI-edit to everyone under `only-use-union`).
- Assign `finance` role to `fiona.finance` (id 14).
- Move PO payment set-rights to `finance`; move receiving to a warehouse role if created (D59).
- Re-run D57's dead-scope-table check across the whole schema (only PR/PO/po_lines covered).

## Steps 7–8 (not started)

- **Step 7** — `docs/user-guide.md` backfill for MVPs 1–16. Deferred.
- **Step 8** — hand back: pilot-outcome report into `nb-project-suite`'s `HANDOFF.md`, then retire `myNocobase-project-workflow`.

## How Alexander works (carried over, still applies)

- **Plain simple language, concrete examples** (2026-07-05): no jargon in anything he reads. Every rule/test explained as a story — "Oscar tries to edit Olga's draft — blocked", never "cross-role ownership-scope deny". Explain unavoidable technical terms in one sentence on first use.
- **Review-gated by logical group** (changed 2026-07-05; was one step/rule at a time). Present one coherent group — rules or actions sharing a workflow, ACL grant, or mechanism — get feedback, proceed. No whole-plan blasts, no single-rule drip.
- **Review rules, not payloads.** Business rules for approval; mechanism only if asked.
- **Verify NocoBase claims against live state**, not docs/memory/prior sessions.
- **Never touch VPS/production.** He builds all UI himself unless he delegates a screen. API keys: he pastes them into `.env.test` himself — never in chat or committed files.
- Pragmatic about local dev-only risk, but explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config.
