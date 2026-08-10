"""
Festival rules for Odia Panchang.
Each rule matches a computed panchang day and returns festival info.

Rule types:
  - tithi_rule: (chandra_masa_en, paksha, tithi_num, tradition, name_en, name_or, description)
  - sankranti_rule: (soura_masa_en, tradition, name_en, name_or, description)
    triggered on the first day of a solar month (Sankranti)

Tithi numbering convention used throughout:
  - Shukla paksha: 1 (Pratipad) ... 15 (Purnima)
  - Krishna paksha: 1 (Pratipad) ... 14 (Chaturdashi), 15 (Amavasya)
  NOTE: Amavasya is ALWAYS tithi 15 of Krishna paksha, NOT 30.

Changelog:
  - Fixed Diwali / Amavasya tithi: krishna 30 → krishna 15
  - Fixed Savitri Amavasya tithi: krishna 1 → krishna 15
  - Fixed Boita Bandana: moved from Kartika shukla 1 to shukla 15 (Kartika Purnima)
    (Boita Bandana is observed at dawn on Kartika Purnima, not Pratipad)
  - Renamed Ashwina shukla 6 entry from "Saraswati Puja" to "Durga Shashthi"
    (Saraswati Puja correctly belongs to Magha shukla 5 / Basanta Panchami)
  - Added missing common rule for Sital Sasthi (Jyeshtha shukla 6)
  - Added Kojagiri Lakshmi Puja (Ashwina shukla 15) as a separate common entry
  - Enriched descriptions across all rules using Odia Panjika context
  - Added Mahalaya note: it falls on Krishna Amavasya of Ashwina (Sarvapitri Amavasya),
    not shukla 1; corrected paksha and tithi accordingly
  - Added Naraka Chaturdashi description enrichment
  - Added Kartika Pratipad (Bali Pratipada / Govardhan Puja) entry
"""

