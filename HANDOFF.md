# HANDOFF — havenbeheer retrofit, Step 6 continues (rewritten 2026-07-02, seventh session)

**Read this first, then `~/nocobase/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (the authoritative step list) and this project's `CLAUDE.md`.** Also skim `~/nocobase/nb-project-suite/HANDOFF.md` if you're touching `runner.py` itself or the `nocobase-test` skill — it's the shared tool's own history, not repeated here.

This file replaces the previous revision. Older session detail (D55–D59, the approval-chain mechanism, the scope-table bug, the director-whitelist fix) is preserved in `decisions.md` and git history — not repeated here except where it's still actionable.

## What this is

`Havenbeheer Purchasing` is `nb-project-suite`'s deliverable-6 pilot: proving the test suite works end-to-end on a real, already-mature project (16+ MVPs shipped). Steps 0–5 are done. Step 6 (extend `tests/plan.yaml` with a full ACL/workflow audit) is in progress and is the bulk of remaining work — expected to span several more sessions.

## Where Step 6 stands right now

**Suite is 14/14 green.** Run `python3 ~/nocobase/nb-project-suite/tools/nb-test/runner.py run --project-dir .` from this project root to confirm. On a fresh shell you may need `python3 -m pip install requests pyyaml --break-system-packages` first.

**The purchase_orders/po_lines ACL audit across all 5 roles is DONE (D59).** This finishes the audit D56 began. Result: the live grant matrix is correct as-is. Two grants were reviewed and **deliberately kept as an interim — they are NOT bugs, do not re-flag them on a future audit:**
- `procurement` holds `payment_status`/`payment_date` set-rights on PO create+update. D33a says payment is Finance's domain, but there are no finance users or payment stage yet, so procurement holds it for now. Move to `finance` at go-live.
- `procurement` records receiving (`po_lines.received_quantity` update). No warehouse role exists yet; a future warehouse role may take it over.

Both are logged as go-live TODOs in `notes.md`. Alexander confirmed both explicitly this session (leave as-is). No live ACL write was made.

**R15/R17–R24 rule text is now DRAFTED** in `tests/plan.yaml` from that audit, business rules approved by Alexander. Only R19 and R23 are **active** (finance/operations cannot create a PO or po_line — verified live this session). The other seven (R15, R17, R18, R20, R21, R22, R24) are held as a **comment block** in `plan.yaml`, because the runner rejects any active rule that has no case (`HYGIENE: rule X has no cases` → exit 2), and all seven need a seeded PO record they don't have yet.

**Runner bug found and FIXED this session:** `run --seed` used to re-send `password` when updating an already-existing `test_*` user, and NocoBase invalidates that user's tokens on any password write (`HTTP 401 INVALID_TOKEN "User password changed"`) — which broke auth for the rest of that same run (R12 flaked; fixture creation crashed). Fixed in `~/nocobase/nb-project-suite/tools/nb-test/runner.py` `seed_users()`: `password` is now sent only on create, never on update. Verified `run --seed` twice = 14/14 both times. `--seed` is safe to run repeatedly again; the old "seed once then plain run" workaround is no longer needed. (Detail in the suite's `HANDOFF.md`.)

**Known leftover debris (unchanged):** a scratch `[TEST-SCRATCH]` PR from an earlier session sits at `status: approved`, locked by Guard A, uncleanable via API. Harmless, ignore or clean manually.

## Next step, in order

1. **Build a PO-record fixture — this is the gate for the seven drafted rules.** They all need a real purchase order (and its lines) seeded, which the "Guard: Create PO (PR must be approved)" workflow blocks unless the source PR is `approved`. So:
   - Extend `fixtures.approvals` to drive a PR through the **full** approval chain to `status: approved` (the current fixture only drives one step to `pending_director_approval` for R12). Derive the exact chain and the real approver persona per stage from the live PR Approval workflow + D40 (`departments.main_approver`: Procurement→11, Director→12, Finance→14, Operations→10; each is a real `existing: true` persona like `pat_procurement`, since `approvalRecords:submit` checks the assigned `userId`).
   - Add a `fixtures.records` entry that creates a `purchase_orders` row from that approved PR **as `procurement_a`** (procurement is the PO creator). This is R15's allow case.
   - With a draft PO + po_lines in hand, promote R17/R20/R21/R22 from comments to active rules and write their cases. For R18/R24 (terminal immutability), drive a PO to `completed`/`closed` and assert update/destroy are blocked.
   - Each promoted rule gets `# TODO verify`; Alexander reviews the rule text word by word before it's trusted. Don't transcribe live ACL as correct-by-definition — the D58/D59 findings show why. Split across sessions as needed.

2. **Then the untouched collections/roles:** `projects` (has its own `Project Approval` workflow — expect the same approval-chain fixture pattern), `suppliers`, `departments`.

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
