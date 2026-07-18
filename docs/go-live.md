# Go-live runbook — Havenbeheer Purchasing

Everything between "the app works locally" and "real users work in it at
https://app.ttga.cloud". Written 2026-07-18. One file, four parts, in order:

1. **App readiness** — finish and verify the app locally.
2. **Server rebuild** — wipe the RackNerd VPS, set it up from scratch.
3. **Migration** — move the app from the Mac to the server.
4. **Backups & maintenance** — keep it alive afterwards.

---

## Part 1 — App readiness (local, before anything touches the server)

### 1.1 Build the Complete Project button (the only missing UI piece)

The backend already exists and is verified: the **Complete Project** workflow
(key `px2xvjaxoqf`) sets an approved project to `completed`, stamps
`completed_at`, and rejects any project that isn't approved. Only procurement
can trigger it (rule R27, suite-green). You only build the button:

- **Where:** the project detail (View) page on the Projects page — completing
  is deliberate, so the detail page beats a table row action.
- **Button type:** a one-click **Trigger workflow** button (not a form Submit —
  custom-action workflows only bind to these). In the binding dropdown pick
  the workflow named **Complete Project**.
- **Confirmation:** turn on Secondary confirmation. Suggested text:
  *"Complete this project? No new PRs can draw on it afterwards."*
