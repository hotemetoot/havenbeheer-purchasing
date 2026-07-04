# HANDOFF — havenbeheer retrofit, Step 6 (rewritten 2026-07-03, eleventh session)

**Read this first, then:** `~/.claude/skills/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D55–D64 (PO/po_lines audit + the new projects hardening). `notes.md` holds non-queryable traps and the go-live checklist. Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` only if you touch `runner.py` or the `nocobase-test` skill. (The suite moved from `~/nocobase/nb-project-suite/` to `~/.claude/skills/nb-project-suite/` on 2026-07-03 — it's now installed as a skills-directory plugin.)

Per-session narrative lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). Steps 0–5 done. **Step 6** (extend `tests/plan.yaml` with a full ACL/workflow audit, rule by rule, verified live) is in progress: PR/PO/po_lines covered; **projects backend hardening just landed (D63/D64); projects test rules are the next work**. Then `suppliers`, `departments`.

## Current state

**Suite is 33/33 green, 18 rules** (unchanged this session — the eleventh session built live config, no new plan.yaml rules yet). Run it with:

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`). Bare `python3` is non-deterministic here: `.zprofile` prepends Homebrew only for login shells, so a non-login shell gets `/usr/bin/python3` (3.9.6, no deps) and the runner exits "Missing dependency: requests." Don't install into system python — just pin the interpreter. (`--seed` only when adding a new `test_*` fixture user; `existing: true` personas are sign-in-only.)

**What's covered.** `purchase_requests` (R1–R3, R12–R16) and `purchase_orders`/`po_lines` ACL across all 5 roles: R4/R5 (create-deny), R15 (create-from-approved allow), R16 (create-from-unapproved deny), R17 (procurement PO header update allow / delete deny), R18 (terminal-PO immutability), R19/R23 (finance/operations create-deny), R20 (director/finance/operations PO update+destroy deny), R21 (procurement line add/update/over-budget/delete-while-draft), R24 (director/finance/operations line update+destroy deny). R22 (receiving) closed out the PO/po_line set in the tenth session.

**Fixture toolkit** (all verified live this project — reuse as templates):
- `fixtures.records` with `trigger_workflow:` — create a record *into* an approval workflow (via `approvals:create`; a plain create does NOT trigger it).
- `fixtures.approvals` — drive a record through N approval decisions as the real assigned approvers (`pat_procurement` id 11 / `dana_director` id 12, both `existing: true`, shared `nbtest` password; assignees resolve from `departments.main_approver`, D40).
- `fixtures.records` with `after_approvals: true` — seed a record in a second pass *after* approvals run (D61).
- `fixtures.actions` — fire a custom-action / one-click workflow via `triggerWorkflows` and assert the result status (D62). Used to close a PO; will be used to close a project.

## Projects — hardened this session (eleventh, 2026-07-03), D63/D64

Business rules locked with Alexander 2026-07-03:
- **Operations creates a project → approval ladder → approved → PRs draw against `budget_usd` → procurement closes it when finished. Approved projects are immutable.**
- **Director-skip for project-linked PRs stays unconditional** (any PR on an approved project: dept + procurement approve, director + board skipped — D49 confirmed, no threshold).
- **Board stage approver = procurement (Pat) is intended** — the real board approval is a physical document; procurement uploads it (`approval_document`).

Built + live-verified (both `enabled`+`current`, zero test debris left):
- **`Guard: Project Immutability`** — request-interception `2h75zryz3cb` (id `373520806248448`), global, update+destroy on projects. Locked from submission onward (all `pending_*`, `approved`, `closed`); directly editable only in `draft`/`info_requested`/`rejected`. **Admin/root exempt via in-chain roles lookup** (deliberate — keeps teardown possible, avoids the po_lines global-guard debris problem). Approval-plugin writes bypass interception structurally — proven 15/15 with a full live ladder incl. dept **return → applicant resubmit with edited justification** while the guard was active (D63).
- **`Close Project`** — custom-action `px2xvjaxoqf` (id `373522687393792`, sync), fired via `POST projects:trigger?filterByTk=<id>&triggerWorkflows=px2xvjaxoqf`. Only procurement (or admin/root), only on `approved`; sets `status=closed` + new `closed_at` field. Procurement got an explicit **`trigger` action grant on projects**. Verified 7/7 (D64). The Close PO post-action pattern was NOT reusable — D63's guard would block the underlying update; `:trigger` is not an update.

Key live facts for the projects test rules (audited node-by-node this session):
- **Project Approval `hzykothf9cx`, current ver `372552255471616`.** Ladder: submit → status `pending_dept_approval` (+ submitter/department write) → skip-dept condition (creator == own dept's `mainApproverId`) → Dept Owner Approval (assignee = creator's `mainDepartment.mainApproverId`) → Procurement Approval (Pat) → Director Approval (Dana) → board condition `budget_usd >= 15000` → Board Approval (Pat). All stages `endOnReject: true`, `withdrawable: false`, `centralized: true`.
- **Projects ACL:** operations create/update `[title, description, budget_usd, justification, attachments]`; procurement update `[rejection_*, approval_document, attachments]` + **trigger**; director update `[rejection_*, attachments]`; view for everyone via member's global `view` strategy; finance has no per-resource entry; **nobody has destroy** (admin only). All scopes = all records.
- **`<collection>:trigger` IS ACL-gated** — needs an explicit `trigger` action in the role's resource config (403 without). The tenth session's "non-admin procurement not ACL-blocked on the verb" note was true only because procurement's PO grant already contained `trigger`. (Corrects the R22 narrative.)
- **Creating a field auto-appends it to existing ACL field whitelists** (`closed_at` appeared in procurement's view/update lists unasked).
- **PR-side budget enforcement** (unchanged, D53): create guard blocks linking a PR to a non-approved project (covers closed); the real cap is the PR-Approval backstop at procurement-approve (Σ approved siblings + this PR > `budget_usd` → auto-reject); commit-on-approval. PRs have **no amount at creation** — `quoted_total` comes from procurement during review, so creation-time blocking is impossible by design.
- **The drawdown branch has never run live** — zero PRs link to a project; `committed_usd` = 0 on both live projects. Recompute A/B + backstop are enabled but unexercised.
- Two real approved projects exist: PRJ-26-0015 ($10k) / PRJ-26-0016 ($20k), both created by oliver via the **skip-dept path** — the dept stage first ran during this session's guard verification, not before. Both have `department = null` (see open items).

### Open items on projects (next session starts here)

1. **Rule C — department-null fix (approved in principle, not built):** the ladder's first update node writes `departmentId` from `{{$context.applicant.mainDepartmentId}}`, which resolves null (both live projects prove it). Fix: use the appended `{{$context.data.createdBy.mainDepartment.id}}`. Needs a **same-key revision** of `hzykothf9cx` (it has executed). Cosmetic — assignee routing doesn't use the record field.
2. **Draft the projects test rules** (live ACL/guard audit is done — go straight to rules → Alexander's word-by-word review → cases → run). Candidate rule set: only operations creates; immutability denies (mid-flow + approved + closed, per role) with the approval-path pass-through as the allow side; close allow (procurement on approved) / denies (operations 403, draft 400, re-close 400); PR-link guard (non-approved/closed project deny); over-budget backstop auto-reject; unconditional director-skip on a project PR.
3. **Fixture note:** seeded `test_*` users have **no mainDepartment** — a project submitted by one stalls at the dept stage (assignee resolves null). Do NOT add a department to the existing seeded users (it would change the already-green PR-test approval chains). Pattern that worked this session: a dedicated fixture user whose `departmentsUsers` row points at the **Procurement dept (363554444476416, main approver = Pat)** so pat handles the dept stage with known credentials; or submit as a user who is their own dept approver to use the skip path deliberately.
4. **UI (Alexander builds):** Close button on the Projects page = "Trigger workflow" button bound to `px2xvjaxoqf`; the D49 deferred item "board `approval_document` required" is still open; the procurement-form remaining-budget guardrail (D53) is still a UX-layer-only idea.
5. After projects: same method for `suppliers` and `departments` (untouched — no audit done yet).

## Standing review gate — `# TODO verify`

