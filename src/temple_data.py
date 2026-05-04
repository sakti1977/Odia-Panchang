"""
Static reference data for the three main temples of Odisha:
  - Jagannath Temple, Puri (Vaishnava)
  - Biraja Temple, Jajpur (Shakti)
  - Lingaraj Temple, Bhubaneswar (Shaiva)

Also contains Odia Heritage data: important personalities and historical events.
All text is bilingual (English + Odia script where applicable).
"""

# ─── Jagannath Temple, Puri ────────────────────────────────────────────────

JAGANNATH_NITIS = [
    {
        "time": "5:00 AM",
        "name_en": "Mangal Arati",
        "name_or": "ମଙ୍ଗଳ ଆଳତି",
        "description": "First darshan of the day. The main door (Singhadwara) opens. "
                       "Priests perform Arati with lamps, conch-shell blowing, and drum beats.",
    },
    {
        "time": "6:00 AM",
        "name_en": "Mailam",
        "name_or": "ମୈଳମ",
        "description": "Ritual cleaning — the previous night's flower garlands and offerings are removed.",
    },
    {
        "time": "6:30 AM",
        "name_en": "Abakasha",
        "name_or": "ଅବକାଶ",
        "description": "Morning ablution ritual: deities are offered symbolic tooth-cleaning, "
                       "bathing with scented water, and fresh clothes.",
    },
    {
        "time": "7:00 AM",
        "name_en": "Surya Puja",
        "name_or": "ସୂର୍ଯ୍ୟ ପୂଜା",
        "description": "Worship of the Sun God at sunrise. Prayers are offered at the Aruna Stambha "
                       "(the tall pillar at the temple gate).",
    },
    {
        "time": "7:30 AM",
        "name_en": "Dwarpita Niti",
        "name_or": "ଦ୍ୱାରପୀଟ ନୀତି",
        "description": "The inner sanctum door is opened with formal ritual. Only authorised sevayats may enter.",
    },
    {
        "time": "8:00 AM",
        "name_en": "Gopal Ballav Bhoga",
        "name_or": "ଗୋପାଳ ବଲ୍ଲଭ ଭୋଗ",
        "description": "First food offering (bhoga) of the day — rice, dal, and sweets prepared "
                       "in the world's largest temple kitchen (Ananda Bazar).",
    },
    {
        "time": "9:00 AM",
        "name_en": "Sakala Dhupa",
        "name_or": "ସକାଳ ଧୂପ",
        "description": "Main morning food offering with 56 varieties of bhoga (Chhappan Bhoga). "
                       "Regarded as the most important meal offering of the day.",
    },
    {
        "time": "11:00 AM",
        "name_en": "Bhog Mandap",
        "name_or": "ଭୋଗ ମଣ୍ଡପ",
        "description": "Mid-morning ritual in the Bhog Mandapa hall. Special sweets and fruits offered.",
    },
    {
        "time": "12:00 PM",
        "name_en": "Madhyanha Dhupa",
        "name_or": "ମଧ୍ୟାହ୍ନ ଧୂପ",
        "description": "Midday food offering. Rice (Arua Chaula), Dalma, and Khechudi are the main items.",
    },
    {
        "time": "1:00 PM",
        "name_en": "Madhyanha Pahuda",
        "name_or": "ମଧ୍ୟାହ୍ନ ପହୁଡ଼",
        "description": "Midday rest of the deities. The main door (Jaya Vijaya Dwara) is closed for ~2 hours.",
    },
    {
        "time": "4:00 PM",
        "name_en": "Sandhya Dhupa",
        "name_or": "ସଂଧ୍ୟ ଧୂପ",
        "description": "Evening food offering after the deities awaken from rest.",
    },
    {
        "time": "5:30 PM",
        "name_en": "Sandhya Arati",
        "name_or": "ସଂଧ୍ୟ ଆଳତି",
        "description": "Evening Arati with lamps and incense. The temple is lit and devotees gather for darshan.",
    },
    {
        "time": "6:30 PM",
        "name_en": "Chandana Lagi",
        "name_or": "ଚନ୍ଦନ ଲାଗି",
        "description": "Sandalwood paste is applied to the deities as an evening cooling ritual.",
    },
    {
        "time": "8:00 PM",
        "name_en": "Badasinghara Besha",
        "name_or": "ବଡ଼ ଶୃଙ୍ଗାର ବେଶ",
        "description": "Night-time floral decoration (Singhara). The deities are adorned with the finest "
                       "flowers of the day — this is the most elaborately decorated form of the deities.",
    },
    {
        "time": "9:00 PM",
        "name_en": "Badasinghara Dhupa",
        "name_or": "ବଡ଼ ଶୃଙ୍ଗାର ଧୂପ",
        "description": "Final food offering of the night (light snack — Khai, Kadamba, Nadia Ladu).",
    },
    {
        "time": "10:00 PM",
        "name_en": "Khata Seja Lagi",
        "name_or": "ଖଟ ଶୋଇ ଲାଗି",
        "description": "Bedtime ritual — the deities are symbolically put to sleep on a cot (Khata). "
                       "The inner sanctum doors are then closed for the night.",
    },
]

