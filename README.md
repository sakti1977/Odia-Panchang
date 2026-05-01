# Odia Panchang API (ଓଡ଼ିଆ ପଞ୍ଜିକା)

A trusted, bilingual (Odia + English) Panchang REST API covering **Jagannath (Puri)** and **Biraja (Jajpur)** temple traditions.

## Features

- **Tithi, Nakshatra, Yoga, Karana, Soura Masa, Chandra Masa, Vara** for any date (2020–2030)
- **Sunrise & Sunset** times for Puri, Odisha
- **Festival calendars** for:
  - 🛕 Jagannath Temple, Puri (Rath Yatra, Snana Yatra, Chandan Yatra, Niladri Bije, etc.)
  - 🛕 Biraja Temple, Jajpur (Maa Biraja Ashtami, Nuakhai, Shivaratri, etc.)
  - 🎉 Common Odia festivals (Pana Sankranti, Kumar Purnima, Durga Puja, etc.)
- **Pre-computed** database (SQLite) using Swiss Ephemeris with **Lahiri ayanamsa**
- Bilingual responses — every field in **Odia script (ଓଡ଼ିଆ) + English**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api` | Health check |
| `GET` | `/today` | Full Panchang for today |
| `GET` | `/panchang/{date}` | Full Panchang for a date (`YYYY-MM-DD`) |
| `GET` | `/panchang/{year}/{month}` | Full month's Panchang |
| `GET` | `/festivals/{year}` | All festivals for a year |
| `GET` | `/festivals/{year}?tradition=jagannath` | Filter by tradition (`jagannath`, `biraja`, `common`, `all`) |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database (run once)

```bash
python3 seed.py --start 2020 --end 2030
```

### 3. Run the API

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

A trusted odia panchang API based on Jagannath and Biraja panjika
