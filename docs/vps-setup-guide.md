# VPS Prep & Setup Guide

**Ubuntu 24.04 · Docker Compose · Cloudflare Tunnel · any containerized app**

A general-purpose guide for preparing a fresh VPS and deploying a Dockerized
application on it. Nothing in here is specific to one project — use it every
time. Written 2026-07-18; supersedes the earlier Caddy-based guide (that
setup survives as Appendix A, for when a tunnel is not an option).

---

## Before you start

### Placeholders used throughout

| Placeholder | Meaning | Example |
| --- | --- | --- |
| `YOUR_USER` | your non-root admin user | `alex` |
| `SERVER_IP` | the VPS's public IP | `203.0.113.10` |
| `YOUR_DOMAIN` | the zone managed in Cloudflare | `ttga.cloud` |
| `app.YOUR_DOMAIN` | the public hostname for this app | `app.ttga.cloud` |
| `PROJECT` | short name of the app/project | `havenbeheer` |
| `~/apps/PROJECT` | where the app lives on disk | `~/apps/havenbeheer` |

### How to edit files on the server

Use `nano`, pre-installed on Ubuntu:

```bash
sudo nano /path/to/file
```

Inside nano: arrow keys move, type to insert, `Ctrl+W` searches, `Ctrl+K`
cuts a line, `Ctrl+O` then `Enter` saves, `Ctrl+X` exits. A file that does
not exist yet is created when you save.

### How to read this guide

Each section follows the same pattern:

1. **What this does** — the goal in plain language
2. **Why** — the reason the step exists
3. **Commands** — exact commands, in order
4. **Verify** — how to confirm it worked before moving on

---

## 1. The big picture

```
  Internet users
       │
       ▼
  Cloudflare  ← DNS, TLS certificates, hides the server's real IP
       │
       │  ← the tunnel: an OUTBOUND connection the server opens
       ▼     and keeps open; visitor traffic rides down it
  Your VPS (Ubuntu 24.04)
  ├── UFW firewall   ← only the SSH port is open. Nothing else.
  └── Docker (private network per project)
      ├── cloudflared   ← holds the tunnel open, hands requests to the app
      ├── your app      ← internal only, never exposed to the internet
      └── your database ← internal only, never exposed to the internet
```

- **Cloudflare** owns the public side: DNS for your domain, the HTTPS
  certificate visitors see, and the DDoS-absorbing front. Visitors never
  learn your server's IP.
- **The tunnel** (`cloudflared`, a small container) is the only bridge
  between Cloudflare and your machine — and the machine builds that bridge
  itself, outbound. No inbound web ports exist.
- **UFW** blocks every incoming port except SSH.
- **The app and its database** live on a private Docker network. They can
  talk to each other by container name; the internet cannot talk to them
  at all.

---

## 2. Choosing the front door: why a tunnel, and where Caddy fits

Every web deployment needs two jobs done somewhere:

1. **TLS termination** — someone holds a valid certificate for your domain
   and encrypts traffic to the visitor's browser.
2. **Reverse proxying** — something receives requests and routes them to the
   right container.

There are three common topologies:

