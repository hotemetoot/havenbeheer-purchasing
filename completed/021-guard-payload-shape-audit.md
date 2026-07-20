# 021 — Guard payload-shape audit (purchase requests, projects, everything else)

**Status:** COMPLETE 2026-07-19 (D94). Audit + fix, not a feature.
**Result:** 14 enabled interception guards read, **one fault found** — "Guard: Create PO (PR must be approved)" (`vgv8hcrtjvx`), the oldest guard in the set. Fixed with the D89 resolver head, new live version `376416662847488`, predecessor `366562380808192` disabled. Covered by new rule **R52** (5 cases, 2 new fixtures). Suite **121/121**.
**What turned out clean** — recorded so nobody re-audits it: `c9c14tyn876` and `eiscjvwiqr6` (the two D89 left unchecked) read only scalars; both PR Budget guards already carried resolver heads, so the PR-side associations this chunk feared most were never exposed; `2h75zryz3cb`, `xvcsdv07c5j`, `f3dkb37te22`, `v61hc3ou3pa`, `496ookqmg01` read nothing from the payload at all; `b6brl8r9c58` and `mhfp4d15uee` are scalar-only.
**Sharpening the plan's "force the same key" step:** revise with `--filter '{"key":"<key>"}'`, never `--filter-by-tk` — by record id the endpoint forks a brand-new lineage, which is what happened here and cost a recovery revision. `workflows update` cannot repair it afterwards; only the revision endpoint honors `key`, passed in `--body`. Check the returned `key` before building on a revision. Passing `--title` prevents D84's " copy" suffix.

**Size:** half a session if the guards are clean, longer if any need a revision.
**Do this before go-live.** A guard with this fault does not fail safe — it returns a server error page to the caller, and in one of the two cases found so far it let requests through entirely for as long as the broken version was live.

## The story

Pat adds a line to a purchase order from the PO screen. It works. A program — an import, a script, another system, anything talking to the app directly — adds the same line, and gets a server error page instead of either a clean refusal or a saved line.

The reason: NocoBase lets a request name a linked record in more than one way. `purchase_order: 12345`, `purchase_order: {id: 12345}`, and `purchaseOrderId: 12345` all mean the same thing and are all legal. A guard that takes that value straight from the request and hands it to the database only understands the first one. Give it the second and the database is asked to match a whole record against an id column, which it refuses — the guard crashes, and the caller sees a server error.

Every screen in the app writes it the first way. That is why nothing was ever visible in the UI, why the test suite stayed green, and why this sat undiscovered in two guards at once.

## What is already done (D89)

Two guards on PO lines, both found and fixed 2026-07-19:

| Guard | Key | Fixed version |
|---|---|---|
| PO Line Create — block on terminal PO | `polncreateg1` | `376333087145984` |
| PO Line Create — budget ceiling (PR amount) | `8u81nd3vxhc` | `376358445907968` |

Four other interception guards on `po_lines` were checked and are clean — `c9c14tyn876`, `mhfp4d15uee`, `f3dkb37te22`, `v61hc3ou3pa`. They read only `quantity_ordered`, `unit_price` and `received_quantity`, which are plain numbers with nothing to misread.

Covered by test rule R50 (6 cases).

## What is left

`po_lines` is done. **No other collection has been looked at.** Purchase requests and projects have their own interception guards, and the PR guards in particular read associations — `project`, `department`, `submitter` — which is exactly the shape that breaks.

### 1. Find every candidate

List the enabled interception guards and dump their node configs:

```
nb api resource list --resource workflows --filter '{"enabled":true}' --page-size 100 --env havenbeheer
nb api resource list --resource flow_nodes --filter '{"workflowId":<id>}' --page-size 100 --env havenbeheer
```

A node is a candidate when a **query**, **aggregate**, **update** or **destroy** node filters on `{{$context.params.values.<association>}}` — an association, not a scalar. Scalars are safe; only linked-record fields have the ambiguity. The grep that found both PO-line cases: pull every `{{$context.params.values.X}}` out of each node config and keep the ones where `X` is an m2o field name on that collection.

Two traps that nearly hid the second one:

- **A guard can sit behind its own first condition.** The budget guard only looks the order up once a quantity *and* a price are both present, so a probe that omits the price never reaches the broken node and reports clean. Read the whole chain and work out what a request must contain to reach the suspect node, then build the probe to satisfy it.
- **Several guards fire on the same action.** Fixing one and re-testing proves nothing about the others. That is precisely how the first fix was reported as done while the app was still returning a 500 on every realistic create.

### 2. Confirm each one live before changing anything

Send the same request twice, once with the link written each way, and compare. Plain id succeeding while the nested form returns *"Workflow on your action failed, please contact the administrator"* is the signature. Probe against a record where the guard should **refuse**, so a healthy guard blocks and nothing is written. Otherwise a passing probe leaves a row behind.

### 3. Fix

Copy the `plc_pid` / `bud_pid` head node verbatim from either fixed guard. It picks the first of `values.<assoc>.id`, `values.<assoc>`, `values.<assoc>Id` that is greater than zero, and every downstream filter then reads `{{$jobsMapByNodeKey.<node>}}` instead of the raw value.

Written unquoted — `N({{...}})`, never `N('{{...}}')`. The engine swaps each `{{...}}` for a scope placeholder and binds values separately, so quoting it evaluates the literal text `$$0` and silently yields nothing. That mistake cost most of the D89 session and shipped a guard that allowed everything. `flow-nodes test` cannot catch it: it has no request context, so it happily validates an expression that is broken live.

Whether an unresolvable parent should refuse or allow is a per-guard judgement — ask. For `polncreateg1` Alexander chose refuse, on the grounds that a PO line belonging to no order is meaningless. `8u81nd3vxhc` was left to allow, because a line with no order is already refused by `polncreateg1` and a second refusal message would only confuse.

Normal revision discipline: new revision, force the same key, diff node by node **and** at workflow level, node count included.

### 4. Cover it

Extend R50 or add a sibling rule. One case per guard, sending the link the nested way, expecting the refusal the guard exists to produce. A server error is not a refusal to the runner — 500 is not in `DENY_CODES` — so the case fails loudly if the fault returns. Pair each with an allow case, or a guard that blocks everything reads as green.

## Debugging technique worth reusing

To watch a sync guard's internals without writing rows: build a throwaway revision whose identify-check is forced false (`0>1`), so every request is refused, put a diagnostic expression in the node under suspicion, then read its output from the `jobs` table. That is how the placeholder substitution was finally pinned down — a `CONCATENATE` of the three candidate values came back as the literal string `A[$$0]B[$$1]C[$$2]`.

Two constraints to plan around: a node cannot be edited once its workflow has executed even once, so each iteration costs a fresh revision; and delete the throwaway versions afterwards, since an always-block harness left enabled would refuse every create in the app.

## Done when

- Every enabled interception guard has been read, and each one either has no association read or has the resolver head.
- Each fix confirmed live by sending the link both ways.
- Test cases exist for each fixed guard, and the suite is green.
- A D-entry records what was swept and what was found — including the guards that turned out clean, so the next person does not re-audit them.
