# Go-live runbook — Havenbeheer Purchasing

Everything between "the app works locally" and "real users work in it at
https://app.ttga.cloud". Written 2026-07-18. One file, four parts, in order:

1. **App readiness** — finish and verify the app locally.
2. **Server rebuild** — wipe the RackNerd VPS, set it up from scratch.
3. **Migration** — move the app from the Mac to the server.
4. **Backups & maintenance** — keep it alive afterwards.

---

## Part 1 — App readiness (local, before anything touches the server)

### 1.1 Complete Project button — DONE 2026-07-18 ✓

Built by Alexander; PRJ-26-0079 was completed in the app. The build brief is
kept below for reference.

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

**Status 2026-07-18:** Alexander walked these — "so far so good", no failures
reported. The individual boxes below are left unticked because they weren't
confirmed case by case; treat them as a checklist to spot-check rather than as
outstanding work. Two additions land after chunks 017 and 019 (see §1.2b).

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

### 1.2b Added by the final build phase (chunks 017 and 019)

Written 2026-07-18 when 017 and 019 were scheduled. Fill in after each builds.

- [ ] **019** — on an **issued** PO, editing a line's Quantity or Unit Price is
      rejected; on a **draft** PO the same edit still saves.
- [ ] **019** — entering a Received Quantity on an issued PO's line still saves
      (the freeze must not break receiving).
- [ ] **019** — the **Add new** button is gone from the PO table, and Generate
      PO on an approved PR still produces a draft PO carrying supplier,
      currency, total and FX rate.
- [ ] **017** — reject a PR at each stage; the submitter, their dept head, and
      (where the PR reached them) the procurement head each get a notification
      naming the stage. The person who rejected gets nothing.
- [ ] **017** — the same for a rejected project.
- [ ] **017** — approve a PR to final; the three notification titles now read
      correctly (they currently say "reassigned to custom approver").

### 1.3 Config flips

- [x] **`member`'s `ui.*` snippet — MOVED to §3.2, on the server.** Alexander's
      call 2026-07-18: he does this flip in the online version after the
      restore, keeping the dev convenience on the Mac. **This means the backup
      shipped to the server still carries the permissive setting** — §3.2 now
      owns the flip itself, not just the verification. Nothing to do locally.
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
3. **Backups move into NocoBase itself.** The old guide hand-rolled a
   `pg_dump` + `tar` + `rclone` cron stack. NocoBase's Backup manager plugin
   already does all of it — database *and* uploaded attachments, on a
   schedule, with retention, uploaded to a bucket — so the cron stack is
   gone. See 4.1.
4. **That also retires two bugs in the old cron:** it missed the `storage/`
   directory entirely (every uploaded attachment, including signed
   board-approval documents), and its `docker exec postgres …` assumed a
   container literally named `postgres` while Compose names it
   `nocobase-postgres-1`. Neither can recur now. (`container_name:` is still
   pinned in the compose file below — it makes every other `docker exec` you
   type reliable.)
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
>
> This is the **same VPS** being wiped and rebuilt, so app.ttga.cloud is
> simply down from the wipe until Part 3 finishes. That's fine — no real
> users exist on it yet. The restore source is the Mac, untouched by the
> wipe.

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
# No /opt/backups here: the Backup manager writes inside the app's own
# storage/ directory (which is bind-mounted below) and pushes copies to the
# bucket. See 4.1.
sudo mkdir -p /opt/apps/nocobase/storage
sudo chown -R alex:alex /opt/apps/nocobase
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
- [ ] **Re-negate `member`'s `ui.*` snippet** (change it to `!ui.*`). Moved
      here from §1.3 on 2026-07-18 — Alexander chose to do this on the server
      rather than locally, so the dev convenience survives on the Mac. Until
      this is done, **every user on production can enter UI-edit mode**,
      because role permissions are unioned (D54). Do it before real accounts
      get handed out, not after.
- [ ] Verify the flip: log in as a normal user — no UI-edit pencil anywhere.

### 3.3 Production smoke test

- [ ] One real (small) PR through the full ladder with real users.
- [ ] One PO: generate → line → issue → print (the PDF print is server-side;
      confirm it works in the container just like locally).
- [ ] An attachment upload + download (checks `storage/` is writable and
      served).
- [ ] Check the clock: a PR created now shows the right Paramaribo time.

---

## Part 4 — Backups & maintenance (production)

### 4.1 Automated backups — NocoBase's own Backup manager

**No cron, no `pg_dump`, no `rclone`.** NocoBase ships a Backup manager
plugin that already does the whole job: it dumps the database *and* the
uploaded files into one `.nbdata` file, on a schedule, keeps N of them, and
uploads each finished backup to a bucket. It's enabled in this app already —
it's the same thing `nb backup create` drives.

Verified against the running container, not just the docs: the plugin's
settings are `scheduled`, `cron`, `keep`, `enableFilesBackup`, `storageId`
and `encryptionPassword`, and its upload step ships the finished file to any
configured file storage whose type isn't `local`.

