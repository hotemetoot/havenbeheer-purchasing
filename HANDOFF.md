# HANDOFF — havenbeheer retrofit, Step 6 continues (updated 2026-07-03, ninth session)

**Ninth session (D61): `po_draft` fixture seeded AND R17/R20/R21/R24 promoted — suite 28/28.** PR→PO 1:1 is confirmed enforced live (the create-guard blocks a second PO on an already-consumed PR), so `pr_approved_2` was added as the fixture PO's own source; the runner gained an `after_approvals: true` flag on `fixtures.records` so a PO can be seeded *after* its source PR is approved (two-pass `op_run`; see `nb-project-suite` HANDOFF). Then R17 (procurement update-header allow / PO destroy-deny), R20 (director/finance/operations PO update+destroy deny), R21 (procurement line add/update allow + over-budget create deny), R24 (director/finance/operations po_line update+destroy deny) were promoted with cases against `po_draft`. All ACL grants + guard scopes verified live. **Next step: the issued/terminal-PO fixture** — see the revised "Next step" below. The rest of this file is the eighth-session (D60) state, still accurate.

---


**Read this first, then `~/nocobase/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (the authoritative step list) and this project's `CLAUDE.md`.** Also skim `~/nocobase/nb-project-suite/HANDOFF.md` if you're touching `runner.py` itself or the `nocobase-test` skill — it's the shared tool's own history, not repeated here.

This file replaces the previous revision. Older session detail (D55–D59, the approval-chain mechanism, the scope-table bug, the director-whitelist fix) is preserved in `decisions.md` and git history — not repeated here except where it's still actionable.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, already-mature project (16+ MVPs shipped). Steps 0–5 are done. Step 6 (extend `tests/plan.yaml` with a full ACL/workflow audit) is in progress and is the bulk of remaining work — expected to span several more sessions.

## Where Step 6 stands right now

**Suite is 15/15 green.** Run `python3 ~/nocobase/nb-project-suite/tools/nb-test/runner.py run --project-dir .` from this project root to confirm. On a fresh shell you may need `python3 -m pip install requests pyyaml --break-system-packages` first. (`--seed` is only needed when adding a new `test_*` fixture user; `existing: true` personas are sign-in-only.)

**New this session (D60): R15 is live and the full approval-chain fixture works.** R15 (procurement can create a PO from an *approved* PR) is now an active, runtime-verified rule. It's driven by a new `fixtures.approvals` entry that runs a `pr_approved` record through the **full** two-step chain (Procurement → Director → `approved`), derived from the live PR Approval workflow (id `372610390622208`), not from prior notes. Approvers resolve from `departments.main_approver` (D40): Procurement → `pat_procurement` (id 11), Director → `dana_director` (id 12, added this session, `dana@havenbeheer.test`, shared `nbtest` password). This is the reusable template for any rule needing an approved PR or a PO.

**Runner bug found + fixed this session (`nb-project-suite`-side, see D60 + that project's HANDOFF):** `Client.act` json-encoded the `fields` list, so `fields=["id"]` went as `'["id"]'` and NocoBase silently returned empty `{}` records → teardown sweep crashed on `rec["id"]`. Fixed: json-dump dicts only, pass lists as repeated params. Surfaced only because this is the first run leaving an undeleteable approved PR for the sweep to list.

**The purchase_orders/po_lines ACL audit across all 5 roles is DONE (D59).** This finishes the audit D56 began. Result: the live grant matrix is correct as-is. Two grants were reviewed and **deliberately kept as an interim — they are NOT bugs, do not re-flag them on a future audit:**
- `procurement` holds `payment_status`/`payment_date` set-rights on PO create+update. D33a says payment is Finance's domain, but there are no finance users or payment stage yet, so procurement holds it for now. Move to `finance` at go-live.
- `procurement` records receiving (`po_lines.received_quantity` update). No warehouse role exists yet; a future warehouse role may take it over.

Both are logged as go-live TODOs in `notes.md`. Alexander confirmed both explicitly this session (leave as-is). No live ACL write was made.

**R15/R17–R24 rule text is DRAFTED** in `tests/plan.yaml` from that audit, business rules approved by Alexander. **Active + verified live: R15, R19, R23** (R15 = procurement can create a PO from an approved PR; R19/R23 = finance/operations cannot create a PO/po_line). The remaining **six** (R17, R18, R20, R21, R22, R24) are still held as a **comment block** in `plan.yaml`, because the runner rejects any active rule with no case (`HYGIENE: rule X has no cases` → exit 2), and all six need a seeded PO/po_line record they don't have yet. `# TODO verify` was cleared on R15 (reviewed word-by-word + passed live); R4/R5/R12/R13/R14/R16 still carry it (they pass, but Alexander hasn't done the word-by-word review — the marker tracks review, not passing; his to clear).

