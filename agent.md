# agent.md — Operating manual for coding agents

You are working on **Odia Panchang**: a trust-sensitive panji API.
Read `spec.md` and `eval.md` before changing calculation or festival code.

This file is the schema for how you behave in this repo — not a user README.

---

## Mission

Ship **correct** Odia panji. Prefer boring correctness over features.
If accuracy and convenience conflict, accuracy wins.

---

## Read order (every non-trivial task)

1. `spec.md` — product contract  
2. `eval.md` — golden cases and pass criteria  
3. Touch only the files required for the task  
4. Run the relevant evals before claiming done  

Do not treat `CORRECTIONS_SUMMARY.md` or old TEST_*.md as ground truth without
checking `eval.md` sources — some “fixes” were overfit to single dates.

---

## Permission boundary

| You may | You must not |
|---------|----------------|
| Edit engine, festivals, API, UI, seed, tests | Invent festival dates without a cited source |
| Add fixtures under `tests/` or `eval/` | Commit secrets (`.env`, API keys, Twitter tokens) |
| Reseed `data/panchang.db` after engine fixes + eval green | “Hotfix” one DB row for a wrong masa/tithi |
| Improve prompts to **reduce** fabrication | Let Layer 2 override tithi/masa/nakshatra |
| Propose hosting changes | Deploy/push production without human OK if irreversible |
| Refactor for clarity when it reduces bug surface | Drive-by refactors unrelated to the task |

---

## Principles (Karpathy-style)

1. **Think before coding** — For calendar math, state the formula and which golden cases it must pass. If two cases conflict under a proposed formula, stop and ask.
2. **Simplicity first** — Smallest change that fixes the bug. No new framework.
3. **Surgical diffs** — Do not reformat whole files. Do not rewrite working festival lists for style.
4. **Goal-driven** — Done = eval green + spec still true. Not “tests exist.”
5. **No silent success** — Missing DB, missing city, failed tweet → explicit error/status. Never 200 with fake panji.
6. **Say when wiki/spec has no answer** — If a ritual detail is unknown, omit it; do not synthesize temple lore.

### Absolute non-negotiables

- **Accuracy / authenticity** — Never invent tithi, masa, festival civil dates, or temple lore. Stub or ask.
- **Odia script** — Every `or` string is real Odia with proper yuktākṣara. No English fallback in `or`.
  No Devanagari body text. Run `validate_all_stories()` / tests before merging story edits.
  Prefer a short correct Odia sentence over long broken Odia.

---

## Domain landmines (read carefully)

### Chandra masa (highest risk)

- Odisha panji uses **Purnimanta** naming for lunar months in this product.
- Shukla paksha month names align with Amanta; **Krishna paksha month names differ**.
- A constant solar-index offset (`+2`) is **not** an acceptable fix unless every festival golden case in `eval.md` passes.
- After any masa change: reseed full range, then run festival + masa evals.

### Tithi numbering

- API `tithi.num` is 1–15 within paksha.
- Amavasya = Krishna **15**, never 30.
- Festival rules use the same convention (`src/festivals.py`).

### Place

- Default: **Bhubaneswar** (or Puri if product decides — document in spec).
- `render.yaml` / host env must not ship Bangalore as default.
- City endpoints must change sunrise/sunset; do not only relabel the city name.

### Festivals

- Rules live in `src/festivals.py`.
- Major Puri dates (Snana, Rath, Bahuda, …) must match `eval.md` Tier A sources.
- If engine masa is wrong, festivals look “randomly wrong” — fix engine first.

### Dual tradition (Jagannath vs Biraja)

- **One** Lahiri/Swiss engine for all traditions. Never invent a “Biraja ephemeris.”
- Differ by: **place** (Puri / Jajpur / Bhubaneswar) + **festival overlay** + labels.
- Defaults (when city omitted): `jagannath`→Puri, `biraja`→Jajpur, `common`→Bhubaneswar.
- Do not collapse Simhadhwaja into Jagannath Rath.
- Biraja civil dates only from print/peetha sources (`eval.md` Tier C2/A4); otherwise `rule_only`.
- Day responses should carry honest `meta` (engine, masa_system, tradition, city) per `spec.md`.

### Festival stories

- Every festival needs `story` + `why_today` via `src/festival_stories.py` (not AI freewrite).
- When adding a festival rule, add a curated story in the same PR (`coverage_report()` must stay empty missing list).
- Prefer traditional/public lore; use `story_kind` honestly; stubs beat inventions.
- Odia prose must pass `validate_odia_text` / `validate_all_stories()` — correct conjuncts (ଯୁକ୍ତାକ୍ଷର), NFC, no Latin in `or`.

### AI layers

- Layer 1 math is rule-based; LLM is optional commentary.
- Layer 2 must not assert specific temple nitis without sources.
- Prefer deleting a sentence to polishing a guess.

