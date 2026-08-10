"""
Curated festival stories for Odia Panchang.

NON-NEGOTIABLES (see also spec.md):
  1. Accuracy & authenticity — traditional/public lore only; no invented nitis.
  2. Proper Odia script — real Odia prose with correct yuktākṣara (ଯୁକ୍ତାକ୍ଷର);
     never fall back to English in the `or` field; never paste Devanagari body text.

Stories attach at API time by festival name_en (no DB reseed required).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

# Odia block + common marks allowed in Odia prose
_ODIA_CHAR = re.compile(r"[\u0B00-\u0B7F]")
# Devanagari *letters* not allowed in Odia body (danda U+0964 is shared Indic punctuation — allowed)
_DEV_LETTER = re.compile(r"[\u0900-\u0963\u0966-\u097F]")
_LATIN_LETTER = re.compile(r"[A-Za-z]")


def validate_odia_text(text: str, *, field: str = "or") -> None:
    """
    Raise ValueError if Odia text violates script non-negotiables.
    Allowed: Odia letters/signs, spaces, digits (ASCII or Odia),
    common punctuation including Indic danda (।), quotes, em-dash.
    """
    if text is None or not str(text).strip():
        raise ValueError(f"{field}: Odia text is empty")
    t = unicodedata.normalize("NFC", str(text).strip())
    if not _ODIA_CHAR.search(t):
        raise ValueError(f"{field}: no Odia characters found")
    if _DEV_LETTER.search(t):
        raise ValueError(f"{field}: Devanagari letters are not allowed in Odia text")
    if _LATIN_LETTER.search(t):
        raise ValueError(f"{field}: Latin letters are not allowed in Odia text")


def _b(en: str, or_text: str) -> dict[str, str]:
    """Bilingual pair — both required; Odia validated."""
    en_s = (en or "").strip()
    or_s = unicodedata.normalize("NFC", (or_text or "").strip())
    if not en_s:
        raise ValueError("English text is required")
    validate_odia_text(or_s, field="or")
    # Never allow identical copy of English into Odia
    if or_s == en_s:
        raise ValueError("Odia text must not be a copy of English")
    return {"en": en_s, "or": or_s}


def _story(
    story_en: str,
    story_or: str,
    why_en: str,
    why_or: str,
    kind: str,
    sources: list[str],
) -> dict[str, Any]:
    assert kind in {
        "puranic_tradition",
        "historical_cultural",
        "ritual_observance",
    }, kind
    return {
        "story": _b(story_en, story_or),
        "why_today": _b(why_en, why_or),
        "kind": kind,
        "sources": list(sources),
    }


# ── Shared authentic narratives ────────────────────────────────────────────

_RATH = _story(
    "In the Puri tradition, Lord Jagannath, Balabhadra and Subhadra leave the main temple "
    "in three great wooden chariots and travel along the Bada Danda to Gundicha Temple — "
    "remembered as the Lord’s maternal aunt’s house, linked with Queen Gundicha, consort of "
    "legendary King Indradyumna. Devotees pull the chariots; after a stay at Gundicha comes "
    "the return journey (Bahuda Yatra).",
    "ପୁରୀ ପରମ୍ପରାରେ ମହାପ୍ରଭୁ ଶ୍ରୀଜଗନ୍ନାଥ, ବଳଭଦ୍ର ଓ ସୁଭଦ୍ରା ତିନୋଟି ବିଶାଳ କାଠ ରଥରେ "
    "ବଡ଼ଦାଣ୍ଡ ଦେଇ ଗୁଣ୍ଡିଚା ମନ୍ଦିରକୁ ଯାତ୍ରା କରନ୍ତି। ଏହାକୁ ରାଣୀ ଗୁଣ୍ଡିଚାଙ୍କ ଘର — ମାଉସୀ ମା’ଙ୍କ ଘର — "
    "ବୋଲି ପରମ୍ପରାରେ କୁହାଯାଏ। ଭକ୍ତମାନେ ରଥ ଟାଣନ୍ତି। କିଛି ଦିନ ଗୁଣ୍ଡିଚାରେ ରହିବା ପରେ ବାହୁଡ଼ା ଯାତ୍ରାରେ "
    "ମୂଳ ମନ୍ଦିରକୁ ପ୍ରତ୍ୟାବର୍ତ୍ତନ ହୁଏ।",
    "Today is Ashadha Shukla Dwitiya — the principal chariot day in the Sri Mandir calendar.",
    "ଆଜି ଆଷାଢ଼ ଶୁକ୍ଳ ଦ୍ୱିତୀୟା — ଶ୍ରୀମନ୍ଦିର କ୍ୟାଲେଣ୍ଡରରେ ମୁଖ୍ୟ ରଥଯାତ୍ରା ଦିନ।",
    "puranic_tradition",
    ["Puri Ratha Yatra public tradition", "Gundicha / Indradyumna lore"],
)

_SNANA = _story(
    "On Jyeshtha Purnima the deities are taken to the Snana Mandapa and bathed with many "
    "pots of scented water — classically remembered as one hundred and eight. After this "
    "Deva Snana, tradition holds that the deities enter Anavasara (a period of privacy). "
    "Public darshan of the wooden forms pauses until Nava Jaubana and Rath Yatra.",
    "ଜ୍ୟେଷ୍ଠ ପୂର୍ଣ୍ଣିମାରେ ଚତୁର୍ଦ୍ଧାମୂର୍ତ୍ତିଙ୍କୁ ସ୍ନାନମଣ୍ଡପକୁ ନିଆଯାଇ ସୁବାସିତ ଜଳରେ ସ୍ନାନ କରାଯାଏ — "
    "ପରମ୍ପରାରେ ଏହାକୁ ଏକଶହ ଆଠ କଳସ ସ୍ନାନ ବୋଲି କୁହାଯାଏ। ଦେବସ୍ନାନ ପରେ ଦେବତାମାନେ ଅନବସରକାଳରେ ରୁହନ୍ତି। "
    "ନବଯୌବନ ଦର୍ଶନ ଓ ରଥଯାତ୍ରା ପର୍ଯ୍ୟନ୍ତ ସାଧାରଣ ଦାରୁବିଗ୍ରହ ଦର୍ଶନ ବନ୍ଦ ରହେ।",
    "Today is Snana Purnima — the ceremonial bath that begins Anavasara before Rath Yatra.",
    "ଆଜି ଦେବସ୍ନାନ ପୂର୍ଣ୍ଣିମା — ରଥଯାତ୍ରା ପୂର୍ବରୁ ଅନବସର ଆରମ୍ଭର ଦିନ।",
    "ritual_observance",
    ["Deva Snana / Anavasara (Puri temple tradition)"],
)

_BOITA = _story(
    "On Kartika Purnima, Odisha observes Boita Bandana: people float small boats with lamps "
    "and flowers, chanting “Aa Ka Ma Boi”. The rite remembers the Sadhabas — merchant mariners "
    "of ancient Kalinga who sailed toward Southeast Asia. It is living memory of Odisha’s "
    "maritime heritage as much as a full-moon festival.",
    "କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମାରେ ଓଡ଼ିଶାରେ ବୋଇତ ବନ୍ଦନ ପାଳିତ ହୁଏ। ଲୋକେ ଛୋଟ ନୌକାରେ ଦୀପ ଓ ଫୁଲ ରଖି ଭସାନ୍ତି "
    "ଏବଂ «ଆ କା ମା ବୋଇ» ଗୀତ ଗାଆନ୍ତି। ଏହା ପ୍ରାଚୀନ କଳିଙ୍ଗର ସାଧବ ବଣିକମାନଙ୍କ ସମୁଦ୍ରଯାତ୍ରାକୁ ସ୍ମରଣ କରେ। "
    "ଏହା କେବଳ ପୂର୍ଣ୍ଣିମା ନୁହେଁ — ଓଡ଼ିଶାର ସାମୁଦ୍ରିକ ଐତିହ୍ୟର ଜୀବନ୍ତ ସ୍ମୃତି।",
    "Kartika full moon — principal day for Boita Bandana in Odisha.",
    "କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମା — ବୋଇତ ବନ୍ଦନର ମୁଖ୍ୟ ଦିନ।",
    "historical_cultural",
    ["Boita Bandana / Kalinga maritime tradition", "Odisha cultural practice"],
)

_RAJA = _story(
    "Raja Parba, around Mithuna Sankranti, honours womanhood and the earth’s fertility. "
    "In popular Odia belief Mother Earth rests as if in her annual menstruation for three days; "
    "ploughing stops. Girls swing on dolis, wear new clothes, and share pithas. The fourth day "
    "is Basumati Snana — the earth’s ceremonial bath.",
    "ମିଥୁନ ସଂକ୍ରାନ୍ତି ସମୟରେ ପାଳିତ ରଜ ପର୍ବ ନାରୀତ୍ୱ ଓ ପୃଥିବୀର ଉର୍ବରତାକୁ ସମ୍ମାନ ଦିଏ। "
    "ଲୋକବିଶ୍ୱାସ ଅନୁସାରେ ମା’ ପୃଥିବୀ ତିନିଦିନ ଋତୁକାଳରେ ରୁହନ୍ତି; କୃଷିକାର୍ଯ୍ୟ ବନ୍ଦ ରହେ। "
    "ଝିଅମାନେ ନୂଆ ଲୁଗା ପିନ୍ଧି ଡୋଳି ଖେଳନ୍ତି ଓ ପିଠା ଖାଆନ୍ତି। ଚତୁର୍ଥ ଦିନ ବସୁମତୀ ସ୍ନାନ।",
    "Solar entry into Mithuna begins the Raja festival season — a distinctly Odia observance.",
    "ମିଥୁନ ସଂକ୍ରାନ୍ତିରୁ ରଜ ପର୍ବ — ଓଡ଼ିଆ ସମାଜର ବିଶେଷ ପର୍ବ।",
    "historical_cultural",
    ["Raja Parba (Odia tradition)", "Mithuna Sankranti"],
)

_BIRAJA_PEETH = _story(
    "Jajpur’s Biraja peetha is counted among the great Shakti peethas. Traditional accounts "
    "say the navel of Goddess Sati fell in Viraja kshetra of Utkala. The goddess is worshipped "
    "as Biraja–Durga; local calendars highlight her extended autumn worship and the Simhadhwaja "
    "chariot whose flag bears a lion.",
    "ଯାଜପୁରର ବିରଜା ପୀଠକୁ ମହାଶକ୍ତିପୀଠ ମଧ୍ୟରେ ଗଣାଯାଏ। ପରମ୍ପରା ଅନୁସାରେ ଦେବୀ ସତୀଙ୍କ ନାଭି "
    "ଉତ୍କଳର ବିରଜା କ୍ଷେତ୍ରରେ ପତିଥିଲା। ଏଠାରେ ଦେବୀ ବିରଜା-ଦୁର୍ଗା ରୂପେ ପୂଜିତ। ସ୍ଥାନୀୟ ପାଞ୍ଜିରେ "
    "ଦୀର୍ଘ ଶାରଦୀୟ ପୂଜା ଓ ସିଂହଧ୍ୱଜ ରଥଯାତ୍ରା — ଯାହାର ଧ୍ୱଜରେ ସିଂହ ଚିହ୍ନ — ବିଶେଷ ଭାବେ ଉଲ୍ଲେଖିତ।",
    "Biraja-tradition days honour Maa Biraja’s peetha at Jajpur, distinct from Puri’s Jagannath cycle.",
    "ବିରଜା ପରମ୍ପରାର ଦିନ — ଯାଜପୁର ମା’ ବିରଜା ପୀଠ; ପୁରୀ ଜଗନ୍ନାଥ ଚକ୍ରଠାରୁ ଅଲଗା।",
    "puranic_tradition",
    ["Biraja peetha tradition", "Shakti peetha lists (traditional)"],
)

_PANA = _story(
    "Pana Sankranti (Maha Bishuba / Mesha Sankranti) is the Odia solar New Year. Families offer "
    "sweet pana to guests; Hanuman is remembered; temples hold special rites. The civil Odia year "
    "turns with the Sun’s entry into Mesha.",
    "ପଣା ସଂକ୍ରାନ୍ତି ବା ମହାବିଷୁବ ସଂକ୍ରାନ୍ତି ହେଉଛି ଓଡ଼ିଆ ସୌର ନୂତନ ବର୍ଷ। ଘରେ ମିଠା ପଣା ବଣ୍ଟାଯାଏ; "
    "ହନୁମାନଙ୍କୁ ସ୍ମରଣ କରାଯାଏ; ମନ୍ଦିରରେ ବିଶେଷ ନୀତି ହୁଏ। ସୂର୍ଯ୍ୟ ମେଷରାଶିରେ ପ୍ରବେଶ କରିବା ସହିତ "
    "ଓଡ଼ିଆ ସୌର ବର୍ଷ ଆରମ୍ଭ ହୁଏ।",
    "First day of solar Mesha — Odia New Year in the panji civil calendar.",
    "ମେଷ ସଂକ୍ରାନ୍ତି — ଓଡ଼ିଆ ପାଞ୍ଜିର ସୌର ନୂତନ ବର୍ଷ।",
    "ritual_observance",
    ["Odia calendar / Pana Sankranti", "Maha Bishuba Sankranti"],
)

_NUAKHAI = _story(
    "Nuakhai is western Odisha’s harvest thanksgiving. The first grains of new rice are offered "
    "to the household deity — often Samaleswari — before the family eats. People exchange "
    "“Nuakhai Juhar”. At Biraja peetha the same first-fruit spirit is observed with local rites.",
    "ନୂଆଖାଇ ପଶ୍ଚିମ ଓଡ଼ିଶାର ଫସଲ ଧନ୍ୟବାଦ ପର୍ବ। ନୂଆ ଧାନର ପ୍ରଥମ ଅନ୍ନ ଘରଦେବୀ — ପ୍ରାୟଃ ସମଲେଶ୍ୱରୀ — "
    "ଙ୍କୁ ଅର୍ପଣ କରାଯିବା ପରେ ପରିବାର ଭୋଜନ କରନ୍ତି। ଲୋକେ «ନୂଆଖାଇ ଜୁହାର» ଆଦାନପ୍ରଦାନ କରନ୍ତି। "
    "ବିରଜା ପୀଠରେ ମଧ୍ୟ ନୂଆ ଅନ୍ନ ଅର୍ପଣର ପରମ୍ପରା ରହିଛି।",
    "Bhadrapada Shukla Panchami — traditional Nuakhai day in many Odia calendars.",
    "ଭାଦ୍ରବ ଶୁକ୍ଳ ପଞ୍ଚମୀ — ନୂଆଖାଇ ପାଳନର ପାରମ୍ପରିକ ଦିନ।",
    "historical_cultural",
    ["Nuakhai (western Odisha)", "first-grain custom"],
)

_KUMAR = _story(
    "Kumar Purnima (Ashwina full moon) is a distinctly Odia festival for unmarried girls. "
    "They worship the rising moon, wear new clothes, prepare pithas, and play in moonlight, "
    "praying for a good life.",
    "କୁମାର ପୂର୍ଣ୍ଣିମା ଓଡ଼ିଆ ସମାଜର ବିଶେଷ ପର୍ବ। ଅବିବାହିତା ଝିଅମାନେ ଉଦୀୟମାନ ଚନ୍ଦ୍ରଙ୍କୁ ପୂଜା କରନ୍ତି, "
    "ନୂଆ ଲୁଗା ପିନ୍ଧନ୍ତି, ପିଠା ତିଆରି କରନ୍ତି ଓ ଜୋତ୍ସ୍ନାରେ ଖେଳନ୍ତି।",
    "Ashwina Purnima — Kumar Purnima moon worship.",
    "ଆଶ୍ୱିନ ପୂର୍ଣ୍ଣିମା — କୁମାର ପୂର୍ଣ୍ଣିମା।",
    "historical_cultural",
    ["Kumar Purnima (Odia tradition)"],
)

_PRATHAMA = _story(
    "Prathamastami is uniquely Odia: mothers pray for the long life of the first-born "
    "(or eldest child), prepare Enduri pitha, and offer puja on Margashira Shukla Ashtami.",
    "ପ୍ରଥମାଷ୍ଟମୀ କେବଳ ଓଡ଼ିଆ ଘରର ପର୍ବ। ମା’ମାନେ ପ୍ରଥମ ସନ୍ତାନଙ୍କ ଦୀର୍ଘାୟୁ ପାଇଁ ପୂଜା କରନ୍ତି "
    "ଓ ଏଣ୍ଡୁରି ପିଠା ତିଆରି କରନ୍ତି। ଏହା ମାର୍ଗଶୀର ଶୁକ୍ଳ ଅଷ୍ଟମୀରେ ପଡ଼େ।",
    "Margashira Shukla Ashtami — day of blessing for the first child.",
    "ମାର୍ଗଶୀର ଶୁକ୍ଳ ଅଷ୍ଟମୀ — ପ୍ରଥମାଷ୍ଟମୀ।",
    "historical_cultural",
    ["Prathamastami (Odia household tradition)"],
)

_SAVITRI = _story(
    "Savitri Amavasya remembers Savitri, who through devotion and wisdom prevailed before Yama "
    "for her husband Satyavan’s life. Married women fast and worship the banyan, praying for "
    "their husbands’ long life.",
    "ସାବିତ୍ରୀ ଅମାବାସ୍ୟାରେ ସାବିତ୍ରୀଙ୍କ କାହାଣୀ ସ୍ମରଣ କରାଯାଏ — ଯେ ଭକ୍ତି ଓ ବୁଦ୍ଧି ଦ୍ୱାରା "
    "ସ୍ୱାମୀ ସତ୍ୟବାନଙ୍କ ଜୀବନ ପାଇଁ ଯମଙ୍କ ସମ୍ମୁଖରେ ଦୃଢ଼ ରହିଥିଲେ। ବିବାହିତା ନାରୀମାନେ ଉପବାସ କରି "
    "ବଟବୃକ୍ଷ ପୂଜା କରନ୍ତି ଓ ସ୍ୱାମୀଙ୍କ ଦୀର୍ଘାୟୁ ପ୍ରାର୍ଥନା କରନ୍ତି।",
    "Jyeshtha Krishna Amavasya — Savitri / Vat Savitri vrat.",
    "ଜ୍ୟେଷ୍ଠ କୃଷ୍ଣ ଅମାବାସ୍ୟା — ସାବିତ୍ରୀ ବ୍ରତ।",
    "puranic_tradition",
    ["Savitri–Satyavan tradition", "Vat Savitri vrat"],
)

_HERA = _story(
    "On Hera Panchami, tradition says Goddess Lakshmi goes from the main temple in search of "
    "Jagannath who is still at Gundicha. Temple lore describes her hurt and the later "
    "reconciliation at Niladri Bije — popularly remembered with an offering of rasagola.",
    "ହେର ପଞ୍ଚମୀରେ ପରମ୍ପରା ଅନୁସାରେ ମା’ ଲକ୍ଷ୍ମୀ ମୂଳ ମନ୍ଦିରରୁ ଗୁଣ୍ଡିଚାରେ ଥିବା ମହାପ୍ରଭୁଙ୍କୁ "
    "ଖୋଜିବାକୁ ଯାଆନ୍ତି। ମନ୍ଦିର କାହାଣୀରେ ତାଙ୍କ ଅଭିମାନ ଓ ପରେ ନୀଳାଦ୍ରି ବିଜେ ସମୟରେ ସମାଧାନର ବର୍ଣ୍ଣନା "
    "ରହିଛି — ଲୋକସ୍ମୃତିରେ ରସଗୋଲା ଅର୍ପଣ ସହିତ ଏହା ଯୋଡ଼ା।",
    "Ashadha Shukla Panchami during the Gundicha stay — Lakshmi’s search for the Lord.",
    "ଗୁଣ୍ଡିଚା ଅବସ୍ଥାନ କାଳର ଆଷାଢ଼ ଶୁକ୍ଳ ପଞ୍ଚମୀ — ହେର ପଞ୍ଚମୀ।",
    "puranic_tradition",
    ["Hera Panchami / Niladri Bije (Puri temple lore)"],
)

_NILADRI = _story(
    "Niladri Bije is the deities’ re-entry into the main Jagannath Temple after Rath Yatra. "
    "Temple tradition tells that Lakshmi bars the door in hurt; Jagannath pacifies her — "
    "in popular Odia memory with rasagola — and the temple household is restored.",
    "ନୀଳାଦ୍ରି ବିଜେ ରଥଯାତ୍ରା ପରେ ଚତୁର୍ଦ୍ଧାମୂର୍ତ୍ତିଙ୍କ ମୂଳ ଶ୍ରୀମନ୍ଦିରକୁ ପ୍ରବେଶ। ପରମ୍ପରାରେ ମା’ ଲକ୍ଷ୍ମୀ "
    "ଅଭିମାନରେ ଦ୍ୱାର ରୁନ୍ଧନ୍ତି; ମହାପ୍ରଭୁ ତାଙ୍କୁ ସନ୍ତୁଷ୍ଟ କରନ୍ତି — ଓଡ଼ିଆ ଲୋକସ୍ମୃତିରେ ରସଗୋଲା ଅର୍ପଣ "
    "ସହିତ — ଏବଂ ମନ୍ଦିରର ଘରକଥା ସୁସ୍ଥ ହୁଏ।",
    "Return into the main temple after the chariot festival — day of reconciliation with Lakshmi.",
    "ରଥଯାତ୍ରା ପରେ ମୂଳ ମନ୍ଦିର ପ୍ରବେଶ — ନୀଳାଦ୍ରି ବିଜେ।",
    "puranic_tradition",
    ["Niladri Bije (Puri)", "popular rasagola reconciliation retelling"],
)

_SITAL = _story(
    "Sital Shashthi celebrates the divine wedding of Shiva and Parvati. In western Odisha, "
    "especially Sambalpur, it is a major community festival with processions and vivah-lila of the deities.",
    "ସୀତଳ ଷଷ୍ଠୀରେ ଶିବ-ପାର୍ବତୀଙ୍କ ବିବାହ ଉତ୍ସବ ପାଳିତ ହୁଏ। ପଶ୍ଚିମ ଓଡ଼ିଶାରେ, ବିଶେଷକରି ସମ୍ବଲପୁରରେ, "
    "ଏହା ବିଶାଳ ସାମୁହିକ ପର୍ବ — ଶୋଭାଯାତ୍ରା ଓ ଦେବବିବାହ ଲୀଳା ସହିତ।",
    "Jyeshtha Shukla Shashthi — Shiva–Parvati vivah observance.",
    "ଜ୍ୟେଷ୍ଠ ଶୁକ୍ଳ ଷଷ୍ଠୀ — ସୀତଳ ଷଷ୍ଠୀ।",
    "puranic_tradition",
    ["Sital Shashthi (western Odisha)"],
)

_MANABASA = _story(
    "Manabasa Gurubara is Lakshmi worship on the Thursdays of Margashira. Odia homes clean, "
    "draw jhoti, and recall the Lakshmi Purana associated with Balarama Dasa — teaching that "
    "Lakshmi blesses humility and rejects pride of birth.",
    "ମାର୍ଗଶୀର ମାସର ଗୁରୁବାରଗୁଡ଼ିକରେ ମନବସା ଗୁରୁବାର — ମା’ ଲକ୍ଷ୍ମୀଙ୍କ ପୂଜା। ଓଡ଼ିଆ ଘରେ ଘର ସଫା, "
    "ଝୋଟି ଓ ବଳରାମ ଦାସଙ୍କ ଲକ୍ଷ୍ମୀ ପୁରାଣର ଶିକ୍ଷା ସ୍ମରଣ କରାଯାଏ — ଲକ୍ଷ୍ମୀ ବିନୟକୁ ଆଶୀର୍ବାଦ କରନ୍ତି, "
    "ଜାତି ଅହଙ୍କାରକୁ ନୁହେଁ।",
    "Thursdays of Margashira — Odia household Lakshmi rite.",
    "ମାର୍ଗଶୀର ଗୁରୁବାର — ମନବସା।",
    "historical_cultural",
    ["Manabasa Gurubara", "Lakshmi Purana (Balarama Dasa) tradition"],
)

_DOLA = _story(
    "Dola Purnima is Odisha’s Holi: Radha–Krishna (and in Puri, Jagannath) are placed on a "
    "decorated swing; colours and folk songs fill the day.",
    "ଡୋଳ ପୂର୍ଣ୍ଣିମା ଓଡ଼ିଶାର ହୋଲି। ରାଧାକୃଷ୍ଣ — ପୁରୀରେ ଜଗନ୍ନାଥ — ଙ୍କୁ ସଜା ଡୋଳରେ ବସାଯାଏ; "
    "ରଙ୍ଗଖେଳ ଓ ଲୋକଗୀତରେ ଦିନ ଭରିଯାଏ।",
    "Phalguna Purnima — Dola / Odia Holi.",
    "ଫାଲ୍ଗୁନ ପୂର୍ଣ୍ଣିମା — ଡୋଳ ପୂର୍ଣ୍ଣିମା।",
    "ritual_observance",
    ["Dola Purnima / Odia Holi"],
)

_AKSHAYA = _story(
    "Akshaya Tritiya is named for what never diminishes. Tradition holds the day good for "
    "beginnings and charity. In Puri, Chandan Yatra begins on this tithi — sandal-paste rites "
    "and boat processions on Narendra tank.",
    "ଅକ୍ଷୟ ତୃତୀୟା — ଯାହା କ୍ଷୟ ହୁଏ ନାହିଁ। ପରମ୍ପରାରେ ଏହି ଦିନ ଶୁଭାରମ୍ଭ ଓ ଦାନ ପାଇଁ ଉତ୍ତମ। "
    "ପୁରୀରେ ଏହି ତିଥିରୁ ଚନ୍ଦନ ଯାତ୍ରା ଆରମ୍ଭ — ଚନ୍ଦନ ଲେପ ଓ ନରେନ୍ଦ୍ର ପୁଷ୍କରିଣୀରେ ଚାପଖେଳ।",
    "Vaishakha Shukla Tritiya — auspicious beginnings; Chandan Yatra start at Puri.",
    "ବୈଶାଖ ଶୁକ୍ଳ ତୃତୀୟା — ଅକ୍ଷୟ ତୃତୀୟା; ପୁରୀରେ ଚନ୍ଦନ ଯାତ୍ରା ଆରମ୍ଭ।",
    "ritual_observance",
    ["Akshaya Tritiya", "Chandan Yatra (Puri)"],
)

_MAKARA = _story(
    "Makar Sankranti marks the Sun’s entry into Makara. Odias prepare sesame–jaggery foods, "
    "bathe in rivers, and fly kites. At Jajpur’s Dashaswamedha ghat on the Baitarani, "
    "Makar snanam draws large crowds.",
    "ମକର ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ ମକରରାଶିରେ ପ୍ରବେଶ କରନ୍ତି। ଓଡ଼ିଆ ଘରେ ତିଳଗୁଡ଼, ନଦୀସ୍ନାନ ଓ ଗୁଡ଼ିଉଡ଼ା "
    "ଦେଖାଯାଏ। ଯାଜପୁର ବୈତରଣୀ ତୀରର ଦଶାଶ୍ୱମେଧ ଘାଟରେ ମକର ସ୍ନାନ ପାଇଁ ବିପୁଳ ଜନସମାଗମ ହୁଏ।",
    "Solar Makara ingress — winter festival and holy bath day.",
    "ମକର ସଂକ୍ରାନ୍ତି — ସୂର୍ଯ୍ୟଙ୍କ ମକର ପ୍ରବେଶ; ପୁଣ୍ୟସ୍ନାନର ଦିନ।",
    "ritual_observance",
    ["Makar Sankranti", "Jajpur Makar snanam"],
)

_DURGA = _story(
    "Sharadiya Durga Puja retells Durga’s victory over Mahishasura. In Odisha the days from "
    "Shashthi through Dashami structure the main rites. At Biraja peetha the goddess is at home; "
    "a longer autumn cycle and Simhadhwaja ratha mark Jajpur’s Shakti calendar.",
    "ଶାରଦୀୟ ଦୁର୍ଗାପୂଜାରେ ମହିଷାସୁର ଉପରେ ଦେବୀ ଦୁର୍ଗାଙ୍କ ବିଜୟର କାହାଣୀ ସ୍ମରଣ କରାଯାଏ। ଓଡ଼ିଶାରେ "
    "ଷଷ୍ଠୀରୁ ଦଶମୀ ପର୍ଯ୍ୟନ୍ତ ମୁଖ୍ୟ ପୂଜା ଚାଲେ। ବିରଜା ପୀଠରେ ଦେବୀ ନିଜ ଘରେ; ଦୀର୍ଘ ଶାରଦୀୟ ଚକ୍ର "
    "ଓ ସିଂହଧ୍ୱଜ ରଥ ଯାଜପୁରର ଶକ୍ତି ପାଞ୍ଜିକୁ ଅଲଗା କରେ।",
    "Ashwina bright fortnight — Durga’s annual victory cycle.",
    "ଆଶ୍ୱିନ ଶୁକ୍ଳପକ୍ଷ — ଦୁର୍ଗାପୂଜାର ବିଜୟ ଚକ୍ର।",
    "puranic_tradition",
    ["Durga–Mahishasura (puranic)", "Biraja Sharadiya rites"],
)

_GAMHA = _story(
    "Gamha Purnima in Odisha is thanks to cattle: cows and bullocks are bathed and decorated. "
    "It coincides with Raksha Bandhan in many homes and is linked to Balabhadra’s birthday "
    "in the Jagannath tradition.",
    "ଗହ୍ମା ପୂର୍ଣ୍ଣିମାରେ ଓଡ଼ିଶାରେ ଗୋଧନଙ୍କୁ ସ୍ନାନ କରାଇ ସଜାଯାଏ — କୃଷି ଓ ଗୋରକ୍ଷାର ଧନ୍ୟବାଦ। "
    "ଅନେକ ଘରେ ରକ୍ଷାବନ୍ଧନ ମଧ୍ୟ ଏହି ଦିନ। ଜଗନ୍ନାଥ ପରମ୍ପରାରେ ଏହା ବଳଭଦ୍ରଙ୍କ ଜନ୍ମଦିନ ସହିତ ଯୋଡ଼ା।",
    "Shravana Purnima — Gamha festival and Balabhadra remembrance.",
    "ଶ୍ରାବଣ ପୂର୍ଣ୍ଣିମା — ଗହ୍ମା ପୂର୍ଣ୍ଣିମା।",
    "historical_cultural",
    ["Gamha Purnima (Odia)", "Balabhadra birthday tradition"],
)

_CHANDAN = _story(
    "Chandan Yatra cools the Lord with sandalwood paste in the Vaishakha heat. For weeks, "
    "boat processions on Narendra tank in Puri bring public joy, beginning on Akshaya Tritiya.",
    "ଚନ୍ଦନ ଯାତ୍ରାରେ ଗ୍ରୀଷ୍ମରେ ମହାପ୍ରଭୁଙ୍କୁ ଚନ୍ଦନ ଲେପ କରାଯାଏ। ପୁରୀ ନରେନ୍ଦ୍ର ପୁଷ୍କରିଣୀରେ "
    "ସପ୍ତାହ ଧରି ଚାପଖେଳ ଚାଲେ। ଅକ୍ଷୟ ତୃତୀୟାରୁ ଏହା ଆରମ୍ଭ।",
    "From Akshaya Tritiya — start of the sandalwood and boat festival at Puri.",
    "ଅକ୍ଷୟ ତୃତୀୟାରୁ — ପୁରୀରେ ଚନ୍ଦନ ଯାତ୍ରା ଆରମ୍ଭ।",
    "ritual_observance",
    ["Chandan Yatra (Puri)"],
)

_RUKUNA = _story(
    "Lingaraj’s Rukuna Rath on Ashokastami is Bhubaneswar’s great chariot outing of the Lord "
    "of Ekamra toward Rameswara — Shaiva Odisha’s ratha festival, with a later return (Bahuda).",
    "ଅଶୋକାଷ୍ଟମୀରେ ଲିଙ୍ଗରାଜଙ୍କ ରୁକୁଣା ରଥ ଭୁବନେଶ୍ୱରର ବିଶାଳ ରଥଯାତ୍ରା। ଏକାମ୍ରାଧିପତି "
    "ରାମେଶ୍ୱର ଆଡ଼କୁ ଯାତ୍ରା କରନ୍ତି — ଓଡ଼ିଶାର ଶୈବ ରଥ ପରମ୍ପରା; ପରେ ବାହୁଡ଼ା।",
    "Chaitra Shukla Ashtami — Lingaraj chariot festival of Ekamra.",
    "ଚୈତ୍ର ଶୁକ୍ଳ ଅଷ୍ଟମୀ — ଲିଙ୍ଗରାଜଙ୍କ ରୁକୁଣା ରଥ।",
    "ritual_observance",
    ["Rukuna Rath / Ashokastami (Lingaraj)"],
)


def _short(
    story_en: str,
    story_or: str,
    why_en: str,
    why_or: str,
    kind: str = "ritual_observance",
    sources: list[str] | None = None,
) -> dict[str, Any]:
    return _story(
        story_en,
        story_or,
        why_en,
        why_or,
        kind,
        sources or ["Odia panji / common Hindu observance"],
    )


# ── Primary map: exact name_en from festivals.py ───────────────────────────

FESTIVAL_STORIES: dict[str, dict[str, Any]] = {
    "Odia New Year (Lunar)": _short(
        "Some lists also mark Chaitra Shukla Pratipada with new-year style rites, alongside "
        "the main solar Pana Sankranti. Biraja peetha notes special puja on this tithi.",
        "କେତେକ ପାଞ୍ଜିରେ ଚୈତ୍ର ଶୁକ୍ଳ ପ୍ରତିପଦାକୁ ମଧ୍ୟ ନୂତନ ବର୍ଷ ଭାବରେ ଚିହ୍ନିତ କରାଯାଏ — "
        "ମୁଖ୍ୟ ସୌର ପଣା ସଂକ୍ରାନ୍ତି ସହିତ। ବିରଜା ପୀଠରେ ଏହି ତିଥିରେ ବିଶେଷ ପୂଜା ଉଲ୍ଲେଖିତ।",
        "Chaitra Shukla Pratipada — lunar-side new-year note in some calendars.",
        "ଚୈତ୍ର ଶୁକ୍ଳ ପ୍ରତିପଦା — କେତେକ ପାଞ୍ଜିରେ ଚାନ୍ଦ୍ର ନୂତନ ବର୍ଷ ସୂଚନା।",
        "ritual_observance",
        ["Regional panji lists"],
    ),
    "Rama Navami": _short(
        "Rama Navami celebrates the birth of Rama. Devotees fast, recite the Ramayana, and visit Rama temples.",
        "ରାମ ନବମୀରେ ଭଗବାନ ରାମଙ୍କ ଜନ୍ମ ଉତ୍ସବ ପାଳିତ ହୁଏ। ଭକ୍ତମାନେ ଉପବାସ କରନ୍ତି, ରାମାୟଣ ପାଠ କରନ୍ତି "
        "ଓ ରାମ ମନ୍ଦିର ଦର୍ଶନ କରନ୍ତି।",
        "Chaitra Shukla Navami — Rama’s birth tithi.",
        "ଚୈତ୍ର ଶୁକ୍ଳ ନବମୀ — ରାମ ନବମୀ।",
        "puranic_tradition",
        ["Ramayana tradition"],
    ),
    "Akshaya Tritiya": _AKSHAYA,
    "Buddha Purnima": _short(
        "Buddha Purnima remembers Gautama Buddha on the Vaishakha full moon — birth and, in many "
        "traditions, enlightenment and mahaparinirvana. Sacred baths and quiet merit-making mark the day.",
        "ବୈଶାଖ ପୂର୍ଣ୍ଣିମାରେ ବୁଦ୍ଧ ପୂର୍ଣ୍ଣିମା — ଗୌତମ ବୁଦ୍ଧଙ୍କ ଜନ୍ମ ଏବଂ ଅନେକ ପରମ୍ପରାରେ ବୋଧି ଓ "
        "ମହାପରିନିର୍ବାଣ ସ୍ମରଣ। ପୁଣ୍ୟସ୍ନାନ ଓ ଶାନ୍ତ ପୁଣ୍ୟକର୍ମ ଏହି ଦିନର ଲକ୍ଷଣ।",
        "Vaishakha Purnima — Buddha Purnima.",
        "ବୈଶାଖ ପୂର୍ଣ୍ଣିମା — ବୁଦ୍ଧ ପୂର୍ଣ୍ଣିମା।",
        "historical_cultural",
        ["Buddha Purnima"],
    ),
    "Savitri Amavasya": _SAVITRI,
    "Sital Shashthi": _SITAL,
    "Snana Purnima": _SNANA,
    "Rath Yatra": _RATH,
    "Bahuda Yatra": _story(
        "Bahuda is the return ratha: after days at Gundicha, the three deities ride back toward "
        "the main temple along the Bada Danda. Crowds pull the chariots again; later rites in the "
        "same cycle include Suna Besha (gold adornment) and Niladri Bije (re-entry to the temple).",
        "ବାହୁଡ଼ା ଯାତ୍ରାରେ ଗୁଣ୍ଡିଚାରେ କିଛି ଦିନ ରହିବା ପରେ ଚତୁର୍ଦ୍ଧାମୂର୍ତ୍ତି ରଥରେ ବଡ଼ଦାଣ୍ଡ ଦେଇ "
        "ମୂଳ ମନ୍ଦିର ଆଡ଼କୁ ଫେରନ୍ତି। ଭକ୍ତମାନେ ପୁଣି ରଥ ଟାଣନ୍ତି। ପରେ ସୁନା ବେଶ ଓ ନୀଳାଦ୍ରି ବିଜେ "
        "ଆଦି ନୀତି ହୁଏ।",
        "Ashadha Shukla Dashami — return chariot day in the Puri calendar.",
        "ଆଷାଢ଼ ଶୁକ୍ଳ ଦଶମୀ — ବାହୁଡ଼ା ଯାତ୍ରା।",
        "ritual_observance",
        ["Bahuda Yatra (Puri)"],
    ),
    "Gamha Purnima": _GAMHA,
    "Janmashtami": _short(
        "Janmashtami celebrates Krishna’s birth at midnight of Shravana Krishna Ashtami. "
        "Homes and temples keep vigil, fast, and sing the Bhagavata. In Odisha, many also "
        "remember Balabhadra’s season around Gamha Purnima in the same lunar month.",
        "ଶ୍ରାବଣ କୃଷ୍ଣ ଅଷ୍ଟମୀ ମଧ୍ୟରାତ୍ରିରେ ଜନ୍ମାଷ୍ଟମୀ — ଭଗବାନ ଶ୍ରୀକୃଷ୍ଣଙ୍କ ଜନ୍ମ ଉତ୍ସବ। "
        "ଘର ଓ ମନ୍ଦିରରେ ଜାଗରଣ, ଉପବାସ ଓ ଭାଗବତ ଭଜନ ହୁଏ। ଓଡ଼ିଶାରେ ଏହି ମାସରେ ଗହ୍ମା ପୂର୍ଣ୍ଣିମା "
        "ସହିତ ବଳଭଦ୍ର ଋତୁ ମଧ୍ୟ ସ୍ମରଣ କରାଯାଏ।",
        "Shravana Krishna Ashtami — Krishna Janmashtami.",
        "ଶ୍ରାବଣ କୃଷ୍ଣ ଅଷ୍ଟମୀ — ଜନ୍ମାଷ୍ଟମୀ।",
        "puranic_tradition",
        ["Bhagavata / Krishna birth tradition"],
    ),
    "Ganesh Chaturthi": _short(
        "Ganesh Chaturthi marks Ganesha’s birth — remover of obstacles. Clay idols are installed, "
        "worshipped, and immersed.",
        "ଗଣେଶ ଚତୁର୍ଥୀରେ ବିଘ୍ନହର୍ତ୍ତା ଗଣେଶଙ୍କ ଜନ୍ମ ଉତ୍ସବ। ମାଟିମୂର୍ତ୍ତି ସ୍ଥାପନ, ପୂଜା ଓ ବିସର୍ଜନ ହୁଏ।",
        "Bhadrapada Shukla Chaturthi — Ganesh Chaturthi.",
        "ଭାଦ୍ରବ ଶୁକ୍ଳ ଚତୁର୍ଥୀ — ଗଣେଶ ଚତୁର୍ଥୀ।",
        "puranic_tradition",
        ["Ganesha tradition"],
    ),
    "Nuakhai": _NUAKHAI,
    "Mahalaya": _short(
        "Mahalaya (Sarvapitri Amavasya) opens ancestral remembrance and the approach of Devi Paksha. "
        "Families offer tarpan for the pitrs; in eastern India the day is also linked with the "
        "invocation of Durga before the main autumn puja.",
        "ମହାଳୟ ବା ସର୍ବପିତୃ ଅମାବାସ୍ୟାରେ ପିତୃପୁରୁଷଙ୍କୁ ତର୍ପଣ କରାଯାଏ ଓ ଦେବୀପକ୍ଷର ଆରମ୍ଭ ହୁଏ। "
        "ପୂର୍ବ ଭାରତରେ ଏହି ଦିନ ଶାରଦୀୟ ଦୁର୍ଗାପୂଜାର ଆହ୍ୱାନ ସହିତ ଯୋଡ଼ା।",
        "Ashwina Krishna Amavasya — Mahalaya.",
        "ଆଶ୍ୱିନ କୃଷ୍ଣ ଅମାବାସ୍ୟା — ମହାଳୟ।",
        "ritual_observance",
        ["Pitru Paksha / Mahalaya"],
    ),
    "Durga Shashthi": _DURGA,
    "Durga Saptami": _DURGA,
    "Durga Ashtami": _DURGA,
    "Mahanavami": _DURGA,
    "Dussehra / Vijaya Dashami": _story(
        "Vijaya Dashami celebrates Durga’s victory and, in many regions, Rama’s triumph over Ravana. "
        "In Odisha, immersion and processions close the autumn goddess festival.",
        "ବିଜୟ ଦଶମୀରେ ଦେବୀଙ୍କ ବିଜୟ ଉତ୍ସବ — ଅନେକ ଅଞ୍ଚଳରେ ରାମଙ୍କ ଦ୍ୱାରା ରାବଣ ବଧର ସ୍ମୃତି ମଧ୍ୟ। "
        "ଓଡ଼ିଶାରେ ପ୍ରତିମା ବିସର୍ଜନ ଓ ଶୋଭାଯାତ୍ରାରେ ଶାରଦୀୟ ପୂଜା ସମାପ୍ତ ହୁଏ।",
        "Ashwina Shukla Dashami — Dussehra / Vijaya Dashami.",
        "ଆଶ୍ୱିନ ଶୁକ୍ଳ ଦଶମୀ — ବିଜୟ ଦଶମୀ।",
        "puranic_tradition",
        ["Vijaya Dashami tradition"],
    ),
    "Kumar Purnima": _KUMAR,
    "Naraka Chaturdashi": _short(
        "Naraka Chaturdashi remembers the vanquishing of Narakasura and the lighting of lamps "
        "before the Amavasya Lakshmi night. Oil bath before sunrise is a common custom.",
        "ନରକ ଚତୁର୍ଦ୍ଦଶୀରେ ନରକାସୁର ବଧର ସ୍ମରଣ ଓ ଅମାବାସ୍ୟା ଲକ୍ଷ୍ମୀପୂଜା ପୂର୍ବରୁ ଦୀପାଳି। "
        "ସୂର୍ଯ୍ୟୋଦୟ ପୂର୍ବରୁ ତୈଳସ୍ନାନ ଏକ ସାଧାରଣ ପ୍ରଥା।",
        "Kartika Krishna Chaturdashi — pre-Diwali day.",
        "କାର୍ତ୍ତିକ କୃଷ୍ଣ ଚତୁର୍ଦ୍ଦଶୀ — ନରକ ଚତୁର୍ଦ୍ଦଶୀ।",
        "puranic_tradition",
        ["Naraka Chaturdashi / Diwali cycle"],
    ),
    "Diwali / Lakshmi Puja": _short(
        "On Kartika Amavasya, homes light rows of lamps for Lakshmi (and in many places Kali). "
        "The festival of lights marks hope for prosperity after Naraka Chaturdashi and before "
        "Bali Pratipada / Govardhan day in the Odia panji sequence.",
        "କାର୍ତ୍ତିକ ଅମାବାସ୍ୟାରେ ଦୀପାବଳୀ — ଘରେ ଲକ୍ଷ୍ମୀ ପୂଜା ଓ ଧାଡ଼ି ଧାଡ଼ି ଦୀପାଳି; ଅନେକ ସ୍ଥାନରେ "
        "କାଳୀପୂଜା ମଧ୍ୟ। ନରକ ଚତୁର୍ଦ୍ଦଶୀ ପରେ ଓ ବଳି ପ୍ରତିପଦା / ଗୋବର୍ଦ୍ଧନ ପୂଜା ପୂର୍ବରୁ "
        "ଏହି ରାତ୍ରି ଓଡ଼ିଆ ପାଞ୍ଜିରେ ମୁଖ୍ୟ ଦୀପାଳି ଦିନ।",
        "Kartika Krishna Amavasya — Diwali / Lakshmi Puja.",
        "କାର୍ତ୍ତିକ କୃଷ୍ଣ ଅମାବାସ୍ୟା — ଦୀପାବଳୀ।",
        "ritual_observance",
        ["Diwali / Lakshmi Puja"],
    ),
    "Bali Pratipada / Govardhan Puja": _short(
        "The day after Diwali is linked to Bali’s story and to Govardhan Puja — Krishna lifting "
        "Govardhan hill. Regional emphasis varies; Odisha panji lists often note both names.",
        "ଦୀପାବଳୀ ପରଦିନ ବଳି ପ୍ରତିପଦା ଓ ଗୋବର୍ଦ୍ଧନ ପୂଜା — କୃଷ୍ଣଙ୍କ ଦ୍ୱାରା ଗୋବର୍ଦ୍ଧନ ଧାରଣର କାହାଣୀ। "
        "ଓଡ଼ିଆ ପାଞ୍ଜିରେ ଉଭୟ ନାମ ଦେଖାଯାଏ।",
        "Kartika Shukla Pratipada — Bali / Govardhan day.",
        "କାର୍ତ୍ତିକ ଶୁକ୍ଳ ପ୍ରତିପଦା — ବଳି ପ୍ରତିପଦା / ଗୋବର୍ଦ୍ଧନ ପୂଜା।",
        "puranic_tradition",
        ["Govardhan / Bali Pratipada tradition"],
    ),
    "Kartik Purnima / Boita Bandana": _BOITA,
    "Prathamastami": _PRATHAMA,
    "Pausha Purnima": _short(
        "Pausha Purnima is a full-moon bath and merit day at river ghats in the cold month. "
        "Devotees seek punya snanam and quiet charity as the solar year leans toward Makara.",
        "ପୌଷ ପୂର୍ଣ୍ଣିମାରେ ନଦୀଘାଟରେ ପୁଣ୍ୟସ୍ନାନ — ଶୀତକାଳୀନ ପୂର୍ଣ୍ଣିମାର ବ୍ରତ। ଭକ୍ତମାନେ "
        "ଦାନ ଓ ସ୍ନାନ ଦ୍ୱାରା ପୁଣ୍ୟ ଅର୍ଜନ କରନ୍ତି; ମକର ଋତୁ ନିକଟତର ହୁଏ।",
        "Pausha full moon — sacred bath day.",
        "ପୌଷ ପୂର୍ଣ୍ଣିମା — ପୁଣ୍ୟସ୍ନାନର ଦିନ।",
        "ritual_observance",
        ["Pausha Purnima snanam"],
    ),
    "Vasanta Panchami / Saraswati Puja": _short(
        "Vasanta Panchami welcomes spring and honours Saraswati — learning and the arts. "
        "Children place books before the goddess; yellow is auspicious.",
        "ବସନ୍ତ ପଞ୍ଚମୀରେ ବସନ୍ତର ଆଗମନ ଓ ବିଦ୍ୟାଦେବୀ ସରସ୍ୱତୀଙ୍କ ପୂଜା। ପିଲାମାନେ ବହି ଦେବୀ ଆଗରେ ରଖନ୍ତି; "
        "ହଳଦିଆ ରଙ୍ଗ ଶୁଭ।",
        "Magha Shukla Panchami — Saraswati / spring.",
        "ମାଘ ଶୁକ୍ଳ ପଞ୍ଚମୀ — ସରସ୍ୱତୀ ପୂଜା / ବସନ୍ତ ପଞ୍ଚମୀ।",
        "puranic_tradition",
        ["Saraswati Puja / Vasanta Panchami"],
    ),
    "Magha Purnima": _short(
        "Magha Purnima is a great bathing full moon; pilgrims seek rivers, tanks, and cold-season "
        "merit before the approach of Shivaratri and Holi season.",
        "ମାଘ ପୂର୍ଣ୍ଣିମାରେ ବିଶେଷ ପୁଣ୍ୟସ୍ନାନ — ନଦୀ ଓ ପୁଷ୍କରିଣୀରେ ଶୀତକାଳୀନ ପୂର୍ଣ୍ଣିମାର ବ୍ରତ। "
        "ଶିବରାତ୍ରି ଓ ହୋଲି ଋତୁ ଆଗରୁ ଏହି ସ୍ନାନ ପୁଣ୍ୟ ବୋଲି ଗଣାଯାଏ।",
        "Magha full moon — major snanam day.",
        "ମାଘ ପୂର୍ଣ୍ଣିମା — ବିଶେଷ ପୁଣ୍ୟସ୍ନାନ।",
        "ritual_observance",
        ["Magha Purnima snanam"],
    ),
    "Maha Shivaratri": _short(
        "Maha Shivaratri is the great night of Shiva: fasting, bilva leaves, milk abhisheka, and "
        "night-long vigil. In Odisha, Lingaraj (Bhubaneswar) and Biraja kshetra (Jajpur) draw "
        "especially large night gatherings.",
        "ମହା ଶିବରାତ୍ରି — ମହାଦେବଙ୍କ ରାତ୍ରି। ଉପବାସ, ବେଲପତ୍ର, ଦୁଗ୍ଧାଭିଷେକ ଓ ରାତ୍ରିଜାଗରଣ ହୁଏ। "
        "ଓଡ଼ିଶାରେ ଭୁବନେଶ୍ୱର ଲିଙ୍ଗରାଜ ଓ ଯାଜପୁର ବିରଜା କ୍ଷେତ୍ରରେ ବିଶେଷ ଭିଡ଼ ହୁଏ।",
        "Phalguna Krishna Chaturdashi — Maha Shivaratri.",
        "ଫାଲ୍ଗୁନ କୃଷ୍ଣ ଚତୁର୍ଦ୍ଦଶୀ — ମହା ଶିବରାତ୍ରି।",
        "puranic_tradition",
        ["Maha Shivaratri", "Lingaraj / Biraja night vigil custom"],
    ),
    "Dola Purnima": _DOLA,
    # Jagannath
    "Chandan Yatra Begins": _CHANDAN,
    "Snana Yatra": _SNANA,
    "Nava Jaubana Darshan": _short(
        "After Anavasara the deities reappear in youthful splendour (nava jaubana) before Rath Yatra — "
        "a highly sought darshan.",
        "ଅନବସର ପରେ ରଥଯାତ୍ରା ପୂର୍ବରୁ ନବଯୌବନ ଦର୍ଶନ — ଦେବତାମାନେ ନୂତନ ଯୌବନରେ ପ୍ରକାଶ ପାଆନ୍ତି। "
        "ଏହା ଅତ୍ୟନ୍ତ ଲୋକପ୍ରିୟ ଦର୍ଶନ।",
        "Day before Rath Yatra — rejuvenated darshan after Anavasara.",
        "ରଥଯାତ୍ରା ପୂର୍ବଦିନ — ନବଯୌବନ ଦର୍ଶନ।",
        "ritual_observance",
        ["Nava Jaubana (Puri)"],
    ),
    "Gundicha Marjana": _short(
        "Gundicha Marjana is the ritual cleaning of Gundicha Temple by servitors before the Lord arrives.",
        "ଗୁଣ୍ଡିଚା ମାର୍ଜନ — ରଥଯାତ୍ରା ପୂର୍ବରୁ ସେବକମାନେ ଗୁଣ୍ଡିଚା ମନ୍ଦିର ପରିଷ୍କାର କରନ୍ତି, "
        "ଯାହାକୁ ମାଉସୀ ମା’ଙ୍କ ଘର ବୋଲି କୁହାଯାଏ।",
        "Temple cleaning day before the deities’ arrival at Gundicha.",
        "ଗୁଣ୍ଡିଚା ମାର୍ଜନ — ମନ୍ଦିର ପରିଷ୍କାରର ଦିନ।",
        "ritual_observance",
        ["Gundicha Marjana (Puri)"],
    ),
    "Hera Panchami": _HERA,
    "Suna Besha": _short(
        "Suna Besha adorns Jagannath, Balabhadra and Subhadra with gold ornaments on the chariots.",
        "ସୁନା ବେଶରେ ରଥ ଉପରେ ଜଗନ୍ନାଥ, ବଳଭଦ୍ର ଓ ସୁଭଦ୍ରାଙ୍କୁ ସୁନା ଅଳଙ୍କାରରେ ସଜାଯାଏ — "
        "ଏକ ଅତି ମନୋରମ ଦର୍ଶନ।",
        "Gold adornment day on the chariots in the Rath Yatra cycle.",
        "ରଥ ଚକ୍ରରେ ସୁନା ବେଶର ଦିନ।",
        "ritual_observance",
        ["Suna Besha (Puri)"],
    ),
    "Adhara Pana": _short(
        "Adhara Pana offers a special sweet drink (pana) to the deities while they are still "
        "seated on the chariots after Bahuda — a late-cycle niti before Niladri Bije.",
        "ଅଧର ପଣାରେ ବାହୁଡ଼ା ପରେ ରଥ ଉପରେ ଥିବା ଦେବତାମାନଙ୍କୁ ବିଶେଷ ମିଠା ପଣା ଭୋଗ ଲଗାଯାଏ — "
        "ନୀଳାଦ୍ରି ବିଜେ ପୂର୍ବର ଏକ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ନୀତି।",
        "Special pana offering on the chariots after the return journey.",
        "ବାହୁଡ଼ା ପରେ ରଥ ଉପରେ ଅଧର ପଣା ଭୋଗ।",
        "ritual_observance",
        ["Adhara Pana (Puri)"],
    ),
    "Niladri Bije": _NILADRI,
    "Jhulana Yatra Begins": _short(
        "Jhulana is the swing festival of the monsoon — deities enjoy the jhula, echoing Krishna’s "
        "rainy-season pastimes.",
        "ଝୁଲଣ ଯାତ୍ରା ବର୍ଷାକାଳୀନ ଝୁଲଣ ଉତ୍ସବ। ଦେବତାମାନେ ଝୁଲଣରେ ବିଞ୍ଜନ୍ତି — କୃଷ୍ଣଲୀଳାର ସ୍ମୃତି ସହିତ।",
        "Start of Jhulana (swing) festival in the Jagannath calendar.",
        "ଜଗନ୍ନାଥ ପାଞ୍ଜିରେ ଝୁଲଣ ଯାତ୍ରା ଆରମ୍ଭ।",
        "ritual_observance",
        ["Jhulana Yatra (Puri)"],
    ),
    "Utthana Ekadashi": _short(
        "Utthana (Prabodhini) Ekadashi marks the end of Chaturmasya when Vishnu is said to awaken "
        "from cosmic sleep; full ritual life resumes.",
        "ଉତ୍ଥାନ ଏକାଦଶୀ ବା ପ୍ରବୋଧିନୀ ଏକାଦଶୀରେ ଚାତୁର୍ମାସ୍ୟ ଶେଷ। ପରମ୍ପରାରେ ବିଷ୍ଣୁ ଯୋଗନିଦ୍ରାରୁ "
        "ଉଠନ୍ତି; ପୂର୍ଣ୍ଣ ନୀତି ପୁନରାରମ୍ଭ ହୁଏ।",
        "Kartika Shukla Ekadashi — end of Chaturmasya.",
        "କାର୍ତ୍ତିକ ଶୁକ୍ଳ ଏକାଦଶୀ — ଉତ୍ଥାନ ଏକାଦଶୀ।",
        "puranic_tradition",
        ["Prabodhini / Utthana Ekadashi"],
    ),
    "Pancha Uka Osha": _short(
        "Pancha Uka Osha is an Odia Lakshmi-oriented vrat across days in Margashira, kept especially by women.",
        "ପଞ୍ଚ ଉକ ଓଷା ମାର୍ଗଶୀରରେ ପାଳିତ ଓଡ଼ିଆ ଲକ୍ଷ୍ମୀ-ସମ୍ବନ୍ଧୀୟ ଓଷା — ବିଶେଷକରି ନାରୀମାନେ ପାଳନ୍ତି।",
        "Margashira period — Pancha Uka Osha.",
        "ମାର୍ଗଶୀର — ପଞ୍ଚ ଉକ ଓଷା।",
        "historical_cultural",
        ["Odia osha / Lakshmi vrat custom"],
    ),
    "Dola Yatra (Jagannath)": _DOLA,
    "Ashokastami": _short(
        "Ashokastami in the Jagannath calendar carries special besha and rites; in Bhubaneswar "
        "the same tithi is Lingaraj’s Rukuna Rath day.",
        "ଅଶୋକାଷ୍ଟମୀ ଜଗନ୍ନାଥ ପାଞ୍ଜିରେ ବିଶେଷ ବେଶ ଓ ନୀତିର ଦିନ। ଭୁବନେଶ୍ୱରରେ ଏହି ତିଥିରେ "
        "ଲିଙ୍ଗରାଜଙ୍କ ରୁକୁଣା ରଥ ହୁଏ।",
        "Chaitra Shukla Ashtami — Ashokastami.",
        "ଚୈତ୍ର ଶୁକ୍ଳ ଅଷ୍ଟମୀ — ଅଶୋକାଷ୍ଟମୀ।",
        "ritual_observance",
        ["Ashokastami (Puri / Odisha)"],
    ),
    # Lingaraj
    "Banajaga Jatra (Rukuna Rath)": _short(
        "Banajaga marks the forest rite of selecting timber for Lingaraj’s Rukuna chariot.",
        "ବନଯାଗ ଯାତ୍ରାରେ ଲିଙ୍ଗରାଜଙ୍କ ରୁକୁଣା ରଥ ପାଇଁ ବନରୁ କାଠ ଚିହ୍ନଟ କରାଯାଏ — ରଥନିର୍ମାଣର ପ୍ରଥମ ପବିତ୍ର ପଦକ୍ଷେପ।",
        "Preparatory forest rite for Rukuna Rath.",
        "ରୁକୁଣା ରଥ ପାଇଁ ବନଯାଗ।",
        "ritual_observance",
        ["Lingaraj Rukuna Rath cycle"],
    ),
    "Lingaraj Maha Shivaratri": _short(
        "Lingaraj Temple’s Maha Shivaratri is one of Ekamra’s largest night gatherings.",
        "ଲିଙ୍ଗରାଜ ମନ୍ଦିରରେ ମହା ଶିବରାତ୍ରି ଏକାମ୍ରର ବିଶାଳ ରାତ୍ରିଜାଗରଣ — ହଜାର ହଜାର ଭକ୍ତଙ୍କ ସମାଗମ।",
        "Maha Shivaratri at Lingaraj, Bhubaneswar.",
        "ଭୁବନେଶ୍ୱର ଲିଙ୍ଗରାଜରେ ମହା ଶିବରାତ୍ରି।",
        "ritual_observance",
        ["Lingaraj Temple Shivaratri"],
    ),
    "Ashokastami — Rukuna Rath Yatra": _RUKUNA,
    "Rukuna Rath Bahuda Yatra": _short(
        "Rukuna Bahuda is Lingaraj’s return from Rameswara to the main temple — Swarnadri Bije in local speech.",
        "ରୁକୁଣା ବାହୁଡ଼ାରେ ଲିଙ୍ଗରାଜ ରାମେଶ୍ୱରରୁ ମୂଳ ମନ୍ଦିରକୁ ଫେରନ୍ତି — ସ୍ଥାନୀୟ ଭାଷାରେ ସ୍ୱର୍ଣ୍ଣାଦ୍ରି ବିଜେ।",
        "Return journey of Lingaraj’s chariot.",
        "ଲିଙ୍ଗରାଜଙ୍କ ରୁକୁଣା ବାହୁଡ଼ା।",
        "ritual_observance",
        ["Rukuna Bahuda (Lingaraj)"],
    ),
    # Biraja
    "Biraja Akshaya Tritiya": _story(
        _AKSHAYA["story"]["en"] + " At Biraja peetha the day also opens local seasonal rites.",
        _AKSHAYA["story"]["or"] + " ବିରଜା ପୀଠରେ ମଧ୍ୟ ଏହି ଦିନରୁ ସ୍ଥାନୀୟ ଋତୁଗତ ନୀତି ଆରମ୍ଭ ହୁଏ।",
        "Akshaya Tritiya with Biraja peetha emphasis.",
        "ବିରଜା ପୀଠରେ ଅକ୍ଷୟ ତୃତୀୟା।",
        "ritual_observance",
        _AKSHAYA["sources"] + ["Biraja local calendar"],
    ),
    "Sitala Shashthi (Biraja)": _SITAL,
    "Nuakhai Juhar": _NUAKHAI,
    "Shodasha Dinatatmika Puja Begins": _story(
        _BIRAJA_PEETH["story"]["en"]
        + " The Shodasha Dinatatmika puja is Biraja’s extended autumn worship — longer than "
        "the common city Durga Puja rhythm.",
        _BIRAJA_PEETH["story"]["or"]
        + " ଷୋଡ଼ଶ ଦିନାତ୍ମିକ ପୂଜା ବିରଜାର ଦୀର୍ଘ ଶାରଦୀୟ ପୂଜା — ସାଧାରଣ ନଗର ଦୁର୍ଗାପୂଜା ଚକ୍ରଠାରୁ ଅଧିକ ଦିନ।",
        "Start of Biraja’s 16-day Sharadiya cycle.",
        "ବିରଜାର ଷୋଡ଼ଶ ଦିନିଆ ଶାରଦୀୟ ପୂଜା ଆରମ୍ଭ।",
        "ritual_observance",
        _BIRAJA_PEETH["sources"],
    ),
    "Simhadhwaja Rath Yatra": _story(
        "Simhadhwaja is Maa Biraja’s own chariot festival in Jajpur. The ratha flag bears a lion; "
        "the goddess processes during Navratri — a Shakti peetha ratha, not Puri’s Jagannath Rath Yatra.",
        "ସିଂହଧ୍ୱଜ ଯାଜପୁରରେ ମା’ ବିରଜାଙ୍କ ନିଜସ୍ୱ ରଥଯାତ୍ରା। ରଥଧ୍ୱଜରେ ସିଂହ ଚିହ୍ନ। ନବରାତ୍ରି କାଳରେ "
        "ଦେବୀଙ୍କ ଶୋଭାଯାତ୍ରା ହୁଏ। ଏହା ଶକ୍ତିପୀଠର ରଥ — ପୁରୀ ଶ୍ରୀଜଗନ୍ନାଥଙ୍କ ରଥଯାତ୍ରାଠାରୁ ଭିନ୍ନ।",
        "Biraja’s lion-flag chariot day in the autumn goddess calendar.",
        "ଶାରଦୀୟ କାଳରେ ବିରଜାଙ୍କ ସିଂହଧ୍ୱଜ ରଥଦିନ।",
        "ritual_observance",
        ["Biraja Temple Simhadhwaja"],
    ),
    "Biraja Shashthi": _DURGA,
    "Maa Biraja Ashtami": _story(
        _DURGA["story"]["en"]
        + " At Biraja, Ashtami–Navami include the peetha’s Sandhi and traditional rites as recorded in peetha custom.",
        _DURGA["story"]["or"]
        + " ବିରଜାରେ ଅଷ୍ଟମୀ-ନବମୀରେ ପୀଠର ସନ୍ଧିପୂଜା ଓ ପାରମ୍ପରିକ ନୀତି ହୁଏ।",
        "Main Ashtami at Maa Biraja peetha.",
        "ମା’ ବିରଜା ପୀଠରେ ମୁଖ୍ୟ ଅଷ୍ଟମୀ।",
        "ritual_observance",
        _DURGA["sources"] + ["Biraja peetha custom"],
    ),
    "Mahanavami at Biraja": _DURGA,
    "Vijaya Dashami at Biraja": _story(
        "Vijaya Dashami at Biraja closes the peetha’s autumn victory rites with local processions.",
        "ବିରଜାରେ ବିଜୟ ଦଶମୀରେ ପୀଠର ଶାରଦୀୟ ବିଜୟ ଉତ୍ସବ ଓ ସ୍ଥାନୀୟ ଶୋଭାଯାତ୍ରାରେ ପୂଜା ସମାପ୍ତ ହୁଏ।",
        "Dashami victory day at Biraja.",
        "ବିରଜା ପୀଠରେ ବିଜୟ ଦଶମୀ।",
        "ritual_observance",
        ["Biraja Vijaya Dashami"],
    ),
    "Biraja Manabasa": _MANABASA,
    "Biraja Shivaratri": _short(
        "Shivaratri at Biraja kshetra joins peetha Shakti with Shaiva night vigil; "
        "Dashaswamedha ghat on the Baitarani also draws snanam crowds in the season.",
        "ବିରଜା କ୍ଷେତ୍ରରେ ଶିବରାତ୍ରି — ଶକ୍ତିପୀଠ ସହିତ ଶୈବ ରାତ୍ରିଜାଗରଣ। ବୈତରଣୀ ତୀରର ଦଶାଶ୍ୱମେଧ ଘାଟରେ "
        "ମଧ୍ୟ ସ୍ନାନ ପାଇଁ ଭିଡ଼ ହୁଏ।",
        "Maha Shivaratri observed at Biraja / Jajpur.",
        "ଯାଜପୁର ବିରଜାରେ ମହା ଶିବରାତ୍ରି।",
        "ritual_observance",
        ["Biraja / Baitarani Shivaratri custom"],
    ),
    "Biraja New Year Puja": _short(
        "Local lists mark special puja at Biraja on Chaitra Shukla Pratipada as a peetha blessing day, "
        "alongside the wider Odia solar new year at Pana Sankranti.",
        "ଚୈତ୍ର ଶୁକ୍ଳ ପ୍ରତିପଦାରେ ବିରଜା ପୀଠରେ ବିଶେଷ ନୂତନ ବର୍ଷ ପୂଜା ଉଲ୍ଲେଖିତ — "
        "ବ୍ୟାପକ ଓଡ଼ିଆ ସୌର ନୂତନ ବର୍ଷ ପଣା ସଂକ୍ରାନ୍ତି ସହିତ।",
        "Biraja peetha new-year style puja day.",
        "ବିରଜା ପୀଠରେ ନୂତନ ବର୍ଷ ପୂଜା।",
        "ritual_observance",
        ["Biraja local calendar"],
    ),
    # Sankranti
    "Pana Sankranti (Odia New Year)": _PANA,
    "Pana Sankranti at Jagannath": _PANA,
    "Pana Sankranti at Biraja": _PANA,
    "Pana Sankranti at Lingaraj": _story(
        _PANA["story"]["en"] + " At Lingaraj, Meru Yatra and special new-year rites mark Ekamra’s solar new year.",
        _PANA["story"]["or"] + " ଲିଙ୍ଗରାଜରେ ମେରୁ ଯାତ୍ରା ଓ ବିଶେଷ ନୂତନ ବର୍ଷ ନୀତି ହୁଏ।",
        "Pana Sankranti at Lingaraj Temple.",
        "ଲିଙ୍ଗରାଜ ମନ୍ଦିରରେ ପଣା ସଂକ୍ରାନ୍ତି।",
        "ritual_observance",
        _PANA["sources"] + ["Lingaraj Meru Yatra"],
    ),
    "Vrishabha Sankranti": _short(
        "Sun enters Vrishabha; planting and summer agricultural rhythm advance in Odisha’s solar months.",
        "ବୃଷଭ ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ ବୃଷରାଶିରେ ପ୍ରବେଶ କରନ୍ତି; ଓଡ଼ିଶାରେ କୃଷି ଓ ଗ୍ରୀଷ୍ମ ଋତୁର ଗତି ବଢ଼େ।",
        "Solar month of Vrishabha begins.",
        "ବୃଷଭ ସଂକ୍ରାନ୍ତି — ସୌର ବୃଷ ମାସ ଆରମ୍ଭ।",
    ),
    "Mithuna Sankranti (Raja Parba)": _RAJA,
    "Karka Sankranti (Dakshinayana)": _short(
        "Karka Sankranti begins Dakshinayana — the Sun’s southward course in traditional astronomy.",
        "କର୍କଟ ସଂକ୍ରାନ୍ତିରେ ଦକ୍ଷିଣାୟନ ଆରମ୍ଭ — ପାରମ୍ପରିକ ଜ୍ୟୋତିଷରେ ସୂର୍ଯ୍ୟଙ୍କ ଦକ୍ଷିଣଗମନ।",
        "Sun enters Karka; Dakshinayana begins.",
        "କର୍କଟ ସଂକ୍ରାନ୍ତି — ଦକ୍ଷିଣାୟନ ଆରମ୍ଭ।",
        "ritual_observance",
        ["Dakshinayana / Karka Sankranti"],
    ),
    "Simha Sankranti": _short(
        "Sun enters Simha; the calendar moves toward Gamha and Janmashtami season.",
        "ସିଂହ ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ ସିଂହରାଶିରେ ପ୍ରବେଶ କରନ୍ତି; ଗହ୍ମା ଓ ଜନ୍ମାଷ୍ଟମୀ ଋତୁ ନିକଟତର ହୁଏ।",
        "Solar Simha month begins.",
        "ସିଂହ ସଂକ୍ରାନ୍ତି — ସୌର ସିଂହ ମାସ ଆରମ୍ଭ।",
    ),
    "Kanya Sankranti": _short(
        "Sun enters Kanya; Navratri and Durga Puja season approaches.",
        "କନ୍ୟା ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ କନ୍ୟାରାଶିରେ ପ୍ରବେଶ କରନ୍ତି; ନବରାତ୍ରି ଓ ଦୁର୍ଗାପୂଜା ଋତୁ ଆସେ।",
        "Solar Kanya month begins.",
        "କନ୍ୟା ସଂକ୍ରାନ୍ତି — ସୌର କନ୍ୟା ମାସ ଆରମ୍ଭ।",
    ),
    "Tula Sankranti": _short(
        "Sun enters Tula; Kartika vows and the Diwali–Boita season draw near.",
        "ତୁଳା ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ ତୁଳାରାଶିରେ ପ୍ରବେଶ କରନ୍ତି; କାର୍ତ୍ତିକ ବ୍ରତ ଓ ଦୀପାବଳୀ-ବୋଇତ ଋତୁ ନିକଟେ।",
        "Solar Tula month begins.",
        "ତୁଳା ସଂକ୍ରାନ୍ତି — ସୌର ତୁଳା ମାସ ଆରମ୍ଭ।",
    ),
    "Vrischika Sankranti": _short(
        "Sun enters Vrischika; Margashira’s Manabasa Thursdays follow in the Odia household calendar.",
        "ବୃଶ୍ଚିକ ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ ବୃଶ୍ଚିକରାଶିରେ ପ୍ରବେଶ କରନ୍ତି; ମାର୍ଗଶୀରର ମନବସା ଗୁରୁବାର ଆଗକୁ।",
        "Solar Vrischika month begins.",
        "ବୃଶ୍ଚିକ ସଂକ୍ରାନ୍ତି — ସୌର ବୃଶ୍ଚିକ ମାସ ଆରମ୍ଭ।",
    ),
    "Dhanu Sankranti": _short(
        "Dhanu Sankranti brings pre-dawn Dhanu bhoga hymns and poda pitha in many Odia homes.",
        "ଧନୁ ସଂକ୍ରାନ୍ତିରେ ଅନେକ ଓଡ଼ିଆ ଘରେ ପ୍ରଭାତରେ ଧନୁ ଭୋଗ ଗୀତ ଓ ପୋଡ଼ପିଠା — ମକର ପୂର୍ବ ଶୀତଭକ୍ତି।",
        "Sun enters Dhanu; Dhanu month rites.",
        "ଧନୁ ସଂକ୍ରାନ୍ତି — ଧନୁ ମାସର ନୀତି।",
        "historical_cultural",
        ["Dhanu Sankranti / Dhanu bhoga (Odia)"],
    ),
    "Makar Sankranti": _MAKARA,
    "Makar Sankranti Snanam at Biraja": _MAKARA,
    "Kumbha Sankranti": _short(
        "Sun enters Kumbha; Shivaratri season approaches as winter softens.",
        "କୁମ୍ଭ ସଂକ୍ରାନ୍ତିରେ ସୂର୍ଯ୍ୟ କୁମ୍ଭରାଶିରେ ପ୍ରବେଶ କରନ୍ତି; ଶିବରାତ୍ରି ଋତୁ ନିକଟତର ହୁଏ।",
        "Solar Kumbha month begins.",
        "କୁମ୍ଭ ସଂକ୍ରାନ୍ତି — ସୌର କୁମ୍ଭ ମାସ ଆରମ୍ଭ।",
    ),
    "Meena Sankranti": _short(
        "Last solar month before Pana Sankranti; Dola / Holi season and new-year preparations begin.",
        "ମୀନ ସଂକ୍ରାନ୍ତି ପଣା ସଂକ୍ରାନ୍ତି ପୂର୍ବର ଶେଷ ସୌର ମାସ; ଡୋଳ-ହୋଲି ଋତୁ ଓ ନୂତନ ବର୍ଷ ପ୍ରସ୍ତୁତି।",
        "Solar Meena month begins.",
        "ମୀନ ସଂକ୍ରାନ୍ତି — ସୌର ମୀନ ମାସ ଆରମ୍ଭ।",
    ),
}


_STUB_OR_STORY = (
    "ଏହି ପର୍ବର ବିସ୍ତୃତ କାହାଣୀ ଏପର୍ଯ୍ୟନ୍ତ ସମ୍ପାଦିତ ହୋଇନାହିଁ। "
    "ତଥାପି ଏହି ତିଥି ବା ସଂକ୍ରାନ୍ତି ପାଞ୍ଜି ଅନୁସାରେ ପାଳନୀୟ।"
)
_STUB_OR_WHY = "ଆଜିର ତିଥି ବା ସୌର ମାସ ନିୟମ ଅନୁସାରେ ଏହି ପର୍ବ ପାଳିତ ହୁଏ।"


def get_festival_story(name_en: str) -> dict[str, Any]:
    """
    Return story payload for a festival English name.
    Always returns a dict; Odia fields are always real Odia (never English copy).
    """
    if name_en in FESTIVAL_STORIES:
        data = FESTIVAL_STORIES[name_en]
        return {
            "story": data["story"],
            "why_today": data["why_today"],
            "kind": data["kind"],
            "sources": list(data["sources"]),
            "complete": True,
        }

    # Honest Odia stub — still proper script, not Latin
    return {
        "story": {
            "en": (
                f"Traditional Odia panji lists mark “{name_en}” on this tithi or sankranti. "
                "A full narrative has not been curated in this release."
            ),
            "or": _STUB_OR_STORY,
        },
        "why_today": {
            "en": "Observed because it matches the lunar or solar rule in the panji for this date.",
            "or": _STUB_OR_WHY,
        },
        "kind": "ritual_observance",
        "sources": ["pending_editorial"],
        "complete": False,
    }


def attach_story(festival: dict) -> dict:
    """Attach narrative fields; expects name_en or nested name.en."""
    name = festival.get("name_en")
    if not name and isinstance(festival.get("name"), dict):
        name = festival["name"].get("en")
    if not name:
        return festival

    s = get_festival_story(name)
    festival["story"] = s["story"]
    festival["why_today"] = s["why_today"]
    festival["story_kind"] = s["kind"]
    festival["story_sources"] = s["sources"]
    festival["story_complete"] = s["complete"]
    return festival


def coverage_report() -> dict[str, Any]:
    """For evals: which festival names lack curated stories."""
    from src.festivals import TITHI_RULES, SANKRANTI_RULES

    names = {r[4] for r in TITHI_RULES} | {r[2] for r in SANKRANTI_RULES}
    missing = sorted(n for n in names if n not in FESTIVAL_STORIES)
    return {
        "total_rules": len(names),
        "curated": len(names) - len(missing),
        "missing": missing,
    }


def validate_all_stories() -> list[str]:
    """Return list of validation errors across all curated Odia fields."""
    errors: list[str] = []
    for name, data in FESTIVAL_STORIES.items():
        for field in ("story", "why_today"):
            try:
                validate_odia_text(data[field]["or"], field=f"{name}.{field}.or")
            except ValueError as e:
                errors.append(str(e))
            if data[field]["or"] == data[field]["en"]:
                errors.append(f"{name}.{field}: Odia equals English")
    # stubs
    for label, text in (("stub_story", _STUB_OR_STORY), ("stub_why", _STUB_OR_WHY)):
        try:
            validate_odia_text(text, field=label)
        except ValueError as e:
            errors.append(str(e))
    return errors
