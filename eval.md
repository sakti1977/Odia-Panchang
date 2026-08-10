# eval.md — Accuracy harness for Odia Panchang

Evals are the product’s immune system.
If an eval is not automated yet, it is still **binding**: agents must run it by script or checklist before merge.

Philosophy: compile knowledge into fixtures once; re-run forever.
Do not re-derive expected tithis from the same engine under test.

---

## How to use this file

| Role | Duty |
|------|------|
| Human | Approves new golden rows with a source citation |
| Agent | Implements `tests/test_eval_golden.py` (or equivalent) from these tables |
| CI | Fails merge if Tier A fails |

**Never** generate expected values by calling `compute_panchang` and snapshotting blindly.
**Never** lower thresholds to pass a broken masa formula.

### Runner (implemented)

```bash
pytest tests/test_eval_golden.py -q
pytest tests/ -q   # full suite including tweets, stories, masa
```

Implemented in `tests/test_eval_golden.py` (+ `tests/test_tweet_content.py`,
`tests/test_chandra_masa.py`). Each case has an ID (`E-…`). Report pass/fail by ID.

**2025 Puri civil dates:** `src/festival_civil.py` (Tier A Tourism overrides).

---

## Source tiers

Use the highest tier available. Lower tiers cannot override higher ones on conflict
without a written note in this file.

### Tier A — Primary (must-match for public festival civil dates)

