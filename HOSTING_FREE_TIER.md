# Hosting: GitHub Actions (no Render)

Daily Facebook + Instagram posting runs **inside GitHub Actions**. There is no
web service to keep warm and nothing to pay Render for.

```text
GitHub Actions (05:00 IST)
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

Actions → **Daily Odia Panjika** → enable. It fires at 05:00 IST
(`cron: 30 23 * * *` UTC) and can be run manually (dry-run checkbox).

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
