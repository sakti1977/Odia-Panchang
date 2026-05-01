"""
Festival rules for Odia Panchang.
Each rule matches a computed panchang day and returns festival info.

Rule types:
  - tithi_rule: (chandra_masa_en, paksha, tithi_num, tradition, name_en, name_or, description)
  - sankranti_rule: (soura_masa_en, tradition, name_en, name_or, description)
    triggered on the first day of a solar month (Sankranti)
"""

TITHI_RULES = [
    # ── COMMON ODIA FESTIVALS ──────────────────────────────────────────────
    # Chaitra
    ("Chaitra",    "shukla",  9,  "common", "Rama Navami",         "ରାମ ନବମୀ",         "Birthday of Lord Rama"),
    ("Chaitra",    "shukla", 15,  "common", "Dola Purnima (Holi)", "ଡୋଳ ପୂର୍ଣ୍ଣିମା",  "Festival of colours, Dola Jatra"),
    # Vaishakha
    ("Vaishakha",  "shukla",  3,  "common", "Akshaya Tritiya",     "ଅକ୍ଷୟ ତୃତୀୟା",    "Most auspicious day; new beginnings"),
    ("Vaishakha",  "shukla", 15,  "common", "Buddha Purnima",      "ବୁଦ୍ଧ ପୂର୍ଣ୍ଣିମା", "Birth of Gautama Buddha"),
    # Jyeshtha
    ("Jyeshtha",   "krishna", 1,  "common", "Savitri Amavasya",    "ସାବିତ୍ରୀ ଅମାବାସ୍ୟା","Vat Savitri — women pray for husband's longevity"),
    ("Jyeshtha",   "shukla", 15,  "common", "Snana Purnima",       "ସ୍ନାନ ପୂର୍ଣ୍ଣିମା", "Sacred bathing festival"),
    # Ashadha
    ("Ashadha",    "shukla",  2,  "common", "Rath Yatra",          "ରଥ ଯାତ୍ରା",        "Chariot festival of Lord Jagannath"),
    ("Ashadha",    "shukla",  5,  "common", "Hera Panchami",       "ହେର ପଞ୍ଚମୀ",       "Goddess Lakshmi visits Gundicha Temple"),
    ("Ashadha",    "shukla", 10,  "common", "Bahuda Yatra",        "ବାହୁଡ଼ା ଯାତ୍ରା",   "Return chariot festival"),
    ("Ashadha",    "shukla", 11,  "common", "Suna Besha",          "ସୁନା ବେଶ",          "Deities adorned with gold ornaments"),
    ("Ashadha",    "shukla", 12,  "common", "Niladri Bije",        "ନୀଳାଦ୍ରି ବିଜେ",    "Deities re-enter the temple"),
    # Shravana
    ("Shravana",   "shukla", 15,  "common", "Gamha Purnima",       "ଗହ୍ମା ପୂର୍ଣ୍ଣିମା", "Raksha Bandhan; cattle worship in Odisha"),
    ("Shravana",   "krishna",  8, "common", "Janmashtami",         "ଜନ୍ମାଷ୍ଟମୀ",       "Birthday of Lord Krishna"),
    # Bhadrapada
    ("Bhadrapada", "shukla",  4,  "common", "Ganesh Chaturthi",    "ଗଣେଶ ଚତୁର୍ଥୀ",    "Festival of Lord Ganesha"),
    ("Bhadrapada", "shukla",  5,  "common", "Nuakhai",             "ନୂଆଖାଇ",            "Odia harvest festival; first grain offered to deity"),
    # Ashwina
    ("Ashwina",    "shukla",  1,  "common", "Mahalaya",            "ମହାଳୟ",             "Beginning of Devi Paksha; ancestors remembered"),
    ("Ashwina",    "shukla",  6,  "common", "Saraswati Puja",      "ସରସ୍ୱତୀ ପୂଜା",    "Worship of Goddess Saraswati"),
    ("Ashwina",    "shukla",  7,  "common", "Durga Saptami",       "ଦୁର୍ଗା ସପ୍ତମୀ",   "Durga Puja begins"),
    ("Ashwina",    "shukla",  8,  "common", "Durga Ashtami",       "ଦୁର୍ଗା ଅଷ୍ଟମୀ",   "Main day of Durga Puja"),
    ("Ashwina",    "shukla",  9,  "common", "Mahanavami",          "ମହାନବମୀ",           "Ninth day of Navratri"),
    ("Ashwina",    "shukla", 10,  "common", "Dussehra / Vijaya Dashami", "ଦଶହରା",      "Victory of good over evil"),
    ("Ashwina",    "shukla", 15,  "common", "Kumar Purnima",       "କୁମାର ପୂର୍ଣ୍ଣିମା","Odia festival; young women worship the moon"),
    # Kartika
    ("Kartika",    "krishna", 14, "common", "Naraka Chaturdashi",  "ନରକ ଚତୁର୍ଦ୍ଦଶୀ",  "Day before Diwali"),
    ("Kartika",    "krishna", 30, "common", "Diwali / Amavasya",   "ଦୀପାବଳୀ",          "Festival of lights"),
    ("Kartika",    "shukla",  1,  "common", "Boita Bandana",       "ବୋଇତ ବନ୍ଦନ",        "Odia maritime heritage festival"),
    ("Kartika",    "shukla", 15,  "common", "Kartik Purnima",      "କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା","End of Kartik month; lamp lighting"),
    # Margashira
    ("Margashira", "shukla",  8,  "common", "Prathamastami",       "ପ୍ରଥମାଷ୍ଟମୀ",      "Odia festival celebrating first-born children"),
    # Pausha
    ("Pausha",     "shukla", 15,  "common", "Pausha Purnima",      "ପୌଷ ପୂର୍ଣ୍ଣିମା",  "Sacred bath at pilgrimage sites"),
    # Magha
    ("Magha",      "shukla",  5,  "common", "Vasanta Panchami",    "ବସନ୍ତ ପଞ୍ଚମୀ",    "Spring festival; Saraswati Puja"),
    ("Magha",      "shukla", 15,  "common", "Magha Purnima",       "ମାଘ ପୂର୍ଣ୍ଣିମା",  "Sacred bathing on full moon"),
    # Phalguna
    ("Phalguna",   "krishna", 14, "common", "Maha Shivaratri",     "ମହା ଶିବରାତ୍ରି",   "Night vigil for Lord Shiva"),
    ("Phalguna",   "shukla", 15,  "common", "Dola Purnima",        "ଡୋଳ ପୂର୍ଣ୍ଣିମା",  "Holi / Dola Jatra celebrated in Odisha"),

    # ── JAGANNATH TRADITION (Puri) ─────────────────────────────────────────
    ("Vaishakha",  "shukla",  3,  "jagannath", "Chandan Yatra Begins",    "ଚନ୍ଦନ ଯାତ୍ରା ଆରମ୍ଭ",  "Start of 21-day sandalwood paste festival"),
    ("Jyeshtha",   "shukla", 15,  "jagannath", "Snana Yatra",             "ସ୍ନାନ ଯାତ୍ରା",        "108-pot bathing of Lord Jagannath, Balabhadra, Subhadra"),
    ("Ashadha",    "shukla",  1,  "jagannath", "Nava Jaubana Darshan",    "ନବ ଯୌବନ ଦର୍ଶନ",      "Deities in rejuvenated form before Rath Yatra"),
    ("Ashadha",    "shukla",  2,  "jagannath", "Rath Yatra (Jagannath)",  "ଜଗନ୍ନାଥ ରଥ ଯାତ୍ରା",  "Grand chariot procession to Gundicha Temple"),
    ("Ashadha",    "shukla",  5,  "jagannath", "Hera Panchami",           "ହେର ପଞ୍ଚମୀ",          "Lakshmi Devi visits Gundicha Temple"),
    ("Ashadha",    "shukla", 10,  "jagannath", "Bahuda Yatra",            "ବାହୁଡ଼ା ଯାତ୍ରା",      "Return journey of Lord Jagannath"),
    ("Ashadha",    "shukla", 11,  "jagannath", "Suna Besha",              "ସୁନା ବେଶ",             "Gold-adorned darshan on chariots"),
    ("Ashadha",    "shukla", 12,  "jagannath", "Niladri Bije",            "ନୀଳାଦ୍ରି ବିଜେ",       "Re-entry of deities; Rasagola offering to Lakshmi"),
    ("Kartika",    "shukla", 11,  "jagannath", "Utthana Ekadashi",        "ଉତ୍ଥାନ ଏକାଦଶୀ",      "End of Chaturmasya; temple rituals resume fully"),
    ("Margashira", "shukla",  5,  "jagannath", "Pancha Uka Osha",         "ପଞ୍ଚ ଉକ ଓଷା",         "Odia vrat observed for Lakshmi"),
    ("Phalguna",   "shukla",  5,  "jagannath", "Dola Yatra (Jagannath)",  "ଡୋଳ ଯାତ୍ରା",          "Swing festival of Lord Jagannath"),
    ("Chaitra",    "shukla",  8,  "jagannath", "Ashokastami",             "ଅଶୋକାଷ୍ଟମୀ",          "Ram Navami eve; important at Lingaraj temple"),

    # ── BIRAJA TRADITION (Jajpur) ─────────────────────────────────────────
    ("Ashwina",    "shukla",  8,  "biraja", "Maa Biraja Ashtami",      "ମା ବିରଜା ଅଷ୍ଟମୀ",    "Main festival of Maa Biraja Temple, Jajpur"),
    ("Ashwina",    "shukla",  6,  "biraja", "Biraja Shashthi",         "ବିରଜା ଷଷ୍ଠୀ",         "Kalasha Sthapana at Biraja Temple"),
    ("Ashwina",    "shukla",  9,  "biraja", "Mahanavami at Biraja",    "ମା ବିରଜା ମହାନବମୀ",   "Special puja at Biraja temple on Navami"),
    ("Ashwina",    "shukla", 10,  "biraja", "Vijaya Dashami at Biraja","ବିରଜା ବିଜୟ ଦଶମୀ",    "Effigy burning and victory procession at Biraja"),
    ("Vaishakha",  "shukla",  3,  "biraja", "Biraja Akshaya Tritiya",  "ବିରଜା ଅକ୍ଷୟ ତୃତୀୟା", "Pana Sankranti celebrations at Biraja Temple"),
    ("Margashira", "shukla",  5,  "biraja", "Biraja Manabasa",         "ବିରଜା ମନବସ",           "Manabasa Gurubara (Lakshmi puja) Thursdays in Margashira"),
    ("Phalguna",   "krishna", 14, "biraja", "Biraja Shivaratri",       "ବିରଜା ଶିବରାତ୍ରି",    "Maha Shivaratri special puja at Biraja and Dashaswamedha ghat"),
    ("Chaitra",    "shukla",  1,  "biraja", "Biraja New Year Puja",    "ବିରଜା ନୂତନ ବର୍ଷ ପୂଜା","Special puja at Biraja Temple on Odia New Year"),
    ("Jyeshtha",   "shukla",  5,  "biraja", "Sitala Shashthi (Biraja)","ସୀତଳ ଷଷ୍ଠୀ",          "Sitala Shashthi celebrated at Biraja with special rituals"),
    ("Bhadrapada", "shukla",  5,  "biraja", "Nuakhai Juhar",           "ନୂଆଖାଇ ଜୁହାର",        "New harvest offered to Maa Biraja before community feast"),
]

