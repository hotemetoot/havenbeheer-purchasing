# Claude Code Desktop + NocoBase CLI — Setup & Workflow Guide

**Project:** Havenbeheer Purchasing  
**Author:** Alexander / TTGA  
**Last updated:** May 2026

---

## Overview

This guide covers how to set up Claude Code Desktop to work with NocoBase via the `nb` CLI, how to use Git to safely track your project, and the day-to-day workflow for building and promoting changes from your local development environment to production.

### The full picture

```
Claude Code Desktop (Code tab)
        ↓
   nb CLI (NocoBase CLI)
        ↓
Local NocoBase — Docker/Colima  ←── development happens here
        ↓
  Migration Manager
        ↓
Production NocoBase — VPS       ←── config promoted here manually
```

Claude Code only ever touches your local Docker instance. Promotion to production is a deliberate manual step you control.

---

## Part 1 — Prerequisites

Before starting, make sure the following are available on your Mac:

- **Node.js** version 22 or higher  
  Check: `node --version`
- **npm** (comes with Node.js)  
  Check: `npm --version`
- **Claude Desktop app** installed and signed in with a paid plan (Pro or Max)
- **Local NocoBase** running in Docker via Colima  
  Check: visit `http://localhost:13000` in your browser — you should see the NocoBase login screen
- **Git**  
  Check: `git --version`  
  If not installed on macOS, run `xcode-select --install` and follow the prompts

---

## Part 2 — Install the NocoBase CLI

Open a terminal (or use the integrated terminal in the Code tab with `Ctrl+\``) and run:

```bash
npm install -g @nocobase/cli@beta
```

Verify the installation:

```bash
nb --version
```

### Connect the CLI to your local NocoBase instance

Run the visual setup wizard:

```bash
nb init --ui
```

Your browser opens automatically. In the wizard:

1. **Start Configuration** — choose **"Connect to Existing Application"**
2. **Enter API Address** — enter `http://localhost:13000/api` (adjust the port if yours differs)
3. **Authentication** — choose OAuth for the quickest setup
4. Give the environment a name, e.g. `havenbeheer-dev`

The CLI saves this connection to `~/.nocobase/config.json`. Every `nb` command going forward uses `-e havenbeheer-dev` to target this environment.

### Verify the connection

```bash
nb api resource list --resource users -e havenbeheer-dev
```

If you get a list of users back, the connection is working.

### Check that NocoBase Skills were installed

Skills are knowledge packages that teach Claude Code how NocoBase works — field types, API shapes, workflow structure, permissions. They are installed automatically by `nb init`.

```bash
nb skills check
```

If nothing shows, install them manually:

```bash
nb skills install
```

---

## Part 3 — Set up Git for your project

Git is a checkpoint system for your project folder. It lets you save named snapshots of your work and return to any of them later.

### One-time setup

Navigate to your project folder and initialize a Git repository:

```bash
cd "/Users/alexander/Documents/Claude/Projects/Havenbeheer Purchasing"
git init
git config user.name "Alexander"
git config user.email "mf.alexander@gmail.com"
```

### Create a .gitignore file

This tells Git which files to never track. Create a file called `.gitignore` in your project folder with the following content:

```
# Binary office files — tracked manually if needed
*.docx
*.xlsx
*.xls
*.doc

# System files
.DS_Store
Thumbs.db

# NocoBase local environment files
.nocobase/
```

### Make your first commit

```bash
git add .
git commit -m "Initial commit — design docs and project setup"
```

You now have your first checkpoint.

---

## Part 4 — Start a Claude Code Desktop session

