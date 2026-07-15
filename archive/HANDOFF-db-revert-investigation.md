# HANDOFF — Havenbeheer live DB reverted ~3 weeks; July data found in iCloud

**Written 2026-07-14 for a fresh agent (Fable) to verify and execute recovery. You start cold — re-verify every claim below with the commands given before acting. Do not trust; check.**

Author's note: the diagnosis below is essentially complete. Your job is to (1) independently confirm it, (2) execute the recovery safely, (3) make the recurrence-prevention change. **Do not do destructive or irreversible actions without Alexander's explicit go-ahead** (see Safety).

---

## TL;DR

- The live Havenbeheer NocoBase DB (`nb env havenbeheer`, http://localhost:13000) is a **stale June-25-2026 snapshot**. Roughly **decisions D52/D53 (Jun 27–28) through D74 (Jul 8)** — ~20 decisions of committed, test-verified work — are **not in it**.
- **Cause:** there are **two `nocobase` trees**. The real working tree is in **iCloud** and is current; the local `~/nocobase` is a stale June-25 copy, and today's containers were started against the stale local one. **iCloud sync**, not any manual action by Alexander, caused the divergence.
- **The July data is NOT lost.** It survives, fully downloaded, at:
  `~/Library/Mobile Documents/com~apple~CloudDocs/TTGA/nocobase/storage/db/postgres` (Postgres data dir, written through **July 8**, 95 MB, 2109 files, 0 iCloud placeholders).
- **`decisions.md` is CORRECT** (it records real work). The DATABASE is what's wrong. **Do NOT "reconcile" decisions.md down to the stale live state** — that would discard real work.

---

## Impact / what's at stake

`decisions.md` D1–D75 is the project's decision log. A drift audit found D63–D73 reference live workflow/ACL objects (real snowflake IDs) that **do not exist** in the current DB, and enum/field changes that aren't applied. The current DB is what an unaware session would build on — so any further build work risks compounding on a 3-week-old base. Recovery must happen before normal work resumes.

---

## How the current (stale) live state was confirmed — re-verify these

Environment: `nb env havenbeheer` is current (`nb env list` shows `*` on havenbeheer, :13000, beta.47). Containers: `nocobase-app-1` (:13000, created Jun 9), `nocobase-postgres-1` (created **today** Jul 14 — a `compose up` recreated it), `nocobase-postgres-1` binds `/Users/alexander/nocobase/storage/db/postgres`.

Direct Postgres proof of staleness (bypasses the nb API layer):
```
podman exec nocobase-postgres-1 psql -U nocobase -d nocobase -tA -c \
  "SELECT to_char(\"createdAt\",'YYYY-MM-DD') d, key, title FROM workflows ORDER BY \"createdAt\" DESC LIMIT 6;"
# => newest before today is 2026-06-25; nothing from Jun 26–Jul 13.

podman exec nocobase-postgres-1 psql -U nocobase -d nocobase -tA -c \
  "SELECT key,title FROM workflows WHERE key IN ('px2xvjaxoqf','2h75zryz3cb','v61hc3ou3pa');"
# => 0 rows. These July decision workflows (D64/D63/D56) were never created here.
```
Filesystem proof: in `/Users/alexander/nocobase/storage/db/postgres/base/16384`, table-file mtimes cluster May–Jun 25 then jump to Jul 14 (today), with a clean gap Jun 26 – Jul 13. The cluster itself is original (PG_VERSION May 8), so it was never re-initialized.

Spot-checks that matched the "June" era (all should be re-confirmable): PR `status` enum still has `draft`/`cancelled` (pre-D68); `projects.status` still `closed` not `completed` (pre-D67); `purchase_orders.budget_override_comment` still present (D74 not applied); director role still has the old 5-field unscoped PR `update` + a stray `create` (pre-D55/D57/D58); procurement still has PO `destroy` (pre-D56); operations PR-update scope points at dead-table row 2 (pre-D72). One thing that IS newer than June 25: `purchase_orders.status` enum trimmed to 6 values + receive-guard revision `375488013926400` — that's **today's D75 edit**, applied on top of the stale base. It will be dropped by the recovery; that's fine (documented in D75, and D69's changes are likely already in the July DB).

---

## Root cause — the two trees

- **Stale local:** `/Users/alexander/nocobase/` — `storage/db/postgres` last real write **June 25** (plus today). This is what the running containers use. `~/nocobase` is a plain directory, **not** a symlink.
- **Real working tree (iCloud):** `/Users/alexander/Library/Mobile Documents/com~apple~CloudDocs/TTGA/nocobase/` — a full nocobase tree (its own `storage/`, `projects/agrofix`, etc.). Its `storage/db/postgres/base/16384` write histogram:
  ```
  find "<iCloud>/storage/db/postgres/base/16384" -type f -exec stat -f '%Sm' -t '%Y-%m-%d' {} \; | sort | uniq -c
  #  ... 31 Jun-27  31 Jun-28  20 Jul-02  42 Jul-04  167 Jul-05  2 Jul-07  21 Jul-08
  ```
  Fully downloaded: `du -sh` = 95M, `find -name '*.icloud' | wc -l` = **0** placeholders.

Almost certainly the July sessions ran `podman-compose` from the **iCloud** tree (its `./storage` = iCloud storage), so July writes landed there; today things were started from `~/nocobase` (stale). iCloud keeping the newer version while the local copy shows June-25 is the classic iCloud version-divergence behavior — hence "nothing manual." **Confirm the exact mechanism** (see Open questions) but it does not block recovery.

---