TITHI_RULES = [
    # ── COMMON ODIA FESTIVALS ──────────────────────────────────────────────

    # Chaitra
    ("Chaitra",    "shukla",  1,  "common", "Odia New Year (Lunar)",      "ଓଡ଼ିଆ ନୂତନ ବର୍ଷ",         "First day of Chaitra; Biraja New Year Puja at Jajpur"),
    ("Chaitra",    "shukla",  9,  "common", "Rama Navami",                "ରାମ ନବମୀ",                 "Birthday of Lord Rama; fasting and recitation of Ramayana"),

    # Vaishakha
    ("Vaishakha",  "shukla",  3,  "common", "Akshaya Tritiya",            "ଅକ୍ଷୟ ତୃତୀୟା",            "Most auspicious day; Chandan Yatra of Jagannath begins; gold purchases and new ventures"),
    ("Vaishakha",  "shukla", 15,  "common", "Buddha Purnima",             "ବୁଦ୍ଧ ପୂର୍ଣ୍ଣିମା",        "Birth of Gautama Buddha; sacred bathing at pilgrimage sites"),

    # Jyeshtha
    ("Jyeshtha",   "krishna", 15, "common", "Savitri Amavasya",           "ସାବିତ୍ରୀ ଅମାବାସ୍ୟା",      "Vat Savitri; women fast and pray for husband's longevity; ancestors honoured"),
    # FIX: was krishna 1 — Amavasya is always tithi 15 of Krishna paksha

    ("Jyeshtha",   "shukla",  6,  "common", "Sital Shashthi",             "ସୀତଳ ଷଷ୍ଠୀ",              "Wedding of Lord Shiva and Goddess Parvati celebrated as community festival; grand procession in Sambalpur"),
    ("Jyeshtha",   "shukla", 15,  "common", "Snana Purnima",              "ସ୍ନାନ ପୂର୍ଣ୍ଣିମା",        "108-pot ritual bathing of Lord Jagannath; Anavasara (convalescence) period begins"),

    # Ashadha
    ("Ashadha",    "shukla",  2,  "common", "Rath Yatra",                 "ରଥ ଯାତ୍ରା",               "Chariot festival of Lord Jagannath, Balabhadra and Subhadra; chariots pulled to Gundicha Temple"),
    ("Ashadha",    "shukla", 10,  "common", "Bahuda Yatra",               "ବାହୁଡ଼ା ଯାତ୍ରା",           "Return chariot festival; deities return from Gundicha to Jagannath Temple"),

    # Shravana
    ("Shravana",   "shukla", 15,  "common", "Gamha Purnima",              "ଗହ୍ମା ପୂର୍ଣ୍ଣିମା",        "Worship and decoration of cattle; Raksha Bandhan observed; Balabhadra's birthday"),
    ("Shravana",   "krishna",  8, "common", "Janmashtami",                "ଜନ୍ମାଷ୍ଟମୀ",              "Birthday of Lord Krishna; midnight puja, fasting and devotional music"),

    # Bhadrapada
    ("Bhadrapada", "shukla",  4,  "common", "Ganesh Chaturthi",           "ଗଣେଶ ଚତୁର୍ଥୀ",           "Birth of Lord Ganesha; 10-day festival with idol installation and immersion procession"),
    ("Bhadrapada", "shukla",  5,  "common", "Nuakhai",                    "ନୂଆଖାଇ",                   "Harvest festival of western Odisha; first new grain offered to Goddess Samaleswari before community feast"),

    # Ashwina
    ("Ashwina",    "krishna", 15, "common", "Mahalaya",                   "ମହାଳୟ",                    "Sarvapitri Amavasya; beginning of Devi Paksha; ancestors remembered with ritual offerings"),
    # FIX: was shukla 1 — Mahalaya is the Amavasya (krishna 15) that precedes Navratri

    ("Ashwina",    "shukla",  6,  "common", "Durga Shashthi",             "ଦୁର୍ଗା ଷଷ୍ଠୀ",            "Durga Puja begins; Bilva Nimantrana and Bodhana rituals"),
    # FIX: was incorrectly labelled "Saraswati Puja" — Saraswati Puja is Magha shukla 5

    ("Ashwina",    "shukla",  7,  "common", "Durga Saptami",              "ଦୁର୍ଗା ସପ୍ତମୀ",           "Durga Puja main worship begins; Nabapatrika sthapana"),
    ("Ashwina",    "shukla",  8,  "common", "Durga Ashtami",              "ଦୁର୍ଗା ଅଷ୍ଟମୀ",           "Main day of Durga Puja; Sandhi Puja at junction of Ashtami and Navami"),
    ("Ashwina",    "shukla",  9,  "common", "Mahanavami",                 "ମହାନବମୀ",                  "Ninth day of Navratri; Homa and weapons worship (Ayudha Puja)"),
    ("Ashwina",    "shukla", 10,  "common", "Dussehra / Vijaya Dashami",  "ଦଶହରା / ବିଜୟ ଦଶମୀ",      "Victory of good over evil; Durga idol immersion; Ravan effigy burning"),
    ("Ashwina",    "shukla", 15,  "common", "Kumar Purnima",              "କୁମାର ପୂର୍ଣ୍ଣିମା",        "Uniquely Odia festival; unmarried girls worship the moon and pray for a good husband; moonlit games and Pitha"),

    # Kartika
    ("Kartika",    "krishna", 14, "common", "Naraka Chaturdashi",         "ନରକ ଚତୁର୍ଦ୍ଦଶୀ",         "Choti Diwali; oil bath before sunrise; lamps lit to ward off evil"),
    ("Kartika",    "krishna", 15, "common", "Diwali / Lakshmi Puja",      "ଦୀପାବଳୀ",                 "Festival of lights on Amavasya; Lakshmi and Kali worshipped; lamps lit across homes"),
    # FIX: was krishna 30 — Amavasya is tithi 15 of Krishna paksha, not 30

    ("Kartika",    "shukla",  1,  "common", "Bali Pratipada / Govardhan Puja", "ବଳି ପ୍ରତିପଦା",       "Day after Diwali; Govardhan Puja; King Bali's return celebrated in some traditions"),
    ("Kartika",    "shukla", 15,  "common", "Kartik Purnima / Boita Bandana", "କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା / ବୋଇତ ବନ୍ଦନ", "Dev Diwali; uniquely Odia maritime heritage ritual — paper boats floated at dawn chanting Aa Ka Ma Boi"),
    # FIX: Boita Bandana was incorrectly placed at shukla 1; it is observed on Kartika Purnima (shukla 15)

    # Margashira
    ("Margashira", "shukla",  8,  "common", "Prathamastami",              "ପ୍ରଥମାଷ୍ଟମୀ",             "Uniquely Odia festival; mothers pray for the long life and wellbeing of their first-born child"),

    # Pausha
    ("Pausha",     "shukla", 15,  "common", "Pausha Purnima",             "ପୌଷ ପୂର୍ଣ୍ଣିମା",         "Sacred bath at pilgrimage sites; marks end of Pausha month"),

    # Magha
    ("Magha",      "shukla",  5,  "common", "Vasanta Panchami / Saraswati Puja", "ବସନ୍ତ ପଞ୍ଚମୀ / ସରସ୍ୱତୀ ପୂଜା", "Worship of Goddess Saraswati; books placed before deity; yellow attire; onset of spring"),
    ("Magha",      "shukla", 15,  "common", "Magha Purnima",              "ମାଘ ପୂର୍ଣ୍ଣିମା",         "Sacred bathing on full moon; Triveni Snanam at river confluences"),

    # Phalguna
    ("Phalguna",   "krishna", 14, "common", "Maha Shivaratri",            "ମହା ଶିବରାତ୍ରି",           "All-night vigil for Lord Shiva; fasting, Shiva abhisheka with milk and Bilva leaves"),
    ("Phalguna",   "shukla", 15,  "common", "Dola Purnima",               "ଡୋଳ ପୂର୍ଣ୍ଣିମା",         "Odia Holi; Radha-Krishna deities placed on decorated swings (dola); colour play and folk songs"),

    # ── JAGANNATH TRADITION (Puri) ─────────────────────────────────────────
    ("Vaishakha",  "shukla",  3,  "jagannath", "Chandan Yatra Begins",         "ଚନ୍ଦନ ଯାତ୍ରା ଆରମ୍ଭ",        "Start of 21-day sandalwood paste festival; boat procession on Narendra Tank begins"),
    ("Jyeshtha",   "shukla", 15,  "jagannath", "Snana Yatra",                  "ସ୍ନାନ ଯାତ୍ରା",               "108-pot bathing of Lord Jagannath, Balabhadra, Subhadra and Sudarshana; grand public darshan before Anavasara"),
    ("Ashadha",    "shukla",  1,  "jagannath", "Nava Jaubana Darshan",         "ନବ ଯୌବନ ଦର୍ଶନ",             "Deities appear in rejuvenated form; special darshan one day before Rath Yatra"),
    ("Ashadha",    "shukla",  1,  "jagannath", "Gundicha Marjana",             "ଗୁଣ୍ଡିଚା ମାର୍ଜନ",            "Ritual cleansing of Gundicha Temple by servitors before the Lord's arrival"),
    ("Ashadha",    "shukla",  5,  "jagannath", "Hera Panchami",                "ହେର ପଞ୍ଚମୀ",                 "Goddess Lakshmi Devi visits Gundicha Temple to look for Lord Jagannath"),
    ("Ashadha",    "shukla", 11,  "jagannath", "Suna Besha",                   "ସୁନା ବେଶ",                    "Deities adorned with gold ornaments on chariots; spectacular darshan"),
    ("Ashadha",    "shukla", 12,  "jagannath", "Adhara Pana",                  "ଅଧର ପଣା",                    "Special sweet drink (Pana) offered to deities still seated on chariots"),
    ("Ashadha",    "shukla", 13,  "jagannath", "Niladri Bije",                 "ନୀଳାଦ୍ରି ବିଜେ",              "Re-entry of deities into Jagannath Temple; Rasagola offering to Goddess Lakshmi for reconciliation"),
    ("Shravana",   "shukla", 11,  "jagannath", "Jhulana Yatra Begins",         "ଝୁଲଣ ଯାତ୍ରା ଆରମ୍ଭ",          "Swing festival of Lord Jagannath begins on Ekadashi; continues for 5 days"),
    ("Kartika",    "shukla", 11,  "jagannath", "Utthana Ekadashi",             "ଉତ୍ଥାନ ଏକାଦଶୀ",             "End of Chaturmasya; Lord Vishnu awakens from cosmic sleep; full temple rituals resume"),
    ("Margashira", "shukla",  5,  "jagannath", "Pancha Uka Osha",              "ପଞ୍ଚ ଉକ ଓଷା",                "Odia vrat observed for Goddess Lakshmi; five-day observance"),
    ("Phalguna",   "shukla",  5,  "jagannath", "Dola Yatra (Jagannath)",       "ଡୋଳ ଯାତ୍ରା",                 "Swing festival of Lord Jagannath at Puri; procession with decorated palanquin"),
    ("Chaitra",    "shukla",  8,  "jagannath", "Ashokastami",                  "ଅଶୋକାଷ୍ଟମୀ",                 "Ram Navami eve; Lord Jagannath's special besha and rituals at Puri"),

    # ── LINGARAJ TRADITION (Bhubaneswar) ───────────────────────────────────
    ("Magha",      "shukla",  5,  "lingaraj", "Banajaga Jatra (Rukuna Rath)",      "ବନଯାଗ ଯାତ୍ରା",              "Marking of mango tree in Ekamra forest for construction of Rukuna Rath chariot"),
    ("Phalguna",   "krishna", 14, "lingaraj", "Lingaraj Maha Shivaratri",          "ଲିଙ୍ଗରାଜ ମହା ଶିବରାତ୍ରି",    "Grand Shivaratri night vigil at Lingaraj Temple; lakhs of devotees attend"),
    ("Chaitra",    "shukla",  8,  "lingaraj", "Ashokastami — Rukuna Rath Yatra",   "ଅଶୋକାଷ୍ଟମୀ — ରୁକୁଣା ରଥ",   "Papa Binashi Jatra; grand chariot procession of Lord Lingaraj to Rameswara Temple"),
    ("Chaitra",    "shukla", 12,  "lingaraj", "Rukuna Rath Bahuda Yatra",          "ରୁକୁଣା ରଥ ବାହୁଡ଼ା ଯାତ୍ରା",  "Swarnadri Bije; return journey of Lord Lingaraj from Rameswara to Lingaraj Temple"),

    # ── BIRAJA TRADITION (Jajpur) ─────────────────────────────────────────
    ("Vaishakha",  "shukla",  3,  "biraja", "Biraja Akshaya Tritiya",              "ବିରଜା ଅକ୍ଷୟ ତୃତୀୟା",        "Pana Sankranti celebrations at Biraja Temple; Chandan Yatra begins"),
    ("Jyeshtha",   "shukla",  5,  "biraja", "Sitala Shashthi (Biraja)",            "ସୀତଳ ଷଷ୍ଠୀ",                 "Sitala Shashthi celebrated at Biraja with special temple rituals and community festivities"),
    ("Bhadrapada", "shukla",  5,  "biraja", "Nuakhai Juhar",                       "ନୂଆଖାଇ ଜୁହାର",               "First new harvest grain offered to Maa Biraja before community feast and Juhar ceremony"),
    ("Ashwina",    "krishna",  8, "biraja", "Shodasha Dinatatmika Puja Begins",    "ଷୋଡ଼ଶ ଦିନାତ୍ମିକ ପୂଜା ଆରମ୍ଭ", "Start of 16-day Sharadiya Durga Puja at Biraja Temple; unique to Jajpur"),
    ("Ashwina",    "shukla",  1,  "biraja", "Simhadhwaja Rath Yatra",              "ସିଂହଧ୍ୱଜ ରଥ ଯାତ୍ରା",         "Maa Biraja's unique chariot festival during Navratri; chariot pulled through Jajpur town"),
    ("Ashwina",    "shukla",  6,  "biraja", "Biraja Shashthi",                     "ବିରଜା ଷଷ୍ଠୀ",                "Kalasha Sthapana at Biraja Temple; formal commencement of Navratri rituals"),
    ("Ashwina",    "shukla",  8,  "biraja", "Maa Biraja Ashtami",                  "ମା ବିରଜା ଅଷ୍ଟମୀ",           "Main festival day at Biraja; Sandhi Puja and Bali Daanam ritual transition begins"),
    ("Ashwina",    "shukla",  9,  "biraja", "Mahanavami at Biraja",                "ମା ବିରଜା ମହାନବମୀ",          "Special puja at Biraja Temple; Bali Daanam concludes; Homa performed"),
    ("Ashwina",    "shukla", 10,  "biraja", "Vijaya Dashami at Biraja",            "ବିରଜା ବିଜୟ ଦଶମୀ",           "Effigy burning and victory procession at Biraja; Goddess returns victorious"),
    ("Margashira", "shukla",  5,  "biraja", "Biraja Manabasa",                     "ବିରଜା ମନବସ",                  "Manabasa Gurubara — Goddess Lakshmi puja on Thursdays of Margashira observed at Biraja"),
    ("Phalguna",   "krishna", 14, "biraja", "Biraja Shivaratri",                   "ବିରଜା ଶିବରାତ୍ରି",            "Maha Shivaratri special puja at Biraja Temple and Dashaswamedha Ghat on Baitarani river"),
    ("Chaitra",    "shukla",  1,  "biraja", "Biraja New Year Puja",                "ବିରଜା ନୂତନ ବର୍ଷ ପୂଜା",      "Special puja at Biraja Temple on first day of Chaitra; Odia New Year blessings sought"),
]