JAGANNATH_BESHAS = [
    {
        "name_en": "Chandan Besha",
        "name_or": "ଚନ୍ଦନ ବେଶ",
        "trigger": "Vaishakha Shukla Tritiya to Jyeshtha Shukla Navami (21 days)",
        "trigger_or": "ବୈଶାଖ ଶୁକ୍ଳ ତୃତୀୟା ରୁ ଜ୍ୟେଷ୍ଠ ଶୁକ୍ଳ ନବମୀ ପର୍ଯ୍ୟନ୍ତ",
        "description": "The deities are adorned with cool sandalwood paste (chandan) for 21 days "
                       "of the Chandan Yatra. Replica idols (Madanmohan) are taken on a boat ride on Narendra Tank.",
    },
    {
        "name_en": "Snana Besha (Deba Snana)",
        "name_or": "ଦେବ ସ୍ନାନ ବେଶ",
        "trigger": "Jyeshtha Shukla Purnima (Snana Purnima)",
        "trigger_or": "ଜ୍ୟେଷ୍ଠ ଶୁକ୍ଳ ପୂର୍ଣ୍ଣିମା",
        "description": "The three deities are bathed with 108 pots of sacred water on the Snana Mandapa "
                       "(bathing platform). After this, they enter Anasara (isolation) for 15 days.",
    },
    {
        "name_en": "Nava Jaubana Besha",
        "name_or": "ନବ ଯୌବନ ବେଶ",
        "trigger": "Ashadha Krishna Paksha — after Anasara (15 days of isolation)",
        "trigger_or": "ଆଷାଢ଼ କୃଷ୍ଣ ପ୍ରତିପଦା",
        "description": "The rejuvenated form (Nava Jaubana — 'new youth') of the deities after isolation. "
                       "Devotees throng the temple for the first darshan after 15 days.",
    },
    {
        "name_en": "Suna Besha (Golden Attire)",
        "name_or": "ସୁନା ବେଶ",
        "trigger": "Ashadha Shukla Ekadashi (Bahuda Yatra day + 1 — on the chariot) and Kartika Purnima",
        "trigger_or": "ଆଷାଢ଼ ଶୁକ୍ଳ ଏକାଦଶୀ ଏବଂ କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା",
        "description": "The most spectacular besha: the deities are adorned with hundreds of kilograms "
                       "of gold ornaments donated by the kings of Odisha over centuries. The gold weighs "
                       "over 208 kg. Darshan lasts the entire day.",
    },
    {
        "name_en": "Pralambi Besha",
        "name_or": "ପ୍ରଲମ୍ବି ବେଶ",
        "trigger": "Ashadha Shukla Dwadashi (Niladri Bije — return to temple)",
        "trigger_or": "ଆଷାଢ଼ ଶୁକ୍ଳ ଦ୍ୱାଦଶୀ",
        "description": "The deities are dressed in the Pralambi (hanging) style as they re-enter "
                       "the Jagannath Temple after the Rath Yatra journey. Rasagolla (sweetened cheese balls) "
                       "are offered to Lakshmi Devi to appease her.",
    },
    {
        "name_en": "Hathi Besha (Elephant Attire)",
        "name_or": "ହାତୀ ବେଶ",
        "trigger": "Bhadrapada Shukla Chaturthi (Ganesh Chaturthi)",
        "trigger_or": "ଭାଦ୍ରବ ଶୁକ୍ଳ ଚତୁର୍ଥୀ",
        "description": "Lord Jagannath is dressed as an elephant (Ganesha form) on Ganesh Chaturthi, "
                       "symbolising the victory of devotion over obstacles.",
    },
    {
        "name_en": "Lakshmi Narayan Besha",
        "name_or": "ଲକ୍ଷ୍ମୀ ନାରାୟଣ ବେଶ",
        "trigger": "Kartika Shukla Ekadashi (Utthana Ekadashi)",
        "trigger_or": "କାର୍ତ୍ତିକ ଶୁକ୍ଳ ଏକାଦଶୀ",
        "description": "Lord Jagannath and Goddess Lakshmi are dressed together as Lakshmi Narayan "
                       "on the auspicious Utthana (awakening) Ekadashi, marking the end of Chaturmasya.",
    },
    {
        "name_en": "Raja Besha (Rajarajeswara)",
        "name_or": "ରାଜ ବେଶ",
        "trigger": "Margashira Shukla Panchami",
        "trigger_or": "ମାର୍ଗଶୀର ଶୁକ୍ଳ ପଞ୍ଚମୀ",
        "description": "Lord Jagannath is dressed as the King of Kings (Rajarajeswara) in royal attire "
                       "— golden crown, royal robes, and full royal insignia.",
    },
    {
        "name_en": "Trivikrama Besha",
        "name_or": "ତ୍ରିବିକ୍ରମ ବେଶ",
        "trigger": "Kartika Shukla Dwadashi",
        "trigger_or": "କାର୍ତ୍ତିକ ଶୁକ୍ଳ ଦ୍ୱାଦଶୀ",
        "description": "The deities are dressed as Trivikrama — the form of Lord Vishnu who measured "
                       "the three worlds in three steps (Vamana Avatar story).",
    },
    {
        "name_en": "Bankachuda Besha",
        "name_or": "ବାଁକ ଚୂଡ଼ା ବେଶ",
        "trigger": "Magha Shukla Panchami (Vasanta Panchami)",
        "trigger_or": "ମାଘ ଶୁକ୍ଳ ପଞ୍ଚମୀ",
        "description": "Lord Jagannath is dressed in the peacock-feather crown (Bankachuda) form "
                       "of Lord Krishna, celebrating the arrival of spring.",
    },
    {
        "name_en": "Dola Besha (Swing Festival)",
        "name_or": "ଡୋଳ ବେଶ",
        "trigger": "Phalguna Shukla Purnima (Dola Purnima / Holi)",
        "trigger_or": "ଫାଲ୍ଗୁନ ଶୁକ୍ଳ ପୂର୍ଣ୍ଣିମା",
        "description": "Lord Jagannath is placed on a floral swing (dola) and swung gently. "
                       "Devotees spray colours (abir/gulal) as part of Holi celebrations.",
    },
    {
        "name_en": "Padma Besha",
        "name_or": "ପଦ୍ମ ବେଶ",
        "trigger": "Bhadrapada Shukla Ashtami",
        "trigger_or": "ଭାଦ୍ରବ ଶୁକ୍ଳ ଅଷ୍ଟମୀ",
        "description": "Lord Jagannath is decorated with lotus flowers (padma) — symbolising purity "
                       "and divine beauty.",
    },
]


# ─── Biraja Temple, Jajpur ─────────────────────────────────────────────────

