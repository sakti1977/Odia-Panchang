# Festival-date disputes and open items

Format per eval.md § "Note on disagreements". Newest first. Each entry says
what the product does today and what would change it.

## 2026-10-18 — Durga Ashtami 2026 (resolved 2026-09-26: 18 Oct, maintainer-confirmed)
- Our value (festival_calendar, midday rule): **18 Oct** (Ashtami 18 Oct 08:28 → 19 Oct 10:52).
- Drik (Bhubaneswar): Mahastami **19 Oct** (udaya Ashtami).
- Odisha Government 2026 list: Mahasaptami 17 Oct, Mahanavami 19 Oct, Vijaya Dashami 20 Oct;
  18 Oct is a Sunday and is not listed — implies Ashtami 18 Oct but does not state it.
- Decision: **18 Oct**. The maintainer confirmed it, and it is recorded as Tier A row
  E-FEST-2026-DURGA-ASHTAMI, so it is now announced.
- Owner: maintainer.

## Reviewed corrections (festival_civil.DATE_CORRECTIONS)
- **Akshaya Tritiya / Chandan Yatra 2023** — engine 23 Apr, published **22 Apr** (Drik, both
  pages). Tritiya lasts 145 min after the 23 Apr sunrise against the 144-min trimuhurta
  threshold — inside ephemeris error.
- **Gamha Purnima 2022, 2023** — engine 12 Aug / 31 Aug, published **11 Aug / 30 Aug**
  (Drik). Purnima covers neither forenoon; Drik follows the Rakhi (Bhadra-aware afternoon)
  convention. Confirm against the Odisha Government lists for those years.

## Sankranti day cutoff (monitoring)
- Odia sankranti falls on the civil date of the transit unless the transit is after about
  21:13–21:32 IST, then the next day (all 132 transits 2020–2030 fit with no overlap). The
  classical cutoff inside that band is not established; `festival_calendar.sankranti_edge_cases()`
  lists transits inside it. None fall in the band for 2020–2030.

## Janmashtami (rule not fully modelled)
- Smarta nishita Ashtami matches the Odisha Government lists (15 Aug 2025, 4 Sep 2026) and
  Drik's Smarta dates in 2020/22/23/25/28. In 2021/27/29/30 Drik keeps the next day because
  of Rohini-nakshatra (Jayanti) conditions this engine does not model. Those years are not
  announced until a Tier A row confirms them.

## Rules with no independent reference (not announced in posts)
Pradosha Vrat, Sankashti Chaturthi, Durga Shashthi, Niladri Bije, Adhara Pana, Gundicha
Marjana, Nava Jaubana Darshan, Jhulana Yatra, Ashokastami / Rukuna Rath, Banajaga Jatra,
Simhadhwaja Rath Yatra, Shodasha Dinatatmika Puja, Biraja Shashthi, Sitala Shashthi (Biraja),
Biraja Manabasa, Pancha Uka Osha, Dola Yatra (Jagannath).
Suspect rule data to review with a panjika: **Pancha Uka Osha** is keyed to Margashira
Shukla 5 (Panchuka is Kartika Shukla 11–15); **Dola Yatra (Jagannath)** to Phalguna Shukla 5
(Puri Dola runs Phalguna Shukla 10–15); **Biraja Manabasa** to Margashira Shukla 5 (Manabasa
is kept on Margashira Thursdays). Fix only with a cited source.
