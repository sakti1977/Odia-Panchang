# Free-tier hosting (Render Free + GitHub Actions)

Stay on **Render Free** without paying $7 for always-on. Daily tweets and optional keep-warm run from **GitHub Actions**.

## Architecture

```text
Users / browsers ──► Render Free web (FastAPI + SQLite)
                           ▲
                           │ wake + POST /tweet/post
GitHub Actions ────────────┘
  daily-tweet.yml   05:00 IST
  keep-warm.yml     every 12 min (optional)
```

| Component | Role |
|-----------|------|
| Render Free web | Serves API + UI; holds `TWITTER_*` secrets |
| GitHub Actions daily tweet | Wakes service, posts tweet |
| GitHub Actions keep-warm | Optional: reduces cold starts |
| In-process APScheduler | **Off by default** (`ENABLE_INPROCESS_SCHEDULER=false`) |

## One-time setup

### 1. Render dashboard (web service)

Confirm env vars (or apply `render.yaml`):

| Key | Value |
|-----|--------|
| `DATABASE_URL` | `sqlite:///./data/panchang.db` |
| `LOCATION_*` | Bhubaneswar (not Bangalore) |
| `ENABLE_INPROCESS_SCHEDULER` | `false` |
| `PUBLIC_API_URL` | your `https://….onrender.com` |
| `TWITTER_API_KEY` / `_SECRET` / `ACCESS_TOKEN` / `ACCESS_SECRET` | same Twitter app |
| Optional | `TWITTER_BEARER_TOKEN`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY` |

Redeploy after env changes. Check logs for:

```text
In-process scheduler OFF (free-tier default)
```

### 2. GitHub repository

1. **Settings → Secrets and variables → Actions → Variables**  
   - Optional: `PUBLIC_API_URL` = `https://your-service.onrender.com`
2. Ensure workflows are enabled (**Actions** tab).
3. Run **Manual Tweet Trigger** once to verify wake + post.
4. Optional: enable **Keep-warm free Render** if you want fewer cold starts  
   (uses free instance hours; one always-warm service ≈ 720 h/mo vs 750 free hours).

### 3. Verify

```bash
# Local ops script (no deps)
python scripts/free_tier_ops.py health --url https://odia-panchang.onrender.com
python scripts/free_tier_ops.py wake  --url https://odia-panchang.onrender.com
python scripts/free_tier_ops.py tweet --url https://odia-panchang.onrender.com

# API status
curl -s https://odia-panchang.onrender.com/api/status | jq .scheduler
```

Expect `scheduler.inprocess: false` and `recommended: github_actions`.

## Daily tweet timeline (IST)

| Time | What |
|------|------|
| ~04:59–05:00 | GH Actions starts (cron `30 23 * * *` UTC) |
| | Wake `GET /api` (retries for cold start) |
| | `POST /tweet/post` |
| | Preview `GET /tweet/today` |

Twitter credentials must be on **Render**, not GitHub (the server posts via Tweepy).

## Cold starts

| Situation | Experience |
|-----------|------------|
| Idle > 15 min, no keep-warm | First request ~30–60s |
| keep-warm every 12 min | Usually warm |
| Free instance hours exhausted | Service suspended until next month |

### Keep-warm decision (P2 default)

**Recommendation: leave Keep-warm enabled** for public UX (fewer 30–60s cold
starts on first API/UI hit). Free workspaces get ~750 instance-hours/month;
always-warm ≈ 720h. If Render suspends mid-month:

1. Disable **Keep-warm free Render** first (Actions → workflow → Disable).
2. Keep **Daily Odia Panjika Tweet** (one wake/day is enough for tweets).
3. Re-enable keep-warm next billing cycle if needed.

Do **not** turn on `ENABLE_INPROCESS_SCHEDULER` on Free — it does not wake a sleeping dyno.

## Database reseed policy

SQLite on Render is created at first boot (`start.sh` seeds only if DB missing).
Engine or festival-rule changes **do not** auto-reseed an existing file.

| When | Action |
|------|--------|
| Change `src/engine.py` masa/tithi logic | Local: `python seed.py --start 2020 --end 2030` (or wipe years). Deploy: delete Render disk DB **or** force reseed, then redeploy |
| Change `src/festivals.py` / `festival_civil.py` | `python seed.py --refresh-festivals --start 2020 --end 2030` (rewrites Festival rows only) |
| Stories only (`festival_stories.py`) | **No reseed** — stories attach at API read time |
| After reseed | Run `pytest tests/test_db_parity.py tests/test_eval_golden.py -q` |

**Never** commit large binary DB churn without need; CI seeds if `data/panchang.db` is empty.

## What not to do on Free

- Rely on in-process APScheduler for 5 AM tweets (process is asleep).
- Pay for Render Cron **and** free web that sleeps (use GH Actions instead).
- Leave `LOCATION_*` as Bangalore (fixed in `render.yaml`).

## Always-on later

If you upgrade to Render Starter or another always-on host:

```env
ENABLE_INPROCESS_SCHEDULER=true
```

Or keep GitHub Actions as the only tweet trigger (simpler, still works).

## Troubleshooting

| Symptom | Check |
|---------|--------|
| Workflow green but no tweet | Render logs; `TWITTER_*` on web service; `/tweet/today` → `twitter_configured` |
| Workflow fails wake | Service suspended / hours exhausted; open Render dashboard |
| 401/403 from Twitter | Same app keys; OAuth 1.0a write; see `TWITTER_AUTH_GUIDE.md` |
| Wrong sunrise | `LOCATION_*` Bhubaneswar or request `?city=puri` |