| | A. Direct + Caddy | B. Cloudflare proxy + Caddy | C. Cloudflare Tunnel |
| --- | --- | --- | --- |
| Open ports on server | 80, 443 | 80, 443 | **none** |
| Who holds the visitor-facing cert | Caddy (Let's Encrypt) | Cloudflare | Cloudflare |
| Server IP visible to attackers | yes | no (but guessable/leakable) | **no, and unreachable even if known** |
| Certificate renewals on server | yes | yes (origin cert) | **none** |
| Extra moving parts | Caddy | Caddy + SSL-mode settings | cloudflared |
| Depends on Cloudflare | no | yes | yes |

**Topology C is this guide's default.** The reasoning:

- With a tunnel, **both of Caddy's jobs are already done by others**. TLS is
  terminated at Cloudflare's edge with Cloudflare's certificate (in topology
  B this was already true — visitors were never seeing your Caddy
  certificate). The path from edge to server is the tunnel itself, which is
  encrypted and authenticated because the server dialed out to create it.
  And the routing job — "requests for app.YOUR_DOMAIN go to container X,
  port Y" — is exactly what a tunnel's *public hostname* rule is. cloudflared
  sits on the Docker network and delivers requests straight to the app
  container. It handles multiple hostnames → multiple containers, so even a
  many-apps-one-VPS setup needs no Caddy.
- **The attack surface shrinks to one port.** In topologies A and B, ports
  80/443 accept connections from the entire internet, and in B, anyone who
  discovers the real IP (old DNS records, other services on the box, a
  misconfigured email header) can bypass Cloudflare and hit the server
  directly. With a tunnel there is nothing to hit: a port scan of your IP
  shows a machine with one SSH port and no web server at all.
- **A whole class of configuration disappears**: no Caddyfile, no ACME
  challenges, no renewal failures, no "SSL mode Full vs Full (strict)"
  ordering problem (that Cloudflare setting doesn't even apply to tunnel
  traffic), no keeping ports 80/443 in the firewall.

**Why official app docs (NocoBase's included) still show Caddy:** they
document the general case — a server the internet connects to directly,
where something on the machine *must* do TLS. They don't assume you use
Cloudflare at all. Their advice is correct for topology A; it's solving a
problem topology C doesn't have. Running Caddy behind a tunnel isn't harmful,
it's just a proxy with no job: Cloudflare → cloudflared → Caddy → app, where
the middle hop adds a config file and a container and removes nothing.

**When you SHOULD use Caddy instead** (→ Appendix A):

- You don't want the Cloudflare dependency, or the domain isn't on
  Cloudflare. Then the server must face the internet and hold certificates —
  that's Caddy's home turf.
- You need server-side proxy features the app lacks and Cloudflare doesn't
  cover in your plan: basic-auth in front of an app with no login,
  path-based routing between apps under one hostname, local mTLS.
- The app's own docs require the proxy to serve its static files (some
  images ship without an internal web server). Check whether your image
  bundles its own — NocoBase's standard `-full` image does (internal nginx),
  so it needs nothing in front.

**Trade-offs of the tunnel, stated honestly:** you are dependent on
Cloudflare's availability and terms (their free tier covers this use); TLS
from the visitor terminates at Cloudflare, meaning Cloudflare can technically
read traffic (true in topology B as well — only topology A avoids it); and
the app sees requests coming from cloudflared, so the *real* visitor IP lives
in the `CF-Connecting-IP` header if you ever need it for logs or audit.

---

## 3. Base OS preparation

### 3.1 Update installed packages

**What this does:** installs all pending updates for the OS.
**Why:** a fresh VPS image may be weeks old; some packages have known,
already-patched vulnerabilities. Close those gaps before anything else.

```bash
sudo apt update && sudo apt upgrade -y
```

**Verify:** finishes without errors. If asked about a config file
("keep local version?"), press `Enter` for the default.

### 3.2 Set the timezone

**Why:** timestamps in logs, cron schedules, and the app itself should match
your local clock, or troubleshooting ("what happened at 3 AM?") becomes
guesswork.

```bash
timedatectl list-timezones | grep -i paramaribo   # find the exact name
sudo timedatectl set-timezone America/Paramaribo
```

**Verify:** `timedatectl` shows the right zone.

### 3.3 Create a non-root admin user

**Why:** root has no guardrails — one mistyped command can be fatal, and
automated attacks target the root account by name. Daily work happens as a
normal user; `sudo` grants root powers only when you ask for them.

```bash
sudo adduser YOUR_USER        # strong password; other prompts: Enter to skip
sudo usermod -aG sudo YOUR_USER
```

**Verify:**

```bash
su - YOUR_USER
sudo whoami     # prints: root
exit
```

> From here on, log in as `YOUR_USER`, never as root.

---

## 4. SSH keys and SSH hardening

SSH is your only door into the server, so it gets the most care. Passwords
can be guessed; keys cannot. Port 22 is scanned constantly; a custom port
sheds almost all of that noise.

> **Order matters:** get key login working (4.1) *before* disabling
> passwords (4.2), or you lock yourself out.

### 4.1 Key pair (on your local machine)

**What this does:** creates a private key (stays on your computer) and a
public key (goes on the server). The server then only admits connections
that prove possession of the private key.

If you already have `~/.ssh/vps_ed25519` from an earlier server, reuse it.
Otherwise:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vps_ed25519 -C "you@example.com"
```

`ed25519` is the current best-practice algorithm. A passphrase protects the
key file if your laptop is stolen; optional.

Install the public key on the server and test:

```bash
ssh-copy-id -i ~/.ssh/vps_ed25519.pub YOUR_USER@SERVER_IP
ssh -i ~/.ssh/vps_ed25519 YOUR_USER@SERVER_IP     # MUST succeed before 4.2
```

### 4.2 Harden the SSH daemon

```bash
sudo nano /etc/ssh/sshd_config
```

Find and set (change existing lines; don't add duplicates — `Ctrl+W` to
search):

```conf
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers YOUR_USER
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

| Setting | Effect |
| --- | --- |
| `Port 2222` | dodges the bots that only scan port 22 |
| `PermitRootLogin no` | the most-attacked account can't log in at all |
| `PasswordAuthentication no` | stolen/guessed passwords are useless |
| `AllowUsers` | every account except yours is refused, even if one exists |
| `MaxAuthTries 3` | drop the connection after 3 bad attempts |
| `ClientAlive*` | dead sessions get cleaned up after ~10 minutes |

**Ubuntu 24.04 trap:** SSH is started by a systemd *socket*, which listens on
port 22 regardless of what the config file says — your `Port 2222` line
would be silently ignored. Switch to classic service mode:

```bash
sudo systemctl disable --now ssh.socket
sudo systemctl enable ssh.service
sudo sshd -t                       # no output = config is valid
sudo systemctl restart ssh
```

**Verify — in a NEW terminal, keeping the old session open as a lifeline:**

```bash
ssh -i ~/.ssh/vps_ed25519 -p 2222 YOUR_USER@SERVER_IP
```

Works? Close the old session. Fails? Fix the config from the still-open one.

Make future logins painless — on your local machine, add to `~/.ssh/config`:

```plaintext
Host myvps
    HostName SERVER_IP
    User YOUR_USER
    Port 2222
    IdentityFile ~/.ssh/vps_ed25519
```

Now `ssh myvps` is all you type. (Use a distinct alias per server.)

---

## 5. Automatic security updates

**What this does:** Ubuntu installs security patches daily on its own.
**Why:** when a vulnerability is published, attackers scan for unpatched
servers within hours. You will not log in every day; the server must patch
itself. Two defaults need taming: it must not reboot on its own, and it
should stick to security fixes.

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades   # answer: Yes
```

Confirm the schedule file `/etc/apt/apt.conf.d/20auto-upgrades` contains:

```conf
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```

Then forbid surprise reboots — in
`/etc/apt/apt.conf.d/50unattended-upgrades` find the `Automatic-Reboot`
line, uncomment it (remove `//`) and set:

```conf
Unattended-Upgrade::Automatic-Reboot "false";
```

Kernel updates still need a reboot to take effect — but at a moment you
choose (§15.1). Leave `Allowed-Origins` at its default (security-only).

**Verify:**

```bash
sudo unattended-upgrade --dry-run --debug 2>&1 | head -40
```

You should see it read the config and check for updates without installing.

---

## 6. UFW firewall

**What this does:** blocks every incoming connection except SSH on 2222.
**Why:** default-deny means a misconfigured or accidentally-exposed service
is unreachable anyway. Thanks to the tunnel, no web ports are needed —
compare the old Caddy guide, which had to open 80 and 443.

**Docker note:** Docker punches its own holes in the firewall for *published*
ports (`ports:` in compose), bypassing UFW — a classic footgun. This guide's
compose files publish nothing (or bind only to `127.0.0.1`), so the footgun
never fires. Rule of thumb: **never write `ports: - "80:80"`-style lines on
a tunnel setup**; if you need local debugging access, bind to loopback:
`"127.0.0.1:PORT:PORT"`.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp comment "SSH"
sudo ufw logging low
sudo ufw enable            # answer y — 2222 is open, you won't be dropped
```

**Verify:** `sudo ufw status verbose` shows exactly one ALLOW rule (2222),
and your SSH session is still alive.

---

## 7. Fail2ban

**What this does:** watches SSH logs; IPs that fail login repeatedly get a
temporary firewall ban.
**Why:** bots will still find port 2222 eventually. They can't get in (keys
only), but fail2ban cuts the log noise and slows them to a crawl.

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
```

Why a small `jail.local` instead of copying all of `jail.conf` (as the old
guide did): fail2ban reads `jail.conf` first and overlays `jail.local` on
top, so the local file only needs your *changes* — less to drift out of date
when the package updates its defaults. `backend = systemd` is required on
Ubuntu 24.04 (SSH logs live in the journal, not a text file); do not add a
`logpath` alongside it.

**Verify:**

```bash
sudo fail2ban-client status sshd
```

The jail is up and "Journal matches" is populated.

---

## 8. Docker + log rotation

**What this does:** installs Docker from its official repository and caps
container log growth *before* the first container exists.
**Why:** Docker's default logging keeps every line forever; a chatty app
fills the disk in months. The `local` driver rotates automatically — but
only containers created *after* the setting applies inherit it, hence the
ordering.

```bash
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker YOUR_USER
```

Log rotation, then restart Docker:

```bash
echo '{ "log-driver": "local" }' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

Log out and back in (group membership), then **verify:**

```bash
docker run --rm hello-world                  # "Hello from Docker!"
docker info | grep "Logging Driver"          # Logging Driver: local
```

---

## 9. Swap

**What this does:** a 4 GB disk file the OS uses as overflow RAM.
**Why:** when RAM runs out, Linux's out-of-memory killer terminates the
biggest process — usually your database. Swap turns "sudden death" into
"temporarily slower", and gives you time to notice. Persistent heavy swap
use means the VPS needs more RAM.

```bash
sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl --system
```

`swappiness=10` (default 60) tells the OS: prefer RAM, use swap only under
real pressure — the right bias for a server.

**Verify:** `swapon --show` lists 4G; `cat /proc/sys/vm/swappiness` prints 10.

---

## 10. Directory layout convention

**Why a convention:** every project on every server in the same shape means
backups, debugging, and future-you always know where to look.

```bash
mkdir -p ~/apps/PROJECT ~/backups
cd ~/apps/PROJECT
```

```plaintext
~/apps/PROJECT/
├── compose.yaml     ← the services
├── .env             ← secrets (chmod 600, never in git)
└── <data dirs>      ← whatever the app persists, bind-mounted (e.g. ./storage)
~/backups/           ← only if you use the cron fallback (§13.2); apps that
                       back themselves up write inside their own data dir
```

**Why the home directory and not `/opt`:** `/opt` is the convention for
root-owned, system-wide software, and it costs you a `sudo mkdir` plus a
`chown` on every project. These stacks are run by one person under one
account, so the home directory is simpler: you create the tree, write `.env`,
and run `docker compose` as yourself, with no sudo anywhere. Use `/opt`
instead only if several admin accounts must reach the same app — `/home/user`
is mode 750, so nobody else can. Compose files are unaffected either way;
their paths are relative.

This does **not** change ownership *inside* the bind mounts. Container
processes write there as their own users — Postgres as uid 999 mode 700, many
app images as root — wherever the directory lives. That is normal, and it is
why reading or archiving those files still needs sudo.

Multiple projects = multiple `~/apps/<name>` directories, each with its
own compose file, its own Docker network, and its own tunnel or its own
public-hostname rule on a shared tunnel.

---

## 11. Cloudflare Tunnel setup

**Prerequisite:** the domain's nameservers point at Cloudflare (the domain
can be registered anywhere — e.g. Porkbun; the registrar then only holds the
registration, all DNS lives in the Cloudflare dashboard).

**What happens underneath:** you create a named tunnel in Cloudflare's
dashboard and get a **token** — the tunnel's credential. The `cloudflared`
container presents that token and establishes a few persistent outbound
connections to Cloudflare's nearest datacenters. Cloudflare creates a DNS
record for your hostname that points *into the tunnel* (not at your IP —
your IP appears nowhere in public DNS). Requests for that hostname arrive at
Cloudflare's edge, ride down the established connection, and cloudflared
hands them to the container you named. WebSockets pass through fine.

**Dashboard steps:**

1. dash.cloudflare.com → confirm `YOUR_DOMAIN` is listed and **Active**.
2. **DNS** → delete any existing `A`/`CNAME` record for the hostname you're
   about to use (leftovers collide with the record the tunnel creates).
3. **Zero Trust → Networks → Tunnels → Create a tunnel** → connector
   **Cloudflared** → name it after the project.
4. On the connector screen choose **Docker** — don't run their command, just
   copy the token string (after `--token`) into the server's `.env`.
5. **Public hostname** tab → Add: subdomain (e.g. `app`), your domain,
   service **HTTP**, URL `appcontainer:PORT` — the *container name and
   internal port* of your app as defined in compose. Save; Cloudflare
   creates the DNS record itself.
6. Zone settings → **SSL/TLS → Edge Certificates** → enable **Always Use
   HTTPS**.

Treat the token like a password: it lives only in `.env` (mode 600). If it
ever leaks, revoke the tunnel in the dashboard and create a new one.

**Optional hardening:** Cloudflare **Access** can put a login page (email
one-time-code, SSO) in front of the hostname *before* traffic ever reaches
your app — useful for admin-only tools. Zero Trust → Access → Applications.

---

## 12. The Compose pattern

The same three-service shape works for most single-app projects. Example
skeleton (adapt image names, env vars, and mounts to the app — check the
app's own docs for its required variables):

**`.env`** (then `chmod 600 .env`):

```dotenv
# generate secrets with:  openssl rand -base64 32
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=REPLACE_ME
APP_SECRET=REPLACE_ME
TZ=America/Paramaribo
TUNNEL_TOKEN=REPLACE_ME        # from §11 step 4
```

**`compose.yaml`:**

```yaml
networks:
  PROJECT:
    driver: bridge

services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: PROJECT-cloudflared
    restart: unless-stopped
    networks: [PROJECT]
    command: tunnel --no-autoupdate run --token ${TUNNEL_TOKEN}
    depends_on: [app]

  postgres:
    image: postgres:16                # pin the major version
    container_name: PROJECT-postgres
    restart: unless-stopped
    networks: [PROJECT]
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 12

  app:
    image: vendor/app:1.2.3           # ALWAYS a pinned, exact tag
    container_name: PROJECT-app
    restart: unless-stopped
    networks: [PROJECT]
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      # the app's own variables — from its documentation
      DB_HOST: postgres
      DB_PORT: 5432
      DB_DATABASE: ${POSTGRES_DB}
      DB_USER: ${POSTGRES_USER}
      DB_PASSWORD: ${POSTGRES_PASSWORD}
      TZ: ${TZ}
    volumes:
      - ./storage:/app/storage        # whatever the app persists
    ports:
      # loopback ONLY — reachable via `ssh -L PORT:localhost:PORT myvps`,
      # never from the internet. Optional; delete if not wanted.
      - "127.0.0.1:13000:80"
```

Why each choice:

- **Pinned image tags, always.** Floating tags (`latest`, `beta`) upgrade
  whenever the container is recreated — silently, possibly breaking, and you
  won't know which version you were on yesterday. A pinned tag makes
  upgrades a decision (§15.2). This is the single most common cause of
  "the server mysteriously runs a different version than my machine."
- **`container_name:`** — without it, Compose generates names like
  `PROJECT-postgres-1`, and any cron job or script that says
  `docker exec postgres …` fails silently. Fixed names make automation
  reliable. (The old guide's backup cron had exactly this bug.)
- **healthcheck + `condition: service_healthy`** — plain `depends_on` only
  waits for the database *container* to start, not for the database to
  accept connections; apps then crash-loop on first boot. The healthcheck
  makes "started" mean "ready".
- **No published ports** except an optional loopback-only debug binding —
  see the Docker/UFW note in §6.
- **`restart: unless-stopped`** — containers come back by themselves after
  a reboot or a crash; no manual `up` needed.
- **One named network per project** — containers reach each other by name
  (`postgres`, `app`); different projects on the same box stay isolated.

### First boot

```bash
cd ~/apps/PROJECT
docker compose up -d
docker compose logs -f app        # watch until the app reports ready
```

**Verify:** `docker compose ps` shows everything `running` (postgres
`healthy`); the tunnel connector shows **HEALTHY** in the Zero Trust
dashboard; `https://app.YOUR_DOMAIN` loads in a browser. Then do the app's
initial setup (create admin account, change default passwords) immediately —
the URL is public from the moment the tunnel is up.

---

## 13. Backups

Two separate loss scenarios, two answers:

1. **Bad data** (accidental delete, corrupting bug) → daily on-server dumps
   you can restore from.
2. **Dead server** (hardware failure, account mishap, fat-fingered wipe) →
   copies that live somewhere else. An on-server backup dies with the
   server; **off-site is not optional.**

And two kinds of state to save:

- the **database** — via the DB's own dump tool (a file-level copy of a
  running database's directory is corrupt-by-default; `pg_dump` produces a
  consistent snapshot even mid-traffic);
