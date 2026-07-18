# Demo 2 — PO workflow + Project (budget) workflow

A step-by-step script for the person giving the demo. Follow it top to bottom.
Every step says **who logs in**, **what to click**, and **what you should see**.

---

## Before you start (do this once, not in front of the audience)

**Logins** (all use password `nbtest`):

| Role in the demo | Login email |
|---|---|
| Owner | `oliver@havenbeheer.test` |
| Procurement | `pat@havenbeheer.test` |
| Director | `dana@havenbeheer.test` |
| Finance (optional) | `fiona@havenbeheer.test` |

To switch person: log out, log back in as the next email. Same password for all.

**Pre-stage one approved request for Demo A.** Demo A starts from a purchase request
that is already **Approved**. Have one ready before the session (Alexander can set this
up, or run a request through as Pat → Dana beforehand). You want to open the demo at
"Generate PO", not spend it clicking through approvals again — that was Demo 1.

> **Dry-run tip:** click through *both* approval chains once before the real demo (approve
> one project and one request end to end). This confirms the approve buttons work on the
> current workflow versions. It takes 10 minutes and removes the only real risk in this demo.

---

## Demo A — The Purchase Order lifecycle

The story: a request has been approved. Procurement now turns it into a real order,
sends it, receives the goods, and closes it out. **There is no separate "Send" step** — the
order goes out when you **Issue** it.

### A1. Generate the order — *log in as Pat (Procurement)*

1. Open the approved purchase request.
2. Click **Generate PO**.
3. **You should see:** a new purchase order opens at status **Draft**. Supplier, currency,
   FX rate, and the approved amount (**Invoice Total**) are already filled in from the request.
   The PO number mirrors the request (PR-26-0001 → PO-26-0001).

*Talking point:* one order per request — the **Generate PO** button disappears afterwards.

### A2. Add the order lines — *still Pat*

1. In the **Lines** area, add a line: fill **Description**, **Unit of Measure**,
   **Quantity Ordered**, **Unit Price**.
2. **You should see:** **Line Total** fills in automatically (quantity × unit price).
3. Add a second line the same way.

*Show the budget rule:* try to add a line that pushes the order total **over** the approved
amount. **You should see** the save blocked with a message like:
"Adding this line would bring the PO to 5200 USD, over the approved 5000 USD…". Lower the
quantity so it fits, then save. → **The order can never cost more than what was approved.**

### A3. Issue the order — *still Pat*

1. Click **Issue PO**.
2. **You should see:** the order moves **Draft → Issued** and the issue date is stamped.
3. Aftes issuuing the PO, click the Print button and wait for the PO documment to be generated. Optionally you can add a supplier note first that will show up on the PO pdf.

*Show a guard (optional):* before issuing, set one line's **Unit Price** to 0 and click
**Issue PO** — it's blocked ("…every line needs a unit price greater than 0."). Fix the
price and issue for real.

*Talking point:* once **Issued**, lines can no longer be deleted. The order is now final
and considered sent to the supplier.

### A4. Receive the goods — *still Pat*

1. On a line, set **Received Quantity** to fewer than were ordered (e.g. 4 of 10).
2. **You should see:** that line shows **Partially Received**, and the whole order shows
   **Partially Received**.
3. Now set **Received Quantity** to the full amount (10 of 10). You can also click the reveive link to instantly receive the full quantity.
4. **You should see:** the line shows **Received**, the order shows **Received**, and
   Procurement gets an in-app notification: "…is fully received and ready to complete."

### A5. Complete the order — *still Pat*

1. Attach the supplier invoice in **Invoice**. 
2. Check **Invoice Total**, **Currency**, and **FX Rate to USD** are right.
3. Click **Complete**.
4. **You should see:** the order moves to **Completed** and the completion date is stamped.

*Show a guard (optional):* click **Complete** with no invoice attached first — it's blocked
("An invoice attachment is required to complete this PO.").

