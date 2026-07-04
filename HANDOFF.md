# HANDOFF — havenbeheer retrofit, Step 6 (rewritten 2026-07-04, thirteenth session)

**Read this first, then:** `~/.claude/skills/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D63–D68. `notes.md` holds non-queryable traps and the go-live checklist. Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` if you touch `runner.py`.

> **Concurrency note (2026-07-04):** Alexander committed **D68** (`d8927a4`) from a second terminal *during* this session — PR `draft` + `cancelled` retired, applied live. This session's commits stacked cleanly on top, but two sessions were editing havenbeheer at once. Before the next write-heavy step, make sure no other session is open on this repo.

Per-session narrative lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). Steps 0–5 done. **Step 6** (extend `tests/plan.yaml` with a full ACL/workflow audit, rule by rule, verified live) is in progress: PR / PO / po_lines covered and green; the **projects rules R25–R30 are now reviewed** (this session). `suppliers` and `departments` still have no audit.

## What landed this session (2026-07-04, thirteenth — review only, no runner execution)

Alexander reviewed the projects rules R25–R30 word by word; each claim re-verified against live state as it was presented. Two committed checkpoints: `edf1592` (the twelfth session's uncommitted draft, committed at session start) and `c99f137` (this review). **Working tree clean.**

| Rule | Outcome | Marker |
|---|---|---|
| R25 | Verified live — only operations holds a projects `create` grant | cleared |
| R26 | **Rewritten** from live "any operations edits any draft" to owner- and stage-scoped intent (D66) | build+verify |
| R27 | **Renamed** project terminal `closed → completed` (D67); chain logic verified live 7/7 | build+verify |
| R28 | Verified live (not-approved link check on create *and* update guards); reworded off the stale terminal word | cleared |
| R29 | Verified live (over-budget auto-reject on procurement approval; strict `>`; committed recompute approved-only) | cleared |
| R30 | Verified live (drawdown skips director+board unconditionally, no amount operand — confirmed from branch topology) | cleared |

**Two decisions logged, both live builds NOT done (Alexander approves/runs):**
- **D66** — projects edit ACL to match rewritten R26: operations `update` → `createdBy` own-records scope; drop `remaining_usd` (a formula) from the operations/procurement/director update whitelists; enforce per-stage approver edits (dept head at pending_dept_approval, procurement at pending_purchasing_review, director at pending_director_approval) — likely via the approval process's node-level editable fields, since the D63 immutability guard blocks all direct `projects:update` at every pending stage.
- **D67** — rename `closed → completed`: `projects.status` enum value+label, `closed_at` field → `completed_at` (+ migrate any existing `status: closed` rows), Close Project workflow (`373522687393792` / `px2xvjaxoqf`) → "Complete Project" success node + reject messages, D63 guard (`373520806248448`) locked-status list, and the `proj_closed` fixture/cases.

## Current state

**Old suite last known green 33/33** (twelfth session; **not re-run this session** — this session read and reviewed only). `plan.yaml` = **24 rules / 55 cases**. Run it with:

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`). Bare `python3` non-deterministically resolves to system 3.9.6 without deps.

**DO NOT run the projects rules yet.** R25/R28/R29/R30 would pass, but the **R26/R27 cases are now stale** — they still assert the old "any operations edits any draft" behavior and use `proj_closed`. They must be reworked to the new model (D66) and `completed` (D67) before a run means anything. The projects fixtures still build on any run.

**Rule C revision (D65) still NOT activated** — verified live this session: `373589018214400` disabled + not current; buggy `372552255471616` current+enabled. Activation is Alexander's one-step action: enable+current on `373589018214400`, disable `372552255471616`.

**D68 broke part of the PR suite — fix before ANY run.** Alexander applied D68 live this session: `purchase_requests.status` no longer has `draft` or `cancelled` (default now `pending_dept_approval`), and the `cancellation_reason`/`cancelled_at` fields were dropped. Consequences for `plan.yaml`, not yet fixed (Alexander's review territory): the **`pr_draft_a` fixture seeds `status: draft`, which is now an invalid enum value** — it will fail on the next run; **R2 is reopened** (D68: "draft or info_requested" → info_requested only) even though it was previously cleared; and the header note on `cancelled` is stale. These fixture/rule fixes gate a clean run alongside the R26/R27 work.

## Next session starts here (order set by Alexander)

1. **Backlog word-review FIRST** — Alexander reviews the older rule TEXTS still carrying `# TODO verify`: **R4, R5, R12, R13, R14, R16, R17, R18, R20, R21, R22, R24**, plus **R2 (reopened by D68)**. These were green in the suite before D68; this is the review gate (his sign-off on wording), not test-pass. Present ONE at a time, re-verify each claim live, clear the marker on his OK. While here, **reconcile D68**: any PR rule referencing `draft`/`cancelled` needs updating, and the `pr_draft_a` fixture (`status: draft`) must be re-pointed to a valid status. (R1, R3, R15, R19, R23 stay cleared; R2 no longer.)
2. **Then D67 (the rename) in a fresh session** — Alexander's explicit sequencing. Mechanical live build; unblocks clean R27 cases.
3. **D66** — projects-edit ACL + approval-process build (the heavier one). Then rework the R26/R27 cases.
4. **Rule C activation (D65)** — one-step user action, still pending; do whenever convenient.
5. **First projects run** — `run --seed --project-dir .` once R26/R27 cases are reworked (seed creates `test_operations_proj@test.local`, main department Procurement `363554444476416`). Expect 55 cases. On failure, classify rule / case / app before touching anything.

## Standing review gate — `# TODO verify`

Tracks Alexander's word-by-word review, NOT test-pass; he clears it. Carrying: **R2 (reopened by D68), R4, R5, R12, R13, R14, R16, R17, R18, R20, R21, R22, R24**. Cleared: R1, R3, R15, R19, R23, **R25, R28, R29, R30**. On `# TODO build+verify` (approved text, needs a build to pass): **R26, R27**.

## Fixture design notes (projects) — carry over

- `operations_proj` is the ONLY dept-bearing test user. **Do not add departments to the existing seeded users** — it would change the already-green PR approval chains.
- Chains: projects need 3 steps (Pat dept → Pat procurement → Dana director; budgets 5000 < 15k board threshold). Drawdown PRs need 1 step each (Pat; drawdown branch replaces director/board — R30).
- **Teardown:** project fixtures delete cleanly (guard exempts admin). The two terminal drawdown PRs do NOT (Guard A) — **debris grows by 2 labeled PRs per full run**, on top of the existing 4-PR/PO/line set (D60/D62 policy).
- Case order in the file is load-bearing: R28's link-allow and the R29/R30 state cases sit BEFORE the R27 block, whose allow case closes/completes `proj_approved`.
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

- **Step by step, review-gated.** Present ONE step, get feedback, proceed.
- **Review rules, not payloads.** Business rules for approval; mechanism only if asked.
- **Verify NocoBase claims against live state**, not docs/memory/prior sessions.
- **Never touch VPS/production.** He builds all UI himself unless he delegates a screen. API keys: he pastes them into `.env.test` himself — never in chat or committed files.
- Pragmatic about local dev-only risk, but explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config.
