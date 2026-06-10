# Plan — MVP013 regular-purchase flag

Source: [chunks/013-regular-purchase-flag.md](../chunks/013-regular-purchase-flag.md). Approved 2026-06-09.

**Blocker:** OAuth expired — user must run `nb env auth havenbeheer` before any live `nb api` step.

## Step 0 — re-auth + live snapshot (pre-flight)
- User runs `nb env auth havenbeheer`.
- Re-read active workflow `369076269481984` and confirm: condition `bizoy1sj87j` config (the two OR
  leaves + read paths), Procurement node `ec2h8cqal32` ProcessForm uid, node count = 30.
- Confirm `needs_director_approval` is absent from the create form (expected).

## Step 1 — field (013.1) · `nocobase-data-modeling`
- Create `purchase_requests.is_regular`: boolean / checkbox, `defaultValue: false`, title "Is regular".
- No append needed (scalar). Verify it reads back on the collection.

## Step 2 — workflow revision (013.2) · `nocobase-workflow-manage`
- Revision `cv237r8h7k9` from active `369076269481984`, **force same key** via raw `--body`
  (`{"key":"cv237r8h7k9","enabled":false,"current":false}`).
- Verify the copy has 30 nodes; recreate any dropped condition-branch nodes.
- Edit condition `bizoy1sj87j`: replace the `needs_director_approval == true` leaf with
  `is_regular != true` reading `{{$jobsMapByNodeKey.ec2h8cqal32.data.is_regular}}`; keep the
  `quoted_total_usd >= 300` (gte) leaf; keep OR group, basic engine, true→Director / false→approved.
- Do NOT enable yet (enable after flow-nodes test + UI in place + user verify).

## Step 3 — UI (013.3) · `nocobase-ui-builder`
- Add `is_regular` **editable** to the new Procurement ProcessForm (the regenerated one on the new
  revision). Confirm per-action comment models carry over (no 403 for Pat).
- Add `is_regular` **read-only** to detail popup `2b367dbd157`.

## Step 4 — verify (013.4)
- `flow-nodes test` condition `bizoy1sj87j` across 4 quadrants:
  - (≥300, regular) → true (Director); (≥300, not) → true; (<300, regular) → false (approved);
    (<300, not) → true (Director). Plus no-quote(0)/not → true; (0/regular) → false.
- Enable the revision (set current+enabled, disable predecessor).
- Hand to user for A1–A7 end-to-end with Pat/Oliver/Dana.

## Step 5 — docs (013.5)
- decisions.md: add **D37** (amends D30, retires D23 routing role of `needs_director_approval`;
  list affected: MVP4, MVP013).
- project_current_state.md: new field row, new active workflow version id + condition description,
  ProcessForm/popup wrapper IDs, stale-ID the prior version.
- roadmap.md: flip MVP013 to built/verified.
- chunk 013 "As built" section; move chunk to `completed/` if convention (012 is still in chunks/, so leave).
- Commit after each verified milestone.
