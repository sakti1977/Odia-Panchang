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
| `TWEET_CRON_SECRET` | **Required** for `POST /tweet/post` (Bearer). Same value in GH Actions secret |
| Optional | `TWITTER_BEARER_TOKEN`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY` |

Redeploy after env changes. Check logs for:

```text
In-process scheduler OFF (free-tier default)
```

### 2. GitHub repository

1. **Settings → Secrets and variables → Actions → Variables**  
   - Optional: `PUBLIC_API_URL` = `https://your-service.onrender.com`
2. **Settings → Secrets → Actions → Secrets**  
   - **Required:** `TWEET_CRON_SECRET` = long random string (**same** as Render env `TWEET_CRON_SECRET`)
3. Ensure workflows are enabled (**Actions** tab).
4. Run **Manual Tweet Trigger** once to verify wake + post (needs secret on both sides).
5. Optional: enable **Keep-warm free Render** if you want fewer cold starts  
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

`GET /api` returns **200** only if today’s panji row exists; otherwise **503 degraded**
(so keep-warm / monitors can notice a missing seed).

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

`start.sh` runs `python seed.py --ensure-engine`:

| Condition | Action |
|-----------|--------|
| `data/.engine_version` ≠ `ENGINE_VERSION` in `src/engine.py` | **Force reseed** astronomy + festivals for 2020–2030 |
| Versions match | Festival-only refresh (civil overrides / rules stay current) |
| Stories only (`festival_stories.py`) | No reseed — attach at API read time |

Manual:

```bash
python seed.py --force --start 2020 --end 2030   # full rewrite
python seed.py --refresh-festivals                 # festivals only
python seed.py --ensure-engine                     # same as start.sh
```

Bump `ENGINE_VERSION` whenever masa/tithi/anchor formula changes.

After reseed: `pytest tests/test_db_parity.py tests/test_eval_golden.py -q`.

## Tweet cron auth (required)

```http
POST /tweet/post
Authorization: Bearer <TWEET_CRON_SECRET>
```

Without secret → **401**. Without secret configured on server → **503**.
Rate limit: **5/hour** per IP.

## Facebook & Instagram (Meta)

See **`SOCIAL_META.md`** for full Meta app setup.

| Env | Purpose |
|-----|---------|
| `META_PAGE_ID` | Facebook Page ID |
| `META_PAGE_ACCESS_TOKEN` | Long-lived Page token |
| `META_IG_USER_ID` | Instagram Business user ID |
| `PUBLIC_API_URL` | Required for IG (public HTTPS card URL) |

```bash
# Preview card + captions
curl -s "$PUBLIC_API_URL/social/preview" | jq .

# Publish FB + IG
python scripts/free_tier_ops.py social --url "$PUBLIC_API_URL"

# X + FB + IG
python scripts/free_tier_ops.py all --url "$PUBLIC_API_URL"
```

Daily GH workflow posts X, then FB/IG (`continue-on-error` if Meta not configured).

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