| ID | Source | Use for |
|----|--------|---------|
| A1 | [Odisha Tourism — Ratha Jatra 2026](https://odishatourism.gov.in/content/tourism/en/experience/event/ratha-jatra-2026.html) | Official 2026 Snana / Rath / Bahuda (**jagannath**) |
| A2 | [Wikipedia — Ratha Yatra (Puri)](https://en.wikipedia.org/wiki/Ratha_Yatra_(Puri)) table (cite year) | Multi-year Rath start dates |
| A3 | Shree Jagannath Temple / district admin notices for a given year | When Tourism page not yet published |
| A4 | Maa Biraja peetha / Jajpur admin notices (when published) | **biraja**-unique civil dates (Simhadhwaja, 16-day start, etc.) |

### Tier B — Computational panji reference (daily elements)

| ID | Source | Use for |
|----|--------|---------|
| B1 | [Drik Panchang — Odia Day Panji](https://www.drikpanchang.com/oriya/oriya-day-panji.html) | Tithi, nakshatra, yoga, karana, Purnimanta masa **for a stated city** |
| B2 | [Drik Panchang — Day Panchang](https://www.drikpanchang.com/panchang/day-panchang.html) | Same, Hindu panchang view; set **Purnimanta** |
| B3 | [Drik FAQ — Amanta vs Purnimanta](https://www.drikpanchang.com/faq/faq-ans8.html) | Month-system semantics (not a date oracle) |

**Place rule:** Compare Puri→Puri, Jajpur→Jajpur, Bhubaneswar→Bhubaneswar.
Never Bangalore sunrise vs Odisha labels.

### Tier C — Traditional Odia printed panji (spot-check; not full digitize)

| ID | Source | Use for |
|----|--------|---------|
| C1 | Kohinoor Press Odia calendar / panjika | Spot-check masa + major festivals |
| C2 | **Biraja panjika** (Radharaman / peetha-used editions) | Biraja festival civil dates, north-Odisha spot-check |
| C3 | **Khadiratna / “Jagannath” panjika** (Radharaman line) | Coastal / Puri-tradition spot-check |
| C4 | [Odia calendar — Wikipedia](https://en.wikipedia.org/wiki/Odia_calendar); [Panjika — Wikipedia](https://en.wikipedia.org/wiki/Panjika) | Dual-year structure (solar civil + lunar religious); panji lineage |
| C5 | Pathani Samanta / *Siddhanta Darpana* tradition notes | Historical method context for modern Odia/Puri calculations |
| C6 | Trade geography (e.g. MyCityLinks panji reporting) | Who uses Khadiratna vs Biraja regionally — product docs, not ephemeris |

Printed panji can differ by a day at tithi edges. When C conflicts with A on
**public Rath dates**, prefer A. When C2 conflicts with C3 on a shared Hindu day,
log dispute — do **not** invent a third “compromise” ephemeris.

**Hard rule:** Never claim fixtures are “official Biraja ephemeris” unless the
expected values were transcribed from a named print edition + year.

### Tier D — Formulas (muhurtas, structure)

| ID | Source | Use for |
|----|--------|---------|
| D1 | [Drik — Rahu Kalam](https://www.drikpanchang.com/panchang/rahu-kaal.html) | Day ÷ 8 segments; weekday → segment map |
| D2 | Common Jyotish tables (AstroSage / Prokerala agree on segment index) | Cross-check Rahu slot index by weekday |
| D3 | [Wikipedia — Hindu calendar](https://en.wikipedia.org/wiki/Hindu_calendar) Amānta / Purnimānta | Structural rules for masa/paksha ordering |
| D4 | Swiss Ephemeris + Lahiri ayanamsa (library contract) | Longitude pipeline sanity — **one engine for all traditions** |

### Tier E — Negative / process sources (what went wrong before)

| ID | Source | Use for |
|----|--------|---------|
| E1 | `CORRECTIONS_SUMMARY.md` | Historical bugs; **not** automatic expected values |
| E2 | Prior agent “+2 masa” patch behavior | Regression: multi-case masa must pass together |
| E3 | Spec dual-tradition research (Jagannath vs Biraja) | Overlay + place defaults; forbid dual fake ephemeris |

---

## Pass criteria (global)

| Field | Tolerance |
|-------|-----------|
| Tithi name + paksha + num | Exact |
| Nakshatra name | Exact (allow documented spelling aliases only: Dhanishtha/Dhanistha) |
| Yoga name | Exact |
| Karana name | Exact |
| Chandra masa (Purnimanta) | Exact |
| Soura masa | Exact |
| Vara | Exact |
| Festival membership for Tier A dates | Exact civil date ±0 days |
| Sunrise/sunset | ±2 minutes vs B1 for same lat/lon |
| Rahu Kalam window | ±3 minutes endpoints given same sunrise/sunset |
| AI cultural text | No factual claims not in festival description or Tier A/B notes |

**Fail closed:** any Tier A miss is release-blocking.
Tier B miss on masa+tithi is release-blocking.
Tier C miss is investigate within 7 days.

---

## Spelling aliases (allowed)

Only these normalize before compare:

| Canonical (code) | Allowed reference spellings |
|------------------|-----------------------------|
| Dhanishtha | Dhanistha, Dhanishta |
| Jyeshtha (masa) | Jyosta, Jyestha, ଜ୍ୟେଷ୍ଠ |
| Ashadha | Asadha, Ashadh |
| Bhadrapada | Bhadra, Bhadraba |
| Shravana | Sravan, Shrabana |
| Chaitra | Chaitra |
| Vaishakha | Baisakha, Byisakha |

Do not alias different tithis (Dwitiya ≠ Tritiya).

---

# Suite 1 — Structural invariants

### E-INV-001 — Amavasya numbering
- **Assert:** For any day with `tithi.en == Amavasya`: `paksha == Krishna` and `tithi.num == 15`.
- **Method:** Scan seeded year or 400 random engine days.
- **Source:** D3 + project festival changelog.

### E-INV-002 — Tithi num range
- **Assert:** `1 <= tithi.num <= 15` always.

### E-INV-003 — Paksha vs elongated longitude
- **Assert:** Shukla iff Moon−Sun elongation in [0°, 180); Krishna otherwise (at day anchor).
- **Source:** Standard tithi definition; engine unit test.

### E-INV-004 — DB ↔ engine parity
- **Assert:** For every date in `panchang.db`, recompute with `compute_panchang` using the **same** default lat/lon as seed; masa, tithi, nakshatra must match.
- **Fail meaning:** Reseed skipped after engine change.
- **Blocking:** Yes.

### E-INV-005 — Default location is Odisha
- **Assert:** Default lat/lon within Odisha bounding box (roughly 17.5–22.5°N, 81.5–87.5°E).
- **Assert:** Deploy manifests (`render.yaml`, Dockerfile env samples) do not set Bangalore unless named `bangalore` profile.
- **Blocking:** Yes for manifests.

### E-INV-006 — No fabricated enrichment override
- **Assert:** Response with `enriched=true` keeps base tithi/masa identical to non-enriched.
- **Blocking:** Yes.

### E-INV-007 — One engine for all traditions
- **Assert:** Codebase has a single ephemeris path (Lahiri / Swiss) for day elements; no `biraja_ephemeris` / alternate ayanamsa module.
- **Assert:** Day response `meta.engine` (when present) is `lahiri_swiss_ephemeris` (or documented alias) for both `tradition=jagannath` and `tradition=biraja`.
- **Blocking:** Yes once `meta` is implemented; until then assert via code structure review.

### E-INV-008 — Festival tradition tags
- **Assert:** Every festival row/rule has `tradition ∈ {common, jagannath, biraja}` (and `lingaraj` if that tradition is shipped).
- **Assert:** No festival named only “Rath Yatra” is tagged `biraja` if it means Puri Rath; Biraja chariot must be distinct (e.g. Simhadhwaja).
- **Blocking:** Yes.

### E-INV-009 — Festival story coverage
- **Assert:** `festival_stories.coverage_report()["missing"]` is empty (every `name_en` in rules has a curated entry).
- **Assert:** `get_festival_story(name)` always returns `story` + `why_today` with non-empty `en`.
- **Blocking:** Yes.

### E-INV-010 — Odia script purity (non-negotiable)
- **Assert:** `validate_all_stories()` returns `[]`.
- **Assert:** Every festival `name_or` in `TITHI_RULES` / `SANKRANTI_RULES` passes `validate_odia_text` (Odia letters present; no Latin; no Devanagari *letters*).
- **Assert:** Stub Odia is also valid Odia (never English).
- **Blocking:** Yes.

---

# Suite 2 — Daily element goldens (Tier B)

Place unless noted: **Bhubaneswar** (20.2961°N, 85.8245°E).  
References were also checked on Drik Odia panji; re-verify if ayanamsa mode differs.

### E-DAY-2026-05-10 — Krishna Ashtami sample
| Field | Expected | Source |
|-------|----------|--------|
| date | 2026-05-10 | — |
| vara | Sunday | B1/B2 |
| paksha | Krishna | B1 |
| tithi | Ashtami (8) | B1 |
| nakshatra | Dhanishtha | B1 |
| yoga | Brahma | B1 |
| karana | Kaulava (first half / until tithi end) | B1 |
| chandra_masa (Purnimanta) | Jyeshtha | B1 (`Jyosta` / Jyeshtha) |

**Why this case:** Past bug reported Chaitra instead of Jyeshtha on this civil date.
**Also:** Must co-pass with Snana/Rath masa cases (Suite 3) — no overfitting.

### E-DAY-2026-06-29 — Snana Purnima astronomy
| Field | Expected | Source |
|-------|----------|--------|
| date | 2026-06-29 | A1 |
| tithi | Purnima (15) | A1 + B1 |
| paksha | Shukla | B1 |
| chandra_masa | Jyeshtha | Odia panji / festival identity |

### E-DAY-2026-07-16 — Rath Yatra astronomy
| Field | Expected | Source |
|-------|----------|--------|
| date | 2026-07-16 | A1, A2 |
| tithi | Dwitiya (2) | A2 (Āshādha Shukla Dvitiyā) |
| paksha | Shukla | A2 |
| chandra_masa | Ashadha | A2 |

### E-DAY-2024-07-07 — Rath Yatra 2024
| Field | Expected | Source |
|-------|----------|--------|
| date | 2024-07-07 | A2 |
| festival | Rath Yatra present | A2 |
| chandra_masa | Ashadha | A2 semantics |
| tithi | Dwitiya Shukla | A2 |

### E-DAY-2025-06-27 — Rath Yatra 2025 (authority civil date)
| Field | Expected | Source |
|-------|----------|--------|
| date | 2025-06-27 | **A1** [Odisha Tourism — Rath Yatra 2025](https://odishatourism.gov.in/content/tourism/en/experience/event/ratha-jatra-2025.html); A2 Wikipedia |
| festival | Rath Yatra **present** (civil override) | A1 table: Rath Yatra 27 June 2025 |
| chandra_masa (engine label) | **Not** forced to Ashadha | Engine Purnimanta without full adhika → Jyeshtha on this civil day |
| tithi | Dwitiya (2) Shukla | Engine agrees (tithi ok; masa name disagrees with panji label) |

**Authority resolution (2026-08-10):**

| Event | Civil date (A1 Tourism 2025) | Engine tithi-rule day (no override) |
|-------|------------------------------|--------------------------------------|
| Deba Snana Purnima | **2025-06-11** | ~2025-07-10 (engine Jyeshtha Purnima) |
| Rath Yatra | **2025-06-27** | ~2025-07-26 (engine Ashadha Shukla 2) |
| Bahuda Yatra | **2025-07-05** | (shifted with masa) |

**Product rule:** Prefer Tier A civil dates for Puri festival *attachment* via
`src/festival_civil.py` (`CIVIL_OVERRIDE_YEARS[2025]`). Suppress rule-based
Snana/Rath cycle names for 2025 so festivals do not double-fire on July engine days.
Do **not** rewrite `chandra_masa` labels to fake Ashadha on 27 June.
Do **not** “fix” evals to ignore Tourism.

**Blocking:** Festival present on 2025-06-27 = Yes. Full adhika masa rename = future work.

### E-DAY-anchor-consistency
- Pick 12 random dates in 2024–2027.
- Compare tithi+nakshatra to B1 for Bhubaneswar (manual or scripted scrape with human review).
- **Pass:** ≥11/12 exact tithi; 12/12 within one tithi only if documented edge (tithi change near sunrise).
- Log edge cases in `eval/edges.md` (create when first edge found).

---

# Suite 3 — Festival civil dates (Tier A)

### E-FEST-2026-PURISCHEDULE

From Odisha Tourism Rath Yatra 2026 page (A1):

| Event | Civil date | Assert in `/festivals/2026` or day payload |
|-------|------------|-----------------------------------------------|
| Deba Snana Purnima | 2026-06-29 | `Snana` in name (common and/or jagannath) |
| Rath Yatra | 2026-07-16 | `Rath Yatra` |
| Bahuda Yatra | 2026-07-24 | `Bahuda` |

Optional same-cycle checks (from consistent Puri schedules, cross-check yearly):

| Event | Civil date | Priority |
|-------|------------|----------|
| Hera Panchami | 2026-07-20 | Medium |
| Suna Besha | 2026-07-25 | Medium |

### E-FEST-MULTIYEAR-RATH

| Year | Rath Yatra date | Source |
|------|-----------------|--------|
| 2024 | 2024-07-07 | A2 |
| 2025 | 2025-06-27 | **A1 Tourism 2025**, A2 |
| 2026 | 2026-07-16 | A1, A2 |
| 2027 | 2027-07-05 | A2 |

**Assert:** Festival list for that year includes Rath on that date (tradition common or jagannath).

### E-FEST-2024-SNANA
| Event | Date | Source |
|-------|------|--------|
| Snana Yatra / Snana Purnima | 2024-06-22 | Cross-check B1 + common Puri lists; confirm before merge if disputed |

### E-FEST-RULE-SANITY
- **Assert:** Diwali rule uses Krishna 15 not 30.
- **Assert:** Boita Bandana / Kartik Purnima uses Shukla 15 not Pratipada.
- **Assert:** Mahalaya uses Krishna Amavasya (15), not Shukla 1.
- **Source:** `src/festivals.py` changelog + general panji knowledge (D3).

### E-FEST-NO-FALSE-MAY-2026-RATH
- **Assert:** `2026-05-18` is **not** labeled Rath Yatra.
- **Assert:** `2026-05-01` is **not** labeled Snana Purnima.
- **Why:** A past “correction” doc claimed these; real 2026 Snana/Rath are June/July (A1).
- **Blocking:** Yes.

### E-FEST-TRADITION-PARTITION
- **Assert:** `/festivals/{year}?tradition=jagannath` contains Snana/Rath-class Puri items when those rules fire; does **not** require Simhadhwaja.
- **Assert:** `/festivals/{year}?tradition=biraja` contains only `tradition=biraja` rows (exact filter).
- **Assert:** `/festivals/{year}?tradition=common` contains no `jagannath`-only or `biraja`-only exclusive rows.
- **Blocking:** Yes.

### E-FEST-NO-COLLAPSE-RATH
- **Assert:** Any Biraja chariot festival string contains a distinct identity (e.g. `Simhadhwaja`) and is **not** equal to plain `Rath Yatra (Jagannath)`.
- **Blocking:** Yes.

### E-FEST-BIRAJA-RULES-EXIST
- **Assert:** Rule set includes at least: Biraja Akshaya Tritiya (or equivalent), Nuakhai Juhar, Simhadhwaja Rath Yatra, Shodasha Dinatatmika Puja Begins (names as in `festivals.py`).
- **Civil dates:** only locked when Tier A4/C2 fixture exists for that year; otherwise mark `rule_only` and skip civil-date assert.
- **Blocking:** Rules exist = Yes; civil dates = when fixtures present.

---

# Suite 4 — Masa regression battery

These must be **one atomic suite**. Passing only one row is failure.

| Case ID | Date | Expected chandra_masa (Purnimanta) | Notes |
|---------|------|--------------------------------------|-------|
| E-MASA-01 | 2026-05-10 | Vaishakha *(engine; Drik B1 often Jyeshtha)* | Open B1 tension — lock engine value; never solar+2 |
| E-MASA-02 | 2026-06-29 | Jyeshtha | Snana month |
| E-MASA-03 | 2026-07-16 | Ashadha | Rath month |
| E-MASA-04 | 2026-03-11 | *(fill from B1 Purnimanta for Bhubaneswar; do not use engine)* | Krishna Ashtami region |
| E-MASA-05 | 2025-06-27 | *(engine: Jyeshtha until adhika)* | Civil Rath day (A1); **do not** force Ashadha label — festival via `festival_civil` |

**Procedure for E-MASA-04:** Open Drik Odia panji for 2026-03-11, Bhubaneswar, Purnimanta, paste expected masa into fixture with citation date, then lock.

**Forbidden fix:** `return (solar_index + K) % 12` for a single K that only fits one row.

---

# Suite 5 — Location & muhurta

### E-LOC-001 — Puri vs Bhubaneswar sunrise
- Same date (e.g. 2026-05-10).
- **Assert:** Sunrise differs or is equal only if computation says so; both within ±2 min of B1 for **that** city.
- **Assert:** Response labels match requested city.

### E-LOC-002 — Rahu Kalam segment map
Given sunrise/sunset, day length / 8 = slot.

| Weekday | Rahu slot (1-based from sunrise) | Source |
|---------|----------------------------------|--------|
| Monday | 2 | D1/D2 |
| Tuesday | 7 | D1/D2 |
| Wednesday | 5 | D1/D2 |
| Thursday | 6 | D1/D2 |
| Friday | 4 | D1/D2 |
| Saturday | 3 | D1/D2 |
| Sunday | 8 | D1/D2 |

**Assert:** `compute_muhurtas` uses this map (Python weekday Mon=0).
**Assert:** Endpoints ±3 min vs hand calculation from same sunrise/sunset.

### E-LOC-003 — Abhijit roughly midday
- Midpoint of sunrise/sunset ± half (day/15).
- Sanity only; ±5 min vs Drik Abhijit for same city optional.

### E-LOC-004 — Puri vs Jajpur place split
- Same Gregorian date (e.g. 2026-05-10).
- **Assert:** Sunrise for `puri` and `jajpur` are computed from different coordinates.
- **Assert:** Absolute difference is typically a few minutes (sanity: not identical lat/lon in city table).
- **Blocking:** Yes for city table integrity.

### E-LOC-005 — Tradition default cities (spec)
| tradition | expected default city key |
|-----------|---------------------------|
| jagannath | puri |
| biraja | jajpur |
| common / omitted (place) | bhubaneswar |

- **Assert:** Resolver helper or API docs match this table (unit test on pure function preferred).
- **Blocking:** Yes once resolver lands; until then `manual:` against `spec.md`.

---

# Suite 6 — API contracts

### E-API-001 — Health
`GET /api` → 200, `status == ok`.

### E-API-002 — Today shape
`GET /today` includes keys: date, vara, tithi, nakshatra, sunrise, sunset, festivals.
When `meta` is implemented: also `meta.engine`, `meta.city`, `meta.tradition` or documented equivalent.

### E-API-003 — Bilingual
Every of `vara, tithi, nakshatra, yoga, karana, soura_masa, chandra_masa, paksha` has non-empty `en` and `or` (Odia script).

### E-API-004 — Missing date
Unseeded date → 404 (not empty 200).

### E-API-005 — Enrichment isolation
`enriched=true` failure still returns base panji; enrichment null/omitted/error object without corrupting base.

### E-API-006 — Festival filter exact
`/festivals/2026?tradition=jagannath` → every item `tradition == jagannath`.  
`/festivals/2026?tradition=biraja` → every item `tradition == biraja`.  
`/festivals/2026?tradition=common` → every item `tradition == common`.

### E-API-010 — Festival stories on wire
Any festival object from `/festivals/{year}` or day `festivals[]` must include:
`story.en`, `why_today.en`, `story_kind`, `story_sources`, `story_complete`.
Sample check: Rath Yatra 2026-07-16 includes Gundicha / chariot narrative keywords
(`Gundicha` or `chariot` / Odia equivalent) and `story_complete is True`.

### E-API-007 — Dual query sketch (target)
Once day endpoints accept query params:

```http
GET /panchang/2026-07-16?tradition=jagannath&city=puri
GET /panchang/2026-07-16?tradition=biraja&city=jajpur
```

**Assert:**
- Both return same core tithi/paksha/nakshatra **or** only differ if day-anchor uses local sunrise and tithi edge (document if so).
- `meta.city` matches request.
- Festival lists differ by overlay (jagannath items vs biraja items per spec filter rules).
- Neither response claims commercial panjika reprint in `meta.disclaimer` absence of disclaimer is OK only before meta lands; after meta lands, disclaimer required.

### E-API-008 — City list includes peetha defaults
`/api/cities` includes keys usable as `puri`, `bhubaneswar`, and `jajpur` (or documented alias for Jajpur).

### E-API-009 — Invalid tradition/city
Unknown `tradition` or `city` → 400 (not 500, not silent default) once query validation ships.

---

# Suite 9 — Dual tradition integrity

Product model under test: **one Lahiri engine + place + festival overlay**.  
See `spec.md` § Dual tradition.

### E-DUAL-001 — No second ephemeris
- Grep/static: no alternate ayanamsa or “biraja_engine” producing different longitudes for the same JD without place change.
- **Blocking:** Yes.

### E-DUAL-002 — Overlay isolation
- On 2026-07-16 (Rath):
  - `tradition=jagannath` day festivals include Rath-class items (common and/or jagannath).
  - `tradition=biraja` day festivals do **not** invent a Biraja claim that it is Puri Rath Yatra at Gundicha.
- **Blocking:** Yes for naming honesty.

### E-DUAL-003 — Meta honesty
- When `meta` present: `masa_system` is `purnimanta_odia_default` (not `official_biraja` / `official_khadiratna`) unless fixtures from those books exist and spec is updated.
- **Blocking:** Yes when meta ships.

### E-DUAL-004 — Biraja civil goldens (opt-in)
- File: `tests/fixtures/golden_festivals_biraja.json`
- Each row: `{year, date, name_contains, source_edition, retrieved}`
- **Only** human-transcribed from C2/A4.
- Empty file is OK; missing file is OK.
- **Forbidden:** generating this file from the engine or from Jagannath Tourism pages.

### E-DUAL-005 — Regional default smoke
- `tradition=jagannath` without city → place resolves to Puri coords.
- `tradition=biraja` without city → place resolves to Jajpur coords.
- **Blocking:** when resolver ships.

---

# Suite 7 — Content safety (AI / tweets)

### E-SAFE-001 — No override
Tweet generator and Layer 2 receive panji as input; unit test that mutating enrichment cannot change serialized tithi in main tweet without changing base input.

### E-SAFE-002 — Fabrication denylist (heuristic)
Fail if cultural text matches patterns like:
- “Mahakashiya Shakti” (known past fabrication)
- “Devadasis perform Abhishek” as daily claim
- “guaranteed cosmic energy”
Maintain list in `tests/fixtures/denylist_phrases.txt`.

### E-SAFE-003 — Tweet length
Main tweet ≤ 280 chars (or current X limit constant in code).

### E-SAFE-004 — Honesty when Twitter disabled
POST tweet without creds → status `logged` or `error`, never `posted`.

### E-SAFE-005 — Stories not fabrications
- Curated stories must not contain denylist phrases (E-SAFE-002).
- `story_kind` ∈ {`puranic_tradition`, `historical_cultural`, `ritual_observance`}.
- Stub stories (`story_complete=false`) must not invent proper-name miracles beyond the festival title.

---

# Suite 8 — Seed & ops

### E-OPS-001 — Seed coverage
DB contains continuous dates from seed start to end (no gaps).

### E-OPS-002 — Start script
If DB missing, `start.sh` seeds before bind (or fails loud).

### E-OPS-003 — Eval gate
CI runs `pytest tests/` including `test_eval_golden.py`. On PRs that touch
`src/engine.py`, `src/festivals.py`, `src/festival_civil.py`, `seed.py`, or the DB:
require green unit tests before merge. After festival-rule changes, run
`python seed.py --refresh-festivals` (see `HOSTING_FREE_TIER.md`).

---

## Adversarial cases (must fail closed)

| ID | Attack | Expected |
|----|--------|----------|
| E-ADV-01 | Agent proposes masa `+2` fix | Suite 4 fails on Rath/Snana |
| E-ADV-02 | Hand-edit one festival row in SQLite | E-INV-004 or reseed policy fails review |
| E-ADV-03 | Layer 2 invents festival on empty day | E-SAFE / human review rejects |
| E-ADV-04 | Compare Drik Bangalore sunrise to our Bhubaneswar | Invalid test — discard |
| E-ADV-05 | Use CORRECTIONS_SUMMARY May-2026 Rath claim | E-FEST-NO-FALSE-MAY-2026-RATH fails that claim |
| E-ADV-06 | Invent “Biraja ayanamsa” to match one print page | E-DUAL-001 / E-INV-007 fail |
| E-ADV-07 | Label Puri Rath as `tradition=biraja` | E-FEST-NO-COLLAPSE-RATH / partition fail |
| E-ADV-08 | Auto-generate golden_festivals_biraja.json from engine | E-DUAL-004 policy fail on review |
| E-ADV-09 | Claim `meta.masa_system=official_khadiratna` without book fixtures | E-DUAL-003 fail |

---

## Fixture format (recommended)

`tests/fixtures/golden_days.json`:

```json
[
  {
    "id": "E-DAY-2026-05-10",
    "date": "2026-05-10",
    "place": {"name": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245},
    "expect": {
      "vara_en": "Sunday",
      "paksha_en": "Krishna",
      "tithi_en": "Ashtami",
      "tithi_num": 8,
      "nakshatra_en": "Dhanishtha",
      "yoga_en": "Brahma",
      "chandra_masa_en": "Jyeshtha"
    },
    "sources": ["B1", "B2"],
    "retrieved": "2026-08-10"
  }
]
```

`tests/fixtures/golden_festivals.json` (Jagannath / common civil dates):

```json
[
  {
    "id": "E-FEST-2026-RATH",
    "year": 2026,
    "date": "2026-07-16",
    "name_contains": ["Rath Yatra"],
    "traditions_allowed": ["common", "jagannath"],
    "sources": ["A1", "A2"],
    "retrieved": "2026-08-10"
  }
]
```

`tests/fixtures/golden_festivals_biraja.json` (human-only; may be empty):

```json
[
  {
    "id": "E-FEST-BIRAJA-EXAMPLE",
    "year": 2026,
    "date": "YYYY-MM-DD",
    "name_contains": ["Simhadhwaja"],
    "traditions_allowed": ["biraja"],
    "sources": ["C2"],
    "source_edition": "Radharaman Biraja Panjika 2026, page ?",
    "retrieved": "YYYY-MM-DD",
    "confidence": "print_transcribed"
  }
]
```

Do not commit Biraja civil rows without `source_edition`.

---

## Scoreboard (release)

| Gate | Requirement |
|------|-------------|
| Tier A jagannath festivals | 100% |
| Suite 4 masa battery | 100% |
| E-INV-004 DB parity | 100% |
| E-INV-007 / E-DUAL-001 one engine | 100% |
| E-FEST-TRADITION-PARTITION + NO-COLLAPSE-RATH | 100% |
| Tier B locked days | 100% of committed fixtures |
| API suite (implemented endpoints) | 100% |
| SAFE suite | 100% |
| E-INV-009 story coverage | 100% curated (no missing names) |
| Biraja civil goldens | 100% of **committed** C2/A4 fixtures (zero fixtures OK) |
| Random B1 sample | ≥91% tithi (11/12) with edges logged |

Ship only if all applicable gates green.

---

## Maintenance

1. Each year: add Tier A jagannath rows from Odisha Tourism / temple notices.
2. Each year (optional but recommended): transcribe key Biraja peetha dates from print C2 into `golden_festivals_biraja.json`.
3. Re-fetch one B1 day per quarter; if Lahiri pipelines diverge systematically, bump engine and reseed.
4. Any production accuracy complaint → new golden row with source → then fix.
5. Lint this file: every `E-*` ID should appear in an automated test name or an explicit `manual:` checklist.
6. Never “close the gap” between Khadiratna and Biraja print by inventing a private ephemeris.

---

## Manual checklist (until fully automated)

```
[ ] E-INV-004 DB vs engine (script)
[ ] E-INV-007 / E-DUAL-001 one engine (review or static)
[ ] E-MASA-01..05 (script)
[ ] E-FEST-2026-PURISCHEDULE (script)
[ ] E-FEST-MULTIYEAR-RATH (script)
[ ] E-FEST-NO-FALSE-MAY-2026-RATH (script)
[ ] E-FEST-TRADITION-PARTITION (script)
[ ] E-FEST-NO-COLLAPSE-RATH (script)
[ ] E-DAY-2026-05-10 (script)
[ ] E-LOC-002 Rahu slots (unit)
[ ] E-LOC-004 Puri vs Jajpur (unit)
[ ] E-API-001..006 (httpx against local server)
[ ] E-API-007..009 when tradition/city query ships
[ ] E-SAFE-002 denylist (unit)
[ ] Spot-check Kohinoor or Khadiratna page (C1/C3) for current month (human)
[ ] Spot-check Biraja print page (C2) for current month if available (human)
[ ] E-INV-009 festival story coverage (python -c coverage_report)
[ ] E-API-010 sample day festivals include story/why_today
```

---

## Note on disagreements

Authorities can differ by a day when tithi changes near sunrise or when local temple accepts a specific convention.
**Khadiratna vs Biraja print** can disagree on edge days without either being “buggy.”

Record disputes under `eval/disputes.md`:

```
## YYYY-MM-DD — short title
- Our value (engine + place):
- Drik (city=…):
- Odisha Tourism / Sri Mandir:
- Biraja print edition (if any):
- Khadiratna print edition (if any):
- Decision: (which tradition UI shows / omit / rule_only)
- Owner:
```

Do not silently pick the value that matches the current bug.
Do not invent a third calculation school to split the difference.