1. Open the **Claude Desktop app** and click the **Code** tab
2. In the prompt area, configure:
   - **Environment:** Local
   - **Project folder:** select your `Havenbeheer Purchasing` folder
   - **Permission mode:** start with **Plan mode** (switch to Auto accept edits once you're comfortable)
3. Type your task and press Enter

### Using your design docs as context

In the Code tab you can reference files with `@`. Claude reads them directly:

```
@"havenbeheer PR — permissions and guards.md"
Review this design and plan the nb CLI commands needed to create 
the PurchaseRequest collection in NocoBase env havenbeheer-dev. 
Don't execute anything yet.
```

Review the plan, then switch to **Auto accept edits** and say "execute the plan."

### Useful keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+\`` | Open/close integrated terminal |
| `Cmd+;` | Open side chat (ask a question without derailing the session) |
| `Ctrl+O` | Cycle view modes (Normal / Verbose / Summary) |
| `Cmd+Shift+D` | Toggle diff view |
| `Esc` | Stop Claude mid-task |

---

## Part 5 — Git daily workflow

### The core habit: commit before and after every significant task

**Before starting work:**
```bash
git add .
git commit -m "Checkpoint before starting [task name]"
```

**After finishing work:**
```bash
git add .
git commit -m "Completed [task name]"
```

### How to write a good commit message

Keep it short and descriptive. Say what changed, not how:

```
# Good
git commit -m "Added PurchaseRequest collection with line items relation"
git commit -m "Updated approval workflow — added finance manager step"
git commit -m "Permissions design for PR creator and approver roles"

# Not useful
git commit -m "changes"
git commit -m "update"
git commit -m "wip"
```

### Check what's changed since your last commit

```bash
git status          # which files have changed
git diff            # what exactly changed in those files (text files only)
```

### See your full history

```bash
git log --oneline
```

Output looks like:

```
a3f9c12 Added PurchaseRequest collection with line items
b8e1204 Updated approval workflow design
c2d7f91 Permissions design for PR creator and approver roles
f4a8b03 Initial commit — design docs and project setup
```

Each line is a commit. The seven-character code (e.g. `a3f9c12`) is its ID.

---

## Part 6 — How to restore a previous state

### Scenario A: You want to look at an old version of a file

```bash
git log --oneline                          # find the commit ID you want
git show a3f9c12:path/to/file.md           # view that file at that commit
```

This doesn't change anything — it just shows you the old content.

### Scenario B: Restore one file to a previous state

```bash
git checkout a3f9c12 -- path/to/file.md
```

This replaces the current file with the version from that commit. Your other files are untouched. Then commit the restoration:

```bash
git commit -m "Restored file.md to version from [date]"
```

### Scenario C: Claude Code made a mess — undo everything since your last commit

This is the most common recovery scenario. It throws away all uncommitted changes and returns your folder to exactly the state of your last commit:

```bash
git checkout .
```

> **Important:** this is permanent for any uncommitted changes. This is why the habit of committing before starting a task matters — it gives you a clean restore point.

### Scenario D: Roll back to a specific earlier commit (keep history)

If you want to fully undo several commits and return to an earlier state, but keep the history intact:

```bash
git revert --no-commit a3f9c12..HEAD
git commit -m "Rolled back to state at [description]"
```

This creates a new commit that undoes everything back to `a3f9c12`. Safer than deleting history.

---

## Part 7 — Promoting changes to production

This is a manual step — Claude Code never touches your production VPS directly.

### Pre-flight checklist before promoting

- [ ] All changes committed in Git (`git status` shows nothing pending)
- [ ] Tested the feature in local NocoBase
- [ ] Production NocoBase version matches local version
- [ ] Backup Manager plugin is installed and active on production
- [ ] `.env` variables are consistent between local and production (especially `DB_UNDERSCORED`, `DB_TABLE_PREFIX`)

### The promotion process

1. In your **local NocoBase** UI: go to **Migration Manager → New Migration**
2. Select the appropriate migration rule (Schema-only for structure, Upsert for config data)
3. Download the generated `.nbdata` file
4. On your **production VPS**: upload the file and run it via **Migration Manager → Execute Migration**
   - The system auto-backs up production before applying
   - Review the environment variable and plugin checks — don't skip them
5. Verify the result in production

### CLI alternative for production (if you have SSH access)

```bash
yarn nocobase migration run /path/to/migration_file.nbdata
```

### If something goes wrong in production

The Migration Manager creates an automatic backup before every migration. Use the Backup Manager to restore it. See the Migration Manager rollback documentation for the full procedure.

---

## Part 8 — Recommended session workflow

This is the sequence to follow for every build session:

1. **Commit your current state** — `git add . && git commit -m "Checkpoint before [task]"`
2. **Open Code tab** — set environment to Local, project folder to your Havenbeheer folder
3. **Start in Plan mode** — let Claude map out the approach first
4. **Review the plan** — ask questions via side chat (`Cmd+;`) if needed
5. **Switch to Auto accept edits** — let Claude execute
6. **Review the diff** — check what changed before moving on
7. **Test in local NocoBase** — confirm the result in the browser
8. **Commit the result** — `git add . && git commit -m "Completed [task]"`

---

## Quick reference

### nb CLI commands you'll use most

```bash
nb app start -e havenbeheer-dev          # start the local NocoBase app
nb app stop -e havenbeheer-dev           # stop it
nb app logs -e havenbeheer-dev           # view logs
nb env update havenbeheer-dev            # refresh CLI runtime commands
nb api resource list --resource users -e havenbeheer-dev   # test connection
nb skills list                           # check installed NocoBase skills
nb skills sync                           # reinstall/update skills
```

### Git commands you'll use most

```bash
git status                               # what has changed
git add .                                # stage all changes
git commit -m "your message"             # save a checkpoint
git log --oneline                        # view history
git diff                                 # see what changed in detail
git checkout .                           # discard all uncommitted changes
git checkout abc1234 -- path/to/file     # restore one file from a commit
```
