# Create 3 mock supplier records

## Context

The user wants 3 additional sample suppliers added to the `suppliers` collection (built in MVP7) for testing purposes — e.g. so PR/PO flows have realistic "Suggested supplier" options beyond the single existing record ("Alpha Control N.V." / "Agrofix", Suriname/SRD).

## Schema reference (`suppliers`, collection key `a4ogom91smz`)

- `name` (input, **required**, title field, must be unique)
- `display_name` (input)
- `tax_id` (input)
- `email` (email)
- `phone` (input)
- `address` (textarea)
- `country` (select: NL / SR / US / DE / GB / BE / other)
- `default_currency` (select: USD / SRD / EUR)
- `payment_terms` (select: Net30 / Net60 / Net90 / COD / Prepayment)
- `status` (select: active / inactive / blocked — default `active`)
- `current_rating` (number 1–5, manual per D6; can be left unset = unrated)
- `notes` (textarea)

## Intended changes — 3 new records in `suppliers`

| Field | Supplier 1 | Supplier 2 | Supplier 3 |
|---|---|---|---|
| name | Stena Marine Supplies B.V. | Paramaribo Fuel & Lubricants N.V. | Atlantic Safety Equipment Inc. |
| display_name | Stena Marine | ParboFuel | Atlantic Safety |
| tax_id | NL-MS-88341 | SR-PFL-55210 | US-ASE-77342 |
| email | sales@stenamarine.nl | orders@parbofuel.sr | info@atlanticsafety.com |
| phone | +31 10 4567890 | +597 421100 | +1 305 555 0192 |
| address | Waalhaven Oz 17, 3087 BL Rotterdam, Netherlands | Industrieweg 22, Paramaribo, Suriname | 1420 Port Blvd, Miami, FL 33132, USA |
| country | NL | SR | US |
| default_currency | EUR | SRD | USD |
| payment_terms | Net60 | Net30 | Prepayment |
| status | active | active | active |
| current_rating | 4 | 5 | *(unset — unrated)* |
| notes | Marine hardware, ropes, deck equipment. Reliable EU shipping. | Local fuel and lubricant supplier for port vehicles and generators. | New supplier — PPE, life vests, safety signage. Awaiting first rating. |

## How it will be created

Plain data records — no schema/collection/workflow/ACL changes. Created via:

```
nb api resource create --resource suppliers --values '{...}'
```

run 3 times (one per row above), using the live `havenbeheer` env.

## Expected UI result

The Suppliers page (`gbg516xq3ie`) table will show 4 suppliers total: the existing "Alpha Control N.V." plus these 3 new ones, each with their display name, country, currency, payment terms, status and rating visible per the existing column layout.

## Verification

After creation, run a read-only `nb api resource list --resource suppliers` to confirm all 4 records exist with the expected field values, and spot-check the Suppliers page in the browser if convenient.

## Notes

- This is easily reversible (records can be deleted via the UI or `nb api resource destroy`), so no special rollback plan beyond "delete the 3 new records by id if needed."
- No `project_current_state.md` update needed — mock data doesn't change collection/field structure. No commit needed (data-only change, not config).