- the **file storage** the app writes (uploads, attachments) — via `tar`,
  excluding any live database directory inside it.

### 13.0 First: does the app back itself up?

**Check this before building anything below.** Many apps ship a backup
feature that already covers all four requirements — database, uploaded
files, a schedule, and an off-site destination. If yours does, use it and
skip §13.1–13.2 entirely. A hand-rolled cron stack is code you now own,
with failure modes (wrong container name, unescaped `%`, a dump that was
silently empty for months) that the app's own feature doesn't have.

**NocoBase specifically:** the Backup manager plugin does all four. It
writes one `.nbdata` holding the database *and* `storage/uploads`, runs on a
cron you set in the UI, keeps the N most recent locally, and uploads each
finished backup to any configured file storage that isn't the local one.
Point that at an S3-compatible bucket — the *free* built-in "Amazon S3"
storage type takes a custom endpoint, so Backblaze B2, Cloudflare R2 or
MinIO all work without the paid S3(Pro) plugin. See the Havenbeheer
[go-live guide](go-live.md) §4.1 for the settings, and §4.4 for the drill.

Two gaps to cover by hand whichever route you take: **`compose.yaml` and
`.env` are never in an app-level backup** (copy them off the server once),
and **the bucket credentials live on the server** — so scope the key to that
one bucket and enable object lock or versioning, or anything that
compromises the app can also erase the backups.

