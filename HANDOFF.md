# HANDOFF — havenbeheer retrofit, Step 6 continues (updated 2026-07-02, second session)

**Read this first, then `~/nocobase/nb-project-suite/plans/havenbeheer-retrofit-plan.md` (the authoritative step list) and this project's `CLAUDE.md`.**

**Also read `~/nocobase/nb-project-suite/HANDOFF.md`** before touching `tests/plan.yaml` again — that file now carries pilot feedback (a real bug fixed in `runner.py`, two skill-doc corrections, one new feature needed) that directly affects what you can and can't draft here.

## What this is

This project (`Havenbeheer Purchasing`) is `nb-project-suite`'s deliverable-6 pilot, proving the suite works end-to-end on a real, already-mature project (16+ MVPs shipped). Steps 0–5 are done (see git history / prior HANDOFF revision). Step 6 (extend `tests/plan.yaml`) is in progress and is the bulk of the remaining work — expected to span multiple sessions.

## What's done this session (2026-07-02, second session) — 3 commits

1. Dropped `# TODO verify` on R1–R3 (settled, 4/4 passed previously). First commit of `tests/plan.yaml` itself.
2. Live ACL re-audit of `purchase_requests` across all 5 non-admin roles found two real drift issues in `director`'s permission row (unscoped `update`, an undocumented stray `create` action). Fixed live, recorded as **D55**.
3. Live audit of `purchase_orders`/`po_lines` found procurement could permanently delete a PO or its lines at almost any status. Confirmed unwanted (auditability), fixed: removed procurement's `destroy` on `purchase_orders` entirely, added a new guard workflow blocking `po_lines` destroy once the parent PO leaves `draft`. Recorded as **D56**.
4. Drafted R13/R14/R16 (director denied outside its stage, director denied create, procurement denied creating a PO from a non-approved PR), wrote cases, ran the suite — **first failure caught a much bigger issue**: this NocoBase version silently doesn't enforce custom ACL scopes stored in the `rolesResourcesScopes` table (only `dataSourcesRolesResourcesScopes` is actually read). D55's own scope fix was in the dead table, and so — independently, since 2026-06-11 — was `finance`'s existing render-enabler grant. Both repointed to the correct table, both runtime-verified (not just readback-verified) this time. Recorded as **D57**, corrected `role-acl-guidelines.md` §2 and §6.
5. Suite is green: **7/7 passed** (`tests/reports/` — latest report from this session).
6. Set the 4 real dev personas' (`oliver.owner`, `pat.procurement`, `dana.director`, `fiona.finance`) passwords to a shared `nbtest` value, with Alexander's explicit OK — needed for the next batch of rules (see below). **You still need to set `TEST_USER_PASSWORD=nbtest` in `tests/.env.test` yourself** — Claude does not write that file.

Commits: `888899c` (R1-R3 TODO drop + first plan.yaml commit — got mixed with the D55 commit below by a staging mistake, noted at the time), `eaee92f` (D56 PO deletion lockdown), `af41c0b` (D57 scope-table fix + R13/R14/R16 + notes updates).

## What's left

### Step 6 continued — most of the ACL/workflow surface is still undrafted

Only `purchase_requests` (all 5 roles) and `purchase_orders`/`po_lines` (procurement's create/update/destroy shape) have been re-audited this pilot. Untouched: `projects` (has its own `Project Approval` workflow — same approval-chain fixture problem will apply), `suppliers`, `departments`, and the remaining roles' full permission surface on every collection.

### Blocked: R12, R15, R17–R24 (drafted as rule text, no cases yet)

All need a `purchase_request` fixture actually at `status: approved` (or later), which can't be set directly on create — only reachable by actually driving the PR Approval workflow. **This is fixable, not a hard wall** — see `nb-project-suite`'s `HANDOFF.md` for the exact mechanism (`approvalRecords:submit` is a real, callable REST action; `runner.py` just doesn't have a declarative case type for it yet). Once that case type exists in `runner.py`, come back here: the 4 real dev personas (`dana.director`=12, `pat.procurement`=11, `fiona.finance`=14, `oliver.owner`=10) are already set up as approvers and already have the `nbtest` password — see `notes.md`'s "Approval-chain test fixtures" section for the exact plan.

### Before go-live (see `notes.md`)

- `member`'s `ui.*` snippet must be re-negated.
- `fiona.finance` needs the `finance` role actually assigned (currently only holds `member` — found this session, no current impact since no finance approval stage exists yet).
- D57's dead-scope-table check only covered 3 collections — re-run it against the whole schema before go-live.

### Step 7 — `docs/user-guide.md`

Still starts empty. Still explicitly deferred, not part of this retrofit.

### Step 8 — hand back

Not yet — Step 6 isn't done. When it is: summarize what changed vs. what deliberately didn't, report the pilot outcome to `nb-project-suite`'s own `HANDOFF.md` (already partly done this session — the runner.py bug and skill-doc corrections are recorded there now, ahead of the final Step 8 wrap-up).

## How Alexander works (carried over, still applies)

- Step by step, review-gated. Present ONE step, get feedback, proceed.
- Verify NocoBase-specific claims against live state, not docs/memory/prior sessions — this session's biggest finding (D57) came from exactly this discipline: a test case catching that "verified via readback" didn't mean "actually enforced."
- Never touch VPS/production. Local only.
- Pragmatic about local dev-only risk (test fixtures, shared passwords, reusing real dev personas) — but still stops and asks before touching anything that isn't obviously reversible or that predates the current session (e.g. deleting a pre-existing config row got its own explicit confirmation, separate from general session approval).