**Set it up once, in the app UI** (Settings → Backup manager):

1. **Add the bucket as a file storage** first (Settings → File manager →
   Storages → Add → type **Amazon S3**). That's the *free* built-in S3
   engine, not the paid "S3(Pro)" plugin — it takes a custom **endpoint**,
   which is what makes Backblaze B2 (or any S3-compatible bucket) work.
   Give it the B2 endpoint, region, bucket and application key.
2. **In Backup manager's settings:**
   - **Backup local storage files:** on. This is what pulls
     `storage/uploads` — every attachment, including the signed
     board-approval documents — into the backup.
   - **Run automatic backup on the cron schedule:** on, `0 3 * * *` (03:00).
   - **Maximum number of locally saved backup files:** 7. Older ones are
     deleted from the server automatically; the bucket keeps its own copies.
   - **Sync backup to cloud storage:** the storage from step 1.
   - **Encryption password:** set one. See the warning below.

**Three things the plugin does not cover — handle them by hand:**

- **`compose.yaml` and `.env` are not in the backup.** They live on disk, not
  in the database. Copy both off the server once, into the password manager
  or iCloud. They only change when you upgrade.
- **The encryption password is not recoverable.** Store it somewhere that is
  neither the server nor the bucket. Lost password means the backups are
  unreadable noise.
- **The B2 key can delete.** The app holds that key, so whatever compromises
  the app can also wipe the bucket. Use a B2 *application key scoped to that
  one bucket*, and turn on object lock or a lifecycle rule that retains
  previous versions. Then a wipe is recoverable.

**Keep taking occasional manual backups from the Mac** —
`nb backup create` against the prod environment, landing in iCloud. Not a
second automated system; just a copy in a place the server holds no
credentials for at all. That's the answer to the bullet above.

**Test before trusting:** after the first scheduled run, download the
`.nbdata` from the Backup manager list and confirm it's non-trivial in size
and that the bucket has a copy. Then do a real restore drill — see 4.4. A
backup that's never been restored is a hope, not a backup.

### 4.2 Upgrading NocoBase (the pinned-tag procedure)

Local and prod move **together**, local first:

1. Upgrade local, re-run the test suite, use it for a few days.
2. Back up prod: trigger a fresh backup by hand in the Backup manager and
   wait for it to reach the bucket. Download that `.nbdata` to the Mac too —
   a restore-capable copy that doesn't depend on the server surviving.
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
| Quarterly | Restore drill (4.4) |
| After upgrades | `docker image prune -f` |

### 4.4 The restore drill

A NocoBase restore is a **full replace** of the target app — it is not a
merge, and it is not something to try on production to "see if the file is
good". Restore into a throwaway target instead:

1. On the Mac, spin up a scratch NocoBase on the **same version**
   (`2.1.0-beta.47`) — `nb-new-project` scaffolds one in a few minutes.
2. Restore the downloaded prod `.nbdata` into it (you'll need the encryption
   password).
3. Log in, open a PR with an attachment, and download that attachment. That
   proves both halves — database *and* files — actually survived.
4. Delete the scratch app.

**The version rule:** a backup restores onto the same NocoBase version or a
newer one, never onto an older one. This is why local and prod move in
lockstep (4.2), and it's the reason a backup taken today may be unrestorable
onto a server you rebuild next year from a stale image tag — the tag pinned
in `compose.yaml` is part of the backup story.

---

## Final go-live checklist

**App (Part 1):** ~~Complete Project button built and self-tested~~ ✓ ·
~~014.6 walkthrough passed~~ ✓ · 016 walkthrough passed (incl. B8 import
recompute) · **chunk 019 built (PO execution lock)** · **chunk 017 built
(approval notifications)** · §1.2b checks passed · dept-head edit check ·
R42 reviewed · final `nb backup create` taken last.
(`member` `ui.*` moved to §3.2 — done on the server, not here.)

**Server (Part 2):** old-VPS data rescued if needed · Ubuntu 24.04 fresh ·
alex + keys, SSH on 2222, root and passwords disabled, ssh.socket disabled ·
UFW active with only 2222 · fail2ban jail up · unattended-upgrades on,
auto-reboot off · Docker with `local` log driver · 4G swap · tunnel HEALTHY ·
app answers at https://app.ttga.cloud · `.env` is `chmod 600` with fresh
secrets.

**Migration (Part 3):** restore succeeded, local login works on prod · test
data pruned · real users created, real approvers set, no `nbtest` passwords ·
smoke test passed (PR ladder, PO print, attachment, timezone).

**Afterwards (Part 4):** B2 bucket added as an S3 file storage · Backup
manager scheduled, files-backup on, keep 7, cloud sync on, encryption
password set **and stored off the server** · `compose.yaml` + `.env` copied
off the server · first scheduled backup landed in the bucket · restore drill
done (4.4) · upgrade procedure understood (versions move in lockstep, local
first).