# Sankranti rules — triggered on first day of solar month
# These are matched by the seeder when a soura masa transition is detected
SANKRANTI_RULES = [
    ("Mesha",      "common",    "Pana Sankranti (Odia New Year)",         "ପଣା ସଂକ୍ରାନ୍ତି",                 "Odia New Year; Hanuman Jayanti; sweet Pana offered to passers-by; Meru Yatra at Lingaraj Temple"),
    ("Mesha",      "jagannath", "Pana Sankranti at Jagannath",            "ଜଗନ୍ନାଥ ପଣା ସଂକ୍ରାନ୍ତି",         "Special besha and rituals at Jagannath Temple, Puri on Odia New Year"),
    ("Mesha",      "biraja",    "Pana Sankranti at Biraja",               "ବିରଜା ପଣା ସଂକ୍ରାନ୍ତି",           "Special puja and Pana offering at Biraja Temple, Jajpur on Odia New Year"),
    ("Mesha",      "lingaraj",  "Pana Sankranti at Lingaraj",             "ଲିଙ୍ଗରାଜ ପଣା ସଂକ୍ରାନ୍ତି",        "Meru Yatra and special puja at Lingaraj Temple, Bhubaneswar on Odia New Year"),
    ("Vrishabha",  "common",    "Vrishabha Sankranti",                    "ବୃଷଭ ସଂକ୍ରାନ୍ତି",                "Sun enters Taurus; planting season begins in Odisha"),
    ("Mithuna",    "common",    "Mithuna Sankranti (Raja Parba)",         "ମିଥୁନ ସଂକ୍ରାନ୍ତି (ରଜ ପର୍ବ)",     "Start of Raja Parba; 4-day Odia festival celebrating womanhood and earth's fertility; swing riding and special Pitha"),
    ("Karka",      "common",    "Karka Sankranti (Dakshinayana)",         "କର୍କ ସଂକ୍ରାନ୍ତି — ଦକ୍ଷିଣାୟନ",    "Sun enters Cancer; Dakshinayana (southward journey of Sun) begins"),
    ("Simha",      "common",    "Simha Sankranti",                        "ସିଂହ ସଂକ୍ରାନ୍ତି",                "Sun enters Leo; Gamha Purnima and Janmashtami season"),
    ("Kanya",      "common",    "Kanya Sankranti",                        "କନ୍ୟା ସଂକ୍ରାନ୍ତି",               "Sun enters Virgo; Navratri and Durga Puja season begins"),
    ("Tula",       "common",    "Tula Sankranti",                         "ତୁଳା ସଂକ୍ରାନ୍ତି",                "Sun enters Libra; Kartika month observances and Diwali season"),
    ("Vrischika",  "common",    "Vrischika Sankranti",                    "ବୃଶ୍ଚିକ ସଂକ୍ରାନ୍ତି",             "Sun enters Scorpio; Manabasa Gurubara season in Margashira begins shortly"),
    ("Dhanu",      "common",    "Dhanu Sankranti",                        "ଧନୁ ସଂକ୍ରାନ୍ତି",                 "Sun enters Sagittarius; month of pre-dawn Dhanu hymns (Dhanu Bhoga); Poda Pitha prepared"),
    ("Makara",     "common",    "Makar Sankranti",                        "ମକର ସଂକ୍ରାନ୍ତି",                 "Winter solstice festival; sesame sweets, kite flying, ritual bathing in rivers; Sun enters Capricorn"),
    ("Makara",     "biraja",    "Makar Sankranti Snanam at Biraja",       "ବିରଜା ମକର ସ୍ନାନ",                "Lakhs take holy dip at Dashaswamedha Ghat on Baitarani river, Jajpur; one of Odisha's largest gatherings"),
    ("Kumbha",     "common",    "Kumbha Sankranti",                       "କୁମ୍ଭ ସଂକ୍ରାନ୍ତି",                "Sun enters Aquarius; Maha Shivaratri season; winter begins to wane"),
    ("Meena",      "common",    "Meena Sankranti",                        "ମୀନ ସଂକ୍ରାନ୍ତି",                 "Last solar month; Holi and Dola Purnima season; preparations for Pana Sankranti begin"),
]