The rest of this section is the fallback: what to build when the app has no
backup feature of its own.

### 13.1 Prove the backup works once, by hand

```bash
docker exec PROJECT-postgres pg_dump -U appuser -Fc appdb > ~/backups/db-manual-test.dump
ls -lh ~/backups/       # non-zero size

# restore drill — a backup you never restored is a hope, not a backup:
docker exec PROJECT-postgres psql -U appuser -c "CREATE DATABASE restore_test;"
docker exec -i PROJECT-postgres pg_restore -U appuser -d restore_test < ~/backups/db-manual-test.dump
docker exec PROJECT-postgres psql -U appuser -c "DROP DATABASE restore_test;"
```

`pg_restore` finishing without errors proves the dump is usable.

### 13.2 Automate with cron

`crontab -e` as YOUR_USER:

```cron
# 03:00 — database dump (custom format = compressed, flexible restore)
0 3 * * * docker exec PROJECT-postgres pg_dump -U appuser -Fc appdb > $HOME/backups/db-$(date +\%F).dump
# 03:30 — app file storage (exclude a live DB dir if it lives inside)
30 3 * * * tar -czf $HOME/backups/storage-$(date +\%F).tar.gz -C $HOME/apps/PROJECT --exclude=storage/db storage
# 04:00 — keep 7 days locally
0 4 * * * find $HOME/backups \( -name "*.dump" -o -name "*.tar.gz" \) -mtime +7 -delete
# 05:00 — off-site copy (rclone configured once against any S3-style bucket)
0 5 * * * rclone copy $HOME/backups remote:BUCKET/PROJECT/
```