BIRAJA_NITIS = [
    {
        "time": "5:00 AM",
        "name_en": "Mangal Arati & Pratah Puja",
        "name_or": "ମଙ୍ଗଳ ଆଳତି ଓ ପ୍ରାତଃ ପୂଜା",
        "description": "The first puja of the day. Incense, lamp (deepa), conch-shell, and bell. "
                       "The Goddess is awakened and offered flowers, water, and fruits.",
    },
    {
        "time": "7:00 AM",
        "name_en": "Abada (Morning Offering)",
        "name_or": "ଅବଡ଼",
        "description": "Morning food offering: cooked rice, dal, banana, curd, and seasonal fruits.",
    },
    {
        "time": "11:00 AM",
        "name_en": "Bikala Puja (Noon Puja)",
        "name_or": "ବିକାଳ ପୂଜା",
        "description": "Mid-morning puja with Panchamruta Abhisheka (ritual bathing with five sacred substances: "
                       "milk, curd, honey, ghee, and sugar water) on special occasions.",
    },
    {
        "time": "12:30 PM",
        "name_en": "Madhyanha Dhupa",
        "name_or": "ମଧ୍ୟାହ୍ନ ଧୂପ",
        "description": "Midday food offering. The main hall is open for darshan. "
                       "The 64-yogini form of Maa Biraja is especially venerated.",
    },
    {
        "time": "1:30 PM",
        "name_en": "Pahuda (Rest)",
        "name_or": "ପହୁଡ଼",
        "description": "The Goddess rests. Inner shrine doors close briefly.",
    },
    {
        "time": "4:00 PM",
        "name_en": "Aparahna Puja",
        "name_or": "ଅପରାହ୍ନ ପୂଜା",
        "description": "Afternoon puja. Fresh flowers, incense, and camphor Arati.",
    },
    {
        "time": "6:30 PM",
        "name_en": "Sandhya Arati & Dhupa",
        "name_or": "ସଂଧ୍ୟ ଆଳତି ଓ ଧୂପ",
        "description": "Evening Arati with lamps, dhoop (incense), and the blowing of conch shells. "
                       "Evening food offering follows.",
    },
    {
        "time": "9:00 PM",
        "name_en": "Ratri Puja & Khata Seja",
        "name_or": "ରାତ୍ରି ପୂଜା ଓ ଖଟ ଶୋଇ",
        "description": "Final night puja. The Goddess is offered flowers, fruits, and betel leaves. "
                       "The shrine is then closed for the night.",
    },
]

BIRAJA_SPECIAL = [
    {
        "name_en": "Navratri (Biraja Dashahara)",
        "name_or": "ନବରାତ୍ରି — ବିରଜା ଦଶହରା",
        "time": "Ashwina Shukla 1–10",
        "description": "The grandest festival at Biraja. Thousands gather for 10 days. "
                       "On Maha Ashtami, a special Chandi Puja is performed with 108 diyas. "
                       "On Mahanavami, animal sacrifice (Balidana) is offered. "
                       "On Vijaya Dashami, an effigy is burnt at Dashaswamedha Ghat on the Baitarani river.",
    },
    {
        "name_en": "Makar Sankranti Snanam",
        "name_or": "ମକର ସଂକ୍ରାନ୍ତି ସ୍ନାନ",
        "time": "Makara Sankranti (January ~14)",
        "description": "Lakhs of pilgrims take a holy dip at Dashaswamedha Ghat on the Baitarani river. "
                       "The Baitarani river is considered as sacred as the Ganges at this ghat. "
                       "Special Abhisheka of Maa Biraja is performed.",
    },
    {
        "name_en": "Sitala Shashthi",
        "name_or": "ସୀତଳ ଷଷ୍ଠୀ",
        "time": "Jyeshtha Shukla Shashthi",
        "description": "The marriage procession of Lord Shiva and Parvati. "
                       "A grand procession through Jajpur town re-enacts the divine wedding. "
                       "Biraja Temple celebrates with special puja and decorations.",
    },
    {
        "name_en": "Pana Sankranti (Odia New Year)",
        "name_or": "ପଣ ସଂକ୍ରାନ୍ତି",
        "time": "Mesha Sankranti (April ~14)",
        "description": "Odia New Year is celebrated at Biraja with special puja, distribution of Pana "
                       "(a sweet drink of water, jaggery, chhena, banana), and night-long devotional singing.",
    },
    {
        "name_en": "Maha Shivaratri",
        "name_or": "ମହା ଶିବରାତ୍ରି",
        "time": "Phalguna Krishna Chaturdashi",
        "description": "A major festival at both Biraja and the Dashaswamedha Shiva Linga at Jajpur. "
                       "Night vigil, Abhisheka, and devotional music.",
    },
]


# ─── Lingaraj Temple, Bhubaneswar ──────────────────────────────────────────

