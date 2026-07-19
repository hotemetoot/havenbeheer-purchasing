# HANDOFF — havenbeheer, current state (updated 2026-07-19, maintenance pass)

**Read this first, then:** this project's `CLAUDE.md` (session workflow), `roadmap.md` (chunk table), `decisions.md` D80–D89 (the recent stretch), `notes.md` (traps + go-live pointers), and `workflows-explained.md` (plain-English reference for the approval ladders and guards). Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` if you touch `runner.py`.

## Where things stand (2026-07-19)

- **The retrofit pilot is done** (steps 0–8). The one open remnant of Step 7: `docs/user-guide.md`'s **Appendix — Suppliers** stub. Everything else in the guide is written from the live app; `📷` markers await Alexander's screenshots.
- **Suite: 43 rules / 109 cases, green 109/109 on 2026-07-19** (report `tests/reports/20260719-154652.md`). No `# TODO verify` markers.
- **First `nb-explore` exploratory session ran 2026-07-19** — invariants now live in `tests/invariants.md`; its three receiving-lifecycle finds became chunk 020.
- **In-flight chunks** (statuses in `roadmap.md`):
  - **017** — approval notifications (D88): built + suite-green, **pending Alexander's UI walkthrough** (reject a PR at each of the five stages and a project, driving real approver users — go-live §1.2b).
  - **019** — PO execution lock (D87): built + suite-green, **pending UI check**.
  - **020** — receiving integrity + print gating: **in progress.** Receiving roll-up and negative-quantity refusal are built and green; the draft watermark and the widened Phase-2 value-bound sweep are not yet confirmed done.
  - **021** — guard payload-shape audit (D89 leftover): scoped, not started. The two hit `po_lines` guards are fixed (R50); PR and project guards are unaudited, and they read associations — the shape that breaks. D89 also names `c9c14tyn876` and `eiscjvwiqr6` as unchecked for the nested shape.
- **Policy decisions this stretch:** D85 (stranded project commitment is fixed by a director budget raise, never auto-release — MVP 018 scoped, not built), D86 (production backups use the built-in Backup manager, not a cron stack — configured at go-live Part 4).

> **Concurrency note:** before any write-heavy step, make sure no other session is open on this repo (a rule-number collision R46 happened 2026-07-19 between two concurrent sessions; D68 was once committed from a second terminal mid-session).

## Open items

- The three UI checks above (017 / 019 / 020) — Alexander, go-live §1.2b.
- **R42's bulk-import clause has no automated case** — manual check owed, belongs with D83's parked 016 B-cases (see `notes.md` "Drift / open issues").
- **D80 open issue (suite side):** each full suite run leaves ~9 status-0 approval executions behind (fixture PRs/projects deleted, their pending approval executions not). Harmless under D79's settings, but the backlog regrows; the fix belongs in `runner.py`'s teardown.
- **42 disabled predecessor workflow revisions** exist live (2026-07-19 count). D81's standing rule: per lineage keep current + 2 newest predecessors, delete older — apply on the next maintenance pass with Alexander's approval.
- From chunk 020's out-of-scope list: a dangling `member` scope on `purchase_orders`/`po_lines` (`scopeId: 363334209503233` resolves to no row), and `director`'s strategy-mode view grant has no field whitelist (any new PO field becomes director-visible automatically).
- **Guard meter (2026-07-19 maintenance pass):** 14 enabled request-interception guards — past the point where the suite's guidance says to revisit consolidation (shared admin-exempt heads via subflows, value bounds onto field validation — 020 started the latter). Parked for Alexander.

## How to run the suite

```
/opt/homebrew/bin/python3 ~/.claude/skills/nb-project-suite/tools/nb-test/runner.py run --project-dir .
```

**Use the explicit `/opt/homebrew/bin/python3`** (3.14, has `requests`+`pyyaml`); bare `python3` non-deterministically resolves to system 3.9.6 without deps. `runner.py acl` = config checks only (seconds); `--tag canary` = enforcement canaries; `--tag prflow` = PR-branch cases; `--tag projects` = projects cases.

## Standing review gate — `# TODO verify`

**Nothing marked.** Review protocol: short verdicts; coverage is one case per mechanism, not per role; never flag missing role×action matrix combinations. Codified in `nb-test/SKILL.md`.

## Fixture design notes (carry over)

- `operations_proj` is the ONLY dept-bearing test user; its dept is Procurement (363554444476416, main approver Pat). **Do not add departments to the other seeded PR users** — it would change the already-green PR approval chains. Dept-stage fixtures reuse operations_proj for exactly this reason.
- `oliver_owner` (existing persona, id 10, nbtest) is the head-skip witness; `pr_regular_small`/`pr_regular_300` are created **as admin** (is_regular not in the operations create whitelist).
- **The four `purchase_orders` fixtures create as admin, not procurement** (since D87: supplier/currency/FX/total/issued_at left procurement's create whitelist; a procurement-created fixture PO can't pass the Issue guard).
- Approvals-entry order is load-bearing in the after_records pass: within (1000) → boundary (4000) → over (9500) against the 5000 budget; committed_usd asserts 5000.
- Case order in the file is load-bearing: R28's link-allow and the R29/R30 state cases sit BEFORE the R27 block, whose allow case completes `proj_approved`.
- Director return steps need `returnToNodeKey` (see R37's fixture comment and `notes.md`'s fixtures section).
- Teardown: clean — every lock guard exempts admin (D71 for PRs, D82 for the PO side), so terminal fixtures delete too.

## Before go-live

Runbook: `docs/go-live.md`. Short list (detail in `notes.md`): re-negate `member`'s `ui.*` snippet; assign `finance` to `fiona.finance` (id 14); move PO payment set-rights to `finance` and receiving to a warehouse role if created (D59).

## How Alexander works

Single home: auto-memory — `feedback_plain_language_concrete_examples` is the anchor (plain language, concrete stories, front-end labels not API names). Review protocol above; review gates by logical group; he builds all UI; never touch a VPS. Plus one project-level point: pragmatic about local dev-only risk, but explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config.
