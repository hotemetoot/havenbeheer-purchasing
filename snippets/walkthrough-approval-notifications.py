#!/usr/bin/env python3
"""017 notification walkthrough — drives every terminal decision path as the
real approver users via the API and verifies who received an in-app message,
against the D88 recipient matrix. Cleans up after itself."""
import importlib.util, sys, time
from pathlib import Path

RUNNER = Path.home() / ".claude/skills/nb-project-suite/tools/nb-test/runner.py"
spec = importlib.util.spec_from_file_location("nbrunner", RUNNER)
nb = importlib.util.module_from_spec(spec)
sys.modules["nbrunner"] = nb
spec.loader.exec_module(nb)

PROJECT = Path("/Users/alexander/Documents/Claude/Projects/Havenbeheer Purchasing")
env = nb.load_env_file(PROJECT / "tests/.env.test")
AUTH = env.get("AUTHENTICATOR", "basic")
admin = nb.Client(env["NOCOBASE_URL"], env["ADMIN_API_KEY"], AUTH)

OPS_DEPT = 363554454962178      # Operations
OLIVER, PAT, DANA = 10, 11, 12
PR_WF, PROJ_WF = "cv237r8h7k9", "hzykothf9cx"
WANDA_EMAIL = "test_walkthrough_wanda@test.local"

def die(msg):
    sys.exit(f"ABORT: {msg}")

def d(r):
    return nb.data_of(r)

# ---- preflight: Operations dept head must be Oliver -------------------------
r = admin.act("departments", "get", params={"filterByTk": OPS_DEPT})
dept = d(r) or {}
if dept.get("mainApproverId") != OLIVER:
    die(f"Operations mainApproverId is {dept.get('mainApproverId')}, expected 10")
print(f"preflight ok: Operations dept head = {OLIVER} (Oliver)")

# ---- temp submitter wanda (Operations dept, operations role) ---------------
r = admin.act("users", "list", params={"filter": {"email": WANDA_EMAIL}})
rows = d(r) or []
if rows:
    wanda_id = rows[0]["id"]
else:
    r = admin.act("users", "create", values={
        "email": WANDA_EMAIL, "nickname": "[TEST] walkthrough_wanda",
        "password": env["TEST_USER_PASSWORD"]})
    if not r.ok:
        die(f"create wanda: {r.text[:200]}")
    wanda_id = d(r)["id"]
rr = admin.act(f"users/{wanda_id}/roles", "set", values=["operations", "member"])
if not rr.ok:
    admin.act(f"users/{wanda_id}/roles", "add", values=["operations", "member"])
r = admin.act("departmentsUsers", "list", params={
    "filter": {"userId": wanda_id, "departmentId": OPS_DEPT}})
if not (d(r) or []):
    admin.act(f"users/{wanda_id}/departments", "add", values=[OPS_DEPT])
admin.act("departmentsUsers", "update",
          params={"filter": {"userId": wanda_id, "departmentId": OPS_DEPT}},
          values={"isMain": True})
print(f"wanda ready: id {wanda_id}, dept Operations")

# ---- sign-ins ---------------------------------------------------------------
def signin(email, password):
    c = nb.Client(env["NOCOBASE_URL"], authenticator=AUTH)
    c.sign_in(email, password)
    return c

wanda = signin(WANDA_EMAIL, env["TEST_USER_PASSWORD"])
oliver = signin("oliver@havenbeheer.test", "nbtest")
pat = signin("pat@havenbeheer.test", "nbtest")
dana = signin("dana@havenbeheer.test", "nbtest")
print("signed in: wanda, oliver, pat, dana")

# ---- helpers ----------------------------------------------------------------
created = []   # (collection, id) for teardown

def make(collection, wf_key, values):
    r = admin.act("workflows", "list", params={
        "filter": {"key": wf_key, "enabled": True}})
    wf = (d(r) or [None])[0] or die(f"no enabled workflow {wf_key}")
    r = wanda.act("approvals", "create", values={
        "collectionName": collection, "workflowId": wf["id"],
        "data": values, "status": 2})
    if not r.ok:
        die(f"create {collection}: HTTP {r.status_code} {r.text[:200]}")
    rec = (d(r) or {}).get("data") or {}
    created.append((collection, rec["id"]))
    return rec["id"]

