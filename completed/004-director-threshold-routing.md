# 004 — Director routing via manual checkbox ✓

**Verified:** 2026-05-24 by user. **Design change:** D23 (supersedes original D4 threshold).

## Goal
Decide whether a PR needs Director approval after Procurement signs off, then either route to Director or auto-approve.

## What was built
- `purchase_requests.needs_director_approval` (boolean, default false) — set by submitter.
- `purchase_requests.approved_at` (datetime) — written on final approval (both paths).
- Approval workflow Procurement-Approve branch restructured: condition on `needs_director_approval`:
  - true → set `pending_director_approval` → Director Approval node → approved + `approved_at`
  - false → approved + `approved_at` immediately
- PR create form: checkbox after justification; linkage rule makes `justification` required when checkbox is checked.
- PR detail popup: `needs_director_approval` display field added.
- **Not built:** `approval_limits` collection or Guard E (per D23 — automatic threshold was rejected in favor of manual judgement).

## Design change (D23)
Original plan: `approval_limits` table, USD $1,500 threshold, automatic routing. Replaced 2026-05-24 with manual checkbox — routing rules weren't crisp enough to automate. See [decisions.md](../decisions.md) D23 for the full rationale.
