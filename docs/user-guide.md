# Havenbeheer Purchasing — User Guide

How to raise, approve, and fulfil a purchase in the Havenbeheer Purchasing system.

This guide follows one purchase from start to finish. Each stage is marked with the
role responsible for it, so you can jump to the parts that apply to you. The status
names and field labels here match what the app actually shows on screen.

> **Scope.** This guide covers the features that are live and verified today. Two
> areas are built but not yet documented here: **Projects & budget drawdown** and
> **bulk PO line import**. They will be added once verified.

> **No draft stage.** A purchase request is not saved as a draft first. The moment
> you create it, it is submitted and enters the approval flow. There is no "save for
> later" and no way to cancel a request once it exists — only an approver can return
> or reject it.

---

## 1. Who does what

The system has five kinds of user. Everyone is a **Member** first (the base account);
the roles below add specific rights on top.

| Role | Who they are | What they do here |
|---|---|---|
| **Operations** | Staff who need to buy something | Create purchase requests. Creating one submits it straight into approval. |
| **Department head** | Owner of a department | First approval on requests from their department. Not a separate app role — the system routes the request to the department's owner (or a **Custom approver** the submitter picks). |
| **Procurement** | The purchasing team | Second review of every request; turn approved requests into purchase orders; run the order through to receiving and closing. |
| **Director** | The director | Approval for larger or non-routine requests. |
| **Board** | The board | Final sign-off on the largest requests (USD 15,000 and above), with a signed document on file. |
| **Finance** | The finance team | Payment details on purchase orders. |

A single request can touch several of these people in sequence. The next sections
show exactly when each one is involved.

---

## 2. The lifecycle at a glance

A purchase moves through two linked records:

1. A **Purchase Request (PR)** — what someone wants to buy and why. It is reviewed
   and approved (or returned, or rejected).
2. A **Purchase Order (PO)** — created by Procurement from an approved PR. It is
   issued to a supplier, received, and closed.

```
  PURCHASE REQUEST                                    PURCHASE ORDER
  ────────────────                                    ──────────────
  (created — goes straight in)
    │
    ▼
  Pending Dept Approval ──► Pending Purchasing Review ──► Pending Director Approval
    │                              │                            │
    │  (any stage can send it back to "Info Requested" or "Rejected")
    ▼                              ▼                            ▼
                         ┌──────────────────────────────────────┐
                         │            Approved                   │──► Procurement
                         └──────────────────────────────────────┘    creates a PO
                                                                       │
   (requests of USD 15,000+ also pass Pending Board Approval           ▼
    before reaching Approved)                             Draft ► Issued ►
                                                          Partially Received ►
                                                          Received ► Completed ►
                                                          Closed
```

