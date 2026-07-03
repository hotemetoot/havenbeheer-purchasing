# HANDOFF — havenbeheer retrofit, Step 6 (rewritten 2026-07-03, tenth session)

**Read this first, then:** `~/nocobase/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (authoritative step list), this project's `CLAUDE.md`, and `decisions.md` D55–D62 (the PO/po_lines ACL+workflow work this step is built on). `notes.md` holds non-queryable traps and the go-live checklist. Skim `~/nocobase/nb-project-suite/HANDOFF.md` only if you touch `runner.py` or the `nocobase-test` skill.

This is a full rewrite. Per-session narrative before this (D55–D62, the runner fixes, the ACL audit) lives in `decisions.md` and git history — not repeated here.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, mature project (16+ MVPs shipped). Steps 0–5 done. **Step 6** (extend `tests/plan.yaml` with a full ACL/workflow audit, rule by rule, verified live) is in progress and is the bulk of remaining work.

## Current state

**Suite is 30/30 green, 17 rules.** Run it with:

```
/opt/homebrew/bin/python3 ~/nocobase/nb-project-suite/tools/nb-test/runner.py run --project-dir .
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

## Next step — R22 (receiving), and it's BLOCKED by live drift

R22 (procurement records receiving via `po_lines.received_quantity`) is the last PO/po_line rule. It needs a PO at `issued`/`sent`/`confirmed`, which means driving a PO through the **Issue PO** custom-action (`issue_po`).

**Blocker (found 2026-07-03, in `notes.md` "Drift / open issues"):** the Issue PO guard requires `deliveryAddressId != null`, and procurement's ACL whitelist lists `delivery_address`, but **`purchase_orders` has no `delivery_address` field** (only `supplier` + `purchase_request` belongsTo remain). So no PO can currently be issued. **Resolve this first — it's a live config decision for Alexander** (restore the dropped relation, or clean the stale guard/ACL reference). Don't work around it in the test.

Once unblocked, building R22:
1. Verify live how the **one-click custom-action** trigger fires. `fixtures.actions` was proven against a **post-action** (`type: action`, Close PO) via `?triggerWorkflows=<key>` on an update. Issue PO is `type: custom-action` (type 1, one-click "Trigger workflow" button) — confirm whether the same `triggerWorkflows`-on-action call fires it, or whether it needs a different endpoint (e.g. `workflows:trigger`). If different, extend `advance_actions()` accordingly and log it in the suite HANDOFF.
2. Add fixtures: a supplier record (→ `suppliers`) and a delivery_address value, set on a new `po_issued` PO (from its own `pr_approved_N`); a priced line ≤ the PR total; then a `fixtures.actions` step firing `issue_po`, asserting `status: issued`. Watch the full Issue guard: status==draft, supplierId, deliveryAddressId, currency, total>0, ≥1 priced line, sum(lines) ≤ PR quoted_total.
3. Promote R22: procurement `received_quantity` update on the issued PO's line → allow; a non-owner role → deny.

## After R22 — the untouched collections

`projects` (has its own `Project Approval` workflow, id `372552255471616` — reuse the `fixtures.approvals` pattern; inspect its live node chain first), `suppliers`, `departments`. Same method: live ACL/guard audit per collection → draft rules → cases → run.

## Standing review gate — `# TODO verify`

`# TODO verify` on a rule means **Alexander hasn't reviewed the rule text word-by-word** — it tracks his review, NOT test-pass. He clears it, not you. Currently carrying it: R4, R5, R12, R13, R14, R16, R17, R18, R20, R21, R24. (R1–R3, R15, R19, R23 are clear.)

## Debris (accepted, D60/D62)

Each full run drives 3 approval chains (`pr_approved`/`_2`/`_3`) and leaves 3 approved PRs plus a closed PO — all locked (Guard A + PO immutability are `global: true`, block admin too), uncleanable via API, labeled `[TEST]`. Accepted to keep tests fully real; clean up at the DB level when noisy. Adding `po_issued` makes it a 4th chain. Revisit a persistent-fixture runner mode only if this starts to bite.

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