def pending(client, collection, rec_id, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.act("approvalRecords", "listMine", params={"filter": {
            "$and": [{"approval.collectionName": collection},
                     {"approval.dataKey": str(rec_id)}, {"status": 0}]}})
        rows = d(r) or []
        if len(rows) == 1:
            return rows[0]
        time.sleep(1)
    die(f"no pending approval for {collection}/{rec_id}")

def decide(client, collection, rec_id, decision, comment):
    row = pending(client, collection, rec_id)
    vals = {"status": {"approve": 2, "reject": -1}[decision],
            "comment": comment}
    r = client.act("approvalRecords", "submit",
                   params={"filterByTk": row["id"]}, values=vals)
    if not r.ok:
        die(f"submit {decision}: HTTP {r.status_code} {r.text[:200]}")

def status_of(collection, rec_id):
    return (d(admin.act(collection, "get",
                        params={"filterByTk": rec_id})) or {}).get("status")

NAMES = {wanda_id: "wanda", OLIVER: "oliver", PAT: "pat", DANA: "dana"}

def check_messages(tag, expected_ids, timeout=25):
    """Poll in-app messages whose title contains the tag; compare the
    recipient set with the expectation."""
    expected = set(expected_ids)
    deadline = time.time() + timeout
    rows = []
    while time.time() < deadline:
        r = admin.act("notificationInAppMessages", "list", params={
            "filter": {"title.$includes": tag}, "paginate": False})
        rows = d(r) or []
        if {m["userId"] for m in rows} >= expected:
            break
        time.sleep(1)
    time.sleep(2)  # settle: catch late extra recipients
    r = admin.act("notificationInAppMessages", "list", params={
        "filter": {"title.$includes": tag}, "paginate": False})
    rows = d(r) or []
    got = {m["userId"] for m in rows}
    ok = got == expected
    detail = ", ".join(f"{NAMES.get(m['userId'], m['userId'])}: "
                       f"{m['title']!r}" for m in rows) or "(none)"
    return ok, got, detail

results = []

def scenario(name, tag, expected, sample=None):
    ok, got, detail = check_messages(tag, expected)
    exp_s = "{" + ", ".join(sorted(NAMES.get(u, str(u)) for u in expected)) + "}"
    got_s = "{" + ", ".join(sorted(NAMES.get(u, str(u)) for u in got)) + "}"
    results.append((name, ok, exp_s, got_s, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}: expected {exp_s}, got {got_s}")
    if not ok or sample:
        print(f"      messages: {detail}")

try:
    # W1 — dept head rejects: submitter only
    pr = make("purchase_requests", PR_WF,
              {"title": "[TEST-W1] dept-stage reject", "quoted_total": 100,
               "fx_rate_to_usd": 1})
    decide(oliver, "purchase_requests", pr, "reject", "[TEST] W1 dept reject")
    print(f"W1 pr {pr} status: {status_of('purchase_requests', pr)}")
    scenario("W1 PR rejected by dept head", "[TEST-W1]", {wanda_id}, sample=True)

    # W2 — custom approver (Dana) rejects: submitter + dept head
    pr = make("purchase_requests", PR_WF,
              {"title": "[TEST-W2] custom-approver reject", "quoted_total": 100,
               "fx_rate_to_usd": 1, "use_custom_approver": True,
               "customApproverId": DANA})
    decide(dana, "purchase_requests", pr, "reject", "[TEST] W2 custom reject")
    scenario("W2 PR rejected by custom approver", "[TEST-W2]",
             {wanda_id, OLIVER})

    # W3 — procurement rejects: submitter + dept head (proc head is actor)
    pr = make("purchase_requests", PR_WF,
              {"title": "[TEST-W3] procurement reject", "quoted_total": 100,
               "fx_rate_to_usd": 1})
    decide(oliver, "purchase_requests", pr, "approve", "[TEST] W3 dept ok")
    decide(pat, "purchase_requests", pr, "reject", "[TEST] W3 proc reject")
    scenario("W3 PR rejected by procurement", "[TEST-W3]", {wanda_id, OLIVER})

    # W4 — director rejects: all three
    pr = make("purchase_requests", PR_WF,
              {"title": "[TEST-W4] director reject", "quoted_total": 500,
               "fx_rate_to_usd": 1})
    decide(oliver, "purchase_requests", pr, "approve", "[TEST] W4 dept ok")
    decide(pat, "purchase_requests", pr, "approve", "[TEST] W4 proc ok")
    decide(dana, "purchase_requests", pr, "reject", "[TEST] W4 dir reject")
    scenario("W4 PR rejected by director", "[TEST-W4]",
             {wanda_id, OLIVER, PAT})

    # W5 — board rejects (board task holder is Pat in this env): all three
    pr = make("purchase_requests", PR_WF,
              {"title": "[TEST-W5] board reject", "quoted_total": 15000,
               "fx_rate_to_usd": 1})
    decide(oliver, "purchase_requests", pr, "approve", "[TEST] W5 dept ok")
    decide(pat, "purchase_requests", pr, "approve", "[TEST] W5 proc ok")
    decide(dana, "purchase_requests", pr, "approve", "[TEST] W5 dir ok")
    decide(pat, "purchase_requests", pr, "reject", "[TEST] W5 board reject")
    scenario("W5 PR rejected by board", "[TEST-W5]", {wanda_id, OLIVER, PAT})

    # W6 — project rejected at dept stage: submitter only
    pj = make("projects", PROJ_WF,
              {"title": "[TEST-W6] project dept reject", "budget_usd": 5000,
               "justification": "[TEST] walkthrough"})
    decide(oliver, "projects", pj, "reject", "[TEST] W6 dept reject")
    print(f"W6 project {pj} status: {status_of('projects', pj)}")
    scenario("W6 project rejected by dept head", "[TEST-W6]", {wanda_id},
             sample=True)

    # W7 — project rejected by director: all three
    pj = make("projects", PROJ_WF,
              {"title": "[TEST-W7] project director reject",
               "budget_usd": 5000, "justification": "[TEST] walkthrough"})
    decide(oliver, "projects", pj, "approve", "[TEST] W7 dept ok")
    decide(pat, "projects", pj, "approve", "[TEST] W7 proc ok")
    decide(dana, "projects", pj, "reject", "[TEST] W7 dir reject")
    scenario("W7 project rejected by director", "[TEST-W7]",
             {wanda_id, OLIVER, PAT})

    # W8 — PR approved by director: all three (director is actor, excluded
    # by node position — director-approved node notifies the other three
    # slots which resolve to wanda/oliver/pat)
    pr = make("purchase_requests", PR_WF,
              {"title": "[TEST-W8] director approved", "quoted_total": 500,
               "fx_rate_to_usd": 1})
    decide(oliver, "purchase_requests", pr, "approve", "[TEST] W8 dept ok")
    decide(pat, "purchase_requests", pr, "approve", "[TEST] W8 proc ok")
    decide(dana, "purchase_requests", pr, "approve", "[TEST] W8 dir approve")
    print(f"W8 pr {pr} status: {status_of('purchase_requests', pr)}")
    scenario("W8 PR approved by director", "[TEST-W8]",
             {wanda_id, OLIVER, PAT})

    # W9 — regular <300, procurement final: submitter + dept head only
    pr = make("purchase_requests", PR_WF,
              {"title": "[TEST-W9] procurement-final approved",
               "quoted_total": 250, "fx_rate_to_usd": 1})
    decide(oliver, "purchase_requests", pr, "approve", "[TEST] W9 dept ok")
    r = pat.act("purchase_requests", "update",
                params={"filterByTk": pr}, values={"is_regular": True})
    if not r.ok:
        die(f"W9 pat sets is_regular: HTTP {r.status_code} {r.text[:200]}")
    decide(pat, "purchase_requests", pr, "approve", "[TEST] W9 proc final")
    print(f"W9 pr {pr} status: {status_of('purchase_requests', pr)}")
    scenario("W9 PR approved procurement-final", "[TEST-W9]",
             {wanda_id, OLIVER})

finally:
    print("\n--- teardown ---")
    for collection, rec_id in created:
        r = admin.act(collection, "destroy", params={"filterByTk": rec_id})
        print(f"deleted {collection}/{rec_id}: {r.status_code}")
    r = admin.act("notificationInAppMessages", "destroy", params={
        "filter": {"title.$includes": "[TEST-W"}})
    print(f"deleted walkthrough messages: {r.status_code}")
    r = admin.act("users", "destroy", params={"filterByTk": wanda_id})
    print(f"deleted wanda ({wanda_id}): {r.status_code}")

print("\n=== SUMMARY ===")
for name, ok, exp, got, _ in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}  expected {exp} got {got}")
failed = [x for x in results if not x[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} scenarios passed")
sys.exit(1 if failed else 0)