*Alternative ending — Close:* instead of completing, an order that will not run to the end
(e.g. supplier can't deliver) is ended with **Close** → pick a **Close Reason** → submit.
Note: **Close** is only allowed while the order is Draft, Issued, or Partially Received — a
fully received order must be **Completed**, not closed.

### A6. Finance records payment (optional) — *log in as Fiona (Finance)*

1. Open the completed order and set the **Payment Date**.
2. **You should see:** the payment date saved. (Payment is Finance's part of the record.)

### A7. Print the order — *log in as Pat*

1. On the purchase order, click **Print**.
2. **You should see:** a branded Havenbeheer PO produced as a PDF.

**Demo A done.** A request became an order, the order was priced within budget, issued,
received, completed, and printed.

---

## Demo B — Projects and budget drawdown

The story: instead of approving every purchase one by one, the organisation approves a
**budget envelope** once (a "project"). After that, Procurement can raise several requests
against it **without** going back to the Director each time — but the requests can never add
up to more than the approved budget.

Find projects under the left menu: **Purchasing → Projects**.

### B1. Create the budget envelope — *log in as Oliver (Requester)*

1. Go to **Purchasing → Projects** and click **Add new**.
2. Fill in:
   - **Title** — e.g. "Repair north quay".
   - **Description** — short scope (required).
   - **Budget (USD)** — the envelope, e.g. **10000** (required).
   - **Justification** — why (required).
   - **Attachments** — optional.
3. Click **Submit**.
4. **You should see:** the project is created and enters approval automatically (its status
   moves off Draft into the approval ladder).

*Note:* keep this first project **under USD 15,000** so it doesn't need Board approval —
that keeps the demo short. (At 15,000 and above, an extra **Board Approval** stage appears
and requires a signed document.)

### B2. Approve the envelope — *Procurement, then Director*

The project runs through the same kind of ladder as a request. Because Oliver is the head
of his own department, the **department** step is skipped automatically — the project goes
straight to Procurement.

1. **Log in as Pat (Procurement).** Open the project's approval task, click **Approve**.
   → It moves to the Director.
2. **Log in as Dana (Director).** Open the task, click **Approve**.
3. **You should see:** the project status becomes **Approved**. The envelope is now live.

*Talking point:* each stage also has **Return** (send back for more info) and **Reject** —
same three choices as a purchase request.

### B3. Spend against the envelope — *log in as Oliver*

1. Create a new purchase request as normal.
2. In the **Project** field, pick the project you just approved.
3. Set the request amount to **less than the budget** (e.g. USD 4,000 against the 10,000
   envelope). Submit it.
4. **Log in as Pat (Procurement)** and **Approve** the request.
5. **You should see:** the request becomes **Approved right after Procurement** — it does
   **not** go to the Director. → **This is the whole point: a project-linked request skips
   the Director (and Board). Procurement is the final approver.**

*Show the drawdown:* open the project. Its committed / remaining figures reflect the 4,000
now spent, leaving 6,000 of the 10,000 available.

### B4. Show the budget block — *log in as Oliver*

1. Create another purchase request, pick the **same project**, and set an amount that would
   push the total **over** the budget (e.g. USD 7,000 — that plus the earlier 4,000 = 11,000,
   over the 10,000 envelope).
2. Try to submit.
3. **You should see:** the request is **blocked** with a remaining-budget message (something
   like "Remaining budget: $6,000"). → **The envelope can be split across many requests, but
   the total can never exceed the approved budget.**
4. Lower the amount to fit (e.g. USD 5,000) and submit — now it goes through.

**Demo B done.** One approved budget, several requests drawing on it, the Director bypassed
for each, and a hard stop when the money runs out.

---

## Things to know / caveats

- **No "Close Project" button in the UI yet.** The rule "a closed project blocks new
  requests" exists in the system, but there is currently **no button** on the Projects page
  to close a project. **Do not demo closing a project** — skip it. (If you want it in the
  demo, ask Alexander to wire the button first.)
- **Approval versions are freshly revised and untested live.** Do the 10-minute dry-run in
  the "Before you start" section so the **Approve** buttons don't surprise you on the day.
- **No "Send PO" step** — this is intentional. If someone asks where "send to supplier" is,
  the answer is **Issue PO** does that.