**Runner bug found and FIXED this session:** `run --seed` used to re-send `password` when updating an already-existing `test_*` user, and NocoBase invalidates that user's tokens on any password write (`HTTP 401 INVALID_TOKEN "User password changed"`) — which broke auth for the rest of that same run (R12 flaked; fixture creation crashed). Fixed in `~/nocobase/nb-project-suite/tools/nb-test/runner.py` `seed_users()`: `password` is now sent only on create, never on update. Verified `run --seed` twice = 14/14 both times. `--seed` is safe to run repeatedly again; the old "seed once then plain run" workaround is no longer needed. (Detail in the suite's `HANDOFF.md`.)

**Known leftover debris (growing, accepted):** the old `[TEST-SCRATCH]` PR plus one `[TEST] R15 approved-PR fixture` PR + its PO **per full run** all sit at terminal/approved status, locked by Guard A / PO-immutability (both `global: true`, block admin too), uncleanable via API. Alexander's call this session (D60): accept the accumulation to keep tests fully real, rather than add a runner "persistent existing-record" mode. Clean up manually at the DB level when it gets noisy. All labeled `[TEST]`.

## Next step, in order

The `po_draft` fixture is DONE and R17/R20/R21/R24 are promoted (28/28). What remains needs a PO in a **non-draft** status, because the relevant guards only bite there.

1. **Build an issued/terminal-PO fixture, then promote R18, R22, and R21's delete-deny half.** The three guards involved key off PO status: "Guard: PO Immutability" and "PO Line Immutability" block update/destroy only when the PO is `completed`/`closed`; "Guard: Receive" allows a `received_quantity` update only when the PO is `issued`/`sent`/`confirmed`; "PO Line Destroy — block once PO issued" blocks line delete unless the PO is `draft`. So `po_draft` can't exercise any of them.
   - Inspect live how a PO advances out of draft: the custom actions **Issue PO** (`372351365087232`), **Complete PO** (`368971625791488`), **Close PO** (`369914944225280`), plus any "PO Close Guard" / status-path guards. Drive a fixture PO to `issued` (for R22 receiving + R21 delete-deny) and to `completed`/`closed` (for R18) — likely a new `fixtures.records` PO plus an action/status step, mirroring how the PR chain was driven. This may need a runner addition (a way to invoke a custom-action / status transition on a fixture record) — check before assuming the current fixture mechanism covers it.
   - R22: procurement `received_quantity` update on an issued PO's line → allow; a non-owner role → deny. R18: no role (incl. procurement) can update/destroy a completed/closed PO → deny. R21 delete-deny: procurement line destroy on a non-draft PO → deny.
   - Each new rule gets `# TODO verify` for Alexander's word-by-word review. Don't transcribe ACL as correct-by-definition — verify each guard live first.
   - For **R18/R24** (terminal immutability), drive a PO to `completed`/`closed` (there are PO close/complete guards + likely an approval or status path — inspect live like the PR chain) and assert update/destroy are blocked. This may need its own fixture record + possibly an approval/close step.
   - Each promoted rule gets `# TODO verify`; Alexander reviews the rule text word by word before it's cleared (the marker tracks *his review*, not test-pass). Don't transcribe live ACL as correct-by-definition — D57/D58/D59 show why. Split across sessions.

2. **Then the untouched collections/roles:** `projects` (has its own `Project Approval` workflow — reuse the `fixtures.approvals` pattern; inspect its live node chain first), `suppliers`, `departments`.

## Before go-live (see `notes.md` for detail)

- `member`'s `ui.*` snippet must be re-negated (currently un-negated for dev convenience; grants UI-edit to every user under `only-use-union`).
- `fiona.finance` needs the `finance` role actually assigned (currently only holds `member`).
- D57's dead-scope-table check only covered `purchase_requests`/`purchase_orders`/`po_lines` — re-run across the whole schema.
- **New (D59):** move PO payment set-rights from `procurement` to `finance` when finance users exist; move `received_quantity` receiving to a warehouse role if one is created.

## Step 7 — `docs/user-guide.md`

Still empty, still explicitly deferred, not part of this retrofit.

## Step 8 — hand back

Not yet — Step 6 isn't done. When it is: summarize what changed vs. what deliberately didn't, and do a final pilot-outcome report to `nb-project-suite`'s own `HANDOFF.md`.

## How Alexander works (carried over, still applies)

- Step by step, review-gated. Present ONE step, get feedback, proceed.
- **Review rules, not payloads (new this session, now permanent).** When proposing any live NocoBase config/ACL write, present the **business rule** — who can do what, under which condition, and why — for approval or correction, then execute. Do NOT lead with JSON payloads or field-by-field CLI args; show the mechanism only if asked. Baked into `CLAUDE.md`'s "Live environment changes" section, the suite's bootstrap template, and auto-memory `feedback_review_rules_not_payloads.md`.
- Verify NocoBase-specific claims against live state, not docs/memory/prior sessions. D57 (scope that read back fine but was unenforced) and D58/D59 (whitelist fields with no stated reason) show why — an ACL grant looking configured isn't the same as it being *right*, on top of `nocobase-test`'s job of proving it's *enforced*.
- Never touch VPS/production. Local only.
- Pragmatic about local dev-only risk (test fixtures, shared passwords, reusing real dev personas) — but always get an explicit, specifically-named confirmation before mutating real accounts, data, or live ACL config, not just a general go-ahead.
