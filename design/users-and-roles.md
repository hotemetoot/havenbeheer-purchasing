# Users and Roles

**Reference.** For full role/permission mechanics see [havenbeheer PR — permissions and guards.md](../Planning%20and%20Design/havenbeheer%20PR%20—%20permissions%20and%20guards.md). For live test users and dept IDs see [project_current_state.md](../project_current_state.md).

## Roles

| Role | Who | Typical actions |
|---|---|---|
| `member` | every user (base role, D21+D25 design) | submit / edit own draft PRs; comment; log supplier issues; view suppliers |
| Dept owner (via `main_approver` field, not a role) | the user on `departments.main_approver` | approve / return / reject PRs at the Dept stage; edit PR content while in their queue (D16) |
| `procurement` | Procurement staff (Pat) | review approved Dept PRs; fill quote fields; generate POs; manage suppliers (D6, D8); **cannot submit PRs** (D25) |
| `director` | Director (Dana) | approve / return / reject final stage when `needs_director_approval` is true (D23) |
| Finance head (via dept `main_approver` on Finance) | Finance staff | receives in-app notifications for zone-2 budget overruns (D12, D19) |

## Dept routing (D21)

Routing uses `departments.main_approver` (m2o → users) with `users.on_leave` (boolean) controlling fallback to `secondary_approver`. **Never** use `department.owners[]` — that approach was deprecated.

## Test users

See [project_current_state.md](../project_current_state.md) "Test users" for usernames + IDs.
