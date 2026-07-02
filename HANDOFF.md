# HANDOFF — havenbeheer retrofit, Step 6 continues (rewritten 2026-07-02, sixth session)

**Read this first, then `~/nocobase/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (the authoritative step list) and this project's `CLAUDE.md`.** Also skim `~/nocobase/nb-project-suite/HANDOFF.md` if you're touching `runner.py` itself or the `nocobase-test` skill — it's the shared tool's own history, not repeated here.

This file replaces the previous revision. Older session detail (D55–D58, the approval-chain mechanism build, the scope-table bug) is preserved in `decisions.md` and git history — not repeated here except where it's still actionable.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, already-mature project (16+ MVPs shipped). Steps 0–5 are done. Step 6 (extend `tests/plan.yaml` with a full ACL/workflow audit) is in progress and is the bulk of remaining work — expected to span several more sessions.

## Where Step 6 actually stands right now

**Drafted and green (10/10 passing):** R1–R5, R12, R13, R14, R16. Run `python3 ~/nocobase/nb-project-suite/tools/nb-test/runner.py run --project-dir .` from this project root to confirm. Note: on a fresh shell you may need `python3 -m pip install requests pyyaml --break-system-packages` first — the runner has no bundled env.

**R12 done this session, and it found a real bug, not just a test.** Drafting R12 (director update allowed at `pending_director_approval`) meant checking exactly which fields director's D55/D57 grant whitelisted — `project`, `projectId`, `rejection_comment`, `rejection_reason_category`, `signature`. Alexander flagged `project`/`projectId` as wrong: a director should approve/reject/return and optionally comment, not reassign a PR's project. Checked directly (not assumed): the render-enabler pattern (D38) is explicitly meant to be "minimal fields," and the live Director Approval workflow node's own config doesn't reference `project`/`projectId` anywhere. Confirmed as an oversight, same shape as D55/D57. **Fixed: D58** — narrowed director's update whitelist to 3 fields. R12 now asserts the allow side against the corrected grant; R13 (deny outside the approval stage) still passes unaffected.

**The approval-chain test fixture mechanism (built/verified last session) is now used routinely.** R12's fixture drives a fresh PR one real approval step (Procurement, via the real `pat.procurement` persona — `existing: true` in `fixtures.users`, since `approvalRecords:submit` checks the actual assigned `userId`) to land it at `pending_director_approval`, then asserts. See `tests/plan.yaml`'s `fixtures.approvals` block for the pattern — reuse it directly for R15/R17–R24 below.

**Known leftover debris:** a scratch test PR (`[TEST-SCRATCH] trigger_workflow check`) from last session's mechanism verification landed at `status: approved` and is now locked by Guard A (PR Immutability Guard) — couldn't be destroyed via the API. Still sitting in the live database. Harmless (clearly labeled, no real data), but flagged — clean up manually if it bothers you, otherwise safe to ignore.

## Next steps, in order

1. **R15/R17–R24 need their rule text derived first — it doesn't exist yet.** These rule numbers are reserved for `purchase_orders`/`po_lines` permission rules, but unlike R12 (whose meaning was already written down), R15/R17–R24's actual content requires a live ACL audit of those two collections across all 5 roles — the same kind of audit that produced D55–D58 for `purchase_requests`. Not started. Do this before trying to write any cases for these numbers. Given what R12 just turned up, don't just transcribe whatever the live ACL config currently says — check each grant against a stated reason (workflow node config, an existing decision, or ask) before writing the rule as correct-by-definition.

2. **Untouched collections/roles**, once the above is done: `projects` (has its own `Project Approval` workflow — expect the same approval-chain fixture pattern to apply), `suppliers`, `departments`, and the remaining roles' full permission surface on every collection.

## Before go-live (see `notes.md` for detail)

- `member`'s `ui.*` snippet must be re-negated (currently un-negated for dev convenience; grants UI-edit to every user under `only-use-union` role mode).
- `fiona.finance` needs the `finance` role actually assigned (currently only holds `member`; no impact yet since no finance approval stage exists).
- D57's dead-scope-table check only covered `purchase_requests`/`purchase_orders`/`po_lines` — re-run across the whole schema before go-live.

## Step 7 — `docs/user-guide.md`

Still empty, still explicitly deferred, not part of this retrofit.

## Step 8 — hand back

Not yet — Step 6 isn't done. When it is: summarize what changed vs. what deliberately didn't, and do a final pilot-outcome report to `nb-project-suite`'s own `HANDOFF.md` (already being kept current incrementally).

## How Alexander works (carried over, still applies)

- Step by step, review-gated. Present ONE step, get feedback, proceed.
- Verify NocoBase-specific claims against live state, not docs/memory/prior sessions. D57 (scope config that read back fine but was silently unenforced) and D58 (a field whitelist that read back fine but had no stated reason for two of its fields) are both examples of why — an ACL grant looking configured isn't the same as it being *right*, on top of `nocobase-test`'s existing job of proving it's *enforced*.
- Never touch VPS/production. Local only.
- Pragmatic about local dev-only risk (test fixtures, shared passwords, reusing real dev personas) — but always get an explicit, specifically-named confirmation before mutating real accounts, data, or live ACL config, not just a general go-ahead. This session's D58 ACL write was confirmed explicitly before applying.
