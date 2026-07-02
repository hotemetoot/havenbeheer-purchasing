# HANDOFF — havenbeheer retrofit, Steps 6–8 remain (from a session on 2026-07-02)

**Read this first, then `~/nocobase/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (the authoritative step list) and this project's new `CLAUDE.md`.**

## What this is

This project (`Havenbeheer Purchasing`) is partway through being retrofitted onto `nb-project-suite`'s conventions — the plan above is the one-off retrofit plan written specifically for this project (see that plan's own header for why it's a plan, not a skill mode). It's also `nb-project-suite`'s deliverable-6 pilot: proving the suite works end-to-end on a real, already-mature project (16+ MVPs shipped).

## What's done (Steps 0–5, this session, 2026-07-02) — 6 commits, all reviewed with Alexander

1. **Step 0 (scope check):** all 4 of the plan's open questions resolved — run now; delete the stray `.claude/worktrees/focused-wiles-830d33/` debris (done); leave historical `roadmap.md` rows as-is; keep `role-acl-guidelines.md` standalone.
2. **Step 1 (prereqs):** git dirty-but-expected (smoke-test residue, see below); `.gitignore` already correct; env reachable.
3. **Worktree cleanup:** removed the registered git worktree (`git worktree remove`) and its orphaned branch `claude/focused-wiles-830d33` (no commits ahead of master — confirmed abandoned, 7 weeks stale, its uncommitted content already superseded in master's real history).
4. **Step 2 (drift report):** queried live collections/workflows/roles/ACL via `nb api` + the `nocobase-acl-manage` skill. Findings:
   - `roadmap.md` row 009b was stale (described the retired Send+budget-zones mechanism with no pointer to D46, which superseded it) — **fixed**.
   - `member` role's `ui.*` snippet is un-negated (not vanilla) — **confirmed intentional** by Alexander (dev convenience so any test user can enter UI edit mode). Tracked in `notes.md` under "Before go-live" — **must be re-negated before real end users get accounts.**
   - `systemSettings.roleMode` is live `only-use-union`, undocumented anywhere as a decision (only prior record said `allow-use-union`) — Alexander confirmed this was deliberate (composability + preventing user confusion from accidental role-switching) and gave the reasoning. **Recorded as D54** in `decisions.md`.
5. **Step 3 (mine + retire `project_current_state.md`):** read the full 594-line file. Confirmed almost all decision-shaped content (D40–D53) already existed in `decisions.md` — the file was mostly a redundant running dev-log. Non-queryable content (traps, the Stale IDs list, go-live checklist, test-persona note, project-specific gotchas) migrated to new `notes.md`. File deleted in its own commit.
6. **Step 4 (roadmap fix):** 009b row corrected (see above).
7. **Step 5 (CLAUDE.md):** replaced with `nocobase-bootstrap`'s template, filled in with Havenbeheer specifics. Kept/dropped diff reviewed with Alexander live — see that commit message for the full list. Notably kept: the `nocobase-dsl-reconciler` "don't use it here" warning, after Alexander asked what that skill does — his call was to keep it as a project-specific tripwire since switching this project to a YAML/git-commit build model would be a real fork, not a minor tool choice.
8. **`role-acl-guidelines.md` §6 corrected** to match live reality (roleMode, the `member.ui.*` dev convenience, and — caught mid-edit — the "director/board hardcode approvers" claim was itself already stale; D40 replaced hardcoded ids with data-driven `departments.main_approver` lookups back in 2026-06-11, verified live before writing the correction).

Commits, in order: worktree/branch cleanup (no commit, direct git ops) → `b696e95` (notes.md + decisions.md D54 + role-acl-guidelines.md) → `2a7a62f` (retire project_current_state.md) → `a786794` (roadmap 009b fix) → `b13c95e` (CLAUDE.md replacement).

## What's left

### Step 6 — extend `tests/plan.yaml` (the bulk of the remaining work)

Current state: 3 rules (R1–R3) on `purchase_requests`/`operations`, already passed 4/4 live on 2026-07-02 (`tests/reports/20260702-091759.md`). **First action: drop their `# TODO verify` tags** — they're settled, don't re-flag them.

Then: draft additional rules from a fresh live ACL/workflow inventory (re-query — don't reuse this session's snapshot verbatim, state may have moved). 16+ MVPs means real breadth; this plan explicitly expects it to span multiple sessions, split by collection or MVP group. Every new rule gets `# TODO verify`, reviewed word-by-word by Alexander before being trusted. Generate cases, seed test users, run scoped by group (`--rule`/`--tag`) as rules get reviewed; full suite only once everything drafted so far is reviewed.

Reference points from this session's drift report (re-verify live, don't assume still current):
- Enabled workflows as of 2026-07-02: Guard A (PR immutability), Create-PO guard, PO Receiving recompute, PO/PO-line immutability guards, Generate PO, Complete PO, PO Line Create guards (terminal + budget ceiling ×2), Close PO + Close Guard, Issue PO, PO Lines recompute (create/update + delete), Project Approval, PR Budget guards (create/update), Project Commit recompute (create/update + delete), PR Approval.
- Roles: `admin`, `director`, `finance`, `member`, `operations`, `procurement`, `root`. `procurement` and `operations` both have well-formed independent resource permissions on `purchase_requests` (verified against `role-acl-guidelines.md`, no drift found there).
- First-run failures split three ways (rule wrong / case wrong / app wrong) per the standard ambiguity rule — on a project this mature, an app-wrong finding is a priority fix, not a nuisance.

### Step 7 — `docs/user-guide.md`

Starts empty. Explicitly optional/deferred — backfilling docs for the 16+ already-shipped MVPs is its own future chunk, not part of this retrofit.

### Step 8 — hand back

Once Step 6 covers what Alexander wants covered: summarize what changed vs. what deliberately didn't (see the plan's own Step 8 template), and report back to the `nb-project-suite` build (deliverable 6 pilot outcome) — that project's own `HANDOFF.md` is waiting on this pilot before retiring `myNocobase-project-workflow`.

## How Alexander works (carried over from the nb-project-suite HANDOFF, still applies)

- Step by step, review-gated. Present ONE step, get feedback, proceed. Do not blast ahead. This session ran entirely this way — expect the same.
- Verify NocoBase-specific claims (live state, CLI behavior) rather than trusting docs/memory — this session caught two stale claims this way (roadmap 009b, and a "hardcoded approvers" claim I almost copied into `role-acl-guidelines.md` before checking live data).
- Never touch VPS/production. Local only.
