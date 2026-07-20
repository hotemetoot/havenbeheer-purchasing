# HANDOFF — havenbeheer, current state (updated 2026-07-20, app emptied for go-live)

> **The local app has no business data.** Every purchase request, order, PO line,
> project, comment, attachment and notification was deleted on 2026-07-20 (D95) so
> the go-live backup ships clean. Suppliers, departments, units of measure,
> delivery addresses and all 13 users (personas + `[TEST]` accounts) survive.
> Record counters were reset: the next records are **PR-26-0001** and **PRJ-26-0001**.
> If you open the app expecting fixtures to poke at, there are none — seed your own,
> or let the suite seed and tear down its own as it always has.
> Workflow execution history was purged too — the last 179 rows were stuck in
> "started" and only SQL could remove them (D95 explains why the API cannot).
> **It did not stay empty:** the wipe's own cascade of deletes re-fired the
> workflows, writing 268 fresh executions in a 45-second burst (231 succeeded,
> 25 failed, 9 stuck at status 0). Confirmed by the 2026-07-20 maintenance pass.
> Harmless under D79's settings, but the go-live backup carries those rows, so
> production did not start execution-clean either.

**Read this first, then:** this project's `CLAUDE.md` (session workflow), `roadmap.md` (chunk table), `decisions.md` D80–D89 (the recent stretch), `notes.md` (traps + go-live pointers), and `workflows-explained.md` (plain-English reference for the approval ladders and guards). Skim `~/.claude/skills/nb-project-suite/HANDOFF.md` if you touch `runner.py`.

## Where things stand (2026-07-20)

- **The app is live on production.** Alexander restored the go-live backup onto
  the server (`docs/go-live.md` §3.1) on 2026-07-20. **§3.2, the post-restore
  cleanup, is still entirely open, and two of its items are urgent:** `member`'s
  `ui.*` snippet is still un-negated there, so under D54's union rule *every*
  user who signs in at the production URL can enter UI-edit mode; and the six
  dev personas came across carrying the shared `nbtest` password on a public
  URL. Both must be settled before real accounts are handed out. Server work is
  Alexander's — never touch the VPS from here.
- **A maintenance pass ran 2026-07-20** (this file's execution-history note
  above is one of its findings). See the bottom of `notes.md` for the stale-ID
  list it deleted and why.

- **The retrofit pilot is done** (steps 0–8). The one open remnant of Step 7: `docs/user-guide.md`'s **Appendix — Suppliers** stub. Everything else in the guide is written from the live app; `📷` markers await Alexander's screenshots.
- **Suite: 45 rules / 121 cases, green 121/121 on 2026-07-20** (latest report in `tests/reports/`). No `# TODO verify` markers.
- **First `nb-explore` exploratory session ran 2026-07-19** — invariants now live in `tests/invariants.md`; its three receiving-lifecycle finds became chunk 020.
- **Chunks 017 / 019 / 020 all closed 2026-07-19 (D92).** Alexander delegated the outstanding §1.2b checks; a 9-scenario API walkthrough drove every PR/project rejection and approval terminal path as the real approver users and verified the notification recipients against the D88 matrix (9/9 exact). 019's boxes closed against suite rules R44/R45; 020's receiving corrections are R46's up-and-down cases. Suite re-run after teardown: 116/116. The walkthrough pattern (temp submitter in a dept whose head is not Pat, read `notificationInAppMessages` back, delete everything) is in D92.
- **Chunk 021 closed 2026-07-19 (D94) — no build chunks remain before go-live.** All 14 enabled interception guards were read for the D89 payload-shape fault. One hit: "Guard: Create PO (PR must be approved)" (`vgv8hcrtjvx`), the oldest guard in the set, confirmed live as an HTTP 500 on `purchase_request: {id: N}` and a wrong-reason refusal on `purchaseRequestId: N`. Fixed with the same resolver head as `polncreateg1`; new version `376415305990144`, covered by R52 (5 cases). **Everything else is clean and does not need re-auditing** — see D94 for the per-guard list, including `c9c14tyn876` and `eiscjvwiqr6`, which D89 had left as open questions.
- **Chunk 016 closed 2026-07-20.** Its last open item was the B8 screen check — that Lines Total updates per imported row after the D83 fix. Alexander confirmed it in the UI. Both 014 and 016 moved to `completed/`.
- **Pre-go-live cleanup ran 2026-07-20 (D95).** See the note at the top of this file. Suite re-verified green **121/121** before the wipe.
- **In-flight chunks** (statuses in `roadmap.md`): **018** (stranded project commitment, D85) is scoped but not built and is not a go-live blocker. It is the only chunk left.
- **Policy decisions this stretch:** D85 (stranded project commitment is fixed by a director budget raise, never auto-release — MVP 018 scoped, not built), D86 (production backups use the built-in Backup manager, not a cron stack — configured at go-live Part 4).

> **Concurrency note:** before any write-heavy step, make sure no other session is open on this repo (a rule-number collision R46 happened 2026-07-19 between two concurrent sessions; D68 was once committed from a second terminal mid-session).

## Open items

- **R42's bulk-import clause will never have an automated case** — import is a UI action the runner can't drive, so it is a permanent manual check. What to check and why is in `notes.md` "Drift / open issues"; whether it currently passes is go-live case B8 in `docs/go-live.md`, the single status home.
- **D80 open issue (suite side):** each full suite run leaves ~9 status-0 approval executions behind (fixture PRs/projects deleted, their pending approval executions not). Harmless under D79's settings, but the backlog regrows; the fix belongs in `runner.py`'s teardown. **Now known to be worse than "harmless": these rows cannot be deleted through the API at all** — `executions destroy` reports success and removes nothing, `executions cancel` 500s once the approval record is gone, so only SQL clears them (D95). 179 had piled up by go-live. Raising the priority of the `runner.py` teardown fix accordingly.
- From chunk 020's out-of-scope list: a dangling `member` scope on `purchase_orders`/`po_lines` (`scopeId: 363334209503233` resolves to no row), and `director`'s strategy-mode view grant has no field whitelist (any new PO field becomes director-visible automatically).
- **Guard meter (re-counted 2026-07-20, unchanged):** 14 enabled request-interception guards — past the point where the suite's guidance says to revisit consolidation (shared admin-exempt heads via subflows, value bounds onto field validation — 020 started the latter). Parked for Alexander.
- **A cross-project trap was lost** in the 2026-07-19 merge of the trap memories into `gotchas.md`: the CLI storing the *string* `"false"` as a boolean field's default, which is truthy. Its original wording is unrecoverable and reproducing it needs a throwaway field created live, so it was not restored to the catalogue. The audit step it backed now stands on its own in `role-acl-guidelines.md` §5.7. Live check 2026-07-20: all three `purchase_requests` flag fields store `null` — clean.
- Live debris and revision depth clean as of 2026-07-20: no business records at all (post-D95), no `[TEST]` rows, 40 disabled revisions with no lineage deeper than D81's keep-2, no stray test registry, `tests/reports/` pruned to the last green run plus the exploratory pilot.

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

Single home: auto-memory — `feedback_plain_language_concrete_examples` is the anchor (plain language, concrete stories, front-end labels not API names). **Verification split (D93, standing):** Claude runs every API-reachable walkthrough/check itself as real signed-in users; Alexander is asked only for screen-only items (print layout, button visibility, form appearance), named one by one. Review protocol above; review gates by logical group; he builds all UI; never touch a VPS. Plus one project-level point: pragmatic about local dev-only risk, but explicit, specifically-named confirmation before mutating real accounts, data, or live ACL/config.
