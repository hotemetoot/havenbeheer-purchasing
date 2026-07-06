# HANDOFF — havenbeheer retrofit, Step 7 IN PROGRESS (updated 2026-07-06, twentieth session)

**Read this first, then:** `~/.claude/skills/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D63–D73. `notes.md` holds non-queryable traps and the go-live checklist (and, top of file, **how to write for Alexander** — plain language, concrete examples; non-negotiable). Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` if you touch `runner.py`.

## What landed 2026-07-05 (nineteenth session — Step 6 finished, suite 77/77)

1. **New-model conversion done.** 29 ACL-ish runtime cases became 24 `type: acl` config checks (`runner.py acl`, seconds); 6 runtime cases tagged `canary`, one per enforcement mechanism class (R2 pair scoped-grant in/out, R17 plain-grant allow, R20 no-grant deny, R26 field-whitelist ignore, R27 trigger gating). Approved by Alexander as "new test model A".
2. **R31–R41 drafted, reviewed, approved, and green.** PR Approval branch rules from the live node chain (boundaries quoted from condition nodes: director unless regular AND < 300; board >= 15000; drawdown strict >), project dept-reject (R39), suppliers/departments audit (R40/R41). All markers cleared on Alexander's explicit approval this session.
3. **Two live ACL holes found by the new checks, both fixed on Alexander's approval:**
   - **D72** — the 2026-07-04 R2 "scope trim" had landed in the dead scope table; live, a submitter could edit their own mid-flow PR (Dana approves what Pat never saw). Fixed: new scope `373881040338944` (own + info_requested), grant repointed, readback clean.
   - **D73** — procurement's role strategy carried a global `update` fallback reaching departments/users/roles/files/pr_comments (Pat could rewire any department's main approver). Trimmed to `{view, trigger}`; products/units_of_measure unaffected (own entries).