The exact route through the approval stages depends on the amount and the type of
purchase — see [Stage 2](#stage-2--approval-ladder-dept-procurement-director-board).

---

## 3. Status reference

Every PR and PO shows a colored status tag. Here is what each one means.

### Purchase Request status

| Status | Meaning |
|---|---|
| **Pending Dept Approval** | The status a request starts in. Waiting for the department head (or the chosen **Custom approver**) to approve. |
| **Pending Purchasing Review** | Waiting for Procurement to review. |
| **Pending Director Approval** | Waiting for the Director. |
| **Pending Board Approval** | Waiting for the Board (requests of USD 15,000+). |
| **Info Requested** | An approver asked the submitter for more information. Back with the submitter, who can edit and resubmit. |
| **Approved** | Fully approved. Procurement can now create a purchase order. |
| **Rejected** | Turned down. Final. |

### Purchase Order status

| Status | Meaning |
|---|---|
| **Draft** | Just created from the PR. Being prepared by Procurement. |
| **Issued** | Locked in and issued to the supplier. This is the point the order goes out. |
| **Partially Received** | Some ordered lines have arrived, not all. |
| **Received** | Everything ordered has arrived. |
| **Completed** | Order finished and invoiced. |
| **Closed** | Order closed out. Final. |

### PO line status

Each line on a purchase order tracks its own delivery:

| Status | Meaning |
|---|---|
| **Pending** | Nothing received yet. |
| **Partially Received** | Part of the ordered quantity has arrived. |
| **Received** | The full ordered quantity has arrived. |

---

## Stage 1 — Create and submit a purchase request
**Responsible role: Operations (the submitter)**

This is where every purchase starts. You describe what you need and create the request.
**Creating it submits it** — there is no separate draft step, so get the details right
before you save.

The form marks **required** fields with a red asterisk (*). You cannot save until those
are filled; everything else is optional. Some fields also become required only in certain
situations, and the form shows this as you go — for example, once you enter a quoted
price the exchange rate is needed to convert it.

### Create the request

Open **Purchase Requests** and start a new one. The main fields:

- **Title** — a short name for the request.
- **Description** — what you want to buy.
- **Justification** — why it is needed.
- **Department** — the department the purchase is for. This decides who does the first
  approval.
- **Needed by** — the date you need it.
- **Is emergency** — tick if this is urgent.
- **Expenditure type** — the kind of spend.

### Supplier and quote (optional)

You do **not** have to name a supplier or attach a quote to raise a request. Often you
know what you need but not who to buy it from. In that case leave these blank — Procurement
sources a supplier and requests quotes later. Fill them in only when you already have them:

- **Suggested Supplier** — the supplier you propose (chosen from the supplier list).
- **Quoted Total** — the price from the supplier's quote.
- **Quoted Currency** — the currency of that price.
- **FX Rate to USD** — the exchange rate to US dollars. Enter the rate as **local
  currency per 1 USD**. The system fills in **Quoted Total (USD)** for you from this
  rate — you do not type the USD figure yourself. The USD figure is what decides the
  approval route, so if you do enter a price, the rate matters.
- **Quotation Attachment** — upload the supplier's quote.
- **Other attachments** — any supporting files.

> The **PR Number** is assigned automatically. You do not set it.

### Choose a different first approver (optional)

By default the request goes to your department's head for the first approval. If you
need someone else in the department to approve it instead:

- Tick **Use custom approver**.
- Pick the person in **Custom approver**.

The department head is notified either way, so they stay in the loop.

### Save — the request is now submitted

When you save the request, it is created directly at **Pending Dept Approval** and
moves to the first approver. There is no draft to hold it back and no submit button to
press separately — saving *is* submitting.

Once the request exists you can no longer edit it or withdraw it. If you need changes,
an approver has to return it to you (**Info Requested**) or reject it. So check the
details before you save.

---

## Stage 2 — Approval ladder (dept → procurement → director → board)
**Responsible roles: Department head, Procurement, Director, Board**

Once a request is submitted it climbs an approval ladder. It always starts with the
**department head**, then goes to **Procurement**. From there it may stop, or continue to
the **Director**, and for the largest requests to the **Board**. How far it climbs
depends on the amount and on whether Procurement marks it a regular purchase — the rules
are in [2.2](#22--procurement-review--and-the-regular-purchase-flag) and
[2.3](#23--director-approval).

### The three actions every approver has

Wherever you sit on the ladder, you act on a request the same way. You open it and choose
one of three buttons:

| Action | What it does | Where the request goes |
|---|---|---|
| **Approve** | Accepts the request at your stage. | Up to the next stage — or to **Approved** if you are the last approver. |
| **Return** | Sends it back to the submitter for changes. Add a comment saying what you need. | Back to the submitter as **Info Requested**. |
| **Reject** | Turns the request down for good. Add a reason. | To **Rejected**. This is final — nobody can revive it. |

> 📷 **Screenshot — the approval form with its three buttons.**
> Show a request open in approval, with the **Approve**, **Return**, and **Reject**
> buttons visible. Confirm the exact button labels here match what the app shows.

### Where you find requests waiting for you

When a request reaches your stage, the system creates an **approval task** for you and
notifies you in the app. Open the task to see the full request and the three action
buttons above.

> 📷 **Screenshot — where an approver's waiting tasks appear.**
> Show the place a new approver goes to find requests waiting on them (a to-do / tasks
> list, the notification bell, or the request itself). This is the one part the written
> steps below can't pin down — the screenshot settles where to click.

---

### 2.1 — Department approval (first stage)
**Responsible role: Department head (or the Custom approver the submitter picked)**

Every request lands here first, at status **Pending Dept Approval**. The task goes to the
head of the request's department — for an Operations request that is Oliver, the
Operations department head. If the submitter chose a custom approver in Stage 1, the task
goes to that person instead, and the department head gets an FYI notification so they stay
in the loop.

Open the task and choose an action:

- **Approve** → the request moves to **Pending Purchasing Review** and a task opens for
  Procurement.
- **Return** → the request goes back to the submitter as **Info Requested** (see
  [2.5](#25--when-a-request-is-returned-to-you-submitter)).
- **Reject** → the request is **Rejected** and stops here.

> **One exception — the submitter is the department head.** If Oliver (the Operations
> head) raises his own request, there is no point asking him to approve it. The request
> skips the department stage and starts straight at **Pending Purchasing Review**. No
> department task is created.

> 📷 **Screenshot — a request at Pending Dept Approval, open in the approval form.**
> Show the department head's view: the request details on one side, the Approve / Return
> / Reject buttons on the other.

---

### 2.2 — Procurement review — and the regular-purchase flag
**Responsible role: Procurement (Pat)**

Every request passes through Procurement, at status **Pending Purchasing Review**. This
stage does two things: Procurement reviews the request, and Procurement decides whether
the Director needs to see it.

That decision is made with one checkbox on the Procurement approval form:

- **Is regular** — tick it if this is a routine, everyday purchase.

The rule for whether the Director is needed:

- **Regular *and* under USD 300** → Procurement can approve it outright. Ticking
  **Is regular** and approving takes the request straight to **Approved**. No Director, no
  Board.
- **Everything else** → **Approve** sends it up to **Pending Director Approval**.

Three concrete cases make the rule clear:

- Pat opens Alice's **USD 250** request, ticks **Is regular**, and approves. It goes
  straight to **Approved** — small and routine, no Director needed.
- Pat opens a different **USD 250** request but leaves **Is regular** unticked and
  approves. It still goes to the **Director**. Under USD 300 alone is not enough; it also
  has to be marked regular.
- Pat opens a **USD 5,000** request. The amount is USD 300 or more, so the **Is regular**
  flag makes no difference — approving always sends it to the **Director**.

Procurement can also **Return** the request (→ **Info Requested**) or **Reject** it, the
same as any other approver.

> 📷 **Screenshot — the Procurement approval form showing the Is regular checkbox.**
> Show Pat's view with the **Is regular** checkbox and the Approve button.

---

### 2.3 — Director approval
**Responsible role: Director (Dana)**

A request reaches **Pending Director Approval** when Procurement approved it and it was
not a regular purchase under USD 300. The task goes to the Director, Dana.

Open the task and choose an action:

- **Approve** →
  - if the request is **under USD 15,000**, it goes straight to **Approved** — the ladder
    ends here.
  - if the request is **USD 15,000 or more**, it goes to **Pending Board Approval** for a
    final board sign-off (see [2.4](#24--board-approval-usd-15000-and-above)).
- **Return** → back to the submitter as **Info Requested**.
- **Reject** → **Rejected**, final.

> 📷 **Screenshot — a request at Pending Director Approval, open in the Director's approval form.**

---

### 2.4 — Board approval (USD 15,000 and above)
**Responsible role: Board, recorded by the head of Procurement**

Only the largest requests reach here — **USD 15,000 or more**, after the Director has
approved. Status is **Pending Board Approval**.

The board makes its decision outside the app and signs a document. That signed decision is
then recorded in the system by the **head of Procurement** (Pat), who holds the board task.
Before approving, Pat must upload the signed board document:

- **Board Approval Document** — the board's signed sign-off. This is **required**. Trying
  to **Approve** without it is blocked until a document is attached.

Once the document is attached, **Approve** takes the request to **Approved** — the ladder
ends. Pat can also **Reject** the board task, which sets the request to **Rejected**.

Example: a **USD 20,000** request has cleared the Director. Pat opens the board task and
clicks **Approve** with nothing attached — the system blocks it and asks for the document.
Pat uploads the board's signed PDF and approves again — the request becomes **Approved**
and the document stays on file.

> 📷 **Screenshot — the board task showing the required Board Approval Document upload.**
> Ideally show the blocked-without-document state and the upload field.

---

### 2.5 — When a request is returned to you (submitter)
**Responsible role: Operations (the submitter)**

When any approver clicks **Return**, the request comes back to you at status **Info
Requested**, with the approver's comment saying what they need. This is the *only* time a
submitted request becomes editable again — normally you cannot touch it once it is in the
approval flow.

To move it forward again:

1. Open your request. It is now editable (only while it is **Info Requested**, and only
   your own request).
2. Make the changes the approver asked for.
3. Resubmit. The request returns to **Pending Dept Approval** and climbs the ladder again
   from the start.

Example: Oliver returns Alice's request asking for a clearer quote. Alice's request shows
**Info Requested** with his comment. She opens it, uploads the better quote, and resubmits.
It goes back to **Pending Dept Approval**, and Oliver sees it again.

> 📷 **Screenshot — a submitter's request at Info Requested, showing the approver's comment
> and the request editable again.**

---

### 2.6 — When a request is rejected

If any approver clicks **Reject**, the request becomes **Rejected**. This is final. The
request is locked — the submitter can no longer edit it, and there is no way to reopen or
resubmit it. If the purchase is still needed, raise a new request.

> 📷 **Screenshot — a Rejected request, showing it locked / no edit action for the submitter.**

---

## Stage 3 — Create the purchase order
**Responsible role: Procurement (Pat)**

Once a request is **Approved**, Procurement turns it into a **Purchase Order (PO)**. The
PO is where you record what is actually being ordered — the individual lines, quantities,
and prices — before the order goes to the supplier.

### Generate the PO from the approved request

Open the approved request and click **Generate PO**. This creates one purchase order and
carries these details straight over from the request:

- **Supplier** — copied from the request.
- **Currency** and **FX Rate to USD** — copied from the request.
- **Invoice Total** — set to the request's approved amount. This is the ceiling for the
  order (see the budget rule below).
- **Delivery Address** — set to the default delivery address on file.
- **PO Number** — the request's number with `PR-` changed to `PO-`
  (PR-26-0001 → PO-26-0001).

The new order opens at **Draft**.

> **One PO per request.** Once a request has a purchase order, the **Generate PO** button
> disappears from it — you cannot generate a second one. And you can only generate from an
> **Approved** request: trying it on a request that is still in approval is blocked
> ("You cannot generate a PO for this purchase request").

> 📷 **Screenshot — the Generate PO button on an Approved request.**
> Show an approved request with the **Generate PO** action. Confirm the exact button label.

### Add the order lines

A Draft PO starts with no lines. Open the **Lines** area and add one line per item:

- **Description** — what the line is for (or pick a **Product**).
- **Unit of Measure** — how it is counted (each, box, hour, …).
- **Quantity Ordered** — how many.
- **Unit Price** — price per unit, in the PO's currency.

The system fills in **Line Total** (Quantity Ordered × Unit Price) for you.

While the PO is **Draft** you can freely add, edit, and delete lines. That freedom ends
when you issue the order (Stage 4).

### The budget ceiling — lines can't exceed the approved amount

The lines together may not add up to more than the approved request amount (the PO's
**Invoice Total**). This is checked the moment you add or change a line, so you cannot
save a line that would push the order over budget.

Example: the request was approved for **USD 5,000**. Pat adds lines totalling USD 4,800 —
fine. Pat then adds one more line for USD 400, which would bring the order to USD 5,200.
The system blocks the save: "Adding this line would bring the PO to 5200 USD, over the
approved 5000 USD. Reduce the quantity or unit price." Pat lowers the quantity so the
order stays at or under USD 5,000.

If the order genuinely needs to cost more than approved, the request has to go back
through approval for the higher amount — the PO cannot exceed what was approved.

> 📷 **Screenshot — the add-line form, showing Description, Quantity Ordered, and Unit Price.**
> Show where lines are added on a Draft PO and where the line list appears.

---

## Stage 4 — Issue the order
**Responsible role: Procurement (Pat)**

Issuing is the point the order becomes final and goes to the supplier. There is one action
for it — **Issue PO** — and it does everything: it locks the order and moves it from
**Draft** to **Issued**. There is no separate "send" or "confirm" step.

### What must be ready before you can issue

**Issue PO** runs a set of checks first. If any fails, the order stays at **Draft** and you
get a message saying what is missing:

| Must be true | Message if not |
|---|---|
| The order is still **Draft**, and has a **Supplier**, a **Delivery Address**, a **Currency**, and an **Invoice Total** greater than 0 | "Cannot issue this PO: it needs a supplier, a delivery address, a currency, a total greater than 0, and at least one line." |
| There is **at least one line** | "Cannot issue this PO: add at least one PO line first." |
| **Every line has a Unit Price greater than 0** | "Cannot issue this PO: every line needs a unit price greater than 0." |
| The **line totals do not exceed the approved request amount** | "Cannot issue this PO: line items total … exceeds the approved PR amount …. Reduce the lines or revise the PR before issuing." |

Most of these are already filled in from the request (supplier, currency, delivery
address, invoice total). In practice the two you check yourself are that every line has a
price and that the lines stay within budget.

### What issuing locks

Issuing is the point of no return. The order has gone to the supplier, so from here the
lines are the printed document — and the system keeps them matching it.

Once the order is **Issued**:

- You can no longer **add** a line (the **Import** button disappears).
- You can no longer **delete** a line ("Cannot delete a PO line once the PO has been
  issued.").
- You can no longer **change** a line. Quantity Ordered, Unit Price, Description and
  Line Status are all fixed. Clearing a value counts as changing it. You get:
  *"Once a PO has been issued, its lines can only be updated to record receiving.
  Quantity and unit price are fixed at issue."*
- **Recording deliveries still works** — that is the next stage, and it is the one
  change the order still accepts.

Example: Pat has a Draft PO with two lines, both priced, totalling USD 4,800 against a
USD 5,000 request. Pat clicks **Issue PO**. The order becomes **Issued** and the issue
date is stamped. If Pat had left one line's Unit Price at 0, the click would have been
blocked with the unit-price message instead.

A week later the supplier says one item now costs more. Pat cannot edit the line — the
supplier is holding a PO that says otherwise. The way through is to **Close** this order
and generate a new one from a new request. If it is a genuine mistake rather than a price
change, an administrator can still correct the line.

> 📷 **Screenshot — the Issue PO button on a Draft order.**
> Show the **Issue PO** action. Confirm the exact button label and, if easy, capture one
> of the blocked messages above.

---

## Stage 5 — Receive the goods
**Responsible role: Procurement (a warehouse role in future)**

As the ordered goods arrive, record what came in against each line. You do this by setting
the **Received Quantity** on the line — the statuses update themselves from there.

### Record what arrived

On each line of an **Issued** order, set **Received Quantity** to how many have arrived so
far. The line's own status follows automatically:

| Received Quantity | Line Status |
|---|---|
| None yet | **Pending** |
| Some, but less than ordered | **Partially Received** |
| Equal to (or more than) ordered | **Received** |

The whole order's status follows the lines:

- If any line has something received but not everything is in, the order is **Partially
  Received**.
- When every line is fully **Received**, the order becomes **Received**.

### The "ready to complete" nudge

The moment the last line is fully received and the order flips to **Received**,
Procurement gets an in-app notification: "PO … is fully received and ready to complete."
That is the cue to move to Stage 6.

Example: a line ordered **10** units. Ten arrive in two deliveries. Pat first sets
**Received Quantity = 4** — the line shows **Partially Received** and the order shows
**Partially Received**. When the rest arrive Pat sets **Received Quantity = 10** — the
line shows **Received**, the order shows **Received**, and the "ready to complete"
notification appears.

> 📷 **Screenshot — a PO line with the Received Quantity field.**
> Show where **Received Quantity** is entered on a line.

> 📷 **Screenshot — where the "ready to complete" notification appears.**
> Show the place Procurement sees the notification (the notification bell / in-app
> message). This is the one thing the written steps can't pin down.

---

## Stage 6 — Complete, invoice, and close
**Responsible roles: Procurement, Finance**

A received order is finished off in one of two ways: **completed** (the normal ending,
with an invoice) or **closed** (an early exit when the order will not be completed).

### Complete the order (the normal ending)

When the order is **Received** and the supplier's invoice is in, complete it:

1. Attach the supplier's invoice in **Invoice**.
2. Set the **Invoice Total** (the amount actually invoiced) and make sure the **Currency**
   and **FX Rate to USD** are right — the system works out **Invoice Total (USD)** from
   them, and that USD figure must be greater than 0.
3. Click **Complete**.

The order moves to **Completed** and the completion date is stamped.

Two things are checked, each with its own message:

- No invoice attached → "An invoice attachment is required to complete this PO."
- Not fully received, or the USD total is 0 → "Complete is only available for a
  fully-received PO with an invoice total (USD)."

### Finance records payment

Payment details on the order are Finance's part. Finance records the **Payment Date** once
the supplier has been paid.

### Close the order (the early exit)

**Close** ends an order that will not run to completion — for example a supplier who
cannot deliver, or a duplicate order. Click **Close**, pick a **Close Reason**, and submit.
The order moves to **Closed** and the close date is stamped.

Close is only allowed while the order is **Draft**, **Issued**, or **Partially Received**.
It is deliberately blocked once the order is **Received**: "This PO cannot be closed in
its current status — only draft, issued, or partially-received POs can be closed. A
received PO should be completed; to bail out, correct a received line down to revert it to
partially-received first." In other words, a fully received order should be **completed**,
not closed.

### Completed and closed orders are locked

Once an order is **Completed** or **Closed** it is final. Nobody can edit the order header
("This PO is finalized and can no longer be edited.") or its lines ("Lines of a finalized
PO can no longer be edited.").

> 📷 **Screenshot — the Complete action with the Invoice attachment and Invoice Total fields.**
> Show the **Complete** button and the invoice fields it requires.

> 📷 **Screenshot — the Close form showing the Close Reason field.**
> Show the **Close** action and the **Close Reason** picker.

---

## Stage 7 — Print the purchase order
**Responsible role: Procurement**

A purchase order can be printed — for example to send or file a copy for the supplier. The
print action sits on the purchase order record.

> 📷 **Screenshot — the Print action on a purchase order, and the printed result.**
> Show the **Print** action on the PO and what it produces. Confirm the exact button label
> and whether it prints a branded PO layout or the plain record view — this decides how the
> paragraph above should read.

---

## Appendix — Suppliers
**Responsible role: Procurement**

_(Draft — to be expanded.)_ Suppliers are kept in their own list and chosen on
requests and orders.

_To write: the supplier list and fields._
```
