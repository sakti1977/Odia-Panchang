# Odia Panchang — Spec

A bilingual (Odia + English) Panchang service for Odisha traditions.
Accuracy is the product. Everything else is packaging.

This file is the contract. Code implements it. `eval.md` checks it.
If code and spec disagree, fix the code — or update the spec with a dated reason.

---

## One-liner

Given a Gregorian date, optional **city**, and optional **tradition**
(`jagannath` | `biraja` | `common` | `all`), return the day’s panji elements
and the festivals that tradition would list — labeled so a devotee knows
**which school and place** were used. Never invent “official Biraja ephemeris”
or “official Khadiratna tables” we do not have.

---

## Non-negotiables (no compromise)

1. **Accuracy & authenticity** — Panji math, festival dates, and cultural text must be
   defensible against panji / temple / published sources. Prefer silence or a stub over
   a confident invention. Wrong tithi or fabricated lore is a product failure.
2. **Proper Odia script** — Every user-facing `or` field must be real Odia (ଓଡ଼ିଆ) with
   correct **yuktākṣara** (ଯୁକ୍ତାକ୍ଷର) and orthography. Never put English, Latin
   transliteration, or Devanagari body text in `or`. Never copy English into `or` as a fallback.

## Non-goals

- Not a general astrology product (no kundali, matching, predictions).
- Not a replacement for temple authorities on ritual muhurta disputes.
- Not a content farm. Do not invent temple practices or “cosmic meanings.”
- Not dependent on always-on AI. Core panji must work offline with no API keys.
- Not optimized for tweet volume. Wrong month name is worse than silence.
- **Not** a second Swiss-Ephemeris pipeline that pretends to be commercial Biraja
  or Khadiratna print tables. One sky; dual **tradition overlays**.

---

## Core idea

Most panji apps recompute or re-prompt every request and drift.
This system **compiles once** into a persistent store, then serves reads.

Four layers:

1. **Engine (one sky)** — Swiss Ephemeris, Lahiri ayanamsa, pure functions.
   Computes tithi, nakshatra, yoga, karana, masa for a place/time anchor.
2. **Place** — lat/lon/tz for sunrise, sunset, muhurtas (Puri ≠ Jajpur ≠ Bhubaneswar).
3. **Compiled store** — SQLite (`data/panchang.db`) pre-seeded for a year range.
   Base day rows; festivals attached by rules tagged with `tradition`.
4. **Presentation** — REST API, web UI, optional enrichment, optional tweets.
   Presentation may never invent astronomical facts.

You reseed when the engine changes. You never “patch” one wrong day by hand
in production without reseeding the whole range (hand patches rot).

---

## Dual tradition (Jagannath vs Biraja)

### What is true in Odisha

Printed Odia panji are not all identical. Two major lines matter for this product:

| Line | Also called | Heartland | Temple anchor |
|------|-------------|-----------|---------------|
| **Jagannath** | Khadiratna / “Jagannath panjika” (popular name) | Coastal: Puri, Khordha, Cuttack belt | Sri Jagannath, Puri |
| **Biraja** | Biraja panjika (Radharaman and related brands) | North: Jajpur, Bhadrak, Balasore; parts of Keonjhar, Mayurbhanj | Maa Biraja, Jajpur |

Shared Odia frame (both lines):

- **Civil year** is sidereal solar; Odia New Year = **Pana Sankranti** (Mesha Sankranti).
- **Religious tithi festivals** use the lunar cycle; this product’s default lunar
  naming is **Purnimanta** (month ends on Purnima; Krishna before Shukla of the
  same named month).
- Extra Odia bookkeeping: Utkaliya era, Sunia / Anka (document when shown; not required for MVP day API).

They differ mainly in:

1. **Festival overlay** (Puri niti cycle vs Biraja peetha cycle)
2. **Place used for sunrise / muhurta**
3. **Rare 1-day edge cases** in commercial print (different pandit tables) — we do
   **not** simulate those tables without digitized sources

Folk shorthand (“Biraja is solar, Jagannath is lunar”) is **emphasis and region**,
not two independent physics engines. Do not implement two ephemerides.

### Architecture rule (non-negotiable)