# Sankranti rules — triggered on first day of solar month
SANKRANTI_RULES = [
    ("Mesha",    "common",    "Pana Sankranti (Odia New Year)", "ପଣ ସଂକ୍ରାନ୍ତି (ଓଡ଼ିଆ ନବ ବର୍ଷ)", "Odia New Year; celebrated with Pana (sweet drink)"),
    ("Mesha",    "jagannath", "Pana Sankranti at Jagannath",    "ଜଗନ୍ନାଥ ପଣ ସଂକ୍ରାନ୍ତି",         "Special rituals at Jagannath Temple on Odia New Year"),
    ("Mesha",    "biraja",    "Pana Sankranti at Biraja",       "ବିରଜା ପଣ ସଂକ୍ରାନ୍ତି",            "Special rituals at Biraja Temple on Odia New Year"),
    ("Makara",   "common",    "Makar Sankranti",                "ମକର ସଂକ୍ରାନ୍ତି",                "Winter solstice festival; sesame sweets, kite flying"),
    ("Dhanu",    "common",    "Dhanu Sankranti",                "ଧନୁ ସଂକ୍ରାନ୍ତି",                "Sun enters Dhanu; chant of Dhanu at pre-dawn"),
    ("Karka",    "common",    "Karka Sankranti",                "କର୍କ ସଂକ୍ରାନ୍ତି",               "Sun enters Cancer; Dakshinayana begins"),
    ("Simha",    "jagannath", "Jhulana Yatra Begins",           "ଝୁଲଣ ଯାତ୍ରା ଆରମ୍ଭ",              "Swing festival of Lord Jagannath; starts on Shravana Shukla 11"),
]