---

## Workflows

### Bug: wrong tithi / nakshatra / masa

```
1. Reproduce with compute_panchang(date) and DB row for same date
2. Compare engine vs DB — if diverge, reseed was skipped
3. Compare against eval.md golden + Drik Odia panji for that date/place
4. Fix engine formula (not a one-off if)
5. python seed.py --start YYYY --end YYYY
6. Run eval suite; commit code + DB together
```

### Bug: wrong festival date

```
1. python scripts/audit_festivals.py            (which festivals/years disagree)
2. Check the rule tuple (festivals.py, Purnimanta month) and its kala (festival_calendar.KALA)
3. Check Tier A (tests/fixtures/golden_festivals.json) and the Drik reference fixture
4. Fix the rule / kala with a classical justification — never tune to one year
5. Knife-edge disagreement with a source → festival_civil.DATE_CORRECTIONS (cited)
6. python seed.py --refresh-festivals; pytest tests/test_festival_dates.py
```

### Festival-date upkeep (yearly — see eval.md § E-FEST-REFERENCE)

```
January        Odisha Government holiday list → Tier A rows (A1)
Before Snana   Temple / Tourism Puri schedule → Tier A rows
By 1 October   python scripts/fetch_festival_reference.py --start Y --end Y+4; review diff
Any time       festival-confirm issue → confirm from a panjika, add a Tier A row
```

### Feature: new API field

```
1. Spec first (add to spec.md)
2. Implement
3. Add eval assertion
4. Keep bilingual en+or where user-facing
```

### Hosting / social reliability

```
1. Panji correctness is independent of host
2. Prefer external cron over in-process scheduler on sleep-prone free tiers
3. Daily path is Facebook + Instagram (POST /social/post); do not retry publishes
```

---

## Commands

```bash
# setup
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# seed
python seed.py --start 2024 --end 2030

# run API
uvicorn main:app --host 0.0.0.0 --port 8001

# smoke
python test_app.py

# preferred: implement and run tests described in eval.md
# e.g. pytest tests/ -q   (once harness exists)
```

---

## File map

| Path | Role |
|------|------|
| `spec.md` | Product contract |
| `eval.md` | Golden cases, sources, pass/fail |
| `agent.md` | This file — agent discipline |
| `src/engine.py` | Swiss Ephemeris panji math |
| `src/festivals.py` | Festival rules |
| `src/translations.py` | en/or names |
| `src/ai_layer1.py` | Muhurtas + optional LLM validate |
| `src/ai_layer2.py` | Cultural enrichment (skeptical) |
| `src/locations.py` | City coordinates |
| `seed.py` | Compile engine → SQLite |
| `data/panchang.db` | Compiled store (must match engine) |
| `main.py` | FastAPI |
| `src/meta_poster.py` | Facebook Page + Instagram Graph client |
| `src/social_card.py` | 4:5 feed JPEG + 9:16 story JPEG |
| `src/lunar_calendar.py` | New moons, Amanta months + Adhika, Purnimanta labels, sankranti instants |
| `src/festival_calendar.py` | Festival civil day per year/place (tithi interval, kala, Adhika, sankranti cutoff) |
| `src/festival_audit.py` | Audit vs reference + Tier A; publication gate for social posts |
| `src/festival_civil.py` | Tier A metadata + reviewed DATE_CORRECTIONS (no overrides) |
| `src/odisha_heritage.py` | Curated "ଜାଣନ୍ତୁ ଓଡ଼ିଶା" daily heritage entries (sourced, Odia-validated) |
| `src/local_day.py` | SQLite day loader for GitHub Actions (no FastAPI) |
| `scripts/post_daily.py` | Daily FB+IG entrypoint |
| `render.yaml` | Optional API host leftover (verify LOCATION_*) |

---

## Output discipline

When you finish a task, report:

1. What changed (files)  
2. Which eval IDs passed  
3. Whether reseed was required and done  
4. Residual risk (e.g. adhika masa year not covered)  

If eval cannot pass, say **BLOCKED** and why — do not ship a green narrative on a red suite.

---

## Anti-patterns

- “Looks right for May 10” without Snana/Rath/Diwali cases  
- Updating only `CORRECTIONS_SUMMARY.md` without tests  
- Using AI to generate expected tithi values  
- Matching Bangalore Drik times while labeling Bhubaneswar  
- Expanding scope into kundali / predictions  
- Quietly weakening eval tolerances to get CI green  
- Dual ephemeris / fake “official Biraja tables” without digitized books  
- Claiming commercial panjika fidelity in API copy without fixtures  

---

## When unsure

Ask the human. Calendar authorities disagree at edges (tithi at sunrise vs moonset,
adhika masa naming). Surface the disagreement; do not pick the answer that is
easier to code.
