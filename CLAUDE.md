# Havenbeheer Purchasing

NocoBase-based PR/PO approval workflow. This file is auto-loaded every session.

## Environment
- NocoBase 2.1.0-beta.47 at http://localhost:13000
- Canonical working tree (compose + storage + Postgres data): `~/nocobase-dev/havenbeheer`, containers `havenbeheer-app-1`/`havenbeheer-postgres-1`. Never start this app from `~/nocobase` or the iCloud `TTGA/nocobase` tree — see notes.md "Environment" and D76 (a twin tree ran for 3 weeks and the DB silently reverted).
- **HARD RULE (D76): one tree, verified before start.** Never copy or relocate the working tree, never create a second runnable copy anywhere (iCloud or otherwise). Before any `podman compose up` / `podman start` / container recreate, verify the postgres bind mount (`podman inspect havenbeheer-postgres-1 --format '{{range .Mounts}}{{.Source}}{{end}}'`) resolves to `~/nocobase-dev/havenbeheer/storage/db/postgres`; wrong path → stop and ask Alexander. Copies for recovery go to `~/nocobase-recovery/` and are never started as the app; the only sanctioned backup form is `nb backup create` (.nbdata).
- CLI env name: `havenbeheer`
- Auth: OAuth (auto-refreshes)
- Multi-project shell isolation: `nb` scopes "current env" per shell session via `NB_SESSION_ID`. Run `nb session setup --shell <shell>` once per shell if not already done. If a chunk's `nb api` calls seem to hit the wrong environment, sanity-check with `nb session id` — this matters because agrofix/qhse are worked on concurrently in other shells.

