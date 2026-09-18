# Facebook & Instagram posting (Meta Graph API)

Daily Odia Panjika publishes to a **Facebook Page** (feed photo + caption) and a
linked **Instagram professional** account (**Story** by default). Twitter/X is an
optional leftover (`POST /tweet/post`).

This matches the Bengali panjika bot: multipart JPEG upload, Instagram ingest
via the Facebook photo CDN, duplicate-post fingerprint, no retry on publish.

## What gets posted

| Platform | Content |
|----------|---------|
| **Facebook Page** | Caption (Odia, ≤2200 chars) + 4:5 JPEG share card |
| **Instagram** | 9:16 Story by default (`INSTAGRAM_AS_STORY=true`). Set `false` for a feed post with the same caption. |
| **X / Twitter** | Optional leftover `/tweet/post` — not the daily path |

Card files: `static/social/cards/panjika_YYYY-MM-DD.jpg` (feed) and
`panjika_YYYY-MM-DD_story.jpg` (story). Instagram does **not** fetch these from
`PUBLIC_API_URL`; the server uploads the JPEG to Facebook and reuses the CDN
URL (litterbox fallback if Meta's crawler cannot fetch the CDN).

## One-time Meta setup

Instagram's publishing API does not work with a personal Instagram account. The
Page ↔ Instagram Professional link is required.

1. Create or pick a Facebook Page (for example "ଓଡ଼ିଆ ପଞ୍ଜିକା").
2. In the Instagram app: Settings → Account type and tools → switch to **Professional** (Business or Creator).
3. Link that Instagram account to the Facebook Page (Meta Business Suite → Pages → connected assets).
4. Create a Meta app at [developers.facebook.com](https://developers.facebook.com/apps/) (type: Business). Add **Facebook Login for Business** and **Instagram**. Add yourself as an app admin.
5. In [Graph API Explorer](https://developers.facebook.com/tools/explorer/):
   - Generate a **User** token with: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `business_management`.
6. Exchange for a long-lived User token, then a never-expiring Page token:

```bash
# put META_APP_ID, META_APP_SECRET, META_USER_ACCESS_TOKEN in .env
python scripts/extend_meta_token.py
```

The script writes `META_PAGE_ID` and `META_PAGE_ACCESS_TOKEN` into `.env` and
prints only expiry facts, never the token.

7. Confirm the linked Instagram account (optional — the poster discovers it):

```bash
curl "https://graph.facebook.com/v22.0/PAGE_ID?fields=instagram_business_account&access_token=PAGE_ACCESS_TOKEN"
```

The returned `instagram_business_account.id` is `META_IG_USER_ID`.

## Env — GitHub Actions secrets (not Render)

Daily posting runs `python scripts/post_daily.py` in GitHub Actions. Put these
in **Settings → Secrets and variables → Actions**:

```text
META_PAGE_ID
META_PAGE_ACCESS_TOKEN
META_IG_USER_ID          # optional; discovered from the Page if omitted
```

Local `.env` is fine for `python scripts/extend_meta_token.py` and a laptop dry
run. Do not commit `.env`.

Optional: `INSTAGRAM_AS_STORY=true` (workflow default).

## Local / Actions commands

```bash
# Dry run (no publish)
TEST_MODE=true python scripts/post_daily.py

# Publish from this checkout (needs META_* in the environment)
python scripts/post_daily.py
```

Daily workflow **Daily Odia Panjika** posts Facebook + Instagram at 05:00 IST.
Use **Manual Panjika Post** with “Dry run” checked to preview in Actions logs.

Duplicate-post prevention is layered:

1. GitHub Actions cache keyed by IST date
2. Recent-caption fingerprint (`🌸 ଓଡ଼ିଆ ପଞ୍ଜିକା | {date}`) so a retry after
   Facebook succeeded and Instagram failed does not double-post to Facebook

A partial failure keeps the workflow **red** so the next run can finish the
missing side. Reads are retried; publishes are not.

## Troubleshooting

1. **Meta Graph API error (code 190 / OAuthException)**
   - Re-run `python scripts/extend_meta_token.py`
   - Update the GitHub secret `META_PAGE_ACCESS_TOKEN`
   - Confirm the Facebook user is an admin of both the app and the Page
2. **Instagram skipped, or `(#10) Application does not have permission`**
   - Instagram must be a Professional account linked to the same Facebook Page
   - Token needs `instagram_basic` and `instagram_content_publish`
   - In Development mode, the Page admin must also have a role on the Meta app
3. **Instagram: image_url / media container ERROR**
   - Instagram only accepts JPEG, 4:5 to 1.91:1 (feed) or 9:16 (Stories)
   - The poster uploads JPEG to Facebook and reuses that CDN URL
4. **Workflow green but nothing on the Page**
   - `META_PAGE_ID` and `META_PAGE_ACCESS_TOKEN` must be GitHub Actions secrets
   - Re-run **Manual Panjika Post** with dry run off
   - Check the Actions log for Graph errors (tokens are not printed)