LINGARAJ_NITIS = [
    {
        "time": "6:00 AM",
        "name_en": "Mangal Arati & Abhisheka",
        "name_or": "ମଙ୍ଗଳ ଆଳତି ଓ ଅଭିଷେକ",
        "description": "The Shivalinga (Harihara — a fusion of Shiva and Vishnu) is bathed with water, "
                       "milk, curd, honey, ghee, and sugar water (Panchamruta). Incense and lamps lit.",
    },
    {
        "time": "7:30 AM",
        "name_en": "Shringara (Decoration)",
        "name_or": "ଶୃଙ୍ଗାର",
        "description": "The Swayambhu Linga is adorned with Bilva leaves (sacred to Shiva), flowers, "
                       "sandalwood paste, and vermillion. Bhasma (sacred ash) is applied.",
    },
    {
        "time": "9:00 AM",
        "name_en": "Sakala Dhupa (Morning Offering)",
        "name_or": "ସକାଳ ଧୂପ",
        "description": "Morning food offering: Puri, Khechudi, Dalma, Khiri (rice pudding), and fruits. "
                       "The prasad is distributed as Mahaprasad.",
    },
    {
        "time": "12:00 PM",
        "name_en": "Madhyanha Puja",
        "name_or": "ମଧ୍ୟାହ୍ନ ପୂଜା",
        "description": "Midday worship. Additional Abhisheka with scented water and flowers. "
                       "The temple sees its busiest darshan hours.",
    },
    {
        "time": "1:00 PM",
        "name_en": "Madhyanha Dhupa",
        "name_or": "ମଧ୍ୟାହ୍ନ ଧୂପ",
        "description": "Midday food offering. Main course: rice, dal, mixed vegetables, laddu.",
    },
    {
        "time": "3:00 PM",
        "name_en": "Aparahna Puja",
        "name_or": "ଅପରାହ୍ନ ପୂଜା",
        "description": "Afternoon worship with flowers, incense, and Panchamruta on auspicious days.",
    },
    {
        "time": "6:00 PM",
        "name_en": "Sandhya Arati",
        "name_or": "ସଂଧ୍ୟ ଆଳତି",
        "description": "Evening Arati — the most attended puja. The temple is illuminated. "
                       "Devotees offer coconuts, flowers, and milk.",
    },
    {
        "time": "8:00 PM",
        "name_en": "Badasinghara & Evening Dhupa",
        "name_or": "ବଡ଼ ଶୃଙ୍ଗାର ଓ ସଂଧ୍ୟ ଧୂପ",
        "description": "Night decoration with elaborate floral arrangements. "
                       "Evening food offering of sweets and fruits.",
    },
    {
        "time": "10:00 PM",
        "name_en": "Pahuda (Night Rest)",
        "name_or": "ପହୁଡ଼",
        "description": "The deity is symbolically put to rest. The inner shrine closes for the night.",
    },
]

LINGARAJ_SPECIAL = [
    {
        "name_en": "Maha Shivaratri",
        "name_or": "ମହା ଶିବରାତ୍ରି",
        "time": "Phalguna Krishna Chaturdashi",
        "description": "The biggest festival at Lingaraj. Over 2 lakh devotees visit. "
                       "Night-long vigil (jagarana), four praharas of puja, special Abhisheka. "
                       "The entire old city of Bhubaneswar celebrates.",
    },
    {
        "name_en": "Ashokastami & Rukuna Rath Yatra",
        "name_or": "ଅଶୋକାଷ୍ଟମୀ ଓ ରୁକୁନ ରଥ ଯାତ୍ରା",
        "time": "Chaitra Shukla Ashtami",
        "description": "Lingaraj is taken out in a chariot procession (Rukuna Rath Yatra) through Bhubaneswar city. "
                       "This is the mini version of Puri's Rath Yatra, unique to Lingaraj. "
                       "The chariot (Rath) is pulled by thousands of devotees.",
    },
    {
        "name_en": "Chandan Yatra",
        "name_or": "ଚନ୍ଦନ ଯାତ୍ରା",
        "time": "Vaishakha Shukla Tritiya (21 days)",
        "description": "Lingaraj's replica idol (Chandana Pratima) is taken on a boat ride on Bindu Sagar "
                       "lake for 21 days. Sandalwood paste is applied daily.",
    },
    {
        "name_en": "Kartika Purnima (Dipaloka)",
        "name_or": "କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା — ଦୀପାଳୋକ",
        "time": "Kartika Shukla Purnima",
        "description": "Thousands of lamps (deep) are lit around Bindu Sagar lake and the Lingaraj temple complex. "
                       "The entire old city glows with diyas on this night.",
    },
    {
        "name_en": "Shiva Vivah (Shivaratri)",
        "name_or": "ଶିବ ବିବାହ",
        "time": "Phalguna Krishna Trayodashi night",
        "description": "A ceremonial divine marriage procession of Lord Lingaraj and Parvati through the city. "
                       "One of the most colourful processions in Bhubaneswar.",
    },
    {
        "name_en": "Prathamastami",
        "name_or": "ପ୍ରଥମାଷ୍ଟମୀ",
        "time": "Margashira Shukla Ashtami",
        "description": "A uniquely Odia festival celebrating first-born children. "
                       "Mothers visit Lingaraj and other Shiva temples to pray for the longevity of their eldest child.",
    },
]


# ─── All 12 Sankrantis ─────────────────────────────────────────────────────

