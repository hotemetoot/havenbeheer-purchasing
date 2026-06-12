# Havenbeheer Purchasing

NocoBase-based PR/PO approval workflow. This file is auto-loaded every session.

## Environment
- NocoBase 2.1.0-beta.36 at http://localhost:13000
- CLI env name: `havenbeheer`
- Auth: OAuth (auto-refreshes)

## Where things live
- Big picture: [design/](design/) — thin pointers to validation docs in `Planning and Design/`
- Roadmap of all MVPs: [roadmap.md](roadmap.md)
- Current chunk (the MVP we're actively building): [chunks/NNN-*.md](chunks/)
- What exists in NocoBase right now: [project_current_state.md](project_current_state.md) (authoritative — update at session end)
- Decision history: [decisions.md](decisions.md) (currently effective) and [decisions-archive.md](decisions-archive.md) (full)
- Cross-project NocoBase patterns: auto-memory `feedback_*.md` (read-only reference)

## Session workflow

When the user names an MVP (e.g. "let's do 008"):

1. Read [project_current_state.md](project_current_state.md) — IDs, what exists, stale IDs. If a section is empty for what you'll act on, verify against the live env before proceeding. **Always re-query active workflow versions live** (`workflows` filter `{"current":true,"enabled":true}`) before touching any workflow — the user makes manual adjustments between sessions, and the doc's active-version IDs lag repeatedly.
2. Read the [roadmap.md](roadmap.md) entry for the MVP.
3. Check [decisions.md](decisions.md) for any D-entries affecting this MVP.
4. Read [design/](design/) files only if the chunk touches their area.
5. **If `chunks/NNN-*.md` does not exist yet**, draft it now using the chunk template (see existing chunks). Source material: roadmap one-liner, design files just read, decisions just checked. Show draft, refine, commit, then continue.
6. **If `chunks/NNN-*.md` already exists**, read it.
7. Enter plan mode; plan is saved to `./plans/` if that works (test once — see open item), else `~/.claude/plans/`.
8. After user approves the plan, execute step by step.
9. Pause before any irreversible action and ask user to verify manually.

At session end:
- Update [project_current_state.md](project_current_state.md) with new collections, fields, workflow node IDs, MVP status. Commit it.
- If the plan changed during the build: edit `chunks/NNN-*.md` in place AND append a D-entry to [decisions.md](decisions.md), listing affected downstream MVPs by number.
- If you learned a NocoBase gotcha that applies to ANY NocoBase project (not just Havenbeheer), save it as `feedback_<topic>.md` in auto-memory.

## Live environment changes

Before modifying live NocoBase configuration (creating/editing collections, workflows, pages, roles, fields), show the user:

- **Intended changes** — what entities/fields/nodes will be created or modified.
- **CLI/API category** — which skill or command group (e.g. `nocobase-data-modeling`, `nocobase-workflow-manage`).
- **Expected UI result** — what the user will see in NocoBase after the change.

Wait for explicit approval before executing.

**For irreversible actions** (deleting data, dropping a published page, destroying workflow history, removing a role with assigned users), additionally provide a rollback plan and get explicit confirmation. Most NocoBase actions are reversible enough that the rollback step is implicit; only require an explicit rollback plan when undoing isn't trivially obvious.

## NocoBase rules

The cross-project gotcha catalogue lives in the `myNocobase-project-workflow` skill (`reference/nocobase-gotchas.md`) — **read it before building or changing workflows, approval forms, ACL, or formula fields.** One-line versions of most gotchas are in the auto-memory index (always loaded). Project-specific rules that live only here:

- **Never use IDs listed under "Stale IDs"** in [project_current_state.md](project_current_state.md), and verify risky IDs against the live env first — the doc is authoritative but can lag.
- **`fieldGroups` requirement.** Any future page using `purchase_requests` needs `defaults.collections.purchase_requests.fieldGroups` (likewise `users` — the `submitter` association generates a view popup with >10 fields).
- **No global `create` for approver roles on `attachments`-adjacent grants** — D25 forbids approvers creating PRs; use narrow independent resource permissions (see catalogue for the pattern).

## Skills

The NocoBase CLI ships skills, auto-installed via `nb init`: `nocobase-env-manage`, `nocobase-plugin-manage`, `nocobase-data-modeling`, `nocobase-acl-manage`, `nocobase-workflow-manage`, `nocobase-ui-builder`, `nocobase-data-analysis`, `nocobase-utils`. **Do NOT use** `nocobase-dsl-reconciler` for this project — we author against the live app, not committed YAML.

## Commits

Commit after:
- Chunk file approval (before any execution).
- Successful implementation of a phase that's been manually verified.
- Updating [project_current_state.md](project_current_state.md) at session end.
- Recording a new D-entry in [decisions.md](decisions.md).

Don't commit half-built or unverified configuration. The commit history should read as a series of "this worked" milestones.