Notes: `%` must be escaped as `\%` inside crontab. Use `$HOME` rather than `~`
in cron lines — cron's shell is minimal and `$HOME` is unambiguous. The
`docker exec PROJECT-postgres` form works *because* compose pins
`container_name`. For the off-site leg, configure `rclone` once
(`rclone config`; Backblaze B2 is a cheap, simple choice — see rclone's
per-provider docs).

**Verify:** `crontab -l` lists the jobs; next morning the dated files exist;
after the first off-site run, the files are visible in the bucket.

---

## 14. Pre-flight checklist

**Access:**
- [ ] key login works: `ssh myvps` (port 2222, key only)
- [ ] `PermitRootLogin no`, `PasswordAuthentication no` active
- [ ] `ssh.socket` disabled (`systemctl status ssh.socket` → inactive/disabled)

**System:**
- [ ] packages updated; correct timezone
- [ ] unattended-upgrades on, `Automatic-Reboot "false"`
- [ ] swap 4G active, swappiness 10
- [ ] Docker logging driver `local`

**Network security:**
- [ ] UFW active — **only** 2222 allowed
- [ ] fail2ban sshd jail running
- [ ] compose publishes no ports (or loopback-only debug binding)
- [ ] tunnel connector HEALTHY; app loads at `https://app.YOUR_DOMAIN`
- [ ] old A/CNAME records for the hostname deleted