- **Visibility:** linkage rule — show only when Status is Approved (any other
  status just gets the workflow's rejection message). Optionally also hide it
  for non-procurement users: condition on current user roles *includes*
  "Procurement" (the capitalized display title, not the lowercase role name).
  The server enforces the role either way.
- **After success:** stay on the page with a refresh, so the status badge
  flips to Completed immediately.
- **Self-test:** as Pat on an approved project → confirm → badge reads
  Completed; the button is hidden on a draft project; a new PR linked to the
  completed project is blocked.

### 1.2 Manual verification walkthroughs (you, in the UI)

**A. Projects end-to-end (014.6, cases A1–F2)** — as Alice/Oliver/Pat/Dana:

- [ ] A1 — a < $15k project goes dept → procurement → director → **approved**.
- [ ] A2 — a ≥ $15k project gets the **board stage**, which requires the
      signed-document upload, then approved.
- [ ] A3 — reject and return behave like on a PR, at each stage.
- [ ] A4 — a project submitted by the dept head itself skips the dept stage.
- [ ] B1 — a PR linked to an approved project, ≥ $300, **skips the director**:
      approved right after Procurement.
- [ ] B2 — the same PR *without* a project link still goes to the director
      (regression check).
- [ ] B3 — the dept-owner stage still runs on a project-linked PR.
- [ ] C1–C4 — budget block: PRs under budget pass; a PR pushing the sum over
      budget is blocked with a remaining-budget message; exactly-on-budget
      passes; two PRs that individually fit but jointly exceed → the second
      is blocked.
- [ ] C5 — a PR linked to a non-approved project is blocked.
- [ ] D1/D2 — Complete Project works (see 1.1 self-test) and a completed
      project blocks new PRs.
- [ ] E1/E2 — the project's committed amount tracks approvals immediately and
      drops when a PR is deleted.
- [ ] F1/F2 — every approver can open and submit their project approval form
      without an error; the board upload works.

**B. PO line import (016, cases B1–B8)** — as Pat:

- [ ] B1 — manually adding a line that breaches the PR budget is still
      blocked per-line (regression).
- [ ] B2 — an **over-budget import succeeds** (that's by design), but Issue PO
      is then rejected with the over-budget message; PO stays draft.
- [ ] B3 — a within-budget import → Issue PO succeeds → issued, Print appears.
- [ ] B4 — the Import button is hidden on any non-draft PO.
- [ ] B5 — the Import button is hidden for non-procurement roles.
- [ ] B6 — imported rows attach to the right PO and line totals compute.
- [ ] B8 — **Lines Total updates per imported row** without touching anything
      (this re-tests yesterday's D83 fix — the one item that was broken
      before). `needs_reprint` stays false on a draft PO.
- [ ] B7 — a clean, priced, within-budget draft still issues; incomplete or
      unpriced ones still reject with their existing messages.

**C. Two small leftovers:**

- [ ] Dept-head content edit: while a project sits at *pending dept approval*,
      the dept head can edit its content fields (incl. budget) from the
      approval form. No automated case exists — one manual check.
- [ ] Review draft rule **R42** in `tests/plan.yaml` (Lines Total catches up
      after any line change, however the line arrived). Approve or correct
      the wording; cases get written after that.

### 1.3 Config flips — after the walkthroughs, before the final backup

These must be in the backup that goes to the server, so do them last, locally.

- [ ] **Re-negate `member`'s `ui.*` snippet** (change it back to `!ui.*`).
      Today every user in the app can enter UI-edit mode — a deliberate dev
      convenience, but a real problem the moment an end user gets an account,
      because role permissions are unioned (D54). *Claude does this on your
      go; it's a one-line ACL change.*
- [ ] **Optional now:** give `fiona.finance` the `finance` role. Only matters
      once a finance approval stage exists — none does today.
- [ ] **No action, just aware:** payment fields and receiving both sit on
      procurement as deliberate interims (D59). Move them to finance /
      warehouse roles when those users exist.

### 1.4 Dead-scope ACL audit — DONE, full app, 2026-07-18 ✓

The pre-go-live item from notes.md ("re-run the D57 dead-scope check across
the whole schema") is complete. Method: every ACL action row (245 total, all
roles, all collections) was cross-checked — does its parent grant still exist,
and does its scope filter still exist?

**Result: PASS.** No live grant points at a missing scope, so no role has a
silently-unscoped permission. Ten action rows do reference dead scope ids
(2/4/5 in the legacy table, plus 10/11 pointing nowhere), but all ten are
orphans — their parent grant rows were deleted long ago, so they grant
nothing (NocoBase leaves these behind; known, harmless). The legacy ACL
tables (`rolesResources`/`rolesResourcesActions`) are empty. Optional cosmetic
cleanup (deleting the 10 orphan rows + 3 dead scope rows) can happen any time;
it changes no behavior.

### 1.5 Final local backup

Once 1.1–1.3 are done: `nb backup create` to the usual iCloud location. This
exact file is what gets restored onto the server in Part 3 — it carries all
settings, ACL, workflows, pages, *and* the dev data (test PRs, personas),
which gets pruned on the server afterwards (3.2). Local keeps its data for
future development.

---

## Part 2 — Server rebuild (RackNerd VPS, from scratch)

> The full teaching version of this part — with the why behind every step,
> the Caddy-vs-tunnel reasoning, and a reusable template for future projects —
> is [vps-setup-guide.md](vps-setup-guide.md). This part is the condensed,
> Havenbeheer-specific run of the same steps; if the two ever disagree, the
> general guide is the reference.

### 2.0 What changes vs. the old setup guide, and why

The old guide (Caddy + proxied A record) was sound for its time. Rebuilding
from scratch, change these six things:

1. **Cloudflare Tunnel replaces Caddy and the open web ports.** The old
   design: visitors → Cloudflare proxy → your server's ports 80/443 → Caddy →
   NocoBase, with Caddy doing Let's Encrypt certificates. The tunnel design:
   a small `cloudflared` container on the server dials **out** to Cloudflare
   and keeps that connection open; visitor traffic comes down that pipe.
   Consequences: ports 80 and 443 are **closed** — nothing on the internet
   can reach your server directly, your real IP is never exposed, there are
   no certificates to obtain or renew, and the whole "SSL mode Full vs Full
   (strict) timing dance" from the old guide disappears. Caddy is dropped
   entirely; NocoBase's image has its own internal web server.
2. **The image tag is pinned.** The old compose used `beta-full`, an
   unpinned tag — that's why the VPS drifted to an old beta while local moved
   on. Production runs `nocobase/nocobase:2.1.0-beta.47-full` — the *exact*
   version running locally, which the backup-restore requires. Upgrades
   become a deliberate act (Part 4).
3. **Backups cover files, not just the database.** The old guide's `pg_dump`
   cron missed the `storage/` directory — which holds every uploaded
   attachment, including signed board-approval documents. Both are backed up
   now, and copied off the server.
4. **The old backup cron was broken anyway:** `docker exec postgres …`
   assumes a container literally named `postgres`; Compose names it
   `nocobase-postgres-1`. Fixed with explicit `container_name:` entries.
5. **Ubuntu 24.04 SSH gotcha fixed:** 24.04 starts SSH via "socket
   activation", which can ignore the `Port 2222` line in the config. One
   extra command (§2.2 step 4) makes the port change actually stick.
6. **Postgres gets a healthcheck** so NocoBase waits for a *ready* database,
   not just a started container.

Kept from the old guide because it was right: non-root user, SSH keys only,
port 2222, UFW, fail2ban, unattended security upgrades without auto-reboot,
Docker log rotation, swap, pinned Postgres 16, `wal_level=logical`,
`chmod 600 .env`.

### 2.1 Target architecture

```
  Internet users
       │
       ▼
  Cloudflare (TLS, DNS, hides your IP)
       │  ← outbound-only tunnel, opened BY the server
       ▼
  RackNerd VPS (Ubuntu 24.04)
  ├── UFW: ONLY port 2222 (SSH) open. 80/443 closed.
  └── Docker (network "nocobase", nothing published to the internet)
      ├── cloudflared  ← keeps the tunnel to Cloudflare open
      ├── nocobase     ← the app (2.1.0-beta.47-full), internal port 80
      └── postgres     ← the database, internal only
```

### 2.2 Wipe and OS baseline

> **Before wiping:** the old VPS runs an old NocoBase at app.ttga.cloud. If
> anything on it matters (it shouldn't — it's months stale), pull a copy of
> `/opt/apps/nocobase/data/` first. Wiping destroys it permanently.

**0.** In the RackNerd control panel: reinstall the VPS with **Ubuntu 24.04**.
Log in as root with the password they give you.

**1. Update everything** (a datacenter image is weeks stale — patch first):

```bash
apt update && apt upgrade -y
timedatectl set-timezone America/Paramaribo
```

**2. Create your user** (never work as root — one bad command has no undo):

```bash
adduser alex          # strong password; other fields Enter to skip
usermod -aG sudo alex
```

**3. SSH key** — on your **Mac** (reuse `~/.ssh/vps_ed25519` if you still have
it; otherwise generate as in the old guide), then:

```bash
ssh-copy-id -i ~/.ssh/vps_ed25519.pub alex@SERVER_IP
ssh -i ~/.ssh/vps_ed25519 alex@SERVER_IP    # MUST work before step 4
```

**4. Harden SSH** — on the server, `sudo nano /etc/ssh/sshd_config`, set:

```conf
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers alex
MaxAuthTries 3
```

Then the 24.04-specific part — without this, SSH keeps listening on 22 and
ignores your port line, because systemd's socket starts it, not the config:

```bash
sudo systemctl disable --now ssh.socket
sudo systemctl enable ssh.service
sudo sshd -t                      # no output = config valid
sudo systemctl restart ssh
```

**Verify from a second terminal before closing the first:**
`ssh -i ~/.ssh/vps_ed25519 -p 2222 alex@SERVER_IP`. Then add the `Host myvps`
shortcut to your Mac's `~/.ssh/config` (HostName, User alex, Port 2222,
IdentityFile) so `ssh myvps` works.

**5. Automatic security updates**, no auto-reboot:

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades   # answer Yes
```

In `/etc/apt/apt.conf.d/50unattended-upgrades` set
`Unattended-Upgrade::Automatic-Reboot "false";` (uncomment if needed).

**6. Firewall — one open port.** This is the tunnel payoff: no 80, no 443.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp comment "SSH"
sudo ufw logging low
sudo ufw enable          # answer y — 2222 is open, you won't be cut off
sudo ufw status verbose  # verify: only 2222
```

**7. Fail2ban** (bans IPs that hammer SSH):

```bash
sudo apt install -y fail2ban
sudo tee /etc/fail2ban/jail.local > /dev/null <<'EOF'
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled  = true
port     = 2222
backend  = systemd
maxretry = 3
EOF
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd   # verify the jail is up
```

(A minimal `jail.local` like this beats copying the whole `jail.conf` — less
to drift from upstream defaults.)

**8. Docker** — official repo (Ubuntu's own package is stale):

```bash
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker alex
```

Log-rotation **before** the first container (default keeps logs forever and
fills the disk):

```bash
echo '{ "log-driver": "local" }' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

Log out and back in (for the docker group), then verify:
`docker run --rm hello-world` and `docker info | grep "Logging Driver"`
(expect `local`).

**9. Swap** (keeps the OOM killer away from Postgres on a small VPS):

```bash
sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl --system
swapon --show    # verify: 4G
```

### 2.3 Cloudflare Tunnel — what it is, and setup

**Plain-language version:** normally a web server sits with ports open,
waiting for anyone on the internet to knock. A tunnel reverses that: a small
program on your server (`cloudflared`) makes an *outgoing* call to Cloudflare
and holds the line open. When someone visits app.ttga.cloud, Cloudflare
answers them and passes the request down the already-open line. Your server
never accepts a single incoming web connection. Attackers scanning your IP
find nothing — not even a hint that a website lives there. Cloudflare
terminates TLS with its own certificate, so there is nothing to renew on the
server, ever.

Your domain state: ttga.cloud is registered at Porkbun, but its nameservers
point at Cloudflare — so all DNS is managed in the Cloudflare dashboard
(that's the "indirectly managed" part). Porkbun is only the registrar now;
you never touch it for this.

**Setup (Cloudflare dashboard):**

1. dash.cloudflare.com → verify **ttga.cloud** is listed and Active.
2. **DNS** → delete any existing `A` or `CNAME` record for `app` — the
   tunnel will create its own and collides with leftovers.
3. **Zero Trust → Networks → Tunnels → Create a tunnel** → connector type
   **Cloudflared** → name it `havenbeheer`.
4. On the connector page, pick **Docker**. Don't run their command — just
   copy the long **token** out of it (the string after `--token`). It goes
   in the server's `.env` in §2.4.
5. **Public hostname** tab → Add: subdomain `app`, domain `ttga.cloud`,
   service type **HTTP**, URL `nocobase:80`. This means: requests for
   app.ttga.cloud go down the tunnel to the container named `nocobase` on
   port 80. Cloudflare creates the DNS record automatically.
6. Optional but recommended, under the zone's **SSL/TLS → Edge Certificates**:
   turn on **Always Use HTTPS**.

The token is the tunnel's credential — treat it like a password (it's in the
`.env`, which is `chmod 600`).

### 2.4 Application files

```bash
sudo mkdir -p /opt/apps/nocobase/storage
sudo mkdir -p /opt/backups
sudo chown -R alex:alex /opt/apps/nocobase /opt/backups
cd /opt/apps/nocobase
```

**`.env`** (`nano .env`, then `chmod 600 .env`):

```dotenv
# Fresh secrets — do NOT reuse the local dev values.
# Generate each with:  openssl rand -base64 32
APP_KEY=REPLACE_ME
POSTGRES_PASSWORD=REPLACE_ME

POSTGRES_DB=nocobase
POSTGRES_USER=nocobase
TZ=America/Paramaribo

# From Cloudflare, §2.3 step 4
TUNNEL_TOKEN=REPLACE_ME
```

(A fresh `APP_KEY` on the server is fine even though we restore a local
backup — it only signs login tokens, so everyone just logs in anew. The local
dev key and DB password have been sitting in a compose file for months and
shouldn't move to production.)

**`compose.yaml`** (`nano compose.yaml`):

```yaml
networks:
  nocobase:
    driver: bridge

services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: nocobase-cloudflared
    restart: unless-stopped
    networks: [nocobase]
    command: tunnel --no-autoupdate run --token ${TUNNEL_TOKEN}
    depends_on: [nocobase]

  postgres:
    image: postgres:16
    container_name: nocobase-postgres
    restart: unless-stopped
    networks: [nocobase]
    command: postgres -c wal_level=logical
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./storage/db/postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 12

  nocobase:
    # PINNED — must equal the local version for backup-restore to work.
    # Upgrades are deliberate: see Part 4.
    image: nocobase/nocobase:2.1.0-beta.47-full
    container_name: nocobase-app
    restart: unless-stopped
    networks: [nocobase]
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      APP_KEY: ${APP_KEY}
      DB_DIALECT: postgres
      DB_HOST: postgres
      DB_PORT: 5432
      DB_DATABASE: ${POSTGRES_DB}
      DB_USER: ${POSTGRES_USER}
      DB_PASSWORD: ${POSTGRES_PASSWORD}
      TZ: ${TZ}
    volumes:
      - ./storage:/app/nocobase/storage
    ports:
      # Loopback only — NOT reachable from the internet. Lets you debug via
      # SSH port-forward:  ssh -L 13000:localhost:13000 myvps
      - "127.0.0.1:13000:80"
```

Notes on the layout: it mirrors the local dev tree exactly (single `./storage`
bind mount, Postgres data inside it at `storage/db/postgres`) — same layout
upstream NocoBase uses, and it keeps "back up the app" = "back up one
directory plus one pg_dump". No Caddy service, no published 80/443, and
`container_name:` entries so cron jobs can address containers reliably.

### 2.5 First boot

```bash
cd /opt/apps/nocobase
docker compose up -d
docker compose logs -f nocobase   # wait for the ready message (first boot
                                  # runs migrations; takes a few minutes)
```

Then open **https://app.ttga.cloud** — you should get the NocoBase initial
screen (default admin login). Log in, change the admin password immediately,
and stop there — don't configure anything, the restore in Part 3 overwrites
it all. In the Cloudflare Zero Trust tunnel page, the connector should show
**HEALTHY**.

---

## Part 3 — Migration (Mac → server)

**The one hard rule: versions must match.** A NocoBase backup only restores
onto the same NocoBase version. Local is 2.1.0-beta.47; the compose above
pins exactly that. Never upgrade one side without the other.

### 3.1 Restore the backup

Done from the Mac with the `nb` CLI (it talks to the server over HTTPS):

1. Register the production app as a second CLI environment (e.g.
   `havenbeheer-prod`, URL `https://app.ttga.cloud`, the admin login from
   §2.5) — a session task for Claude via the env-manage skill.
2. Restore the Part-1.5 backup file into that environment. Restoring is
   destructive to whatever is in the target — which is exactly nothing (a
   fresh install), so no confirmation drama. Restore always requires
   Alexander's explicit go regardless (house rule).
3. The app restarts itself as part of the restore; give it a couple of
   minutes, then log in at app.ttga.cloud **with your local credentials**
   (the restore brought the local user table with it).

### 3.2 Post-restore cleanup — on the server only

The backup carries dev data. Prune it on production; local keeps everything.

- [ ] Delete test/demo records: PRs, POs, projects, suppliers you don't want,
      notifications, and old workflow execution history.
- [ ] Decide the fate of the dev personas (alice.member, pat.procurement,
      oliver.owner, dana.director, simon.supervisor, fiona.finance): delete
      them, or repurpose/rename the ones matching real people. Everyone's
      password on prod must be fresh — the shared `nbtest` password must not
      survive on a public URL.
- [ ] Create the real user accounts, assign roles, set each department's
      main approver to a real person (approval routing reads this).
- [ ] Change/verify the admin (root) password is strong and unique.
- [ ] Confirm the `member` `ui.*` flip from §1.3 arrived: log in as a normal
      user — no UI-edit pencil anywhere.

### 3.3 Production smoke test

- [ ] One real (small) PR through the full ladder with real users.
- [ ] One PO: generate → line → issue → print (the PDF print is server-side;
      confirm it works in the container just like locally).
- [ ] An attachment upload + download (checks `storage/` is writable and
      served).
- [ ] Check the clock: a PR created now shows the right Paramaribo time.

---

## Part 4 — Backups & maintenance (production)

### 4.1 Automated backups

Two things need saving: the **database** (pg_dump) and the **storage
directory** (uploads/attachments — excluded: the live Postgres files, which
are useless as file copies and belong to pg_dump).

`crontab -e` as alex on the server:

```cron
# 03:00 daily — database dump (custom format, compressed)
0 3 * * * docker exec nocobase-postgres pg_dump -U nocobase -Fc nocobase > /opt/backups/db-$(date +\%F).dump
# 03:30 daily — uploaded files (storage minus the raw db dir)
30 3 * * * tar -czf /opt/backups/storage-$(date +\%F).tar.gz -C /opt/apps/nocobase --exclude=storage/db storage
# 04:00 daily — delete local copies older than 7 days
0 4 * * * find /opt/backups -name "*.dump" -o -name "*.tar.gz" | xargs -r ls -1 | head -0; find /opt/backups \( -name "*.dump" -o -name "*.tar.gz" \) -mtime +7 -delete
# 05:00 daily — off-site copy (set up rclone once, see below)
0 5 * * * rclone copy /opt/backups remote:BUCKET/havenbeheer/
```

(The `docker exec nocobase-postgres` works because compose sets
`container_name` — the old guide's version silently failed here.)

**Test before trusting:** run the pg_dump line by hand, then restore it into
a scratch database (`CREATE DATABASE restore_test`, `pg_restore` into it,
drop it). A backup that's never been restored is a hope, not a backup.

**Off-site is not optional:** on-server backups die with the server. Set up
`rclone` against any S3-compatible bucket (Backblaze B2 is cheap) — or, until
that's done, keep taking periodic `.nbdata` backups from the Mac via
`nb backup create` against the prod environment; those land in iCloud and
count as off-site. Do at least one of the two from day one.

### 4.2 Upgrading NocoBase (the pinned-tag procedure)

Local and prod move **together**, local first:

1. Upgrade local, re-run the test suite, use it for a few days.
2. Back up prod (the two cron artifacts, taken fresh, plus an `.nbdata`).
3. Edit the image tag in prod's `compose.yaml` to the new version.
4. `docker compose pull nocobase && docker compose up -d nocobase` — it
   migrates on boot; watch `docker compose logs -f nocobase`.
5. Rollback = old tag back + restore the pre-upgrade backup.

### 4.3 Routine

| When | What |
|---|---|
| Weekly | `ls /var/run/reboot-required` — if present: `docker compose stop`, `sudo reboot` (containers auto-start; `restart: unless-stopped`) |
| Weekly | `df -h` and `docker system df` — disk headroom |
| Monthly | Check backups actually arrive off-site; skim NocoBase release notes |
| Quarterly | Test-restore a backup |
| After upgrades | `docker image prune -f` |

---

## Final go-live checklist

**App (Part 1):** Complete Project button built and self-tested · 014.6
walkthrough passed · 016 walkthrough passed (incl. B8 import recompute) ·
dept-head edit check · R42 reviewed · `member` `ui.*` re-negated · final
`nb backup create` taken **after** the flips.

**Server (Part 2):** old-VPS data rescued if needed · Ubuntu 24.04 fresh ·
alex + keys, SSH on 2222, root and passwords disabled, ssh.socket disabled ·
UFW active with only 2222 · fail2ban jail up · unattended-upgrades on,
auto-reboot off · Docker with `local` log driver · 4G swap · tunnel HEALTHY ·
app answers at https://app.ttga.cloud · `.env` is `chmod 600` with fresh
secrets.

**Migration (Part 3):** restore succeeded, local login works on prod · test
data pruned · real users created, real approvers set, no `nbtest` passwords ·
smoke test passed (PR ladder, PO print, attachment, timezone).

**Afterwards (Part 4):** backup crons installed · manual restore test done ·
off-site copy verified · upgrade procedure understood (versions move in
lockstep, local first).
