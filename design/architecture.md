# Architecture

**Stable design reference.** This file points at the authoritative validation docs in `Planning and Design/`. Extract into standalone notes here when MVP8 starts (or sooner, if these references become inconvenient).

## Guiding principles

1. **Smallest possible slice first.** Each MVP is demoable end-to-end by a human.
2. **Native over custom.** Form-required, native approval nodes, native data-scopes, native owners. Custom JS and Before-Action guards last, not first.
3. **One concern per MVP.** If it touches two concerns, split it.
4. **Stop and validate.** Each MVP ends with a manual test pass by the user before opening the next.
5. **Skip everything not strictly required, especially fields.** Adding fields later is cheap; removing them is not.

## Authoritative design references

- **PR data model and approval flow:** [havenbeheer purchasing — design validation.md](../Planning%20and%20Design/havenbeheer%20purchasing%20—%20design%20validation.md). Use this for the PR collection, status state machine, approval shape.
- **PO data model:** [havenbeheer PO — design validation.md](../Planning%20and%20Design/havenbeheer%20PO%20—%20design%20validation.md). Use this for PO header/lines, status transitions, budget zones, receiving, completion.
- **Permissions matrix and guards:** [havenbeheer PR — permissions and guards.md](../Planning%20and%20Design/havenbeheer%20PR%20—%20permissions%20and%20guards.md). Source for Guards A/C/E/#9 and the role-level ACL grid.

## What lives where (vs. these design docs)

- **Decisions that have superseded design-doc content** live in [decisions.md](../decisions.md) (e.g. D9 collapsed 1-PR-to-many-POs → 1:1; D22 replaced FX-lookup workflow with manual rate; D23 replaced `approval_limits` with manual checkbox). When design doc and decisions disagree, decisions wins.
- **Current live state** (collection IDs, workflow node IDs, surface IDs) lives in [project_current_state.md](../project_current_state.md), never duplicated here.

See also:
- [users-and-roles.md](users-and-roles.md)
- [permissions.md](permissions.md)