`# TODO verify` on a rule means **Alexander hasn't reviewed the rule text word-by-word** — it tracks his review, NOT test-pass. He clears it, not you. Currently carrying it: R4, R5, R12, R13, R14, R16, R17, R18, R20, R21, R22, R24. (R1–R3, R15, R19, R23 are clear. R22's text was approved in-session 2026-07-03 but the marker awaits his explicit clear.)

## Debris (accepted, D60/D62)

Each full run drives 4 approval chains (`pr_approved`/`_2`/`_3`/`_4`) and leaves: 4 approved PRs, a closed PO with its line, and one **orphaned po_line** — teardown deletes the issued PO header fine but the line-destroy guard (`global: true`, blocks admin) keeps the issued PO's line. All labeled `[TEST]`, uncleanable via API; clean up at the DB level when noisy. **The projects guard deliberately exempts admin so projects fixtures will NOT add to this debris** — this session's two verification runs tore down completely (approvals rows cascade-delete with the project).

## Before go-live (detail in `notes.md`)

- Re-negate `member`'s `ui.*` snippet (un-negated for dev convenience; with `only-use-union` it grants UI-edit to every user now).
- Assign the `finance` role to `fiona.finance` (id 14; currently only `member`).
- Move PO payment set-rights (`payment_status`/`payment_date`) from `procurement` to `finance` when finance users exist; move `received_quantity` receiving to a warehouse role if one is created (D59).
- Re-run D57's dead-scope-table check across the whole schema (only PR/PO/po_lines were covered).

## Steps 7–8 (not started)

- **Step 7** — `docs/user-guide.md` backfill for MVPs 1–16. Still empty, deferred, not part of this retrofit.
- **Step 8** — hand back: when Step 6 is done, summarize what changed vs. what deliberately didn't, and write a final pilot-outcome report into `nb-project-suite`'s own `HANDOFF.md`. Then retire `myNocobase-project-workflow`.

## How Alexander works (carried over, still applies)

- **Step by step, review-gated.** Present ONE step, get feedback, proceed. Do not blast ahead through a plan even when it's fully written.
- **Review rules, not payloads.** For any live config/ACL change, present the business rule — who can do what, under which condition, and why — for approval or correction, then execute. Don't lead with JSON/CLI args; show the mechanism only if asked.
- **Verify NocoBase claims against live state**, not docs/memory/prior sessions. An ACL grant that reads back fine isn't the same as being right (D57), let alone enforced (`nocobase-test`'s whole job). This session's example: "the trigger verb isn't ACL-gated" from R22 didn't transfer — it 403'd on projects until the grant existed.
- **Never touch VPS/production.** Local only; he pushes deploys himself. He builds all UI himself unless he delegates a screen. API keys: he pastes them into `.env.test` himself — never in chat or committed files.
- Pragmatic about local dev-only risk (test fixtures, shared passwords, reusing dev personas), but get an explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config — not a general go-ahead.