```text
                    ┌──────────────────────────────┐
                    │  ONE engine (Lahiri / Swiss) │
                    │  tithi, nakshatra, yoga, …   │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        city=puri            city=jajpur         city=bhubaneswar
        (jagannath default)  (biraja default)    (neutral default)
              │                    │                    │
              ▼                    ▼                    ▼
     festivals: common      festivals: common    festivals: common
          + jagannath            + biraja             + both labeled
```

| Do | Do not |
|----|--------|
| Tag every festival with `tradition` | Claim `school: "official_biraja_ephemeris"` |
| Resolve default city from tradition | Invent separate ayanamsa for Biraja |
| Label response with `place` + `tradition` + `engine` | Merge Simhadhwaja Rath into Jagannath Rath |
| Cite Tier A/C sources for peetha-unique days | Average disagreeing print panji into one day |

### Engine metadata (every day response)

Required meta block (names may match implementation):

```json
{
  "meta": {
    "engine": "lahiri_swiss_ephemeris",
    "masa_system": "purnimanta_odia_default",
    "tradition": "jagannath",
    "city": "puri",
    "lat": 19.8135,
    "lon": 85.8312,
    "tz": "Asia/Kolkata",
    "disclaimer": "Lahiri day elements at shared ~06:00 IST sample; city moves sunrise/sunset. Festival overlays follow tradition rules. Not a commercial panjika reprint.",
    "day_elements_anchor": "approx_06:00_IST_lahiri",
    "biraja_civil_status": "rule_only"
  }
}
```

`masa_system` stays `purnimanta_odia_default` until a sourced dual-masa mode exists.
Do not rename it to `biraja` or `khadiratna` without fixtures from those books.

### Tradition → default city

When `city` is omitted, resolve place from `tradition`:

| `tradition` | Default city key | Coordinates (approx) | Rationale |
|-------------|------------------|----------------------|-----------|
| `jagannath` | `puri` | 19.8135°N, 85.8312°E | Sri Mandir / coastal panji use |
| `biraja` | `jajpur` | 20.8500°N, 86.3333°E | Maa Biraja peetha |
| `common` | `bhubaneswar` | 20.2961°N, 85.8245°E | Neutral state capital |
| `all` or omitted tradition on day API | `bhubaneswar` | same | Neutral default |

When **both** `city` and `tradition` are set: **city wins for place**; tradition
only filters/selects festival overlay and cultural notes.

Invalid city key → 400 with list pointer to `/api/cities`.
Unknown tradition → 400.

Deploy env `LOCATION_*` defaults must be an **Odisha** city, never Bangalore.
Per-request city overrides env for that response’s sunrise/muhurta.

### Festival overlays

Festivals are **rules**, not free text:

- Tithi rules: `(chandra_masa, paksha, tithi_num, tradition) → festival`
- Sankranti rules: solar month boundaries (e.g. Pana Sankranti / Mesha)

| `tradition` | Contents |
|-------------|----------|
| `common` | Shared Odia / Hindu observances (Pana Sankranti, Janmashtami, Diwali, …) |
| `jagannath` | Puri cycle: Chandan start, Snana, Rath, Hera, Bahuda, Suna Besha, Niladri Bije, … |
| `biraja` | Jajpur peetha cycle: Simhadhwaja Rath, Shodasha Dinatatmika start, Nuakhai Juhar, Biraja-local days, … |
| `all` | Union of the above, each item still carrying its own `tradition` field |

**Never** collapse Biraja Simhadhwaja into “Rath Yatra” without distinct names.

Authoritative civil dates:

| Tradition | Prefer when rules and civil lists diverge |
|-----------|-------------------------------------------|
| `jagannath` | Odisha Tourism / Shree Jagannath Temple published schedule for that year |
| `biraja` | Peetha notice or **printed Biraja panjika** for that year (Tier C); do not invent |
| `common` | Drik Odia panji + standard tithi rules; Tourism for statewide holidays if needed |

If a Biraja-unique date is not sourced for year Y, **omit** it or mark
`confidence: "rule_only"` — do not fabricate a civil date from guesswork.

### Festival stories (required on every festival object)

Every festival in API responses **must** carry a short narrative so the day is
culturally legible — not only a name.