def match_festivals(panchang_day: dict) -> list[dict]:
    """
    Given a computed panchang dict, return list of matching festivals.
    """
    results = []

    paksha   = panchang_day["paksha_en"].lower()   # "shukla" or "krishna"
    tithi    = panchang_day["tithi_num"]
    chandra  = panchang_day["chandra_masa_en"]
    soura    = panchang_day["soura_masa_en"]

    # Check tithi rules
    for rule in TITHI_RULES:
        r_masa, r_paksha, r_tithi, tradition, name_en, name_or, desc = rule
        if r_masa == chandra and r_paksha == paksha and r_tithi == tithi:
            results.append({
                "name_en":    name_en,
                "name_or":    name_or,
                "tradition":  tradition,
                "description": desc,
            })

    # Check sankranti rules (first day of solar month = tithi calculation at solar ingress)
    # We detect sankranti by checking if this is the first day of a soura masa
    # (handled in seeder by checking soura masa change from previous day)
    # Here we just expose the rules for the seeder to use
    return results


def get_sankranti_festivals(soura_masa_en: str) -> list[dict]:
    """Return sankranti festivals for a given solar month."""
    results = []
    for rule in SANKRANTI_RULES:
        r_masa, tradition, name_en, name_or, desc = rule
        if r_masa == soura_masa_en:
            results.append({
                "name_en":    name_en,
                "name_or":    name_or,
                "tradition":  tradition,
                "description": desc,
            })
    return results