**Application:**
- [ ] image tag pinned to an exact version
- [ ] `.env` chmod 600, all secrets fresh random values (never reused from a
      dev machine)
- [ ] default/admin passwords changed immediately after first boot

**Backups:**
- [ ] decided which route: the app's own backup feature (§13.0) or the cron
      fallback (§13.2) — not both
- [ ] schedule active; first run produced a real, non-empty artifact
- [ ] off-site copy verified in the bucket
- [ ] restore drill done — restored into a scratch target, not production
- [ ] `compose.yaml` + `.env` copied off the server (no backup includes them)

---

## 15. Ongoing maintenance

### 15.1 Reboots after kernel updates

Security patches install themselves (§5), but kernel updates wait for a
reboot you control:

```bash
ls /var/run/reboot-required 2>/dev/null && echo "Reboot required" || echo "No reboot needed"
```

To reboot safely: `cd ~/apps/PROJECT && docker compose stop` (lets the
database flush cleanly), `sudo reboot`, reconnect after a minute,
`docker compose ps` — everything returns on its own thanks to
`restart: unless-stopped`.

### 15.2 Upgrading the app (pinned-tag procedure)

1. Read the release notes; upgrade any local/dev instance first if one exists.
2. Take a fresh backup by hand — via the app's own backup feature if it has
   one (§13.0), otherwise both cron artifacts — and confirm it reached the
   off-site bucket before touching anything.