SANKRANTI_INFO = [
    {
        "soura_masa": "Mesha",
        "soura_masa_or": "ମେଷ",
        "name_en": "Maha Vishubha Sankranti / Pana Sankranti",
        "name_or": "ମହା ବିଷୁବ ସଂକ୍ରାନ୍ତି / ପଣ ସଂକ୍ରାନ୍ତି",
        "approx_date": "April 13–15",
        "significance": "most_important",
        "description": "The most important Sankranti for Odisha — this is the Odia New Year (Utkal New Year). "
                       "The Sun enters Aries (Mesha Rashi). Families prepare Pana (a sacred drink of water, "
                       "jaggery, banana, chhena, and sweet spices) and share it. "
                       "Earthen pots of Pana are hung outside homes. "
                       "Maa Biraja at Jajpur and Jagannath Temple hold special pujas. "
                       "This day also marks the start of the scorching Odia summer season.",
        "customs": [
            "Preparing and sharing Pana drink",
            "Hanging earthen pots (Pana Ghata) outside home",
            "Visit to Maa Biraja, Jagannath and Lingaraj temples",
            "Bathe in rivers — especially at Baitarani Ghat, Jajpur",
            "New year blessings exchanged: 'Nua Barsha Abhinandan'",
        ],
    },
    {
        "soura_masa": "Vrishabha",
        "soura_masa_or": "ବୃଷଭ",
        "name_en": "Vrishabha Sankranti",
        "name_or": "ବୃଷଭ ସଂକ୍ରାନ୍ତି",
        "approx_date": "May 14–16",
        "significance": "moderate",
        "description": "The Sun enters Taurus (Vrishabha Rashi). Farmers observe this Sankranti "
                       "as the season for planting and cultivation begins in Odisha.",
        "customs": ["Farmers pray for good harvest", "Charity and donation (Dana)"],
    },
    {
        "soura_masa": "Mithuna",
        "soura_masa_or": "ମିଥୁନ",
        "name_en": "Mithuna Sankranti (Raja Parba)",
        "name_or": "ମିଥୁନ ସଂକ୍ରାନ୍ତି (ରଜ ପର୍ବ)",
        "approx_date": "June 14–16",
        "significance": "important",
        "description": "The Sun enters Gemini (Mithuna Rashi). This Sankranti is the start of the famous "
                       "Raja Parba — a three-day celebration of womanhood and Mother Earth's menstruation. "
                       "Young girls dress up, swing on decorated swings, eat special foods, and rest. "
                       "Ploughing the earth is prohibited during Raja.",
        "customs": [
            "Raja Parba (3-day festival of womanhood)",
            "Swinging (Doli) on decorated swings",
            "Special Pitha (rice cakes) preparation",
            "Girls rest from household work",
            "No ploughing or digging of earth",
        ],
    },
    {
        "soura_masa": "Karka",
        "soura_masa_or": "କର୍କ",
        "name_en": "Karka Sankranti (Dakshinayana)",
        "name_or": "କର୍କ ସଂକ୍ରାନ୍ତି — ଦକ୍ଷିଣାୟନ",
        "approx_date": "July 16–18",
        "significance": "moderate",
        "description": "The Sun enters Cancer (Karka Rashi), marking the beginning of Dakshinayana "
                       "(when the Sun moves southward). The monsoon is at its peak in Odisha. "
                       "Charitable acts are considered especially auspicious.",
        "customs": ["Charity and donation", "Ritual bathing", "Ancestor prayers (Pitru Tarpana)"],
    },
    {
        "soura_masa": "Simha",
        "soura_masa_or": "ସିଂହ",
        "name_en": "Simha Sankranti",
        "name_or": "ସିଂହ ସଂକ୍ରାନ୍ତି",
        "approx_date": "August 16–18",
        "significance": "moderate",
        "description": "The Sun enters Leo (Simha Rashi). Associated with the Jhulana Yatra (swing festival) "
                       "period of Lord Jagannath. Gold (Simha = lion) donations are considered meritorious.",
        "customs": ["Jhulana Yatra period at Jagannath Temple", "Gold donations", "Fasting"],
    },
    {
        "soura_masa": "Kanya",
        "soura_masa_or": "କନ୍ୟା",
        "name_en": "Kanya Sankranti",
        "name_or": "କନ୍ୟା ସଂକ୍ରାନ୍ତି",
        "approx_date": "September 16–18",
        "significance": "moderate",
        "description": "The Sun enters Virgo (Kanya Rashi). Coincides with the period of Navratri and "
                       "Durga Puja preparations. Pitru Paksha (ancestor fortnight) falls in this period.",
        "customs": ["Pitru Paksha offerings", "Durga Puja preparations", "Fasting"],
    },
    {
        "soura_masa": "Tula",
        "soura_masa_or": "ତୁଳା",
        "name_en": "Tula Sankranti",
        "name_or": "ତୁଳା ସଂକ୍ରାନ୍ତି",
        "approx_date": "October 17–19",
        "significance": "moderate",
        "description": "The Sun enters Libra (Tula Rashi). The post-monsoon harvest season begins in Odisha. "
                       "Kartika month begins, which is especially sacred for Odia Hindus.",
        "customs": ["Start of sacred Kartika month observances", "River bathing before dawn", "Lamp lighting"],
    },
    {
        "soura_masa": "Vrischika",
        "soura_masa_or": "ବୃଶ୍ଚିକ",
        "name_en": "Vrischika Sankranti",
        "name_or": "ବୃଶ୍ଚିକ ସଂକ୍ରାନ୍ତି",
        "approx_date": "November 16–18",
        "significance": "moderate",
        "description": "The Sun enters Scorpio (Vrischika Rashi). Manabasa Gurubara (Thursday Lakshmi Puja "
                       "in Margashira month) preparations begin.",
        "customs": ["Ritual bathing", "Manabasa Gurubara preparations", "Charity"],
    },
    {
        "soura_masa": "Dhanu",
        "soura_masa_or": "ଧନୁ",
        "name_en": "Dhanu Sankranti",
        "name_or": "ଧନୁ ସଂକ୍ରାନ୍ତି",
        "approx_date": "December 15–17",
        "significance": "important",
        "description": "The Sun enters Sagittarius (Dhanu Rashi). A month-long pre-dawn ritual called "
                       "'Dhanu Yatra' begins. Devotees wake before sunrise and chant Dhanu hymns, "
                       "worship the Sun God, and eat Poda Pitha (roasted rice cake). "
                       "Dhanu Yatra (a famous open-air theatrical festival) is celebrated in Bargarh district.",
        "customs": [
            "Pre-dawn Dhanu hymn chanting",
            "Sun worship before sunrise",
            "Eating Poda Pitha (baked rice cake)",
            "Dhanu Yatra theatrical festival (Bargarh)",
        ],
    },
    {
        "soura_masa": "Makara",
        "soura_masa_or": "ମକର",
        "name_en": "Makar Sankranti",
        "name_or": "ମକର ସଂକ୍ରାନ୍ତି",
        "approx_date": "January 14–15",
        "significance": "most_important",
        "description": "The Sun enters Capricorn (Makara Rashi), marking Uttarayana (northward movement of the Sun). "
                       "One of the most important festivals across Odisha. "
                       "Sacred bathing at rivers (especially Baitarani at Jajpur). "
                       "Kite flying is a popular tradition. Sesame (til) and jaggery sweets are prepared "
                       "(Til Gura, Til Laddu). Manabasa Gurubara ends during this period. "
                       "Donating til, blankets, and warm clothes is considered highly meritorious.",
        "customs": [
            "Holy bath at Baitarani, Mahanadi, and other rivers",
            "Kite flying (Patanga Utsav)",
            "Eating Til Gura, Til Laddu, Khichudi",
            "Donating sesame, jaggery, blankets to the poor",
            "Visiting Maa Biraja temple at Jajpur",
            "Special Abhisheka at Lingaraj temple",
        ],
    },
    {
        "soura_masa": "Kumbha",
        "soura_masa_or": "କୁମ୍ଭ",
        "name_en": "Kumbha Sankranti",
        "name_or": "କୁମ୍ଭ ସଂକ୍ରାନ୍ତି",
        "approx_date": "February 12–14",
        "significance": "moderate",
        "description": "The Sun enters Aquarius (Kumbha Rashi). Spring is approaching. "
                       "Maha Shivaratri falls during this period (Phalguna Krishnapaksha). "
                       "Ritual bathing and charity are observed.",
        "customs": ["Ritual bathing", "Charity", "Shivaratri preparations"],
    },
    {
        "soura_masa": "Meena",
        "soura_masa_or": "ମୀନ",
        "name_en": "Meena Sankranti",
        "name_or": "ମୀନ ସଂକ୍ରାନ୍ତି",
        "approx_date": "March 14–16",
        "significance": "moderate",
        "description": "The Sun enters Pisces (Meena Rashi), the last solar month before the Odia New Year. "
                       "People begin preparations for Pana Sankranti. Holi (Dola Purnima) falls "
                       "in this period. Traditional Odia year comes to an end.",
        "customs": [
            "Dola Purnima / Holi celebrations",
            "Pana Sankranti preparations",
            "Visit to Jagannath temple for Dola Yatra",
        ],
    },
]


