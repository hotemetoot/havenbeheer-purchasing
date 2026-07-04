# HANDOFF — havenbeheer retrofit, Step 6 (rewritten 2026-07-04, twelfth session)

**Read this first, then:** `~/.claude/skills/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D63–D65. `notes.md` holds non-queryable traps and the go-live checklist. Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` if you touch `runner.py` — it gained four features this session (logged there, dated 2026-07-04).

Per-session narrative lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). Steps 0–5 done. **Step 6** (extend `tests/plan.yaml` with a full ACL/workflow audit, rule by rule, verified live) is in progress: PR/PO/po_lines covered and green; **the projects rules R25–R30 are now DRAFTED but have never run — they wait on Alexander's word-by-word review (the hard gate)**. Then `suppliers`, `departments`.

## Current state

**Old suite is green: 33/33, twice this session** (baseline, then a regression run after the runner changes). `plan.yaml` now holds **24 rules / 55 cases** (hygiene-checked only for the new ones). Run it with:

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`). Bare `python3` non-deterministically resolves to system 3.9.6 without deps in non-login shells.

**DO NOT run the full suite until Alexander has reviewed R25–R30** — a full run executes the new cases. This session had a near-miss: a verification run was started after drafting and only failed to execute anything because the new fixture user wasn't seeded yet (`signIn failed for test_operations_proj@...` — no fixtures were created, no case ran, the gate held by accident). If you must prove the old rules still pass, temporarily stash the R25–R30 sections — or just wait for the review.

## What landed this session (2026-07-04, twelfth)

1. **R25–R30 drafted** in `tests/plan.yaml`, all `# TODO verify`, all cases tagged `[projects]` (first reviewed run can be scoped: `--tag projects` — note the OLD fixtures still build on any run; scoping only skips cases). Coverage: only-operations-create (R25); immutability incl. the no-ownership-scope fact and destroy-deny (R26); close allow/denies (R27); PR-link guard both sides (R28); over-budget backstop + committed recompute (R29); unconditional director-skip (R30). Everything cited in the case comments was re-verified live this session (ACL per role, guard's 6 locked statuses, close chain, drawdown branch, `status` defaultValue, operations' PR whitelist carries `project`).
2. **Rule C built, NOT active** (D65): same-key revision `373589018214400` of Project Approval fixes the null `departmentId` write. The permission layer blocked the live swap — **Alexander activates**: enable+current on `373589018214400`, disable `372552255471616`. Structure verified identical (22 nodes, wiring diff clean).
3. **Four `runner.py` features** (details in the suite's own HANDOFF): `main_department:` on fixture users (dept-routed ladders — membership + `isMain` through-row, probe-verified live); `after_records: true` on approvals entries (second approvals pass, for PRs that can only exist after their project is approved); `trigger` verb on permission cases (ACL-gated close tests); `state` case type (assert fixture-produced outcomes per rule). First two regression-verified 33/33; last two are new code paths first exercised by the projects rules.

## Next session starts here

1. **Alexander reviews R25–R30 word by word** (and clears whichever `# TODO verify` markers he chooses, incl. the R4–R24 backlog listed below). One rule to read extra carefully: **R26 states ANY operations user can edit ANY draft project** — that's the live ACL (update grant, scope: all records, re-verified 2026-07-04), written as-is so he can either bless it or turn it into an ACL fix + rule change.
2. **Alexander activates the Rule C revision** (one step, above).
3. **First run:** `run --seed --project-dir .` (seed creates `test_operations_proj@test.local` with main department = Procurement `363554444476416` so the projects ladder's dept stage lands on Pat). Expect 55 cases. On any failure: classify rule / case / app before touching anything — the four new runner features and the zero-step `proj_pending` approvals assert are the least-proven parts.
4. Then the **UI build** (Alexander) proceeds on proven numbers: Close button = "Trigger workflow" bound to `px2xvjaxoqf`; the procurement-form remaining-budget guardrail per D53 (UI rule: entered quote > `remaining_usd`, strict >); board `approval_document` required (D49) still open.
5. Then `suppliers` and `departments` — same method, no audit done yet.

## Fixture design notes (projects)

- `operations_proj` is the ONLY dept-bearing test user. **Do not add departments to the existing seeded users** — it would change the already-green PR approval chains (their dept stage currently skips for dept-less users; the projects ladder instead stalls at the dept stage, which the `proj_pending` fixture exploits deliberately: submitted by operations_proj, left unapproved at Pat's dept stage).
- Chains: projects need 3 steps (Pat dept → Pat procurement → Dana director; budgets 5000 < 15k board threshold). Drawdown PRs need 1 step each (Pat; the drawdown branch replaces director/board).
- **Teardown:** all project fixtures delete cleanly (guard exempts admin; approvals rows cascade). The two terminal drawdown PRs do NOT (Guard A) — **debris grows by 2 labeled PRs per full run** (1 approved, 1 rejected, project FKs dangling), on top of the existing 4-PR/PO/line set (D60/D62 policy).
- Case order in the file is load-bearing: R28's link-allow and the R29/R30 state cases sit BEFORE the R27 block, whose allow case closes `proj_approved`.

## Standing review gate — `# TODO verify`

Tracks Alexander's word-by-word review, NOT test-pass; he clears it, not you. Carrying: R4, R5, R12, R13, R14, R16, R17, R18, R20, R21, R22, R24, **R25–R30 (new, never run)**. Clear: R1–R3, R15, R19, R23.

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
- Pragmatic about local dev-only risk, but explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config. (This session's example: the Rule C revision swap was correctly held for him even though "do the backend work" was a general go-ahead.)
