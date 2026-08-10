# Odia Panchang API (ଓଡ଼ିଆ ପଞ୍ଜିକା)

A trusted, bilingual (Odia + English) Panchang REST API covering **Jagannath (Puri)** and **Biraja (Jajpur)** temple traditions — now with **two-layer AI enrichment** and **web interface**.

## Features

- **Web Interface** — Simple, mobile-responsive web UI for easy access
- **Multi-City Support** — Location-based Panchang for 12+ Odisha cities
- **Downloadable Calendars** — Monthly Panchang in text format for offline/print use
- **Tithi, Nakshatra, Yoga, Karana, Soura Masa, Chandra Masa, Vara** for any date (2020–2030)
- **Sunrise & Sunset** times for all major Odisha cities
- **Festival calendars** for:
  - 🛕 Jagannath Temple, Puri (Rath Yatra, Snana Yatra, Chandan Yatra, Niladri Bije, etc.)
  - 🛕 Biraja Temple, Jajpur (Maa Biraja Ashtami, Nuakhai, Shivaratri, etc.)
  - 🎉 Common Odia festivals (Pana Sankranti, Kumar Purnima, Durga Puja, etc.)
- **Pre-computed** database (SQLite) using Swiss Ephemeris with **Lahiri ayanamsa**
- Bilingual responses — every field in **Odia script (ଓଡ଼ିଆ) + English**
- **AI Enrichment** — two-layer reflection system (see below)

---

## 🌐 Web Interface

Visit the root URL (`/`) to access the mobile-friendly web interface featuring:
- Today's Panchang at a glance
- City selector for 12+ Odisha cities
- Downloadable monthly calendars
- Festival information
- Responsive design for mobile and desktop

## 📍 Supported Cities

The API now supports location-based Panchang for major cities across Odisha:
- **Puri** (ପୁରୀ) — Holy city of Lord Jagannath
- **Bhubaneswar** (ଭୁବନେଶ୍ୱର) — Capital city
- **Cuttack** (କଟକ) — Cultural capital
- **Jajpur** (ଯାଜପୁର) — Home of Maa Biraja
- **Berhampur** (ବ୍ରହ୍ମପୁର) — Silk city
- **Sambalpur** (ସମ୍ବଲପୁର) — Western Odisha hub
- **Rourkela** (ରାଉରକେଲା) — Steel city
- **Balasore** (ବାଲେଶ୍ୱର) — Northern coastal
- **Konark** (କୋଣାର୍କ) — Sun Temple
- And more...

Each city gets accurate sunrise/sunset times based on its coordinates.

---

## 🤖 AI Enrichment Layers

Add `?enriched=true` to any daily endpoint, or use `/panchang/{date}/insights` for always-enriched responses.

### Layer 1 — Astronomical (Groq / Llama-3.1-70b — Free)
- **Rahu Kalam**, **Gulika Kalam**, **Yamagandam** — inauspicious time slots
- **Abhijit Muhurta** — most auspicious midday window
- **Brahma Muhurta** — sacred pre-dawn period
- **Special yogas**: Amrit Siddhi, Sarvartha Siddhi, Siddha Yoga detection
- **Special day classification**: Ekadashi, Purnima, Amavasya, Pradosha, etc.
- Falls back to rule-based calculation if Groq key not set

### Layer 2 — Odia Cultural (Claude Haiku — ~$0.001/call)
- **Jagannath temple significance** for the day (bilingual Odia+English)
- **Biraja temple significance** for the day
- **Fasting/Vrat guidance** specific to this tithi and day
- **Auspicious activities** and what to avoid (Odia tradition)
- **Odia proverb/saying** relevant to the day
- **Seasonal context** — what's happening in Odisha right now
- **Household guidance** in Odia script

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface (HTML) |
| `GET` | `/api` | Health check |
| `GET` | `/api/cities` | List all supported Odisha cities |
| `GET` | `/api/panchang/today/{city}` | Today's Panchang for specific city |
| `GET` | `/today` | Full Panchang for today |
| `GET` | `/today?enriched=true` | Today's Panchang + AI enrichment |
| `GET` | `/panchang/{date}` | Full Panchang for a date (`YYYY-MM-DD`) |
| `GET` | `/panchang/{date}?enriched=true` | Panchang + AI enrichment |
| `GET` | `/panchang/{date}/insights` | Always-enriched Panchang with full insights |
| `GET` | `/panchang/{year}/{month}` | Full month's Panchang |
| `GET` | `/api/panchang/monthly/{year}/{month}/download` | Download monthly Panchang as text file |
| `GET` | `/festivals/{year}` | All festivals for a year |
| `GET` | `/festivals/{year}?tradition=jagannath` | Filter by tradition (`jagannath`, `biraja`, `common`, `all`) |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys (`.env`)

```env
DATABASE_URL=sqlite:///./data/panchang.db

# Layer 1: Groq (free) — https://console.groq.com/keys
GROQ_API_KEY=your_groq_key_here

# Layer 2: Claude (Anthropic) — https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_key_here
```

> **Note:** Both keys are optional. Without them, the enrichment falls back to the built-in rule-based engine (muhurtas, special yogas, day significance).

### 3. Seed the database (run once)

```bash
python3 seed.py --start 2020 --end 2030
```

### 4. Run the API

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