| Field | Meaning |
|-------|---------|
| `description` | One-line what/when (rule summary) |
| `story` | `{en, or}` — traditional or historical account behind the day |
| `why_today` | `{en, or}` — why this tithi/sankranti is this festival |
| `story_kind` | `puranic_tradition` \| `historical_cultural` \| `ritual_observance` |
| `story_sources` | Short source labels (not full URLs required) |
| `story_complete` | `true` if curated in `src/festival_stories.py`; `false` if honest stub |

**Rules for stories:**

1. Prefer well-known Odia / panji / temple **public** lore over AI invention.
2. Puranic material uses `story_kind=puranic_tradition` — belief, not lab history.
3. Historical-cultural days (Boita Bandana, Raja, Nuakhai, Prathamastami) use
   `historical_cultural` and stay grounded in documented custom.
4. **Never** invent secret nitis, fake miracles, or peetha “science.”
5. Missing curated story → **Odia stub** that says narrative is pending (`story_complete: false`),
   never a fabricated legend and never English-in-`or`.
6. Stories attach at **read time** from `festival_stories.py` (no reseed required to ship text).
7. Layer 2 AI may not replace or contradict curated `story` / `why_today`.
8. **Odia `or` validation** (enforced in code): must contain Odia Unicode letters; must not
   contain Latin letters or Devanagari *letters*; must not equal the English string;
   NFC-normalized. Indic danda `।` is allowed as shared punctuation.

### Cultural enrichment by tradition

- Layer 2 (if enabled) must track `tradition`: Jagannath notes for Puri nitis;
  Biraja notes for peetha practice; never invent cross-temple claims.
- Prefer curated `story` fields over free-form AI when both exist.
- Empty cultural block beats fiction.

---

## Astronomical contract

### Constants