3. Edit the tag in `compose.yaml` to the new exact version.
4. `docker compose pull app && docker compose up -d app` — only the app
   container is recreated; the database keeps running.
5. Watch `docker compose logs -f app` through its migrations.
6. Rollback = old tag back + `up -d` + restore the step-2 backup if the
   database was migrated.

If a dev machine and the server run the same app, **keep their versions in
lockstep** — many apps (NocoBase included) can only restore a backup onto
the identical version.

Occasionally also refresh the connector:
`docker compose pull cloudflared && docker compose up -d cloudflared`.

### 15.3 Schedule

| When | What |
| --- | --- |
| Weekly | reboot check (§15.1); `df -h` + `docker system df` for disk |
| Monthly | confirm off-site backups are arriving; skim app release notes |
| Quarterly | restore drill — into a scratch target, never production |
| After upgrades | `docker image prune -f` |

---

## Appendix A — the classic Caddy setup (no tunnel)

Use this only when topology C is off the table (§2): no Cloudflare, or a
hard requirement for on-server TLS. Differences from the main guide:

1. **UFW additionally opens the web ports:**

   ```bash
   sudo ufw allow 80/tcp  comment "HTTP (ACME challenges + redirect)"
   sudo ufw allow 443/tcp comment "HTTPS"
   ```

2. **No cloudflared service.** Instead, a `caddy` service in compose — the
   only service with published ports:

   ```yaml
     caddy:
       image: caddy:2
       container_name: PROJECT-caddy
       restart: unless-stopped
       networks: [PROJECT]
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
         - caddy_data:/data          # certificates live here — named volume
         - caddy_config:/config
   ```

   (add `caddy_data:` and `caddy_config:` under top-level `volumes:`)

3. **`caddy/Caddyfile`:**

   ```caddy
   {
       email you@example.com
   }
   app.YOUR_DOMAIN {
       reverse_proxy app:80
       header {
           Strict-Transport-Security "max-age=31536000; includeSubDomains"
           X-Content-Type-Options "nosniff"
           X-Frame-Options "DENY"
           Referrer-Policy "strict-origin-when-cross-origin"
       }
   }
   ```

   Caddy obtains and renews Let's Encrypt certificates automatically via the
   ACME protocol: Let's Encrypt calls back to your port 80 to verify you
   control the domain, then issues the certificate. This is why port 80 must
   be open and why DNS must already point at the server before first start.

4. **DNS:** a plain `A` record for `app.YOUR_DOMAIN` → `SERVER_IP`. If the
   domain is behind Cloudflare's orange-cloud proxy, start with SSL mode
   **Full**, wait for Caddy's "certificate obtained" log line, then switch
   to **Full (strict)** — in that order, or visitors see errors while the
   certificate doesn't exist yet.

5. Everything else in the guide (OS prep, SSH, fail2ban, Docker, swap,
   backups, maintenance) applies unchanged.
