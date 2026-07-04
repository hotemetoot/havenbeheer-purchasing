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
| **Department head** | Owner of a department | First approval on requests from their department. Not a separate app role — the system routes the request to the department's owner (or a stand-in the submitter picks). |
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
    before reaching Approved)                             Draft ► Issued ► Sent ►
                                                          Confirmed ► Partially
                                                          Received ► Received ►
                                                          Completed ► Closed
```

The exact route through the approval stages depends on the amount and the type of
purchase — see [Stage 2](#stage-2--approval-ladder-dept-procurement-director-board).

---

## 3. Status reference

Every PR and PO shows a colored status tag. Here is what each one means.

### Purchase Request status

| Status | Meaning |
|---|---|
| **Pending Dept Approval** | The status a request starts in. Waiting for the department head (or chosen stand-in) to approve. |
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
| **Issued** | Locked in and ready to send to the supplier. |
| **Sent** | Sent to the supplier. |
| **Confirmed** | Supplier has confirmed the order. |
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

This is where every purchase starts. You describe what you need, attach a quote, and
create the request. **Creating it submits it** — there is no separate draft step, so
fill it in completely before you save.

### Create the request

Open **Purchase Requests** and start a new one. Fill in:

- **Title** — a short name for the request.
- **Description** — what you want to buy.
- **Justification** — why it is needed.
- **Department** — the department the purchase is for. This decides who does the first
  approval.
- **Needed by** — the date you need it.
- **Is emergency** — tick if this is urgent.
- **Expenditure type** — the kind of spend.
- **Suggested Supplier** — the supplier you propose (chosen from the supplier list).

### Add the quote and amount

- **Quoted Total** — the price from the supplier's quote.
- **Quoted Currency** — the currency of that price.
- **FX Rate to USD** — the exchange rate to US dollars. Enter the rate as **local
  currency per 1 USD**. The system fills in **Quoted Total (USD)** for you from this
  rate — you do not type the USD figure yourself. The USD figure is what decides the
  approval route, so the rate matters.
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

_(Draft — to be expanded.)_ The submitted request climbs an approval ladder. Each
approver can **approve** it (send it up), **request more information** (send it back to
the submitter), or **reject** it. The route depends on the amount and whether
Procurement marks it a regular purchase:

- Every request starts with **department approval**, then **Procurement review**.
- **Regular purchases under USD 300** can finish at Procurement (no Director needed).
- Larger or non-routine requests also need **Director approval**.
- Requests of **USD 15,000 and above** additionally need **Board approval**, with a
  signed board document uploaded before final approval.

_To write: exact button labels for each action; who the board approver is; how
"Info Requested" comes back to the submitter; how the regular-purchase flag is set._

---

## Stage 3 — Create the purchase order
**Responsible role: Procurement**

_(Draft — to be expanded.)_ Once a request is **Approved**, Procurement generates a
**Purchase Order** from it and adds the order lines (products, quantities, prices).

_To write: the Generate-PO action; adding PO lines; the budget cap at the Issue gate._

---

## Stage 4 — Issue and send the order
**Responsible role: Procurement**

_(Draft — to be expanded.)_ Procurement issues the order (locking it), sends it to the
supplier, and records the supplier's confirmation.

_To write: Issue / Send / Confirm actions and what each locks._

---

## Stage 5 — Receive the goods
**Responsible role: Procurement (warehouse in future)**

_(Draft — to be expanded.)_ As goods arrive, the received quantity is recorded per
line. The order moves to **Partially Received** and then **Received**.

_To write: entering received quantity per line; how line and order status update._

---

## Stage 6 — Complete, invoice, and close
**Responsible roles: Procurement, Finance**

_(Draft — to be expanded.)_ The order is completed with an invoice total, Finance
records payment details, and the order is closed.

_To write: the Complete action and its invoice/USD requirement; the Close action;
Finance's payment fields; what becomes locked._

---

## Stage 7 — Print the purchase order
**Responsible role: Procurement**

_(Draft — to be expanded.)_ A branded PO can be printed to PDF for the supplier.

_To write: the Print action and what the PDF contains._

---

## Appendix — Suppliers
**Responsible role: Procurement**

_(Draft — to be expanded.)_ Suppliers are kept in their own list and chosen on
requests and orders.

_To write: the supplier list and fields._
```