| Item | Value |
|------|--------|
| Ayanamsa | Lahiri (`SIDM_LAHIRI`) |
| Ephemeris | Swiss Ephemeris (`pyswisseph`) |
| Neutral default place | Bhubaneswar — 20.2961°N, 85.8245°E, IST (+5:30) |
| Tradition defaults | See Dual tradition table (Puri / Jajpur / Bhubaneswar) |
| Day anchor | Civil date in IST. Core elements at a **shared ~06:00 IST** Lahiri sample (not local sunrise). City currently changes **sunrise/sunset only**. Sunrise-based day elements are future work (issue #21 Path A). |
| Tithi system | 30 tithis from Moon−Sun elongation; Shukla 1–15 then Krishna 1–15 (Amavasya = Krishna 15, never 30). |
| Lunar month system | **Purnimanta** default (`purnimanta_odia_default`) |
| Solar month | Sidereal rashi of Sun (Mesha…Meena) |

### Required fields per day

Every day object must expose bilingual fields:

- `date` (ISO `YYYY-MM-DD`)
- `meta` (engine, masa_system, tradition, city, lat, lon — see above)
- `vara` (weekday)
- `tithi` `{num, en, or}` with `num` in 1–15 and paksha separate
- `paksha` `Shukla` | `Krishna`
- `nakshatra`, `yoga`, `karana`
- `soura_masa`, `chandra_masa`
- `sunrise`, `sunset` as `HH:MM` local to the **resolved** place
- `festivals[]` (may be empty); each item has `tradition`, `description`, `story`, `why_today`

Missing data → hard error (404/empty seed), not a hallucinated filler day.

### Accuracy priorities (descending)

1. **Tithi identity at the day anchor** (name + paksha + number)
2. **Nakshatra identity**
3. **Chandra masa name under Purnimanta** (critical; has failed before)
4. **Festival attachment** for the **requested** tradition (Jagannath and Biraja both)
5. **Yoga, karana**
6. **Sunrise/sunset** within ±2 minutes of a reference for the **same** lat/lon
7. **Muhurtas** from sunrise/sunset rules for that place
8. **AI cultural copy** — never overrides 1–7

### Hard rules

- Amavasya is always Krishna 15, never tithi 30.
- Do not rename months with a magic `+2` offset unless every golden case in `eval.md` still passes.
- City-specific sunrise must use that city’s coordinates.
- One Lahiri engine only; no fake dual-ephemeris “Biraja mode.”
- Engine change ⇒ reseed full range ⇒ run eval suite. Partial DB edits forbidden for masa/tithi fixes.

---

## API surface

### Endpoints (contract)

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/` | Web UI |
| GET | `/api` | Health `{status: ok}` |
| GET | `/api/status` | Engine/AI/twitter status; include default city/tradition if set |
| GET | `/today` | Today’s panji; query: `city`, `tradition`, `enriched` |
| GET | `/panchang/{YYYY-MM-DD}` | Day panji; query: `city`, `tradition`, `enriched` |
| GET | `/panchang/{year}/{month}` | Month panji; same query params |
| GET | `/festivals/{year}` | Festivals; query: `tradition` (`jagannath`\|`biraja`\|`common`\|`all`) |
| GET | `/api/cities` | Supported cities (include keys `puri`, `jajpur`, `bhubaneswar`, …) |
| GET | `/api/panchang/today/{city}` | Today for path city; query: `tradition`, `enriched` |
| GET | `/panchang/{date}/insights` | Always-enriched; still must not override base fields |
| POST | `/tweet/post` | Manual tweet; use resolved default place in text |

No API key for basic panji. Rate-limit abuse; never rate-limit into silent wrong data.

### Query parameters (day / month / today)

| Param | Values | Default |
|-------|--------|---------|
| `tradition` | `jagannath` \| `biraja` \| `common` \| `all` | `all` for festival filter on day payloads that include festivals; place default uses `common` → Bhubaneswar when city omitted |
| `city` | key from `/api/cities` | From tradition table if omitted |
| `enriched` | `true` \| `false` | `false` |

**Resolution order for place:**

1. Explicit `city` query or path param  
2. Else tradition default city  
3. Else Bhubaneswar  

**Resolution for festival list on a day response:**

| `tradition` | Include |
|-------------|---------|
| `all` (default) | `common` + `jagannath` + `biraja` (each labeled) |
| `jagannath` | `common` + `jagannath` |
| `biraja` | `common` + `biraja` |
| `common` | `common` only |

Rationale: devotees using “Jagannath mode” still want shared Odia days (e.g. Ekadashi labels if present) plus Puri cycle; pure peetha-only filter is available via `/festivals/{year}?tradition=biraja` without `common` if product later adds `include_common=false`. For v1:

- Day API: `jagannath` ⇒ common+jagannath; `biraja` ⇒ common+biraja  
- Festivals API: exact filter as today (`tradition=biraja` returns only biraja rows)

Document this split in OpenAPI descriptions.

### Example requests (sketch — target contract)

```http
GET /today
GET /today?city=puri&tradition=jagannath
GET /today?city=jajpur&tradition=biraja
GET /panchang/2026-07-16?tradition=jagannath&city=puri
GET /panchang/2026-10-01?tradition=biraja&city=jajpur
GET /festivals/2026?tradition=jagannath
GET /festivals/2026?tradition=biraja
GET /api/panchang/today/jajpur?tradition=biraja
```

### Example day response (sketch)

```json
{
  "meta": {
    "engine": "lahiri_swiss_ephemeris",
    "masa_system": "purnimanta_odia_default",
    "tradition": "jagannath",
    "city": "puri",
    "lat": 19.8135,
    "lon": 85.8312,
    "tz": "Asia/Kolkata",
    "disclaimer": "Lahiri day elements at shared ~06:00 IST sample; city moves sunrise/sunset. Festival overlays follow tradition rules. Not a commercial panjika reprint.",
    "day_elements_anchor": "approx_06:00_IST_lahiri",
    "biraja_civil_status": "rule_only"
  },
  "date": "2026-07-16",
  "vara": { "en": "Thursday", "or": "ଗୁରୁବାର" },
  "paksha": { "en": "Shukla", "or": "ଶୁକ୍ଳ" },
  "tithi": { "num": 2, "en": "Dwitiya", "or": "ଦ୍ୱିତୀୟା" },
  "chandra_masa": { "en": "Ashadha", "or": "ଆଷାଢ଼" },
  "soura_masa": { "en": "Mithuna", "or": "ମିଥୁନ" },
  "nakshatra": { "en": "…", "or": "…" },
  "yoga": { "en": "…", "or": "…" },
  "karana": { "en": "…", "or": "…" },
  "sunrise": "05:15",
  "sunset": "18:30",
  "festivals": [
    {
      "name": { "en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା" },
      "tradition": "common",
      "description": "Chariot festival of Lord Jagannath…",
      "story": { "en": "…Gundicha / Indradyumna tradition…", "or": "…" },
      "why_today": { "en": "Ashadha Shukla Dwitiya — main chariot day.", "or": "…" },
      "story_kind": "puranic_tradition",
      "story_sources": ["Puri Ratha Yatra tradition"],
      "story_complete": true
    }
  ]
}
```

### Response invariants

- Astronomical fields come only from engine/DB for the resolved place.
- `enrichment` is a separate object; clients may ignore it.
- If enrichment fails, base panji still returns 200.
- `meta.city` / lat/lon always reflect the place used for sunrise.
- Festival `tradition` field is always present on each festival item.
- Festival `story` + `why_today` always present (curated or honest stub).

### Implementation status

1. `tradition` + `city` on day endpoints — **done**  
2. `meta` block on day payloads — **done**  
3. `puri` / `jajpur` + major Odisha cities — **done**  
4. No second ephemeris module — **done** (one Lahiri engine)  
5. Festival stories + Odia purity — **done**  

Ship API shape even if some Biraja civil goldens are still `rule_only`.

---

## Enrichment (optional)

### Layer 1 — rule-first muhurtas

- Rahu / Gulika / Yamagandam by 8-way day split (standard weekday slots).
- Abhijit around midday; Brahma before sunrise.
- Use sunrise/sunset of the **resolved city**.
- Groq/LLM may validate or label, never replace slot math.

### Layer 2 — cultural text

- Allowed: well-known festival notes for the active tradition, generic vrat guidance, proverbs marked as such.
- Forbidden: invented nitis, fake peetha claims, cross-temple fiction.
- On doubt: omit.

---

## Twitter / X (optional)

- Summary of computed panji for a **stated place** (default Bhubaneswar or configured).
- Must not claim “per Biraja panjika” or “per Khadiratna” unless that source was used.
- Credentials missing → log only. Never pretend success.
- Prefer external cron over sleep-prone free-tier in-process schedulers.

---

## Data lifecycle

```
seed.py (engine → SQLite) → API reads SQLite + festival rules → UI/tweet present
```

- Supported seed range: at least current year−1 through current year+4 (repo may ship 2020–2030).
- Commit or release artifact must match the engine version that produced it.
- Migration: delete DB, reseed, run `eval.md` suite — no in-place month renames.
- Festival rules live in code (`src/festivals.py`); reseed attaches them — changing only rules may require reseed or re-attach job as implemented.

---

## Hosting principles

- Prefer cheap always-on or static+cron over paid sleep-prone free tiers.
- Health check must fail if DB missing or empty for “today.”
- Config defaults: Odisha coordinates. Deploy manifests must not ship Bangalore by mistake.

---

## Definition of done

A change is done only when:

1. It matches this spec (including dual-tradition labeling).
2. `eval.md` golden cases for the touched domain pass.
3. No silent fallback that hides missing data as success.
4. README / OpenAPI examples match real outputs for a sample date **with meta**.

---

## Known debt (do not paper over)

1. ~~Chandra masa `+2`~~ — fixed: closing-Purnima Purnimanta; see `tests/test_chandra_masa.py`.
2. ~~DB lag~~ — reseed after masa fix (2020–2030).
3. ~~Deploy Bangalore~~ — `render.yaml` defaults to Bhubaneswar.
4. **AI layer** can still fabricate culture text if keys set and prompts weaken.
5. **Hosting** — Render free tier may sleep/suspend; prefer always-on host + `.github/workflows/daily-tweet.yml`.
6. ~~Day API `tradition` + `meta`~~ — wired on `/today`, `/panchang/{date}`, city today.
7. **Biraja peetha civil dates** need printed-panji / peetha sources year by year; rule-only until sourced.
8. **Commercial print 1-day edges** between Khadiratna and Biraja books are out of scope until digitized.
9. **2025 Rath civil date** — Wikipedia 27 Jun vs engine Ashadha Shukla 2 = 26 Jul (adhika/authority); documented in tests.

---

## Success metric

A devotee in Puri (Jagannath mode) and a devotee in Jajpur (Biraja mode) each see:

- Correct tithi/masa under the declared Lahiri engine (shared IST sample; sun times place-local)  
- The **right festival overlay** for their tradition  
- An honest **meta** line that does not pretend to be a commercial panjika reprint  

If we cannot be sure, we show less, not more.
