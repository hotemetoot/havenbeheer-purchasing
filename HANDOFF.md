# HANDOFF — havenbeheer retrofit, Step 6 (rewritten 2026-07-03, tenth session)

**Read this first, then:** `~/.claude/skills/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D55–D62 (the PO/po_lines ACL+workflow work this step is built on). `notes.md` holds non-queryable traps and the go-live checklist. Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` only if you touch `runner.py` or the `nocobase-test` skill. (The suite moved from `~/nocobase/nb-project-suite/` to `~/.claude/skills/nb-project-suite/` on 2026-07-03 — it's now installed as a skills-directory plugin, so the `nocobase-test` skill is active in every session and knows where the runner lives.)

This is a full rewrite. Per-session narrative before this (D55–D62, the runner fixes, the ACL audit) lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). Steps 0–5 done. **Step 6** (extend `tests/plan.yaml` with a full ACL/workflow audit, rule by rule, verified live) is in progress and is the bulk of remaining work.

## Current state

**Suite is 33/33 green, 18 rules** (R22 added and run green 2026-07-03, tenth session). Run it with:

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`). Bare `python3` is non-deterministic here: `.zprofile` prepends Homebrew only for login shells, so a non-login shell gets `/usr/bin/python3` (3.9.6, no deps) and the runner exits "Missing dependency: requests." Don't install into system python — just pin the interpreter. (`--seed` only when adding a new `test_*` fixture user; `existing: true` personas are sign-in-only.)

**What's covered.** `purchase_requests` (R1–R3, R12–R16) and `purchase_orders`/`po_lines` ACL across all 5 roles: R4/R5 (create-deny), R15 (create-from-approved allow), R16 (create-from-unapproved deny), R17 (procurement PO header update allow / delete deny), R18 (terminal-PO immutability), R19/R23 (finance/operations create-deny), R20 (director/finance/operations PO update+destroy deny), R21 (procurement line add/update/over-budget/delete-while-draft), R24 (director/finance/operations line update+destroy deny).

**Fixture toolkit now available** (all three verified live this project — reuse as templates):
- `fixtures.records` with `trigger_workflow:` — create a record *into* an approval workflow (via `approvals:create`; a plain create does NOT trigger it).
- `fixtures.approvals` — drive a record through N approval decisions as the real assigned approvers (`pat_procurement` id 11 / `dana_director` id 12, both `existing: true`, shared `nbtest` password; assignees resolve from `departments.main_approver`, D40).
- `fixtures.records` with `after_approvals: true` — seed a record in a second pass *after* approvals run (needed when its create-guard requires an already-approved source; D61).
- `fixtures.actions` — fire a post-action / one-click workflow via `triggerWorkflows` and assert the result status (D62). Used to close a PO.

**Key live-verified facts** (don't re-derive; but re-verify if acting on them — see D57–D59 for why "looks configured" ≠ "is right"):
- PR→PO is **1:1**, enforced only by the "Create PO" guard (`366562380808192`), not the schema. Every PO fixture needs its own approved PR.
- procurement/purchase_orders ACL: view/create/update, **no destroy**. procurement/po_lines: +destroy. director/finance/operations: member view-only baseline on both.
- Guards key off PO status: "PO Immutability" + "PO Line Immutability" block update/destroy only on completed/closed; "PO Line Destroy" blocks line delete unless PO draft; "Receive" allows a `received_quantity` update only on issued/sent/confirmed.

## R22 (receiving) — DONE 2026-07-03 (tenth session), suite 33/33

R22 was the last PO/po_line rule. Completed in one session:

- **The earlier "no delivery_address field" blocker was a false alarm.** Alexander flagged the relation exists; re-verified live: `purchase_orders.delivery_address` is belongsTo → `delivery_addresses`, FK `deliveryAddressId`, matching the Issue guard and procurement's ACL whitelist. `notes.md` drift entry marked resolved.
- **Trigger mechanism verified live:** custom-action workflows fire via the dedicated `POST <collection>:trigger?filterByTk=<id>&triggerWorkflows=<key>` verb (probed against `issue_po` on the closed [TEST] PO — sync guard rejection intercepts as HTTP 400 with the workflow's response-message; execution row logged with status -1 but `executed` counter NOT incremented; non-admin procurement not ACL-blocked on the verb). **No runner change needed** — `action: purchase_orders:trigger` in `fixtures.actions` expresses it. Synced to the suite HANDOFF, `plan.example.yaml`, the `advance_actions()` docstring, and `nocobase-test/SKILL.md` Pitfalls (which had no `fixtures.actions` mention at all — pre-existing drift, fixed).
- **Drafted, reviewed, run green:** rule R22 + fixtures (`pr_approved_4` 4th approval chain, `sup_r22`/`addr_r22` admin reference records, `po_issued` + priced `po_issued_line`, `fixtures.actions` firing `issue_po`) + 3 cases (allow on issued line / Receive-guard deny on draft line / ACL deny as operations). All three po_lines-update guard node chains were read live before drafting. Alexander approved the rule text in-session 2026-07-03 ("go"); the `# TODO verify` marker is still on R22 pending his explicit clear, per the standing gate.

## Next step — the untouched collections

`projects` (has its own `Project Approval` workflow, id `372552255471616` — reuse the `fixtures.approvals` pattern; inspect its live node chain first), `suppliers`, `departments`. Same method: live ACL/guard audit per collection → draft rules → cases → run.

## Standing review gate — `# TODO verify`

`# TODO verify` on a rule means **Alexander hasn't reviewed the rule text word-by-word** — it tracks his review, NOT test-pass. He clears it, not you. Currently carrying it: R4, R5, R12, R13, R14, R16, R17, R18, R20, R21, R22, R24. (R1–R3, R15, R19, R23 are clear. R22's text was approved in-session 2026-07-03 but the marker awaits his explicit clear.)

## Debris (accepted, D60/D62)

Each full run drives 4 approval chains (`pr_approved`/`_2`/`_3`/`_4`) and leaves (verified live after the first 33/33 run, 2026-07-03): 4 approved PRs, a closed PO with its line, and one **orphaned po_line** — teardown deletes the issued PO header fine (PO immutability only bites completed/closed) and sweeps `sup_r22`/`addr_r22` cleanly, but the line-destroy guard (`global: true`, blocks admin) keeps the issued PO's line, which then points at the deleted PO id. All labeled `[TEST]` or traceable to a `[TEST]` fixture, uncleanable via API. Accepted to keep tests fully real; clean up at the DB level when noisy. Revisit a persistent-fixture runner mode only if this starts to bite.

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
- **Verify NocoBase claims against live state**, not docs/memory/prior sessions. An ACL grant that reads back fine isn't the same as being right (D57), let alone enforced (`nocobase-test`'s whole job).
- **Never touch VPS/production.** Local only; he pushes deploys himself. He builds all UI himself unless he delegates a screen. API keys: he pastes them into `.env.test` himself — never in chat or committed files.
- Pragmatic about local dev-only risk (test fixtures, shared passwords, reusing dev personas), but get an explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config — not a general go-ahead.
