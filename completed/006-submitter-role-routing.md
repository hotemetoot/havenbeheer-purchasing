# 006 — Submitter-role routing variants ✓

**Verified:** 2026-05-24. **Design change:** D25 — no new build required.

## Goal
Handle PR routing for non-standard submitters (dept owners, procurement staff).

## What was actually built
**Nothing new.** Per D25 ([decisions.md](../decisions.md)):

- Procurement staff are excluded from submitting PRs by policy/ACL — the "submitter's dept = Procurement → skip to director" variant is moot.
- The dept-owner skip (submitter IS dept main_approver → skip dept stage) was already implemented in MVP1 (condition node `5hed96jh1u7` in the PR Approval workflow).

## Routing as verified
- R1: Operations member (Alice) → normal 3-stage ✓ (verified in MVP1)
- R2: Oliver (Operations owner) submits → skips dept, straight to Procurement ✓ (verified in MVP1)
- R3 / R4: Procurement staff → cannot submit PRs (ACL gate, finalized in MVP7+)
