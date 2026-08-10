# Facebook & Instagram posting (Meta Graph API)

Odia Panjika can publish the daily panji to a **Facebook Page** and linked **Instagram Business** account.

## What gets posted

| Platform | Content |
|----------|---------|
| **Facebook Page** | Caption (Odia main + story thread) + share-card image |
| **Instagram** | Same caption + **required** public image card (4:5 PNG) |
| **X / Twitter** | Existing `/tweet/post` flow (separate) |

Card files: `static/social/cards/panjika_YYYY-MM-DD.png`  
Instagram needs `PUBLIC_API_URL` so Meta can download `https://your-host/static/social/cards/...`.

## One-time Meta setup

1. Create a [Meta developer app](https://developers.facebook.com/) with **Facebook Login** + **Instagram Graph API**.
2. Create/connect a **Facebook Page**.
3. Convert Instagram to **Business/Creator** and link it to that Page.
4. Generate a **long-lived Page access token** with permissions roughly:
   - `pages_manage_posts`, `pages_read_engagement`
   - `instagram_basic`, `instagram_content_publish`
5. Collect IDs:
   - `META_PAGE_ID` — Page ID
   - `META_PAGE_ACCESS_TOKEN` — Page token
   - `META_IG_USER_ID` — Instagram professional account ID  
     (`GET /{page-id}?fields=instagram_business_account`)

## Env on Render

```env
PUBLIC_API_URL=https://odia-panchang.onrender.com
TWEET_CRON_SECRET=...same as GitHub...
META_PAGE_ID=...
META_PAGE_ACCESS_TOKEN=...
META_IG_USER_ID=...
META_GRAPH_VERSION=v21.0
```

## API

```bash
# Preview (no publish)
curl -s "$PUBLIC_API_URL/social/preview" | jq .

# Publish FB + IG (cron secret required)
curl -s -X POST "$PUBLIC_API_URL/social/post?platforms=facebook,instagram" \
  -H "Authorization: Bearer $TWEET_CRON_SECRET" | jq .

# X + FB + IG in one call
curl -s -X POST "$PUBLIC_API_URL/social/post/all" \
  -H "Authorization: Bearer $TWEET_CRON_SECRET" | jq .
```

## Free-tier ops / GitHub Actions

```bash
python scripts/free_tier_ops.py social --url https://odia-panchang.onrender.com
python scripts/free_tier_ops.py all --url https://odia-panchang.onrender.com
```

Daily workflow posts **X**, then **Facebook + Instagram** (`continue-on-error` if Meta keys missing).

## Status

`GET /api/status` → `facebook.configured`, `instagram.configured`.

## Notes

- Without Meta env vars, posts are **logged** to `logs/daily_social.log` (status `logged`), same pattern as Twitter.
- Instagram rejects non-HTTPS or unreachable image URLs — keep the web service awake before IG publish (wake step already runs).
- Do not put Page tokens in GitHub secrets for client-side use; tokens stay on Render only.