# ─── Odia Heritage ─────────────────────────────────────────────────────────

ODIA_PERSONALITIES = [
    {
        "name": "Emperor Kharavela",
        "name_or": "ସମ୍ରାଟ ଖାରବେଳ",
        "period": "c. 193–170 BCE",
        "category": "Ruler",
        "significance": "The greatest king of Kalinga. His achievements are recorded in the famous "
                        "Hathigumpha inscription in Udayagiri, Bhubaneswar. He defeated the Satavahanas, "
                        "Magadha, and even threatened the Shunga empire. He was a devout Jain. "
                        "Under him, Kalinga reached its peak of cultural and military glory.",
    },
    {
        "name": "King Anantavarman Chodaganga Deva",
        "name_or": "ଅନନ୍ତବର୍ମ ଚୋଡ଼ଗଙ୍ଗ ଦେବ",
        "period": "1078–1147 CE",
        "category": "Ruler",
        "significance": "The greatest Gajapati (Eastern Ganga) king. He built the Jagannath Temple at Puri "
                        "(completed c. 1161 CE), one of the four sacred Dhamas of Hinduism. "
                        "He was also responsible for expanding Odia culture across southern India.",
    },
    {
        "name": "King Narasimhadeva I",
        "name_or": "ନରସିଂହ ଦେବ ପ୍ରଥମ",
        "period": "1238–1264 CE",
        "category": "Ruler",
        "significance": "Built the magnificent Sun Temple of Konark (c. 1250 CE) — a UNESCO World Heritage Site. "
                        "Also defeated the Bengal Sultanate army under Tughral Khan.",
    },
    {
        "name": "Kapilendra Deva",
        "name_or": "କପିଳେନ୍ଦ୍ର ଦେବ",
        "period": "1435–1466 CE",
        "category": "Ruler",
        "significance": "The greatest Gajapati king of the Suryavamshi dynasty. He expanded the Odia empire "
                        "from Ganga (Bengal) to Kaveri (Tamil Nadu). Defeated the Bahmani Sultanate multiple times. "
                        "Under him, Odisha (then called Utkala) was the most powerful kingdom of eastern India.",
    },
    {
        "name": "Sarala Das",
        "name_or": "ସାରଳା ଦାସ",
        "period": "c. 14th–15th century CE",
        "category": "Poet / Saint",
        "significance": "Called 'Adi Kavi' (first poet) of Odia literature. "
                        "Wrote the first Odia Mahabharata (Vilanka Ramayana and Chandi Purana). "
                        "He was a devotee of Maa Sarala at Jhankad, Jagatsinghpur.",
    },
    {
        "name": "Atibadi Jagannath Das",
        "name_or": "ଅତିବଡ଼ ଜଗନ୍ନାଥ ଦାସ",
        "period": "1490–1550 CE",
        "category": "Poet / Saint",
        "significance": "The most revered Odia saint-poet. Wrote the Odia Bhagavata (Srimad Bhagavata in Odia) "
                        "which is read in every Odia household during Kartika month and other festivals. "
                        "He was a Panchasakha saint and a great devotee of Lord Jagannath. "
                        "Called 'Atibadi' (the great one) for his wisdom.",
    },
    {
        "name": "Achyutananda Das",
        "name_or": "ଅଚ୍ୟୁତାନନ୍ଦ ଦାସ",
        "period": "1480–1560 CE",
        "category": "Poet / Saint",
        "significance": "The most prolific of the five Panchasakha saints. Wrote hundreds of works including "
                        "Koili Baikuntham, Shunya Samhita, and famous prophecies (Malika). "
                        "His Malika texts are still read for predictions about Odisha's future.",
    },
    {
        "name": "Upendra Bhanja",
        "name_or": "ଉପେନ୍ଦ୍ର ଭଞ୍ଜ",
        "period": "1670–1720 CE",
        "category": "Poet",
        "significance": "Called 'Kabi Samrat' (Emperor of Poets). Wrote ornate and sophisticated Odia poetry. "
                        "His works include Baidehisha Bilasa, Lavanyabati, and Koti Brahmanda Sundari. "
                        "His poetry is renowned for its music, imagery, and command of Odia language.",
    },
    {
        "name": "Kabisurya Baladev Rath",
        "name_or": "କବିସୂର୍ଯ୍ୟ ବଳଦେବ ରଥ",
        "period": "1789–1845 CE",
        "category": "Poet",
        "significance": "Called 'Kabisurya' (Sun among poets). Famous for Odia lyrical poetry. "
                        "His work Chandrakala and romantic poetry in Odia set the standard for "
                        "modern Odia lyric verse.",
    },
    {
        "name": "Jayee Rajguru (Jaykrushna Rajguru)",
        "name_or": "ଜୟ ରାଜଗୁରୁ",
        "period": "1739–1806 CE",
        "birth_date": "1739",
        "category": "Freedom Fighter",
        "significance": "The first martyr of Odisha's resistance to British rule. "
                        "He was the royal teacher (Rajguru) of the Khurda kingdom and a devout Jagannath devotee. "
                        "He was hanged by the British East India Company in 1806 after the Khurda rebellion. "
                        "Revered as the first freedom fighter of Odisha.",
    },
    {
        "name": "Buxi Jagabandhu Bidyadhara",
        "name_or": "ବକ୍ସି ଜଗବନ୍ଧୁ ବିଦ୍ୟାଧର",
        "period": "1773–1829 CE",
        "category": "Freedom Fighter",
        "significance": "Led the famous Paika Rebellion of 1817 against the British East India Company — "
                        "30 years before the 1857 Sepoy Mutiny. The Paikas (traditional warrior class of Odisha) "
                        "rose under him after the British abolished their land rights. "
                        "The rebellion was suppressed, but it remains Odisha's proudest act of resistance.",
    },
    {
        "name": "Fakir Mohan Senapati",
        "name_or": "ଫକୀର ମୋହନ ସେନାପତି",
        "period": "14 Jan 1843 – 14 Jun 1918",
        "birth_date": "January 14",
        "category": "Writer",
        "significance": "Hailed as the 'Father of Odia Prose' and 'Vyasa of Odisha'. "
                        "His novel Chha Mana Atha Guntha (Six Acres and a Third) is the first modern Odia novel "
                        "and one of the great anti-colonial novels of Indian literature. "
                        "He fought for the recognition of Odia as a separate language from Bengali.",
    },
    {
        "name": "Madhusudan Das",
        "name_or": "ମଧୁସୂଦନ ଦାସ",
        "period": "28 Apr 1848 – 4 Feb 1934",
        "birth_date": "April 28",
        "category": "Statesman / Lawyer",
        "significance": "Called 'Utkal Gourab' (Pride of Odisha). The first Odia barrister of the British era. "
                        "Fought tirelessly for the creation of a separate Odia-speaking province. "
                        "Founded the Utkal Union Conference (1903) which campaigned for Odisha's statehood. "
                        "His dream was realised on 1 April 1936 when Odisha became a separate province.",
    },
    {
        "name": "Gopabandhu Das",
        "name_or": "ଗୋପବନ୍ଧୁ ଦାସ",
        "period": "9 Oct 1877 – 17 Jun 1928",
        "birth_date": "October 9",
        "category": "Freedom Fighter / Educationist",
        "significance": "Called 'Utkalmani' (Jewel of Odisha). A poet, freedom fighter, social worker, and educator. "
                        "Founded Satyabadi School (1909) and Satyabadi Bana Vidyalaya — an open-air school in the forest. "
                        "Founded the famous Odia newspaper Samaj (1919), still published today. "
                        "Worked for the uplift of the poor and flood victims. "
                        "He said: 'Mora desa, mora desha ra mati — I love my country and its soil'.",
    },
    {
        "name": "Veer Surendra Sai",
        "name_or": "ବୀର ସୁରେନ୍ଦ୍ର ସାଇ",
        "period": "23 Jan 1809 – 28 Feb 1884",
        "birth_date": "January 23",
        "category": "Freedom Fighter",
        "significance": "The greatest freedom fighter of western Odisha. Fought against British rule for over 40 years. "
                        "He was imprisoned for years but continued to resist. "
                        "He is called 'Veer' (Brave) for his relentless resistance. "
                        "The people of Sambalpur revere him as their greatest hero.",
    },
    {
        "name": "Biju Patnaik",
        "name_or": "ବିଜୁ ପଟ୍ଟନାୟକ",
        "period": "5 Mar 1916 – 17 Apr 1997",
        "birth_date": "March 5",
        "category": "Statesman / Pilot",
        "significance": "The most beloved chief minister of Odisha. A daring pilot who helped the Indonesian "
                        "independence struggle during World War II. Participated in the Indian independence movement. "
                        "His birthday (March 5) is celebrated as Utkala Dibasa (Odisha Day). "
                        "Biju Patnaik International Airport in Bhubaneswar is named after him. "
                        "Known for his fearless personality and love for Odisha.",
    },
]