4. **Suite: 77/77 green** (35 rules / 77 cases; acl checks alone 34/34). One case-layer lesson: the Director Approval node has `returnTo: 1` — a director return REQUIRES `returnToNodeKey` (probed live; plain return 400s). The runner step returns to the procurement node `ec2h8cqal32`: status becomes info_requested AND Pat's procurement task re-opens. Dana's UI will ask the same "return to which step?" question — Alexander may want to check that form renders sensibly.
5. Branches deliberately not in the suite (runner can't express them): in-app notifications, resubmit-after-return, board document-required form validation — walkthrough/UI territory. The Project Approval ladder's own board branch (>= 15k project budget) also has no case; flag if wanted.

> **Concurrency note:** before any write-heavy step, make sure no other session is open on this repo (D68 was once committed from a second terminal mid-session).

Per-session narrative lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). **Steps 0–6 done.** Step 6's audit found and fixed two real ACL holes — the pilot's clearest value evidence yet (D70's guard bypass was the third). Remaining: Steps 7–8.

## Current state

**`plan.yaml` = 35 rules / 77 cases, all reviewed and approved, suite fully green 77/77 (2026-07-05).** No `# TODO verify` markers anywhere. Run with:

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`). Bare `python3` non-deterministically resolves to system 3.9.6 without deps. `runner.py acl` = config checks only (seconds); `--tag canary` = enforcement canaries; `--tag prflow` = PR-branch cases; `--tag projects` = projects cases.

D63–D73 all built + live-verified. Rule C revision activated; D70 guard fix, D71 admin exemption, D72 scope fix, D73 strategy trim all live.

## Next session starts here

**Step 7 — `docs/user-guide.md` backfill, IN PROGRESS.** The guide is **not** empty (CLAUDE.md's "starts empty" note is stale, corrected there). A prior session scaffolded §1 who-does-what, §2 lifecycle, §3 status reference, and a full **Stage 1** (create/submit). This twentieth session (2026-07-06) wrote **Stage 2 — the whole approval ladder** (dept → procurement → director → board: the three actions Approve/Return/Reject, the Is-regular routing rule with worked examples, board document gate, return→resubmit, reject) at task-walkthrough depth, and revised Stage 1 (supplier + quote now marked **optional** — Procurement sources them later; added required-field guidance). **That completes the spine, MVP 001.**

**Still to write** (still `_(Draft — to be expanded.)_` stubs in the file): Stage 3 create-PO, Stage 4 issue/send, Stage 5 receiving, Stage 6 complete/invoice/close, Stage 7 print, Appendix suppliers. Plus the two areas the guide's own scope note defers: Projects & budget drawdown (MVP 014) and bulk PO line import (MVP 016). Source maps: `tests/manual-workflow-walkthrough.md` (a verified click-through — treat as live-derived, not a plan) + `roadmap.md`.

**Sourcing method (Alexander, 2026-07-06):** Claude writes each walkthrough from the live app + the verified walkthrough, inserting **screenshot placeholders** (`> 📷 **Screenshot — …**`) with a clear description; Alexander adds the real screenshots after. Every stage's placeholders must still confirm two things on screen: exact button labels, and **where an approver finds a waiting task** (a to-do list / notification / the record itself — the one thing the written steps can't pin down). Verify field labels live before writing (`nb api resource list --resource fields --filter '{"collectionName":"..."}'` → `uiSchema.title`).

**Doc-writing rules now enforced suite-wide** (Alexander, 2026-07-06): match the app's exact labels ("Is regular", "Custom approver" — not "Regular purchase"/"stand-in"); don't present optional fields as mandatory (required lives on the form + linkage rules, not the collection field); drop retired states from docs. Homes: `nb-bootstrap/references/gotchas.md` → "Docs / user-facing writing" + Fields "Required-ness isn't on the field"; auto-memory `feedback-nocobase-docs-app-language`.

**Live cleanup done this session:** removed `sent`/`confirmed` from the `purchase_orders.status` enum (see D69 addendum — D69's "no field-level enum" claim was wrong; there was a `uiSchema.enum`). Enum now `draft, issued, partially_received, received, completed, closed`.

**Step 8 — DONE 2026-07-06.** Pilot-outcome report written into `nb-project-suite`'s `HANDOFF.md` (the three bugs D70/D72/D73, all found by the suite, all locked green). `myNocobase-project-workflow` retired on Alexander's explicit confirm — archived to `~/.claude/skills-archive/`, `my-setup.md` updated. Only Step 7 remains.

Optional small items if Alexander raises them: delete dead scope rows 2/4/5 (go-live sweep covers it), Guard A's dead `cancelled` clause, the Project Approval board-branch case, a scoped pr_comments grant for procurement if comment-editing was a real flow (D73 note).

## Standing review gate — `# TODO verify`

**Nothing marked.** R1–R41 all reviewed and approved (R31–R41 cleared 2026-07-05, nineteenth session, Alexander's explicit approval; suite green same day).
- **Review protocol (Alexander, 2026-07-05):** short verdicts; coverage is one case per mechanism, not per role; never flag missing role×action matrix combinations. Codified in nb-test SKILL.md + auto-memory `feedback_test_coverage_lean.md`.

## Live-state cleanups flagged, not done (Alexander's call — live writes)

- **Guard A still carries a dead `cancelled` clause** in "Status is terminal?" (harmless post-D68; trimming is a workflow revision).
- **Dead scope rows 2/4/5** still in `rolesResourcesScopes` (unreferenced; row 2 even holds the correct R2 clause). Delete during the go-live dead-scope sweep.
- **Predecessor housekeeping**: Rule C's old revision `372552255471616` still enabled-not-current; D70/D71 + message-fix predecessors disabled as rollback. Alexander says leave them (2026-07-05).
- Right after enabling a workflow revision, `triggerWorkflows`-bound actions can 500 ("Workflow on your action hangs") — `nb api workflow workflows sync --filter '{"enabled": true}'` fixes it (auto-memory `reference_nb_workflow_revision_gotchas` #4).

## Fixture design notes (carry over)

- `operations_proj` is the ONLY dept-bearing test user; its dept is Procurement (363554444476416, main approver Pat). **Do not add departments to the other seeded PR users** — it would change the already-green PR approval chains. Dept-stage fixtures (pr_dept_pending, pr_dept_flow) reuse operations_proj for exactly this reason.
- `oliver_owner` (existing persona, id 10, nbtest) is the head-skip witness; `pr_regular_small`/`pr_regular_300` are created **as admin** (is_regular not in the operations create whitelist; approvals:create as admin persists it — verified live).
- Approvals-entry order is load-bearing in the after_records pass: within (1000) → boundary (4000) → over (9500) against the 5000 budget; committed_usd asserts 5000.
- Case order in the file is load-bearing: R28's link-allow and the R29/R30 state cases sit BEFORE the R27 block, whose allow case completes `proj_approved`.
- Director return steps need `returnToNodeKey` (see R37's fixture comment).
- Teardown: clean since D71 (Guard A exempts admin) — terminal PR fixtures delete too.

## Before go-live (detail in `notes.md`)

- Re-negate `member`'s `ui.*` snippet (dev convenience; grants UI-edit to everyone under `only-use-union`).
- Assign `finance` role to `fiona.finance` (id 14).
- Move PO payment set-rights to `finance`; move receiving to a warehouse role if created (D59).
- Re-run D57's dead-scope-table check across the whole schema; delete dead rows 2/4/5 (D72 note).

## How Alexander works

Single home: auto-memory (`feedback_alexander_working_style`, `feedback_review_rules_not_payloads`, `feedback_test_coverage_lean`, `feedback_plain_language_concrete_examples`). Plus one project-level point: pragmatic about local dev-only risk, but explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config.