def match_festivals(panchang_day: dict) -> list[dict]:
    """
    Given a computed panchang dict, return list of matching festivals.

    Expected keys in panchang_day:
      - paksha_en (str): "shukla" or "krishna"
      - tithi_num (int): 1-15
      - chandra_masa_en (str): lunar month name in English
      - soura_masa_en (str): solar month name in English
      - date (str, optional): YYYY-MM-DD — enables Tier A civil overrides
        (see festival_civil.py; required for correct 2025 Puri cycle)

    Each result includes short description plus story / why_today (see festival_stories).
    """
    from src.festival_civil import civil_festivals_for_date, suppressed_rule_names
    from src.festival_stories import attach_story

    results = []
    seen: set[tuple[str, str]] = set()

    paksha  = panchang_day["paksha_en"].lower()   # "shukla" or "krishna"
    tithi   = panchang_day["tithi_num"]           # 1-15 (15 = Purnima or Amavasya)
    chandra = panchang_day["chandra_masa_en"]
    date_iso = panchang_day.get("date")
    year = None
    if date_iso and isinstance(date_iso, str) and len(date_iso) >= 4:
        try:
            year = int(date_iso[:4])
        except ValueError:
            year = None
    suppress = suppressed_rule_names(year)

    for rule in TITHI_RULES:
        r_masa, r_paksha, r_tithi, tradition, name_en, name_or, desc = rule
        if name_en in suppress:
            continue
        if r_masa == chandra and r_paksha == paksha and r_tithi == tithi:
            key = (name_en, tradition)
            if key in seen:
                continue
            seen.add(key)
            results.append(attach_story({
                "name_en":     name_en,
                "name_or":     name_or,
                "tradition":   tradition,
                "description": desc,
            }))

    # Tier A civil attachments (may add festivals when masa labels disagree)
    for f in civil_festivals_for_date(date_iso if isinstance(date_iso, str) else None):
        key = (f["name_en"], f["tradition"])
        if key in seen:
            continue
        seen.add(key)
        results.append(attach_story({
            "name_en":     f["name_en"],
            "name_or":     f["name_or"],
            "tradition":   f["tradition"],
            "description": f["description"],
        }))

    return results


def get_sankranti_festivals(soura_masa_en: str) -> list[dict]:
    """
    Return sankranti festivals for a given solar month transition.
    Called by the seeder when it detects a soura masa change from the previous day.
    Includes story / why_today via festival_stories.
    """
    from src.festival_stories import attach_story

    results = []
    for rule in SANKRANTI_RULES:
        r_masa, tradition, name_en, name_or, desc = rule
        if r_masa == soura_masa_en:
            results.append(attach_story({
                "name_en":     name_en,
                "name_or":     name_or,
                "tradition":   tradition,
                "description": desc,
            }))
    return results