## Where things live
- Design: [design/](design/) — thin pointers to the heavier validation docs in `Planning and Design/`, not inlined content.
- Roadmap of all MVPs: [roadmap.md](roadmap.md)
- Current chunk: [chunks/NNN-*.md](chunks/); finished ones move to [completed/NNN-*.md](completed/)
- Decisions made along the way: [decisions.md](decisions.md) — append-only, ≤15-line entries (Decision/Why/How to apply/Affects/Status), superseding via `Status: superseded by D#` rather than deletion. [decisions-archive.md](decisions-archive.md) holds older entries from before this convention — kept as a second file rather than merged, since retroactively reformatting ~50+ entries would lose real detail (workflow IDs, node counts) for no benefit. Only *new* entries follow the ≤15-line format; older entries in both files may run much longer.
- Non-queryable context (traps, reasons behind manual changes, env facts, the go-live checklist): [notes.md](notes.md)
- Client-facing docs, grows per chunk: [docs/user-guide.md](docs/user-guide.md) — Step 7 backfill IN PROGRESS (see HANDOFF). Spine done: §1–§3 reference + Stage 1 (create/submit) + Stage 2 (full approval ladder). Stages 3–7 + Appendix are still `_(Draft)_` stubs. Write from the live app, not plans; match exact app labels.
- Tests: [tests/plan.yaml](tests/plan.yaml) (rules + cases), `tests/.env.test` (gitignored, human-filled only)
- Cross-project NocoBase traps: `nb-bootstrap`'s `references/gotchas.md` — the single home; auto-memory only points there
- Kept non-standard folders (organically grown pre-retrofit, deliberately not restructured — real, load-bearing content with no better home in the standard tree): [Planning and Design/](Planning%20and%20Design/) (design validation docs), [nocobase docs/](nocobase%20docs/) (doc cache), [Outputs/](Outputs/), [snippets/](snippets/) (reusable JS, e.g. `po-line-items-total.js` — RunJS isn't version-controlled, so this is the source of truth for it), [templates/](templates/) (PO print-template source, `build_po_template.py`), [archive/](archive/), `backups/` (gitignored — `nb backup create/restore` output), [role-acl-guidelines.md](role-acl-guidelines.md) (standalone ACL reference, kept at root rather than folded into `design/permissions.md`).

One fact, one home: if you're about to write the same fact in two of these files, stop — pick its home and pointer-reference it from elsewhere instead of duplicating it.

There is no state-mirror file. The live app, queried via `nb api`, is the source of truth for everything queryable — collections, fields, roles, ACL, workflows, pages, IDs. Never act on an ID that wasn't just read from the live env. (`project_current_state.md` was retired 2026-07-02 for this reason — see git history if you need the pre-retrofit narrative.)

## Session workflow

When the user names an MVP (e.g. "let's do 014.5"):

1. Delegate the live reads to the `nb-drift-scout` subagent (see "Delegated reads" below): pass it the env name (`havenbeheer`), the canonical tree path (`~/nocobase-dev/havenbeheer` — it verifies the postgres container's bind mount against it, catching a wrong-tree start per D76), what the MVP touches (collections, roles, workflows, pages), and the expected state from roadmap.md, decisions.md, and recent git history. It returns a drift report plus fresh live IDs. **Report drift before doing anything else** — anything live that doesn't match what's expected. Handle consequences immediately: update `tests/plan.yaml`, update `docs/user-guide.md`, adjust the chunk plan.
2. Read the roadmap.md entry for the MVP.
3. Check decisions.md for D-entries with "Affects: <MVP>".
4. Read design/ files only if the chunk touches that area. Read notes.md for anything flagged relevant.
5. **If chunks/NNN-*.md doesn't exist yet, draft it now** from the roadmap one-liner, the design files just read, and the decisions just checked. Show the draft, refine, commit, then continue.
6. **If chunks/NNN-*.md already exists**, read it.
7. Enter plan mode; save the plan to `./plans/`.
8. Once the user approves the plan (once), execute **phase by phase**: after each phase, pause with a summary of what was done and a preview of the next phase before continuing. Irreversible actions (deletes, dropping pages, destroying workflow history) always get an explicit stop and confirmation, regardless of phase boundary.
9. Backend only. Claude does not build UI unless the user explicitly delegates a screen — see "Test gate" below.

## Delegated reads

Bulk `nb api` reads go to read-only Sonnet subagents (defined in `~/.claude/agents/`), so raw JSON dumps never enter the main conversation and stop being re-billed every turn. Always pass the env name (`havenbeheer`) — each agent verifies it before reading. They quote config values verbatim; if a report is ambiguous or contradicts expectations, re-read that one object directly rather than guessing.

- `nb-drift-scout` — session-start drift check (step 1 above). In: MVP scope + expected state. Out: drift report + live IDs.
- `nb-live-reader` — workflow node chains and ACL reads for `nb-test draft`. Out: condition expressions and grants as verbatim JSON.
- `nb-ui-labels` — exact UI labels (menu, block, field, button texts) for `docs/user-guide.md` updates.

Never delegate: rule wording, review gates, user approvals, or any `nb api` write — those stay here.

## Test gate

A chunk isn't complete until `nb-test run` is fully green AND the user has verbally confirmed the UI/behavior works. Not a checkbox ritual — an actual "yes this works" from the user. Once the backend is tested green, write a descriptive interface brief into the chunk file (blocks, field bindings, actions, linkage suggestions) and stop; the human builds the screen. The brief is a suggestion sheet, not a contract — the result may differ completely.

At session end:
- If the plan changed during the build: edit chunks/NNN-*.md in place AND append a D-entry to decisions.md listing affected downstream chunks.
- Update docs/user-guide.md for anything user-visible that changed — written from what the live app actually shows, not from what was planned. Get the exact labels via the `nb-ui-labels` subagent.
- Update roadmap.md status.
- Commit.
- If you learned a NocoBase gotcha that applies to ANY NocoBase project, append it to `nb-bootstrap`'s `references/gotchas.md` (the single cross-project home — never a second copy in auto-memory). If it's specific to this project, put it in notes.md instead.

## Live environment changes

Before modifying live NocoBase configuration (creating/editing collections, workflows, pages, roles, fields), get approval on the **business logic**, not the implementation:
- **The rule in plain language** — who can do what, under which condition, and why (the business reason: a D-entry, a workflow gate, a stated responsibility). This is the thing to review and correct.
- **What changes vs. what stays** — the net effect in business terms (e.g. "procurement can no longer set payment status, but still sees it").
- **Expected UI result** — what the user will see in NocoBase after the change.

Do NOT lead with raw payloads, JSON bodies, or field-by-field CLI arguments. Alexander reviews rules, not wire format — show the mechanism only if he asks. Wait for explicit approval or correction of the rule, then execute.

**For irreversible actions** (deleting data, dropping a published page, destroying workflow history, removing a role with assigned users), additionally provide a rollback plan and get explicit confirmation. Most NocoBase actions are reversible enough that the rollback step is implicit; only require explicit rollback when undoing isn't trivially obvious.

## NocoBase rules
- **Workflow versioning:** once a workflow has been executed, you cannot edit it in place. Create a new revision (`nb api workflow workflows revision`), edit the new version, enable it, disable the old one.
- **Member is the base role:** every user has `member` as their base role. View ACL on shared resources goes on `member`, not duplicated to every specific role. Only add separate ACL to a specific role when it needs MORE than member.
- **`roleMode` is `only-use-union` (D54):** every user's effective permissions are the union of all their roles, always — a derived role's restriction has no effect if any other role the user holds already grants it. Tighten the most-permissive role, not the derived one. See `role-acl-guidelines.md` §1 and `notes.md`'s go-live checklist (`member`'s `ui.*` snippet is currently un-negated as a deliberate dev convenience, and this setting makes that apply to every user right now).
- **`fieldGroups` requirement:** any page using `purchase_requests` needs `defaults.collections.purchase_requests.fieldGroups` set (likewise `users` — the `submitter` association generates a view popup with >10 fields).
- **No global `create` for approver roles on `attachments`-adjacent grants** — D25 forbids approvers creating PRs; use narrow independent resource permissions instead (see the gotchas catalogue for the pattern).
- **Auth failures hand off:** if `nb api` or a direct HTTP call returns 401/403/auth-required, stop and hand off to `nocobase-env-manage` — don't patch around it.

## Skills
Official (auto-installed with NocoBase CLI): nocobase-env-manage, nocobase-plugin-manage, nocobase-data-modeling, nocobase-acl-manage, nocobase-workflow-manage, nocobase-ui-builder, nocobase-data-analysis, nocobase-utils.
This suite (`nb-project-suite`): nb-test (rules/cases, runner, pre-deploy gate), nb-bootstrap (this file's own origin — re-invoke only for a genuinely new project, not per chunk), nb-new-project (scaffold).
Consult `nocobase-runjs` before writing any custom JS (JS Block/Field/Item/Column/Action, linkage rule scripts) — e.g. the `snippets/` JS blocks.
Before building or changing workflows, approval forms, ACL, or formula fields: check `nb-bootstrap`'s gotchas catalogue for a known trap first — cheaper than rediscovering it live.
**Do NOT use `nocobase-dsl-reconciler` for this project** — it authors apps as committed YAML + `cli push`, a fundamentally different model from this project's live-first approach (this file's whole workflow assumes `nb api` is the source of truth). Switching now would mean re-deriving 16+ already-shipped MVPs into YAML for no benefit. The skill's own description is opt-in-only, but this is a real fork in how the project works, not a minor tool choice — don't invoke it here even if asked for "the DSL path" in a generic sense; confirm explicitly first.

## Commits
Commit after:
- Chunk file approval (before any execution)
- A phase that's been built and manually verified
- `tests/plan.yaml` rule or case changes
- A new D-entry in decisions.md

Don't commit half-built or unverified configuration. The commit history should read as a series of "this worked" milestones.

## Build discipline
- One chunk per session, ideally 1–3 hours.
- Manual verification by the user before marking a chunk complete.
- When in doubt about scope: it's out. Defer to a later chunk and write the D-entry.
- When the plan changes mid-build: edit the chunk file in place to reflect what was built, AND add a D-entry to decisions.md naming affected future chunks.
