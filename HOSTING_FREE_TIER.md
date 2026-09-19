# Hosting: GitHub Actions (no Render)

Daily Facebook + Instagram posting runs **inside GitHub Actions**. There is no
web service to keep warm and nothing to pay Render for.

```text
GitHub Actions (05:17 IST, with 07:17/09:17 IST catch-ups)
  checkout + fonts + pip
  python scripts/post_daily.py
       │
       ├─ SQLite  data/panchang.db  (in this repo)
       ├─ JPEG cards
       └─ Meta Graph API ──► Facebook Page + Instagram Story
```

The FastAPI site (`main.py`) is optional. GitHub cannot host it. If Render is
charging you, **delete or suspend the Render service** — posting will keep
working from Actions.

## One-time setup

### 1. GitHub secrets (Settings → Secrets and variables → Actions)

| Secret | Purpose |
|--------|---------|
| `META_PAGE_ID` | Facebook Page ID |
| `META_PAGE_ACCESS_TOKEN` | Long-lived Page token |
| `META_IG_USER_ID` | Optional; discovered from the Page if omitted |

How to mint the Page token: **`SOCIAL_META.md`** / `python scripts/extend_meta_token.py`.

Do **not** put tokens in the repo or in Actions logs. The workflow only
forwards `secrets.*` into the job environment.

### 2. Enable the workflow

Actions → **Daily Odia Panjika** → enable. It fires at 05:17 IST
(`cron: 47 23 * * *` UTC), with two same-day catch-up attempts at 07:17 and
09:17 IST in case the primary run failed outright (e.g. an expired token —
harmless no-ops if the primary already posted). Odd minutes avoid the
2-4 hour scheduling drift GitHub Actions shows on `:00`/`:30` crons. Can
also be run manually (dry-run checkbox).

Optional: set a `NTFY_TOPIC` repo secret (any private string, e.g. a random
slug) and subscribe to that topic in the free [ntfy.sh](https://ntfy.sh) app
to get a push notification on your phone the moment a run fails — instead of
only a GitHub issue you have to remember to check.

A separate **Meta Token Health Check** workflow runs every Monday and pings
the Graph API with `META_PAGE_ACCESS_TOKEN`, filing the same alert issue (and
ntfy push) if the token has gone invalid — so a dead token gets caught
before the next daily post, not after.

### 3. Stop Render (this is what ends the bill)

1. Disable **Keep-warm free Render** (already disabled in this repo).
2. In the [Render dashboard](https://dashboard.render.com/): suspend or delete
   `odia-panjika-api`.
3. Remove any Render credit card / paid instance.

`render.yaml` stays in the repo only as a leftover blueprint if you ever want
a public API again. It is not required for daily posts.

## Local dry run

```bash
pip install -r requirements-social.txt
TEST_MODE=true python scripts/post_daily.py
# or a specific date:
TEST_MODE=true PANJIKA_DATE=2026-08-10 python scripts/post_daily.py
```

Needs `data/panchang.db` (already in the repo). No Meta keys in dry run.

## What GitHub cannot replace

| Need | On GitHub? |
|------|------------|
| Daily Facebook + Instagram | Yes (this workflow) |
| Public FastAPI / web UI | No — use a free host later, or drop it |
| GitHub Pages static site | Possible later; not wired yet |

## Troubleshooting

| Symptom | Check |
|---------|--------|
| Workflow red, Graph 190 | Token expired — `python scripts/extend_meta_token.py`, update the GitHub secret |
| Workflow green, nothing on the Page | Secrets not set; re-run **Manual Panjika Post** with dry run off |
| Odia looks like boxes on the card | `fonts-lohit-orya` step failed |
| Missing date | `data/panchang.db` not in the checkout; reseed and commit |