ODIA_HISTORY = [
    {
        "period": "261 BCE",
        "event_en": "Kalinga War — Ashoka's Transformation",
        "event_or": "କଳିଙ୍ଗ ଯୁଦ୍ଧ",
        "description": "Emperor Ashoka of the Maurya Empire invaded Kalinga (ancient Odisha). "
                       "The war was one of the bloodiest in ancient India — over 100,000 were killed and "
                       "150,000 deported. Ashoka was so devastated by the carnage that he renounced war, "
                       "converted to Buddhism, and propagated ahimsa (non-violence) across Asia. "
                       "His rock edicts at Dhauli (near Bhubaneswar) still stand as a testament.",
    },
    {
        "period": "c. 193–170 BCE",
        "event_en": "Emperor Kharavela's Golden Age",
        "event_or": "ସମ୍ରାଟ ଖାରବେଳଙ୍କ ଶାସନ",
        "description": "King Kharavela of Kalinga rebuilt and expanded the empire. "
                       "He defeated multiple kingdoms including Magadha, Satakarni, and Pandya. "
                       "His inscriptions at Hathigumpha, Udayagiri describe great achievements: "
                       "digging canals, building cities, protecting trade, and patronising art. "
                       "He was a devout Jain and great administrator.",
    },
    {
        "period": "7th–8th century CE",
        "event_en": "Bhaumakara Dynasty — Buddhist Odisha",
        "event_or": "ଭୌମ-କର ବଂଶ",
        "description": "The Bhaumakara dynasty ruled Odisha from Khiching (Keonjhar district). "
                       "They were great patrons of Buddhism and also Shakti worship. "
                       "Many temples at Udayagiri and Ratnagiri (Buddhist ruins) date to this era.",
    },
    {
        "period": "c. 1000–1100 CE",
        "event_en": "Somavanshi Dynasty — Lingaraj Temple Built",
        "event_or": "ସୋମବଂଶ — ଲିଙ୍ଗରାଜ ମନ୍ଦିର ନିର୍ମାଣ",
        "description": "The Somavanshi kings built the magnificent Lingaraj Temple at Bhubaneswar (~11th century CE). "
                       "The temple is one of the finest examples of Kalinga architecture. "
                       "Bhubaneswar was known as 'Ekamra Kshetra' — city of temples — during this era.",
    },
    {
        "period": "1135 CE",
        "event_en": "Jagannath Temple Built (Puri)",
        "event_or": "ଜଗନ୍ନାଥ ମନ୍ଦିର ନିର୍ମାଣ — ପୁରୀ",
        "description": "King Anantavarman Chodaganga Deva of the Eastern Ganga dynasty built the present "
                       "Jagannath Temple at Puri. The 65-metre tall temple tower (Vimana) became one of the "
                       "four sacred Dhamas of Hinduism. It is considered the world's first communal kitchen "
                       "(Ananda Bazar) where 100,000 people can be fed daily.",
    },
    {
        "period": "c. 1250 CE",
        "event_en": "Konark Sun Temple Built",
        "event_or": "କୋଣାର୍କ ସୂର୍ଯ୍ୟ ମନ୍ଦିର ନିର୍ମାଣ",
        "description": "King Narasimhadeva I of the Eastern Ganga dynasty built the spectacular Sun Temple at Konark. "
                       "Designed as a giant chariot with 24 wheels pulled by seven horses, "
                       "the temple represents the Sun God's celestial chariot. "
                       "It is a UNESCO World Heritage Site (1984) and one of the Seven Wonders of India.",
    },
    {
        "period": "1435–1466 CE",
        "event_en": "Kapilendra Deva — Peak of Gajapati Empire",
        "event_or": "କପିଳେନ୍ଦ୍ର ଦେବ — ଗଜପତି ସାମ୍ରାଜ୍ୟ ସର୍ବୋଚ୍ଚ",
        "description": "Kapilendra Deva established the Suryavamshi Gajapati dynasty. "
                       "His empire stretched from the Ganges in the north to the Kaveri in the south. "
                       "He defeated the Bahmani Sultanate and the Vijayanagara empire. "
                       "This was the last great Hindu empire of medieval eastern India.",
    },
    {
        "period": "1568 CE",
        "event_en": "Fall of the Gajapati Empire",
        "event_or": "ଗଜପତି ରାଜ୍ୟ ପ୍ରତ",
        "description": "The Afghan general Suleiman Karrani invaded and defeated Mukundadeva, "
                       "the last Gajapati king. Odisha came under Afghan (and later Mughal) control. "
                       "However, the Khurda kings maintained the tradition of Jagannath worship and "
                       "local governance as the 'Gajapatis' in a reduced capacity.",
    },
    {
        "period": "1751 CE",
        "event_en": "Maratha Rule Begins in Odisha",
        "event_or": "ମରାଠା ଶାସନ — ଓଡ଼ିଶା",
        "description": "The Marathas under Raghoji I Bhonsle defeated the Mughals and took control of Odisha. "
                       "Maratha rule lasted until the British conquest of 1803. "
                       "Under Maratha rule, Jagannath Temple administration was reorganised.",
    },
    {
        "period": "1803 CE",
        "event_en": "British East India Company Takes Control",
        "event_or": "ବ୍ରିଟିଶ ଅଧୀନ ଓଡ଼ିଶା",
        "description": "General Wellesley (later Duke of Wellington) defeated the Marathas in the Second "
                       "Anglo-Maratha War. Odisha became part of the Bengal Presidency under the British "
                       "East India Company. The Khurda kingdom was reduced and eventually annexed by 1817.",
    },
    {
        "period": "1817 CE",
        "event_en": "Paika Rebellion — First War of Independence",
        "event_or": "ପାଇକ ବିଦ୍ରୋହ",
        "description": "Buxi Jagabandhu led the Paikas (Odisha's traditional warrior class) in a revolt against "
                       "British East India Company rule — 40 years before the 1857 Sepoy Mutiny. "
                       "The rebellion began when British policies destroyed the Paikas' traditional land rights. "
                       "Though suppressed, it remains a proud symbol of Odia resistance. "
                       "In 2017, the Indian government officially recognised it as 'the first war of independence'.",
    },
    {
        "period": "1 April 1936",
        "event_en": "Odisha Becomes a Separate Province",
        "event_or": "ଓଡ଼ିଶା ଅଲଗା ରାଜ୍ୟ",
        "description": "After decades of struggle led by Madhusudan Das, Gopabandhu Das, and Utkalmani patriots, "
                       "the British government finally created a separate Odia-speaking province on 1 April 1936. "
                       "This day is celebrated as Utkala Dibasa (Odisha Formation Day) every year. "
                       "It was the first province in India to be created on linguistic lines.",
    },
    {
        "period": "26 January 1950",
        "event_en": "Odisha as a State in Independent India",
        "event_or": "ସ୍ୱାଧୀନ ଭାରତରେ ଓଡ଼ିଶା ରାଜ୍ୟ",
        "description": "With India's Constitution coming into force, Odisha officially became a state of "
                       "the Republic of India. The merger of 24 princely states into Odisha was completed "
                       "under the leadership of Sardar Vallabhbhai Patel and Biswanath Das.",
    },
    {
        "period": "4 November 2011",
        "event_en": "Name changed to 'Odisha'",
        "event_or": "'ଓଡ଼ିଶା' ନାମ ସ୍ୱୀକୃତ",
        "description": "The Indian Parliament passed a bill renaming 'Orissa' to 'Odisha' "
                       "and the language from 'Oriya' to 'Odia' — restoring the original Odia-script name "
                       "of the state. A long-standing demand of the Odia people was fulfilled.",
    },
]