## RECOVERY — proposed procedure (get Alexander's go-ahead per step; snapshot before any overwrite)

Goal: make the **July-8 iCloud DB** the canonical live database, then move the working tree **out of iCloud** so this can't recur.

1. **Stop the running stack** so nothing writes further to the stale DB: `podman stop nocobase-app-1 nocobase-postgres-1`. (The app has already written today's D75 edit to the stale DB; stopping prevents more divergence.)
2. **Snapshot BOTH data dirs to a safe local path** (outside iCloud, outside `~/nocobase`), preserving perms/mtimes:
   - `cp -a /Users/alexander/nocobase/storage/db/postgres  ~/nocobase-recovery/stale-june25-postgres`
   - `cp -a "<iCloud>/storage/db/postgres"  ~/nocobase-recovery/july08-postgres`
   Verify counts/sizes match the source. **Never run Postgres directly against the iCloud path** — iCloud may evict/modify files mid-run and corrupt it. Always work on the local copy.
3. **Verify the July copy actually contains the July work** before trusting it: bring up a **throwaway** Postgres 16 container bound to `~/nocobase-recovery/july08-postgres` on a spare port, then:
   ```
   psql ... -c "SELECT key,title FROM workflows WHERE key IN ('px2xvjaxoqf','2h75zryz3cb','v61hc3ou3pa');"   # expect 3 rows now
   psql ... -c "SELECT count(*) FROM workflows;"                                                              # expect > 80
   # spot-check ACL/enum: director create action gone, projects.status has 'completed', PO budget_override_comment absent
   ```
   If these show the July state, the recovery source is good. Tear down the throwaway container (do not prune volumes/images).
4. **Cut over.** Decide the canonical location WITH Alexander (recommend a **local, non-iCloud** path, e.g. `~/nocobase` itself or `~/nocobase-live`). Put the verified July-8 `postgres` dir there, point the compose/bind mount at it, `compose up`, and confirm via `nb env havenbeheer` reads that the July state is live.
5. **Re-apply only what's newer than July 8:** D75 (today) and anything from the Step-7 July-6 session not captured by July-8 mtimes. Cross-check `decisions.md` D75 and the Jul-6 commit `e631161`. This is a small tail, if anything.
6. **Recurrence prevention (do this, or it happens again):** move the canonical nocobase working tree **out of iCloud Drive** entirely. A live Postgres data directory must never live in an iCloud-synced folder. Keep `.nbdata` logical backups in iCloud if desired, but not the running data dir. Update `notes.md`/`CLAUDE.md` with the canonical local path.

Fallback if the iCloud copy fails verification: newest logical backup is `~/Downloads/backup_20260702_083314_5207.nbdata` (beta.47 = Havenbeheer, Jul 2, covers ~through D54) → `nb backup restore`, then re-apply D55–D74 from `decisions.md` (detailed, but ~20 entries of manual work — the iCloud path avoids this).

---

## Safety constraints (hard)

- **Read-only until the plan is agreed.** No writes to any live config until Alexander approves the cutover.
- **Snapshot before any overwrite.** Both the stale and July dirs, to a safe local path.
- **Do NOT** `podman system prune`, `podman volume prune`, `podman machine reset/rm`, or delete containers/images — a removed container's overlay or a dangling store could be a secondary copy; don't destroy anything until the July DB is confirmed restored.
- **Do NOT run Postgres against files inside iCloud.** Copy out first.
- **Do NOT edit `decisions.md` to match the stale DB.** The log is the source of truth for what the DB *should* contain.
- Per `CLAUDE.md`: auth 401/403 → hand to `nocobase-env-manage`. Env/container recovery is that skill's territory; use it for the cutover mechanics.

---

## Open questions for the investigation

1. Exact sync mechanism: was `podman-compose` run from the iCloud tree during July (check shell history / any launcher script / the July container's `com.docker.compose.project.working_dir` label if any removed-container metadata survives)? Confirm whether `~/nocobase` was ever a symlink into iCloud.
2. Is the July-8 iCloud state the very latest, or is there anything newer in another iCloud copy (there's also `.../TTGA/nocobase/projects/agrofix` and possibly others)? Check for the newest `base/16384` mtime across all `TTGA/nocobase*` copies.
3. Does the July-8 DB already contain D69 and D74 (PO `sent`/`confirmed` removal; `budget_override_comment` drop)? If yes, D75's premise ("D69 was never applied") was itself a symptom of the revert — note it so D75's framing gets corrected after recovery.

---

## Key paths / IDs reference

- Stale local data dir (running): `/Users/alexander/nocobase/storage/db/postgres`
- **Recovery source (iCloud, July 8):** `/Users/alexander/Library/Mobile Documents/com~apple~CloudDocs/TTGA/nocobase/storage/db/postgres`
- Compose (stale): `/Users/alexander/nocobase/docker-compose.yml` (project name `nocobase`; DB `nocobase`/user `nocobase`)
- Containers: `nocobase-app-1`, `nocobase-postgres-1`; VM: `podman-machine-default` (libkrun); no podman volumes (all bind mounts)
- Logical backups: `~/Downloads/*.nbdata`, `~/nocobase/storage/backups/main/*.nbdata` (newest Havenbeheer = Jun 24), iCloud `TTGA/Havenbeheer/*.nbdata` (newest = Jun 27), `~/Downloads/backup_20260702_083314_5207.nbdata` (Jul 2)
- Decision log: `decisions.md` (D52–D74 are the missing range); this project's memory file `project_db_reverted_june25.md` mirrors this summary.
