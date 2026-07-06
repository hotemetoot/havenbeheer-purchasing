# HANDOFF — havenbeheer retrofit, Step 6 (updated 2026-07-05, nineteenth session)

**Read this first, then:** `~/.claude/skills/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D63–D71. `notes.md` holds non-queryable traps and the go-live checklist (and, top of file, **how to write for Alexander** — plain language, concrete examples; non-negotiable). Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` if you touch `runner.py`.

## What landed 2026-07-05 (nineteenth session — new-model conversion + R31–R41 drafts)

All three items from the previous handoff's "next session" list, in two commits (`290df42`, `bfd1a40`), working tree clean:

1. **Conversion to the new nb-test model done and green.** 29 ACL-ish runtime cases became 24 `type: acl` config checks (`runner.py acl`, seconds). Six runtime cases are tagged `canary` — one per enforcement mechanism class: R2 pair (scoped grant inside/outside), R17 allow (plain grant), R20 operations deny (no grant), R26 remaining_usd (field whitelist), R27 operations trigger deny (trigger gating). Guard/workflow runtime cases untouched. Full suite after conversion: **52/53 — the one red is a real finding, not a bug in the suite** (next point).
2. **Finding: R2's scope trim never reached the live grant.** The fourteenth session's "live ACL trimmed" edit landed in the DEAD `rolesResourcesScopes` table (row 2, "PR — own and editable", updatedAt 2026-07-04 proves it). The live operations `purchase_requests:update` grant points at the generic "Own records" scope (`363334209503234`, `createdById` only). Concrete effect: Oscar submits a PR, Pat approves it to the director stage — Oscar can still edit title and amount, so Dana approves something Pat never saw. Only approved/rejected are saved by Guard A. Also: R2's "or submitterId" ownership alternative is not in the live scope. **The R2 config check stays red until the live scope is fixed — a live ACL change, Alexander's call.** (The fourteenth session's R2 "verified" row in old handoffs is wrong.)
3. **Finding: procurement's role strategy is view+update+trigger on everything.** Any collection without a per-collection procurement entry falls back to it — `departments` included, so Pat can update any department's `main_approver` and steer approval routing. Flagged on R41's config check (expected red). Alexander picks: trim the strategy (live change) or amend the rule.
4. **R31–R38 drafted** from the live PR Approval node chain (current revision `373617786945536`): dept stage + submitter/department stamps, dept-head approve, head-skip (submitter is their own dept's main approver), custom approver, director threshold (live condition `is_regular != true OR quoted_total_usd >= 300`; fixtures at 250 regular / 300 regular boundary / 100 not-regular), board (live `>= 15000`; a 15000 fixture through the full 3-step chain incl. the board task), returns (procurement + director), reject with stored comment. **R39** formalizes proj_rejected (project dept-stage reject). **R29** gained an exactly-on-budget drawdown fixture (4000; strict `>` still approves) — its committed_usd case expects **5000** now (1000 + 4000), not 1000. **R40/R41** cover suppliers/departments as pure config checks. All `# TODO verify`, hygiene-checked (35 rules / 77 cases), **NOT run** — review gate.
5. **Mechanism notes for the new fixtures:** `is_regular` is not in the operations create whitelist and the runner's approval steps can't carry form values, so the two R35 "regular" fixtures are created `as: admin` via `approvals:create` — that path persisting `is_regular` was verified live with a throwaway PR (deleted after). `custom_approver` is in the PR Approval trigger's appends, so the R34 condition resolves. `oliver_owner` (id 10, password nbtest, verified) joined `fixtures.users` as the head-skip witness. `departmentId` DOES resolve on PRs (real PRs carry it) — no D65-class null here.

> **Concurrency note:** before any write-heavy step, make sure no other session is open on this repo (D68 was once committed from a second terminal mid-session).

Per-session narrative lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). Steps 0–5 done. **Step 6** (extend `tests/plan.yaml` with a full ACL/workflow audit, reviewed in workflow/mechanism groups, verified live) is nearly done: all collections now have drafted coverage; R31–R41 await review.

## Current state

**`plan.yaml` = 35 rules / 77 cases.** Suite standing: **52/53 on the reviewed set** (R1–R30; the one red is the R2 scope finding above). R31–R41's 24 cases are drafted and NOT yet run. Run with:

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`). Bare `python3` non-deterministically resolves to system 3.9.6 without deps. `runner.py acl --project-dir .` runs just the config checks (seconds); `--tag canary` the canaries; `--tag prflow` the new PR-branch cases (after review).

D63–D71 all built + live-verified (see decisions.md). Rule C revision activated; D70 guard fix live; D71 Guard A admin exemption live — teardown fully clean.

## Next session starts here

1. **Alexander reviews, per group** (short verdicts — verify the cited mechanism, state holds/doesn't, stop):
   - **Group A — conversion + canaries** (committed, already green): spot-check that the acl checks say what the rules say; bless the canary choice. Also decide the **R2 scope fix** (live ACL change: point the operations PR-update grant at a scope with `status = info_requested` + own via createdById OR submitterId — the intended clause sits, ironically correct, in dead row 2).
   - **Group B — R31–R39** (PR Approval branches + project reject): word-by-word rule review, then first run: `runner.py run --project-dir . --tag prflow` (R39 rides `--tag projects` or the full run).
   - **Group C — R40–R41** (suppliers/departments): word-by-word, then `runner.py acl`. Decide the **procurement strategy question** (R41 red): trim strategy or amend rule.
2. After all groups: full suite run — target green across 77, then clear the `# TODO verify` markers Alexander approves.
3. Branches deliberately not drafted (runner can't express them): in-app notifications, resubmit-after-return, board document-required form validation — walkthrough/UI territory; say so if Alexander asks where they went. The Project Approval ladder's own board branch (>= 15k) also has no case — flag if he wants it.
4. Then **Step 7** (user-guide backfill for MVPs 1–16) / **Step 8** (pilot-outcome report into the suite's HANDOFF, retire `myNocobase-project-workflow`).

## Standing review gate — `# TODO verify`

Tracks Alexander's word-by-word review, NOT test-pass; he clears it.
- **Carrying: R31–R41** (drafted 2026-07-05, nineteenth session — see "Next session starts here").
- R1–R30: all reviewed and approved (backlog closed 2026-07-05, eighteenth session). The conversion changed only their CASE layer (machine layer, regenerate-freely); rule texts untouched.
- **Review protocol (Alexander, 2026-07-05):** short verdicts; coverage is one case per mechanism, not per role; never flag missing role×action matrix combinations. Codified in nb-test SKILL.md + auto-memory `feedback_test_coverage_lean.md`.

## Live-state cleanups flagged, not done (Alexander's call — live writes)

- **R2 scope fix** — see finding above. The suite stays 1-red until fixed (deliberate).
- **Procurement role strategy** (view+update+trigger global fallback) — see finding above; R41 will read red until decided.
- **Guard A still carries a dead `cancelled` clause** in "Status is terminal?" (harmless post-D68; trimming is a workflow revision).
- **Predecessor housekeeping**: Rule C's old revision `372552255471616` still enabled-not-current; D70/D71 + message-fix predecessors disabled as rollback. Alexander says leave them (2026-07-05).
- Right after enabling a workflow revision, `triggerWorkflows`-bound actions can 500 ("Workflow on your action hangs") — `nb api workflow workflows sync --filter '{"enabled": true}'` fixes it (auto-memory `reference_nb_workflow_revision_gotchas` #4).

## Fixture design notes (carry over)

- `operations_proj` is the ONLY dept-bearing test user; its dept is Procurement (363554444476416, main approver Pat). **Do not add departments to the other seeded PR users** — it would change the already-green PR approval chains. New dept-stage fixtures (pr_dept_pending, pr_dept_flow) reuse operations_proj for exactly this reason.
- `pr_draft_a` is shared by R2 (owner edit at info_requested), R13-era comments, R16 (not-approved PO-create deny), R37 (procurement return witness). It holds at `info_requested`.
- `pr_regular_small`/`pr_regular_300` are created **as admin** (is_regular not in the operations create whitelist); everything else follows the old patterns.
- Approvals-entry order is load-bearing in the after_records pass: within (1000) → boundary (4000) → over (9500) against the 5000 budget.
- Case order in the file is load-bearing: R28's link-allow and the R29/R30 state cases sit BEFORE the R27 block, whose allow case completes `proj_approved`.
- Teardown: clean since D71 (Guard A exempts admin) — terminal PR fixtures delete too.

## Before go-live (detail in `notes.md`)

- Re-negate `member`'s `ui.*` snippet (dev convenience; grants UI-edit to everyone under `only-use-union`).
- Assign `finance` role to `fiona.finance` (id 14).
- Move PO payment set-rights to `finance`; move receiving to a warehouse role if created (D59).
- Re-run D57's dead-scope-table check across the whole schema — note the R2 finding above is exactly this class; dead rows 2/4/5 still exist.
- Revisit procurement's global strategy (this session's finding) as part of that sweep.

## Steps 7–8 (not started)

- **Step 7** — `docs/user-guide.md` backfill for MVPs 1–16. Deferred.
- **Step 8** — hand back: pilot-outcome report into `nb-project-suite`'s `HANDOFF.md`, then retire `myNocobase-project-workflow`.

## How Alexander works

Single home: auto-memory (`feedback_alexander_working_style`, `feedback_review_rules_not_payloads`, `feedback_test_coverage_lean`, `feedback_plain_language_concrete_examples`). Plus one project-level point: pragmatic about local dev-only risk, but explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config.