Open the interactive docs at: [http://localhost:8001/docs](http://localhost:8001/docs)

---

## Example Responses

### `GET /today`

```json
{
  "date": "2024-07-07",
  "vara": { "en": "Sunday", "or": "ରବିବାର" },
  "soura_masa": { "en": "Karka", "or": "କର୍କ" },
  "chandra_masa": { "en": "Ashadha", "or": "ଆଷାଢ଼" },
  "paksha": { "en": "Shukla", "or": "ଶୁକ୍ଳ" },
  "tithi": { "num": 2, "en": "Dwitiya", "or": "ଦ୍ୱିତୀୟା" },
  "nakshatra": { "en": "Ashlesha", "or": "ଆଶ୍ଲେଷା" },
  "yoga": { "en": "Vyatipata", "or": "ବ୍ୟତୀପାତ" },
  "karana": { "en": "Balava", "or": "ବାଲବ" },
  "sunrise": "05:13",
  "sunset": "18:35",
  "festivals": [
    { "name": { "en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା" }, "tradition": "common", "description": "Chariot festival of Lord Jagannath" },
    { "name": { "en": "Rath Yatra (Jagannath)", "or": "ଜଗନ୍ନାଥ ରଥ ଯାତ୍ରା" }, "tradition": "jagannath", "description": "Grand chariot procession to Gundicha Temple" }
  ]
}
```

### `GET /festivals/2024?tradition=jagannath`

Returns all Jagannath temple festivals for 2024 with dates, names (bilingual), and descriptions.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/panchang.db` | Database connection URL |

For PostgreSQL (production):
```
DATABASE_URL=postgresql://user:password@host:5432/panchang
```

---

## Technical Details

- **Astronomical Engine**: [Swiss Ephemeris](https://www.astro.com/swisseph/) via `pyswisseph`
- **Ayanamsa**: Lahiri (standard for Indian panchang)
- **Default Location**: Puri, Odisha (Lat: 19.8135°N, Lon: 85.8312°E)
- **Panchang System**: Purnimanta (traditional Odia system)
- **Database**: SQLite (pre-seeded for 2020–2030; expandable)

---

## Traditions Covered

### 🛕 Jagannath Panjika (Puri)
Chandan Yatra, Snana Yatra, Rath Yatra, Hera Panchami, Bahuda Yatra, Suna Besha, Niladri Bije, Dola Yatra, and more.

### 🛕 Biraja Panjika (Jajpur)
Maa Biraja Ashtami (Durga Puja), Nuakhai Juhar, Biraja Shivaratri, Pana Sankranti at Biraja, and more.

### 🎉 Common Odia Festivals
Pana Sankranti (Odia New Year), Kumar Purnima, Prathamastami, Gamha Purnima, Boita Bandana, Makar Sankranti, Manabasa Gurubara, and all major Hindu festivals.

---

## 🐦 Twitter Auto-Posting (free-tier friendly)

**Recommended on Render Free:** GitHub Actions wakes the service and calls `POST /tweet/post` at 05:00 IST.  
Do **not** rely on in-process APScheduler while the free web service sleeps.

See full setup: **[HOSTING_FREE_TIER.md](HOSTING_FREE_TIER.md)**

### Setup Twitter Integration

1. **Create Twitter API credentials** at [developer.twitter.com](https://developer.twitter.com)
   - Apply for **Elevated access** or **Basic tier** (required for posting tweets)
   - Note: Free tier typically only allows read operations

2. **Add credentials on the Render web service** (not only GitHub):
   ```env
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   # Optional but recommended for improved authentication:
   TWITTER_BEARER_TOKEN=your_bearer_token
   ENABLE_INPROCESS_SCHEDULER=false
   ```

3. **Enable GitHub Actions** workflow `Daily Odia Panjika Tweet` (and optional `Keep-warm free Render`).

4. **Verify setup** — Check startup logs for:
   ```
   [Panchang] Twitter/X posting: ✅ active
   [Panchang] In-process scheduler OFF (free-tier default)
   ```

### Troubleshooting Twitter Posts

If tweets aren't posting:

1. **Check the startup logs** — Look for warning messages:
   - `⚠️ TWITTER_* keys not set` → Credentials missing
   - `❌ NOT INSTALLED` → Tweepy not installed
   - `✅ active` → Credentials found

2. **Test credentials** — Run the test script:
   ```bash
   python test_twitter_credentials.py
   ```

3. **Common 401 Unauthorized issues**:
   - All 4 credentials must be from the SAME Twitter app
   - If you regenerated API keys, you must also regenerate access tokens
   - OAuth 1.0a must be enabled in app settings
   - See [TWITTER_AUTH_GUIDE.md](TWITTER_AUTH_GUIDE.md) for detailed troubleshooting

4. **Check application logs** for detailed errors:
   ```
   [Twitter] Missing credentials: consumer_key, access_token
   [Twitter] ❌ Post failed: Forbidden: 403 Forbidden
   ```

3. **Common issues**:
   - **403 Forbidden** → Twitter API access level insufficient (need Elevated/Basic tier)
   - **401 Unauthorized** → Incorrect credentials or expired tokens
   - **"Client not available"** → Credentials not set or tweepy import failed
   - **Tweets logged but not posted** → Check `logs/daily_tweets.log` — means fallback mode active

4. **Manual trigger** to test:
   ```bash
   curl -X POST https://your-api.onrender.com/tweet/post
   ```

5. **Preview without posting**:
   ```bash
   curl https://your-api.onrender.com/tweet/today
   ```

### Twitter API Access Levels

| Tier | Can Post? | Cost | Notes |
|------|-----------|------|-------|
| Free | ❌ No | $0 | Read-only access |
| Basic | ✅ Yes | $100/mo | Required for posting |
| Elevated | ✅ Yes | Free (limited) | Need to apply |

If posting fails with 403 errors, verify your Twitter developer account has write permissions.

---

A trusted odia panchang API based on Jagannath and Biraja panjika
