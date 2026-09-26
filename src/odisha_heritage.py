"""
"ଜାଣନ୍ତୁ ଓଡ଼ିଶା" (Know Odisha) — a daily heritage series for the social posts.

One curated entry per day about Odia culture, history, literature, writers
and great Odias. Same rules as `festival_stories.py`:

  1. Accuracy — well-documented public facts only; hedge where scholars
     differ; no invented anecdotes. Prefer dropping a sentence to guessing.
  2. Odia script — every `or` field is real Odia (validated at import).

Selection is deterministic by civil date: an entry whose `anniversary`
(MM-DD) matches the day wins (birth anniversaries, Utkal Divas); then an
entry that complements one of the day's festivals (FESTIVAL_HERITAGE);
otherwise entries rotate with categories spread evenly through the cycle.

`title_or` and `short_or` are painted on the Instagram story card with Noto
Sans Oriya, which has no Latin letters and no ASCII hyphen — keep those two
fields to Odia letters, digits, spaces and । , : only.
"""

from __future__ import annotations

import unicodedata
from datetime import date, timedelta
from typing import Any

from src.festival_stories import validate_odia_text

SERIES_OR = "ଜାଣନ୍ତୁ ଓଡ଼ିଶା"
SERIES_TAG = "#KnowOdisha"

CATEGORIES: dict[str, dict[str, str]] = {
    "literature":  {"or": "ସାହିତ୍ୟ",      "emoji": "📖", "tag": "#OdiaSahitya"},
    "author":      {"or": "ସାହିତ୍ୟିକ",     "emoji": "✍️", "tag": "#OdiaLiterature"},
    "personality": {"or": "ମହାନ ଓଡ଼ିଆ",   "emoji": "🌟", "tag": "#GreatOdias"},
    "history":     {"or": "ଇତିହାସ",       "emoji": "🏛️", "tag": "#OdishaHistory"},
    "heritage":    {"or": "ଐତିହ୍ୟ",        "emoji": "🛕", "tag": "#OdishaHeritage"},
    "culture":     {"or": "ସଂସ୍କୃତି",      "emoji": "🎭", "tag": "#OdiaCulture"},
}

JAYANTI_OR = "ଆଜି ଜୟନ୍ତୀ"

# Characters allowed in fields painted on the card (see module docstring).
_CARD_PUNCT = set(" ।,:0123456789")


def _entry(
    key: str,
    category: str,
    title_en: str,
    title_or: str,
    body_en: str,
    body_or: str,
    short_or: str,
    sources: list[str],
    *,
    anniversary: str | None = None,
    anniversary_or: str = JAYANTI_OR,
) -> dict[str, Any]:
    assert category in CATEGORIES, category
    title_or = unicodedata.normalize("NFC", title_or.strip())
    body_or = unicodedata.normalize("NFC", " ".join(body_or.split()))
    short_or = unicodedata.normalize("NFC", short_or.strip())
    for field, text in (("title_or", title_or), ("body_or", body_or), ("short_or", short_or)):
        validate_odia_text(text, field=f"{key}.{field}")
    for field, text in (("title_or", title_or), ("short_or", short_or)):
        bad = [c for c in text if not ("଀" <= c <= "୿" or c in _CARD_PUNCT)]
        if bad:
            raise ValueError(f"{key}.{field}: characters the card font cannot draw: {bad}")
    if anniversary is not None:
        date.fromisoformat(f"2000-{anniversary}")  # validates MM-DD
    return {
        "key": key,
        "category": category,
        "title": {"en": title_en.strip(), "or": title_or},
        "body": {"en": " ".join(body_en.split()), "or": body_or},
        "short_or": short_or,
        "sources": list(sources),
        "anniversary": anniversary,
        "anniversary_or": anniversary_or if anniversary else "",
    }


HERITAGE: list[dict[str, Any]] = [
    # ── Literature ───────────────────────────────────────────────────────
    _entry(
        "panchasakha", "literature",
        "The Panchasakha", "ପଞ୍ଚସଖା",
        "Balarama Dasa, Jagannatha Dasa, Achyutananda Dasa, Yasobanta Dasa and "
        "Ananta Dasa — these five saint-poets are called the Panchasakha. Instead "
        "of Sanskrit they wrote religion and philosophy in Odia, the language of "
        "ordinary people. Balarama Dasa's Jagamohana Ramayana and Achyutananda's "
        "Malika are still widely read.",
        "ବଳରାମ ଦାସ, ଜଗନ୍ନାଥ ଦାସ, ଅଚ୍ୟୁତାନନ୍ଦ ଦାସ, ଯଶୋବନ୍ତ ଦାସ ଓ ଅନନ୍ତ ଦାସ — "
        "ଏହି ପାଞ୍ଚ ସନ୍ଥ କବିଙ୍କୁ ପଞ୍ଚସଖା କୁହାଯାଏ। ସେମାନେ ସଂସ୍କୃତ ବଦଳରେ ସାଧାରଣ "
        "ଲୋକଙ୍କ ଭାଷା ଓଡ଼ିଆରେ ଧର୍ମ ଓ ଦର୍ଶନ ଲେଖିଥିଲେ। ବଳରାମ ଦାସଙ୍କ ଜଗମୋହନ "
        "ରାମାୟଣ ଓ ଅଚ୍ୟୁତାନନ୍ଦଙ୍କ ମାଳିକା ଆଜି ବି ଲୋକପ୍ରିୟ।",
        "ପାଞ୍ଚ ସନ୍ଥ କବି, ଯେଉଁମାନେ ଧର୍ମକୁ ଲୋକଭାଷା ଓଡ଼ିଆରେ ଆଣିଲେ।",
        ["Mayadhar Mansinha, History of Oriya Literature (Sahitya Akademi)"],
    ),
    _entry(
        "gita_govinda", "literature",
        "Jayadeva's Gita Govinda", "ଜୟଦେବଙ୍କ ଗୀତଗୋବିନ୍ଦ",
        "In the 12th century the poet Jayadeva composed the Gita Govinda in "
        "Sanskrit. Odia tradition reveres him as the poet of Kenduli Sasan near "
        "Puri. The Gita Govinda has long been sung in the Jagannath temple, and "
        "its ashtapadis are essential to Odissi dance.",
        "ଦ୍ୱାଦଶ ଶତାବ୍ଦୀରେ କବି ଜୟଦେବ ସଂସ୍କୃତରେ ଗୀତଗୋବିନ୍ଦ ରଚନା କରିଥିଲେ। ଓଡ଼ିଆ "
        "ପରମ୍ପରାରେ ସେ ପୁରୀ ନିକଟ କେନ୍ଦୁଳି ଶାସନର କବି ଭାବେ ପୂଜିତ। ଶ୍ରୀମନ୍ଦିରରେ "
        "ଗୀତଗୋବିନ୍ଦ ଗାନର ଦୀର୍ଘ ପରମ୍ପରା ରହିଛି ଏବଂ ଓଡ଼ିଶୀ ନୃତ୍ୟରେ ଏହାର ଅଷ୍ଟପଦୀ "
        "ଅପରିହାର୍ଯ୍ୟ।",
        "ଜୟଦେବଙ୍କ ଅଷ୍ଟପଦୀ, ଶ୍ରୀମନ୍ଦିର ଓ ଓଡ଼ିଶୀ ନୃତ୍ୟର ଅଙ୍ଗ।",
        ["Barbara Stoler Miller, Love Song of the Dark Lord (intro)",
         "Prataparudra Deva inscription, Jagannath temple (1499)"],
    ),
    _entry(
        "matira_manisha", "literature",
        "Matira Manisa", "ମାଟିର ମଣିଷ",
        "Kalindi Charan Panigrahi's 'Matira Manisa' (1931) tells the story of "
        "two brothers, Baraju and Chhakadi. It shows, with deep feeling, the bond "
        "of a joint family and a brother's sacrifice to hold it together. Mrinal "
        "Sen later made it into a film.",
        "କାଳିନ୍ଦୀଚରଣ ପାଣିଗ୍ରାହୀଙ୍କ 'ମାଟିର ମଣିଷ' (୧୯୩୧) ଦୁଇ ଭାଇ ବରଜୁ ଓ ଛକଡ଼ିଙ୍କ "
        "କାହାଣୀ। ଏକାଠି ପରିବାରର ବନ୍ଧନ ଓ ତାହାକୁ ବଞ୍ଚାଇ ରଖିବା ପାଇଁ ଭାଇର ତ୍ୟାଗକୁ ଏହି "
        "ଉପନ୍ୟାସ ହୃଦୟସ୍ପର୍ଶୀ ଭାବେ ଦେଖାଏ। ପରେ ମୃଣାଳ ସେନ ଏହାକୁ ନେଇ ଚଳଚ୍ଚିତ୍ର "
        "ନିର୍ମାଣ କରିଥିଲେ।",
        "ଦୁଇ ଭାଇ ଓ ଗୋଟିଏ ପରିବାରର ଅମର ଓଡ଼ିଆ ଉପନ୍ୟାସ।",
        ["Sahitya Akademi, Encyclopaedia of Indian Literature"],
    ),
    _entry(
        "rasakallola", "literature",
        "Dinakrushna Dasa's Rasakallola", "ଦୀନକୃଷ୍ଣ ଦାସଙ୍କ ରସକଲ୍ଲୋଳ",
        "Every line of 'Rasakallola', by the riti-era poet Dinakrushna Dasa, "
        "begins with the letter 'ka'. Written on the life of Sri Krishna, it is a "
        "dazzling showcase of the richness of Odia vocabulary.",
        "ରୀତି ଯୁଗର କବି ଦୀନକୃଷ୍ଣ ଦାସଙ୍କ 'ରସକଲ୍ଲୋଳ'ର ପ୍ରତ୍ୟେକ ପଦ 'କ' ଅକ୍ଷରରେ ଆରମ୍ଭ "
        "ହୁଏ। ଶ୍ରୀକୃଷ୍ଣଙ୍କ ଲୀଳାକୁ ନେଇ ଲେଖା ଏହି କାବ୍ୟ ଓଡ଼ିଆ ଶବ୍ଦ ସମ୍ପଦର ଏକ ଚମତ୍କାର "
        "ନିଦର୍ଶନ।",
        "ପ୍ରତି ପଦ କ ଅକ୍ଷରରେ ଆରମ୍ଭ, ଏମିତି ଏକ ଅଦ୍ଭୁତ କାବ୍ୟ।",
        ["Mayadhar Mansinha, History of Oriya Literature"],
    ),
    _entry(
        "palm_leaf", "literature",
        "Palm-leaf manuscripts", "ତାଳପତ୍ର ପୋଥି",
        "Before printing presses, books in Odisha were written by incising "
        "letters on palm leaves with an iron stylus. Many scholars hold that Odia "
        "letters became rounded so the stylus would not split the leaf. Old "
        "pothis are still carefully kept in many homes.",
        "ଛାପାଖାନା ଆସିବା ପୂର୍ବରୁ ଓଡ଼ିଶାରେ ଲୁହା ଲେଖନୀରେ ତାଳପତ୍ରରେ ଅକ୍ଷର ଖୋଦି ପୋଥି "
        "ଲେଖାଯାଉଥିଲା। ଅନେକ ପଣ୍ଡିତଙ୍କ ମତରେ ପତ୍ର ଚିରିଯିବା ଭୟରେ ଓଡ଼ିଆ ଅକ୍ଷର "
        "ଗୋଲାକାର ହୋଇଛି। ଆଜି ବି ଅନେକ ଘରେ ପୁରୁଣା ପୋଥି ଯତ୍ନରେ ସାଇତା ହୋଇ ରହିଛି।",
        "ଓଡ଼ିଆ ଅକ୍ଷର ଗୋଲ କାହିଁକି, ତା ପଛରେ ତାଳପତ୍ରର କାହାଣୀ।",
        ["Odisha State Museum, palm-leaf manuscript collection"],
    ),
    _entry(
        "classical_odia", "literature",
        "Odia, a classical language", "ଶାସ୍ତ୍ରୀୟ ଭାଷା ଓଡ଼ିଆ",
        "In 2014 Odia was recognised as a classical language of India — the sixth "
        "at the time. That required proving its antiquity, an independent "
        "literary tradition and its distinctness from other languages.",
        "୨୦୧୪ ମସିହାରେ ଓଡ଼ିଆ ଭାରତର ଶାସ୍ତ୍ରୀୟ ଭାଷା ଭାବେ ସ୍ୱୀକୃତି ପାଇଲା — ସେତେବେଳେ "
        "ଏହା ଥିଲା ଷଷ୍ଠ ଶାସ୍ତ୍ରୀୟ ଭାଷା। ଏଥିପାଇଁ ଭାଷାର ପ୍ରାଚୀନତା, ନିଜସ୍ୱ ସାହିତ୍ୟ "
        "ପରମ୍ପରା ଓ ଅନ୍ୟ ଭାଷାଠାରୁ ସ୍ୱତନ୍ତ୍ରତା ପ୍ରମାଣ କରିବାକୁ ପଡ଼ିଥିଲା।",
        "୨୦୧୪ରେ ଓଡ଼ିଆ ପାଇଲା ଶାସ୍ତ୍ରୀୟ ଭାଷାର ମର୍ଯ୍ୟାଦା।",
        ["Ministry of Culture, Government of India, press release (Feb 2014)"],
    ),
    # ── Authors ──────────────────────────────────────────────────────────
    _entry(
        "sarala_das", "author",
        "Adikabi Sarala Das", "ଆଦିକବି ସାରଳା ଦାସ",
        "In the 15th century, during Gajapati Kapilendra Deva's reign, Sarala "
        "Das composed the Mahabharata in Odia. Not a translation of the Sanskrit, "
        "it is a free retelling full of Odisha's land, rivers and folk life — "
        "which is why he is called the Adikabi (first poet) of Odia literature.",
        "ପଞ୍ଚଦଶ ଶତାବ୍ଦୀରେ ଗଜପତି କପିଳେନ୍ଦ୍ର ଦେବଙ୍କ ସମୟରେ ସାରଳା ଦାସ ଓଡ଼ିଆ ଭାଷାରେ "
        "ମହାଭାରତ ରଚନା କରିଥିଲେ। ଏହା ସଂସ୍କୃତର ଅନୁବାଦ ନୁହେଁ, ଓଡ଼ିଶାର ମାଟି, ନଦୀ ଓ "
        "ଲୋକଜୀବନରେ ଭରା ଏକ ସ୍ୱାଧୀନ ପୁନଃସୃଷ୍ଟି। ସେଥିପାଇଁ ତାଙ୍କୁ ଓଡ଼ିଆ ସାହିତ୍ୟର "
        "ଆଦିକବି କୁହାଯାଏ।",
        "ଓଡ଼ିଆ ମହାଭାରତର ସ୍ରଷ୍ଟା, ଓଡ଼ିଆ ସାହିତ୍ୟର ଆଦିକବି।",
        ["Mayadhar Mansinha, History of Oriya Literature"],
    ),
    _entry(
        "jagannatha_dasa", "author",
        "Atibadi Jagannatha Dasa", "ଅତିବଡ଼ି ଜଗନ୍ନାଥ ଦାସ",
        "Jagannatha Dasa, one of the 16th-century Panchasakha, rendered the "
        "Srimad Bhagavata into simple Odia. Villages built Bhagavata Tungis where "
        "people gathered in the evening to hear it read. In many Odia homes the "
        "Bhagavata is still worshipped.",
        "ଷୋଡ଼ଶ ଶତାବ୍ଦୀର ପଞ୍ଚସଖାଙ୍କ ମଧ୍ୟରୁ ଜଗନ୍ନାଥ ଦାସ ସରଳ ଓଡ଼ିଆରେ ଶ୍ରୀମଦ୍ଭାଗବତ "
        "ରଚନା କରିଥିଲେ। ଗାଁ ଗାଁରେ ଭାଗବତ ଟୁଙ୍ଗି ଗଢ଼ି ଉଠିଲା, ଯେଉଁଠି ସନ୍ଧ୍ୟାରେ ଲୋକେ "
        "ଏକାଠି ହୋଇ ଭାଗବତ ଶୁଣୁଥିଲେ। ଅନେକ ଓଡ଼ିଆ ଘରେ ଆଜି ବି ଭାଗବତ ପୂଜା ପାଏ।",
        "ସରଳ ଓଡ଼ିଆରେ ଭାଗବତ ରଚି ଘରେ ଘରେ ପହଞ୍ଚାଇଥିଲେ।",
        ["Mayadhar Mansinha, History of Oriya Literature"],
    ),
    _entry(
        "upendra_bhanja", "author",
        "Kabisamrat Upendra Bhanja", "କବିସମ୍ରାଟ ଉପେନ୍ଦ୍ର ଭଞ୍ଜ",
        "Upendra Bhanja, a prince of Ghumusar, was a magician of words and "
        "ornament. Every line of his 'Baidehisha Bilasa' begins with the letter "
        "'ba'. Works like 'Labanyabati' earned him the title Kabisamrat, emperor "
        "of poets.",
        "ଘୁମୁସରର ରାଜକୁମାର ଉପେନ୍ଦ୍ର ଭଞ୍ଜ ଶବ୍ଦ ଓ ଅଳଙ୍କାରର ଯାଦୁକର ଥିଲେ। ତାଙ୍କ "
        "'ବୈଦେହୀଶ ବିଳାସ'ର ପ୍ରତ୍ୟେକ ପଦ 'ବ' ଅକ୍ଷରରେ ଆରମ୍ଭ ହୁଏ। 'ଲାବଣ୍ୟବତୀ' ଭଳି "
        "କାବ୍ୟ ପାଇଁ ସେ କବିସମ୍ରାଟ ଭାବେ ପରିଚିତ।",
        "ବୈଦେହୀଶ ବିଳାସର ପ୍ରତି ପଦ ବ ଅକ୍ଷରରେ ଆରମ୍ଭ।",
        ["Mayadhar Mansinha, History of Oriya Literature"],
    ),
    _entry(
        "kabisurya", "author",
        "Kabisurya Baladeba Ratha", "କବିସୂର୍ଯ୍ୟ ବଳଦେବ ରଥ",
        "The poet Baladeba Ratha is remembered above all for 'Kishora "
        "Chandrananda Champu'. Its songs remain at the heart of Odissi music and "
        "dance. He is honoured with the title Kabisurya.",
        "କବି ବଳଦେବ ରଥ 'କିଶୋର ଚନ୍ଦ୍ରାନନ୍ଦ ଚମ୍ପୂ' ପାଇଁ ଅମର। ଏହାର ଗୀତଗୁଡ଼ିକ ଆଜି "
        "ବି ଓଡ଼ିଶୀ ସଙ୍ଗୀତ ଓ ଓଡ଼ିଶୀ ନୃତ୍ୟର ପ୍ରାଣ। ସେ କବିସୂର୍ଯ୍ୟ ଉପାଧିରେ ସମ୍ମାନିତ।",
        "କିଶୋର ଚନ୍ଦ୍ରାନନ୍ଦ ଚମ୍ପୂର ଗୀତ, ଓଡ଼ିଶୀ ସଙ୍ଗୀତର ପ୍ରାଣ।",
        ["Mayadhar Mansinha, History of Oriya Literature"],
    ),
    _entry(
        "bhima_bhoi", "author",
        "Santha Kabi Bhima Bhoi", "ସନ୍ଥକବି ଭୀମ ଭୋଇ",
        "Bhima Bhoi, poet of the Mahima Dharma, was blind, yet his bhajans showed "
        "the way to countless people. His most famous line says: let my life fall "
        "into hell, but may the world be redeemed.",
        "ମହିମା ଧର୍ମର କବି ଭୀମ ଭୋଇ ଦୃଷ୍ଟିହୀନ ଥିଲେ, କିନ୍ତୁ ତାଙ୍କ ଭଜନ ଅଗଣିତ ଲୋକଙ୍କୁ "
        "ବାଟ ଦେଖାଇଲା। ତାଙ୍କ ସବୁଠାରୁ ପ୍ରସିଦ୍ଧ ପଦ — 'ମୋ ଜୀବନ ପଛେ ନର୍କେ ପଡ଼ିଥାଉ, "
        "ଜଗତ ଉଦ୍ଧାର ହେଉ'। ନିଜ ଦୁଃଖ ଭୁଲି ଜଗତର ମଙ୍ଗଳ କାମନା, ଏହା ହିଁ ତାଙ୍କ ବାର୍ତ୍ତା।",
        "ମୋ ଜୀବନ ପଛେ ନର୍କେ ପଡ଼ିଥାଉ, ଜଗତ ଉଦ୍ଧାର ହେଉ।",
        ["Sahitya Akademi, Encyclopaedia of Indian Literature"],
    ),
    _entry(
        "salabega", "author",
        "Bhakta Kabi Salabega", "ଭକ୍ତକବି ସାଲବେଗ",
        "The 17th-century devotee-poet Salabega was born a Muslim, yet was a "
        "devotee of Lord Jagannath like no other. Bhajans such as 'Ahe Nila "
        "Saila' are still sung in Odia homes. By tradition, the Rath Yatra "
        "chariot pauses near his tomb on the Bada Danda.",
        "ସପ୍ତଦଶ ଶତାବ୍ଦୀର ଭକ୍ତକବି ସାଲବେଗ ଜନ୍ମରୁ ମୁସଲମାନ, କିନ୍ତୁ ମହାପ୍ରଭୁ "
        "ଜଗନ୍ନାଥଙ୍କ ଅନନ୍ୟ ଭକ୍ତ ଥିଲେ। 'ଆହେ ନୀଳ ଶଇଳ' ଭଳି ତାଙ୍କ ଭଜନ ଆଜି ବି ଓଡ଼ିଆ ଘରେ "
        "ଘରେ ଗାନ ହୁଏ। ପରମ୍ପରା ଅନୁସାରେ ରଥଯାତ୍ରା ବେଳେ ବଡ଼ଦାଣ୍ଡରେ ତାଙ୍କ ସମାଧି ପାଖରେ "
        "ରଥ କିଛି ସମୟ ଅଟକେ।",
        "ଆହେ ନୀଳ ଶଇଳର ସ୍ରଷ୍ଟା, ଯାହାଙ୍କ ସମାଧି ପାଖରେ ରଥ ଅଟକେ।",
        ["Odisha Review (Government of Odisha), articles on Salabega"],
    ),
    _entry(
        "madhusudan_rao", "author",
        "Bhakta Kabi Madhusudan Rao", "ଭକ୍ତକବି ମଧୁସୂଦନ ରାଓ",
        "Generations of Odia children learnt their letters from 'Barnabodha', "
        "written by Madhusudan Rao. With Radhanath Ray and Fakir Mohan Senapati "
        "he is counted among the trinity of modern Odia literature.",
        "ଓଡ଼ିଆ ପିଲାମାନେ ପିଢ଼ି ପରେ ପିଢ଼ି ଯେଉଁ 'ବର୍ଣ୍ଣବୋଧ'ରୁ ଅକ୍ଷର ଶିଖିଛନ୍ତି, ତାହାର "
        "ରଚୟିତା ମଧୁସୂଦନ ରାଓ। ରାଧାନାଥ ରାୟ ଓ ଫକୀରମୋହନ ସେନାପତିଙ୍କ ସହ ସେ ଆଧୁନିକ "
        "ଓଡ଼ିଆ ସାହିତ୍ୟର ତ୍ରିମୂର୍ତ୍ତି ଭାବେ ପରିଚିତ।",
        "ବର୍ଣ୍ଣବୋଧର ରଚୟିତା, ଆଧୁନିକ ଓଡ଼ିଆ ସାହିତ୍ୟର ତ୍ରିମୂର୍ତ୍ତିଙ୍କ ଜଣେ।",
        ["Mayadhar Mansinha, History of Oriya Literature"],
    ),
    _entry(
        "fakir_mohan", "author",
        "Byasakabi Fakir Mohan Senapati", "ବ୍ୟାସକବି ଫକୀରମୋହନ ସେନାପତି",
        "Born in 1843 at Mallikashpur, Balasore, Fakir Mohan is called the "
        "father of modern Odia prose. His novel 'Chha Mana Atha Guntha' uses the "
        "greedy landlord Ramachandra Mangaraj and the poor weaver couple Bhagia "
        "and Saria to satirise colonial society. His 'Rebati' is counted as the "
        "first Odia short story.",
        "୧୮୪୩ ମସିହାରେ ବାଲେଶ୍ୱରର ମଲ୍ଲିକାଶପୁରରେ ଜନ୍ମିତ ଫକୀରମୋହନଙ୍କୁ ଆଧୁନିକ ଓଡ଼ିଆ "
        "ଗଦ୍ୟର ଜନକ କୁହାଯାଏ। ତାଙ୍କ ଉପନ୍ୟାସ 'ଛ ମାଣ ଆଠ ଗୁଣ୍ଠ' ଲୋଭୀ ଜମିଦାର ରାମଚନ୍ଦ୍ର "
        "ମାଙ୍ଗରାଜ ଓ ଗରିବ ଭଗିଆ-ଶାରିଆଙ୍କ କାହାଣୀ ମାଧ୍ୟମରେ ଔପନିବେଶିକ ସମାଜକୁ ତୀକ୍ଷ୍ଣ "
        "ବ୍ୟଙ୍ଗ କରେ। ତାଙ୍କ 'ରେବତୀ'କୁ ଓଡ଼ିଆର ପ୍ରଥମ କ୍ଷୁଦ୍ରଗଳ୍ପ ଭାବେ ଗଣାଯାଏ।",
        "ଛ ମାଣ ଆଠ ଗୁଣ୍ଠ ଓ ରେବତୀର ସ୍ରଷ୍ଟା, ଆଧୁନିକ ଓଡ଼ିଆ ଗଦ୍ୟର ଜନକ।",
        ["Fakir Mohan Senapati, Atma Jeebana Charita",
         "Sahitya Akademi, Makers of Indian Literature: Fakir Mohan Senapati"],
        anniversary="01-13",
    ),
    _entry(
        "radhanath_ray", "author",
        "Kabibara Radhanath Ray", "କବିବର ରାଧାନାଥ ରାୟ",
        "Born in 1848 at Kedarpur, Balasore, Radhanath Ray pioneered modern Odia "
        "poetry. In the poem 'Chilika' he made Odisha's natural beauty immortal. "
        "'Mahayatra' and 'Chandrabhaga' are among his famous works.",
        "୧୮୪୮ ମସିହାରେ ବାଲେଶ୍ୱରର କେଦାରପୁରରେ ଜନ୍ମିତ ରାଧାନାଥ ରାୟ ଆଧୁନିକ ଓଡ଼ିଆ "
        "କବିତାର ପଥପ୍ରଦର୍ଶକ। 'ଚିଲିକା' କାବ୍ୟରେ ସେ ଓଡ଼ିଶାର ପ୍ରକୃତିକୁ ଅମର କରିଦେଇଛନ୍ତି। "
        "'ମହାଯାତ୍ରା' ଓ 'ଚନ୍ଦ୍ରଭାଗା' ମଧ୍ୟ ତାଙ୍କର ପ୍ରସିଦ୍ଧ କୃତି।",
        "ଚିଲିକା କାବ୍ୟର କବି, ଆଧୁନିକ ଓଡ଼ିଆ କବିତାର ପଥପ୍ରଦର୍ଶକ।",
        ["Sahitya Akademi, Makers of Indian Literature: Radhanath Ray"],
        anniversary="09-28",
    ),
    _entry(
        "gangadhar_meher", "author",
        "Swabhaba Kabi Gangadhar Meher", "ସ୍ୱଭାବକବି ଗଙ୍ଗାଧର ମେହେର",
        "Born in 1862 into a weaver family of Barpali, Gangadhar Meher had little "
        "schooling, yet he is counted among the greatest Odia poets. His "
        "'Tapaswini' looks at Sita's life in exile with fresh eyes. His deep love "
        "of nature earned him the title Swabhaba Kabi, poet of nature.",
        "୧୮୬୨ ମସିହାରେ ବରପାଲିର ଏକ ବୁଣାକାର ପରିବାରରେ ଜନ୍ମିତ ଗଙ୍ଗାଧର ମେହେର ବେଶି "
        "ସ୍କୁଲ ପଢ଼ି ନଥିଲେ, ତଥାପି ସେ ଓଡ଼ିଆର ଶ୍ରେଷ୍ଠ କବିଙ୍କ ମଧ୍ୟରେ ଗଣା। ତାଙ୍କ "
        "'ତପସ୍ୱିନୀ' କାବ୍ୟ ସୀତାଙ୍କ ବନବାସ ଜୀବନକୁ ନୂଆ ଦୃଷ୍ଟିରେ ଦେଖାଏ। ପ୍ରକୃତି ପ୍ରତି "
        "ଗଭୀର ପ୍ରେମ ପାଇଁ ସେ ସ୍ୱଭାବକବି ଭାବେ ପରିଚିତ।",
        "ତପସ୍ୱିନୀର କବି, ପ୍ରକୃତି ପ୍ରେମୀ ସ୍ୱଭାବକବି।",
        ["Sahitya Akademi, Makers of Indian Literature: Gangadhar Meher"],
        anniversary="08-09",
    ),
    _entry(
        "gopinath_mohanty", "author",
        "Gopinath Mohanty", "ଗୋପୀନାଥ ମହାନ୍ତି",
        "The first Jnanpith Award for Odia went to Gopinath Mohanty for 'Mati "
        "Matala' (1973). His novel 'Paraja', about tribal life in Koraput, is a "
        "landmark of Indian fiction. For 'Amrutara Santana' he received the first "
        "Sahitya Akademi Award given in Odia.",
        "ଓଡ଼ିଆ ଭାଷା ପାଇଁ ପ୍ରଥମ ଜ୍ଞାନପୀଠ ପୁରସ୍କାର ଆସିଥିଲା ଗୋପୀନାଥ ମହାନ୍ତିଙ୍କ "
        "'ମାଟିମଟାଳ' ପାଇଁ (୧୯୭୩)। କୋରାପୁଟର ଆଦିବାସୀ ଜୀବନକୁ ନେଇ ଲେଖା ତାଙ୍କ 'ପରଜା' "
        "ଉପନ୍ୟାସ ଭାରତୀୟ ସାହିତ୍ୟର ଏକ ମାଇଲଖୁଣ୍ଟ। 'ଅମୃତର ସନ୍ତାନ' ପାଇଁ ସେ ଓଡ଼ିଆରେ "
        "ପ୍ରଥମ ସାହିତ୍ୟ ଏକାଡେମୀ ପୁରସ୍କାର ପାଇଥିଲେ।",
        "ଓଡ଼ିଆରେ ପ୍ରଥମ ଜ୍ଞାନପୀଠ, ମାଟିମଟାଳ ପାଇଁ।",
        ["Bharatiya Jnanpith, list of laureates",
         "Sahitya Akademi Awards, Odia (1955)"],
        anniversary="04-20",
    ),
    _entry(
        "sachi_routray", "author",
        "Sachidananda Routray", "ସଚ୍ଚିଦାନନ୍ଦ ରାଉତରାୟ",
        "Sachi Routray carried Odia poetry into the modern age. His poem 'Baji "
        "Rout' is the immortal ballad of a twelve-year-old boatman who gave his "
        "life for the country. He received the Jnanpith Award in 1986.",
        "ସଚି ରାଉତରାୟ ଓଡ଼ିଆ କବିତାକୁ ଆଧୁନିକ ଯୁଗରେ ପହଞ୍ଚାଇଥିଲେ। ତାଙ୍କ 'ବାଜି ରାଉତ' "
        "କବିତା ଦେଶ ପାଇଁ ପ୍ରାଣ ଦେଇଥିବା ବାର ବର୍ଷର ଏକ ନାଉରିଆ ପିଲାର ଅମର ଗାଥା। ୧୯୮୬ "
        "ମସିହାରେ ସେ ଜ୍ଞାନପୀଠ ପୁରସ୍କାର ପାଇଥିଲେ।",
        "ବାଜି ରାଉତର କବି, ୧୯୮୬ରେ ଜ୍ଞାନପୀଠ ସମ୍ମାନିତ।",
        ["Bharatiya Jnanpith, list of laureates"],
        anniversary="05-13",
    ),
    _entry(
        "pratibha_ray", "author",
        "Pratibha Ray", "ପ୍ରତିଭା ରାୟ",
        "Pratibha Ray's 'Yajnaseni' retells the Mahabharata in Draupadi's own "
        "voice and has been translated into many languages. In 2011 she received "
        "the Jnanpith Award, the first Odia woman to be so honoured.",
        "ପ୍ରତିଭା ରାୟଙ୍କ 'ଯାଜ୍ଞସେନୀ' ଦ୍ରୌପଦୀଙ୍କ ନିଜ ସ୍ୱରରେ ମହାଭାରତକୁ ନୂଆ କରି କହେ ଏବଂ "
        "ଅନେକ ଭାଷାକୁ ଅନୁଦିତ ହୋଇଛି। ୨୦୧୧ ମସିହାରେ ସେ ଜ୍ଞାନପୀଠ ପୁରସ୍କାର ପାଇଥିଲେ — "
        "ଏହି ସମ୍ମାନ ପାଇଥିବା ପ୍ରଥମ ଓଡ଼ିଆ ମହିଳା।",
        "ଯାଜ୍ଞସେନୀର ଲେଖିକା, ଜ୍ଞାନପୀଠ ପାଇଥିବା ପ୍ରଥମ ଓଡ଼ିଆ ମହିଳା।",
        ["Bharatiya Jnanpith, list of laureates"],
    ),
    # ── Great Odias ──────────────────────────────────────────────────────
    _entry(
        "madhusudan_das", "personality",
        "Utkal Gourab Madhusudan Das", "ଉତ୍କଳ ଗୌରବ ମଧୁସୂଦନ ଦାସ",
        "Born in 1848 at Satyabhamapur, Cuttack, Madhu Babu was the first Odia "
        "graduate and a renowned lawyer. In 1903 he founded the Utkal Sammilani "
        "to unite the scattered Odia-speaking regions. Through the Utkal Tannery "
        "he dreamt of making Odia artisans self-reliant.",
        "୧୮୪୮ ମସିହାରେ କଟକର ସତ୍ୟଭାମାପୁରରେ ଜନ୍ମିତ ମଧୁବାବୁ ଓଡ଼ିଆଙ୍କ ପ୍ରଥମ ସ୍ନାତକ ଓ "
        "ଜଣେ ପ୍ରଖ୍ୟାତ ଆଇନଜୀବୀ ଥିଲେ। ୧୯୦୩ରେ ସେ ଉତ୍କଳ ସମ୍ମିଳନୀ ଗଢ଼ି ବିଚ୍ଛିନ୍ନ ଓଡ଼ିଆ "
        "ଭାଷାଭାଷୀ ଅଞ୍ଚଳକୁ ଏକାଠି କରିବାର ଆନ୍ଦୋଳନ ଆରମ୍ଭ କରିଥିଲେ। ଉତ୍କଳ ଟାନେରି "
        "ମାଧ୍ୟମରେ ସେ ଓଡ଼ିଆ କାରିଗରଙ୍କୁ ଆତ୍ମନିର୍ଭର କରିବାର ସ୍ୱପ୍ନ ଦେଖିଥିଲେ।",
        "ଉତ୍କଳ ସମ୍ମିଳନୀର ପ୍ରତିଷ୍ଠାତା, ସ୍ୱତନ୍ତ୍ର ଓଡ଼ିଶାର ସ୍ୱପ୍ନଦ୍ରଷ୍ଟା।",
        ["Odisha Review (Government of Odisha), Madhusudan Das special issues"],
        anniversary="04-28",
    ),
    _entry(
        "gopabandhu", "personality",
        "Utkalmani Gopabandhu Das", "ଉତ୍କଳମଣି ଗୋପବନ୍ଧୁ ଦାସ",
        "In 1909 Gopabandhu started the Bana Vidyalaya at Satyabadi, where "
        "classes were held under the trees. In 1919 he launched the newspaper "
        "'Samaja'. A line from 'Bandira Atmakatha', written in prison — 'let my "
        "body mingle with the soil of this land' — still stirs every Odia heart.",
        "୧୯୦୯ ମସିହାରେ ସତ୍ୟବାଦୀରେ ଗଛ ମୂଳେ ପାଠ ପଢ଼ାଉଥିବା ବନ ବିଦ୍ୟାଳୟ ଆରମ୍ଭ "
        "କରିଥିଲେ ଗୋପବନ୍ଧୁ। ୧୯୧୯ରେ ସେ 'ସମାଜ' ଖବରକାଗଜ ଆରମ୍ଭ କଲେ। ଜେଲରେ ଲେଖା ତାଙ୍କ "
        "'ବନ୍ଦୀର ଆତ୍ମକଥା'ର ପଦ 'ମିଶୁ ମୋର ଦେହ ଏ ଦେଶ ମାଟିରେ' ଆଜି ବି ପ୍ରତି ଓଡ଼ିଆଙ୍କ "
        "ପ୍ରାଣରେ ବାଜେ।",
        "ମିଶୁ ମୋର ଦେହ ଏ ଦେଶ ମାଟିରେ, ଉତ୍କଳମଣିଙ୍କ ଅମର ବାଣୀ।",
        ["Gopabandhu Das, Bandira Atmakatha",
         "Odisha Review (Government of Odisha), Gopabandhu special issues"],
        anniversary="10-09",
    ),
    _entry(
        "krushna_chandra_gajapati", "personality",
        "Maharaja Krushna Chandra Gajapati", "ମହାରାଜା କୃଷ୍ଣଚନ୍ଦ୍ର ଗଜପତି",
        "Maharaja Krushna Chandra Gajapati of Paralakhemundi was a leading voice "
        "of the movement for a separate Odisha province, and became its first "
        "Premier in 1937. Gajapati district is named after him.",
        "ପାରଳାଖେମୁଣ୍ଡିର ମହାରାଜା କୃଷ୍ଣଚନ୍ଦ୍ର ଗଜପତି ସ୍ୱତନ୍ତ୍ର ଓଡ଼ିଶା ପ୍ରଦେଶ ଗଠନ "
        "ଆନ୍ଦୋଳନର ଜଣେ ପ୍ରମୁଖ ନେତା ଥିଲେ ଏବଂ ୧୯୩୭ରେ ଓଡ଼ିଶାର ପ୍ରଥମ ପ୍ରଧାନମନ୍ତ୍ରୀ "
        "ହୋଇଥିଲେ। ଗଜପତି ଜିଲ୍ଲା ତାଙ୍କ ନାମରେ ନାମିତ।",
        "ସ୍ୱତନ୍ତ୍ର ଓଡ଼ିଶା ଆନ୍ଦୋଳନର ନେତା, ଗଜପତି ଜିଲ୍ଲା ତାଙ୍କ ନାମରେ।",
        ["Odisha Review (Government of Odisha), Utkal Divas issues"],
    ),
    _entry(
        "harekrushna_mahtab", "personality",
        "Utkal Keshari Harekrushna Mahtab", "ଉତ୍କଳ କେଶରୀ ହରେକୃଷ୍ଣ ମହତାବ",
        "Freedom fighter Harekrushna Mahtab was Odisha's first Chief Minister. "
        "He played a major role in merging the princely Garjat states into "
        "Odisha. He was also a historian and writer; his history of Odisha is "
        "still read.",
        "ସ୍ୱାଧୀନତା ସଂଗ୍ରାମୀ ହରେକୃଷ୍ଣ ମହତାବ ଓଡ଼ିଶାର ପ୍ରଥମ ମୁଖ୍ୟମନ୍ତ୍ରୀ ଥିଲେ। "
        "ଗଡ଼ଜାତ ରାଜ୍ୟଗୁଡ଼ିକୁ ଓଡ଼ିଶା ସହ ମିଶାଇବାରେ ତାଙ୍କର ବଡ଼ ଭୂମିକା ଥିଲା। ସେ ଜଣେ "
        "ଇତିହାସକାର ଓ ସାହିତ୍ୟିକ ମଧ୍ୟ ଥିଲେ ଏବଂ ତାଙ୍କ ଲେଖା ଓଡ଼ିଶା ଇତିହାସ ଆଜି ବି "
        "ପଢ଼ାଯାଏ।",
        "ଓଡ଼ିଶାର ପ୍ରଥମ ମୁଖ୍ୟମନ୍ତ୍ରୀ, ଗଡ଼ଜାତ ମିଶ୍ରଣର କାରିଗର।",
        ["Odisha Legislative Assembly, list of Chief Ministers"],
        anniversary="11-21",
    ),
    _entry(
        "biju_patnaik", "personality",
        "Biju Patnaik", "ବିଜୁ ପଟ୍ଟନାୟକ",
        "Biju Patnaik was a daring pilot. In 1947 he flew into Dutch-blockaded "
        "Indonesia and brought out the Indonesian leader Sutan Sjahrir. He "
        "founded UNESCO's Kalinga Prize for science popularisation and twice "
        "served as Chief Minister of Odisha.",
        "ବିଜୁ ପଟ୍ଟନାୟକ ଜଣେ ସାହସୀ ବିମାନଚାଳକ ଥିଲେ। ୧୯୪୭ ମସିହାରେ ସେ ନିଜେ ବିମାନ "
        "ଉଡ଼ାଇ ଡଚ୍ ଅବରୋଧ ଭିତରୁ ଇଣ୍ଡୋନେସିଆର ନେତା ସୁତାନ ଶାହରିରଙ୍କୁ ବାହାରକୁ ଆଣିଥିଲେ। "
        "ବିଜ୍ଞାନ ପ୍ରସାର ପାଇଁ ୟୁନେସ୍କୋର କଳିଙ୍ଗ ପୁରସ୍କାର ସେ ପ୍ରତିଷ୍ଠା କରିଥିଲେ ଏବଂ ଦୁଇ "
        "ଥର ଓଡ଼ିଶାର ମୁଖ୍ୟମନ୍ତ୍ରୀ ହୋଇଥିଲେ।",
        "ଇଣ୍ଡୋନେସିଆର ନେତାଙ୍କୁ ଉଦ୍ଧାର କରିଥିବା ସାହସୀ ପାଇଲଟ।",
        ["UNESCO, Kalinga Prize for the Popularization of Science"],
        anniversary="03-05",
    ),
    _entry(
        "netaji_cuttack", "personality",
        "Netaji Subhas Chandra Bose and Cuttack", "କଟକର ନେତାଜୀ",
        "Netaji Subhas Chandra Bose was born in Cuttack in 1897 and studied at "
        "Ravenshaw Collegiate School there. His birthplace, Janakinath Bhawan in "
        "Odia Bazar, is now a museum.",
        "ନେତାଜୀ ସୁଭାଷ ଚନ୍ଦ୍ର ବୋଷ ୧୮୯୭ ମସିହାରେ କଟକରେ ଜନ୍ମଗ୍ରହଣ କରିଥିଲେ ଏବଂ ସେଠାରେ "
        "ରେଭେନ୍ସା କଲେଜିଏଟ ସ୍କୁଲରେ ପଢ଼ିଥିଲେ। ଓଡ଼ିଆ ବଜାରରେ ଥିବା ତାଙ୍କ ଜନ୍ମଗୃହ "
        "ଜାନକୀନାଥ ଭବନ ଆଜି ଏକ ସଂଗ୍ରହାଳୟ।",
        "କଟକରେ ଜନ୍ମିତ ନେତାଜୀ, ଜନ୍ମଗୃହ ଆଜି ସଂଗ୍ରହାଳୟ।",
        ["Netaji Birthplace Museum, Cuttack (Government of Odisha)"],
        anniversary="01-23",
    ),
    _entry(
        "rama_devi", "personality",
        "Maa Rama Devi", "ମା ରମାଦେବୀ",
        "Gandhian freedom fighter Rama Devi brought the women of Odisha into the "
        "freedom movement. After independence she devoted her life to the "
        "Bhoodan movement and village service. People called her 'Maa', and Rama "
        "Devi Women's University in Bhubaneswar bears her name.",
        "ଗାନ୍ଧୀବାଦୀ ସ୍ୱାଧୀନତା ସଂଗ୍ରାମୀ ରମାଦେବୀ ଓଡ଼ିଶାର ମହିଳାଙ୍କୁ ସ୍ୱାଧୀନତା "
        "ଆନ୍ଦୋଳନରେ ଆଗକୁ ଆଣିଥିଲେ। ସ୍ୱାଧୀନତା ପରେ ସେ ଭୂଦାନ ଆନ୍ଦୋଳନ ଓ ଗ୍ରାମସେବାରେ "
        "ଜୀବନ ଉତ୍ସର୍ଗ କଲେ। ଲୋକେ ତାଙ୍କୁ ସ୍ନେହରେ ମା ବୋଲି ଡାକୁଥିଲେ ଏବଂ ଭୁବନେଶ୍ୱରର "
        "ରମାଦେବୀ ମହିଳା ବିଶ୍ୱବିଦ୍ୟାଳୟ ତାଙ୍କ ନାମରେ।",
        "ଓଡ଼ିଶାର ମହିଳାଙ୍କୁ ସ୍ୱାଧୀନତା ସଂଗ୍ରାମକୁ ଆଣିଥିବା ମା।",
        ["Rama Devi Women's University, about the university"],
        anniversary="12-03",
    ),
    _entry(
        "pathani_samanta", "personality",
        "Pathani Samanta", "ପଠାଣି ସାମନ୍ତ",
        "In the 19th century Mahamahopadhyaya Chandrasekhar Singh Samanta of "
        "Khandapara, known as Pathani Samanta, measured the sky with instruments "
        "he built himself from bamboo and wood. Observing with the naked eye, "
        "without a telescope, he wrote the treatise 'Siddhanta Darpana'. The "
        "planetarium in Bhubaneswar is named after him.",
        "ଊନବିଂଶ ଶତାବ୍ଦୀରେ ଖଣ୍ଡପଡ଼ାର ମହାମହୋପାଧ୍ୟାୟ ଚନ୍ଦ୍ରଶେଖର ସିଂହ ସାମନ୍ତ, "
        "ଯାହାଙ୍କୁ ପଠାଣି ସାମନ୍ତ କୁହାଯାଏ, ବାଉଁଶ ଓ କାଠରେ ନିଜେ ତିଆରି ଯନ୍ତ୍ରରେ ଆକାଶ "
        "ମାପୁଥିଲେ। ଟେଲିସ୍କୋପ ବିନା ଖାଲି ଆଖିରେ ଗ୍ରହନକ୍ଷତ୍ର ଦେଖି ସେ 'ସିଦ୍ଧାନ୍ତ ଦର୍ପଣ' "
        "ଗ୍ରନ୍ଥ ରଚନା କରିଥିଲେ। ଭୁବନେଶ୍ୱରର ପଠାଣି ସାମନ୍ତ ପ୍ଲାନେଟୋରିୟମ ତାଙ୍କ ନାମରେ।",
        "ବାଉଁଶ ଯନ୍ତ୍ରରେ ଆକାଶ ମାପିଥିବା ଓଡ଼ିଆ ଜ୍ୟୋତିର୍ବିଜ୍ଞାନୀ।",
        ["Pathani Samanta Planetarium, Bhubaneswar",
         "Siddhanta Darpana (Calcutta, 1899)"],
    ),
    _entry(
        "kelucharan", "personality",
        "Guru Kelucharan Mohapatra", "ଗୁରୁ କେଳୁଚରଣ ମହାପାତ୍ର",
        "Born in Raghurajpur, Kelucharan Mohapatra danced as a Gotipua boy in "
        "his childhood. He went on to give Odissi dance new life and carry it to "
        "the world stage, and was honoured with the Padma Vibhushan.",
        "ରଘୁରାଜପୁରରେ ଜନ୍ମିତ କେଳୁଚରଣ ପିଲାଦିନେ ଗୋଟିପୁଅ ନାଚୁଥିଲେ। ପରେ ସେ ଓଡ଼ିଶୀ "
        "ନୃତ୍ୟକୁ ନୂଆ ଜୀବନ ଦେଇ ବିଶ୍ୱ ମଞ୍ଚରେ ପହଞ୍ଚାଇଲେ ଏବଂ ପଦ୍ମବିଭୂଷଣରେ ସମ୍ମାନିତ "
        "ହୋଇଥିଲେ।",
        "ଗୋଟିପୁଅରୁ ଓଡ଼ିଶୀର ବିଶ୍ୱଗୁରୁ।",
        ["Sangeet Natak Akademi, fellows and awardees"],
        anniversary="01-08",
    ),
    # ── History ──────────────────────────────────────────────────────────
    _entry(
        "utkal_divas", "history",
        "Utkal Divas", "ଉତ୍କଳ ଦିବସ",
        "On 1 April 1936 Odisha was born as a separate province formed on the "
        "basis of language. It was the fruit of the long struggle of Madhusudan "
        "Das, Maharaja Krushna Chandra Gajapati, Gopabandhu Das and many others. "
        "That is why 1 April is celebrated every year as Utkal Divas.",
        "୧୯୩୬ ମସିହା ଏପ୍ରିଲ ୧ ତାରିଖରେ ଭାଷା ଆଧାରରେ ଗଠିତ ଏକ ସ୍ୱତନ୍ତ୍ର ପ୍ରଦେଶ ଭାବେ "
        "ଓଡ଼ିଶା ଜନ୍ମ ନେଲା। ମଧୁସୂଦନ ଦାସ, ମହାରାଜା କୃଷ୍ଣଚନ୍ଦ୍ର ଗଜପତି, ଗୋପବନ୍ଧୁ ଦାସଙ୍କ "
        "ଭଳି ଅନେକଙ୍କ ଦୀର୍ଘ ସଂଗ୍ରାମର ଫଳ ଏହା। ସେଥିପାଇଁ ପ୍ରତିବର୍ଷ ଏପ୍ରିଲ ୧ରେ ଉତ୍କଳ "
        "ଦିବସ ପାଳନ କରାଯାଏ।",
        "୧୯୩୬ ଏପ୍ରିଲ ୧ରେ ଭାଷା ଆଧାରରେ ଜନ୍ମ ନେଲା ସ୍ୱତନ୍ତ୍ର ଓଡ଼ିଶା।",
        ["Government of India Act 1935; Orissa Province constituted 1 April 1936"],
        anniversary="04-01",
        anniversary_or="ଆଜି ଉତ୍କଳ ଦିବସ",
    ),
    _entry(
        "kalinga_war", "history",
        "The Kalinga War and Dhauli", "କଳିଙ୍ଗ ଯୁଦ୍ଧ ଓ ଧଉଳି",
        "Around 261 BCE Emperor Ashoka conquered Kalinga, but the terrible "
        "bloodshed of the war changed his heart. He turned from war to the path "
        "of dharma and non-violence. Ashoka's rock edicts can still be seen on "
        "Dhauli hill near Bhubaneswar.",
        "ଖ୍ରୀଷ୍ଟପୂର୍ବ ପ୍ରାୟ ୨୬୧ରେ ସମ୍ରାଟ ଅଶୋକ କଳିଙ୍ଗ ଜୟ କରିଥିଲେ, କିନ୍ତୁ ଯୁଦ୍ଧର "
        "ଭୟଙ୍କର ରକ୍ତପାତ ତାଙ୍କ ମନକୁ ବଦଳାଇଦେଲା। ସେ ଯୁଦ୍ଧ ଛାଡ଼ି ଧର୍ମ ଓ ଅହିଂସାର ପଥ "
        "ଧରିଲେ। ଭୁବନେଶ୍ୱର ନିକଟ ଧଉଳି ପାହାଡ଼ରେ ଅଶୋକଙ୍କ ଶିଳାଲେଖ ଆଜି ବି ଦେଖିହୁଏ।",
        "ଯେଉଁ ଯୁଦ୍ଧ ଜଣେ ସମ୍ରାଟଙ୍କ ହୃଦୟ ବଦଳାଇଦେଲା।",
        ["Ashoka's Rock Edict XIII", "Archaeological Survey of India, Dhauli"],
    ),
    _entry(
        "kharavela", "history",
        "Emperor Kharavela", "ମହାମେଘବାହନ ଖାରବେଳ",
        "Kharavela was a great emperor of ancient Kalinga. The Hathigumpha "
        "inscription at Udayagiri records his victories and public works such as "
        "extending a canal. He was a patron of Jainism, and the caves of "
        "Udayagiri and Khandagiri bear witness to that age.",
        "ଖାରବେଳ ପ୍ରାଚୀନ କଳିଙ୍ଗର ଜଣେ ମହାନ ସମ୍ରାଟ ଥିଲେ। ଉଦୟଗିରିର ହାତୀଗୁମ୍ଫା "
        "ଶିଳାଲେଖରେ ତାଙ୍କ ବିଜୟ ଓ କେନାଲ ବିସ୍ତାର ଭଳି ପ୍ରଜାହିତକର କାର୍ଯ୍ୟର ବର୍ଣ୍ଣନା ଅଛି। "
        "ସେ ଜୈନ ଧର୍ମର ପୃଷ୍ଠପୋଷକ ଥିଲେ ଏବଂ ଉଦୟଗିରି ଓ ଖଣ୍ଡଗିରିର ଗୁମ୍ଫା ସେହି ଯୁଗର "
        "ସାକ୍ଷୀ।",
        "ହାତୀଗୁମ୍ଫା ଶିଳାଲେଖରେ ଲେଖା କଳିଙ୍ଗ ସମ୍ରାଟଙ୍କ ଗାଥା।",
        ["Hathigumpha inscription", "Archaeological Survey of India, Udayagiri"],
    ),
    _entry(
        "paika_bidroha", "history",
        "The Paika Rebellion of 1817", "ପାଇକ ବିଦ୍ରୋହ",
        "In 1817 the Paikas of Khordha, led by Bakshi Jagabandhu, took up arms "
        "against the East India Company. Loss of land and injustices such as the "
        "salt monopoly were among its causes. Many historians see it as an early "
        "popular uprising against British rule.",
        "୧୮୧୭ ମସିହାରେ ବକ୍ସି ଜଗବନ୍ଧୁଙ୍କ ନେତୃତ୍ୱରେ ଖୋର୍ଦ୍ଧାର ପାଇକମାନେ ଇଷ୍ଟ ଇଣ୍ଡିଆ "
        "କମ୍ପାନୀ ବିରୋଧରେ ଅସ୍ତ୍ର ଧରିଥିଲେ। ଜମି ହରାଇବା ଓ ଲୁଣ ଉପରେ ଏକଚାଟିଆ ଅଧିକାର "
        "ଭଳି ଅନ୍ୟାୟ ଏହାର କାରଣ ଥିଲା। ଅନେକ ଇତିହାସକାର ଏହାକୁ ବ୍ରିଟିଶ ଶାସନ ବିରୋଧରେ "
        "ଏକ ପ୍ରାରମ୍ଭିକ ଜନ ବିଦ୍ରୋହ ଭାବେ ଦେଖନ୍ତି।",
        "୧୮୧୭ରେ ବକ୍ସି ଜଗବନ୍ଧୁଙ୍କ ନେତୃତ୍ୱରେ ଖୋର୍ଦ୍ଧାର ପାଇକଙ୍କ ବିଦ୍ରୋହ।",
        ["P. K. Pattanaik (ed.), The Paika Rebellion of 1817",
         "Odisha State Archives"],
    ),
    _entry(
        "surendra_sai", "history",
        "Veer Surendra Sai", "ବୀର ସୁରେନ୍ଦ୍ର ସାଏ",
        "Veer Surendra Sai of Sambalpur fought British rule for many years and "
        "spent much of his life in prison. During the revolt of 1857 he led the "
        "resistance in western Odisha. He died a prisoner in Asirgarh fort in "
        "1884.",
        "ସମ୍ବଲପୁରର ବୀର ସୁରେନ୍ଦ୍ର ସାଏ ବହୁ ବର୍ଷ ଧରି ବ୍ରିଟିଶ ଶାସନ ବିରୋଧରେ ଲଢ଼ିଥିଲେ "
        "ଏବଂ ଜୀବନର ଅଧିକାଂଶ ସମୟ କାରାଗାରରେ କଟାଇଥିଲେ। ୧୮୫୭ ବିଦ୍ରୋହ ସମୟରେ ପଶ୍ଚିମ "
        "ଓଡ଼ିଶାରେ ସେ ପ୍ରତିରୋଧର ନେତୃତ୍ୱ ନେଇଥିଲେ। ୧୮୮୪ରେ ଅସୀରଗଡ଼ ଦୁର୍ଗରେ ବନ୍ଦୀ "
        "ଅବସ୍ଥାରେ ତାଙ୍କର ଦେହାନ୍ତ ହୋଇଥିଲା।",
        "ପଶ୍ଚିମ ଓଡ଼ିଶାରେ ବ୍ରିଟିଶ ବିରୋଧୀ ସଂଗ୍ରାମର ବୀର ନାୟକ।",
        ["Odisha State Archives", "Odisha Review, Veer Surendra Sai issues"],
    ),
    _entry(
        "baji_rout", "history",
        "Baji Rout", "ବାଜି ରାଉତ",
        "In 1938, at Nilakanthapur ghat in Dhenkanal, twelve-year-old boatman "
        "Baji Rout refused to ferry the police across the Brahmani river and was "
        "shot dead. He is counted among India's youngest martyrs.",
        "୧୯୩୮ ମସିହାରେ ଢେଙ୍କାନାଳର ନୀଳକଣ୍ଠପୁର ଘାଟରେ ବାର ବର୍ଷର ନାଉରିଆ ବାଜି ରାଉତ "
        "ପୋଲିସକୁ ବ୍ରାହ୍ମଣୀ ନଦୀ ପାର କରାଇବାକୁ ମନା କରିଦେଲେ। ପୋଲିସର ଗୁଳିରେ ସେ ଶହୀଦ "
        "ହେଲେ। ସେ ଭାରତର ସର୍ବକନିଷ୍ଠ ଶହୀଦଙ୍କ ମଧ୍ୟରେ ଗଣା।",
        "ବାର ବର୍ଷର ନାଉରିଆ, ଯିଏ ଡଙ୍ଗା ଚଳାଇବାକୁ ମନା କଲା।",
        ["Odisha Review (Government of Odisha), Baji Rout articles"],
    ),
    _entry(
        "laxman_nayak", "history",
        "Shahid Laxman Nayak", "ଶହୀଦ ଲକ୍ଷ୍ମଣ ନାୟକ",
        "Laxman Nayak, a tribal leader of Koraput, led villagers in the 1942 "
        "Quit India movement. The British hanged him in Berhampur jail in 1943. "
        "He is honoured as a symbol of the courage and self-respect of Odisha's "
        "tribal communities.",
        "କୋରାପୁଟର ଆଦିବାସୀ ନେତା ଲକ୍ଷ୍ମଣ ନାୟକ ୧୯୪୨ର ଭାରତ ଛାଡ଼ ଆନ୍ଦୋଳନରେ "
        "ଗ୍ରାମବାସୀଙ୍କୁ ନେତୃତ୍ୱ ଦେଇଥିଲେ। ୧୯୪୩ରେ ବ୍ରିଟିଶ ସରକାର ତାଙ୍କୁ ବ୍ରହ୍ମପୁର ଜେଲରେ "
        "ଫାଶୀ ଦେଇଥିଲା। ଆଦିବାସୀ ସମାଜର ସାହସ ଓ ସ୍ୱାଭିମାନର ପ୍ରତୀକ ଭାବେ ସେ ଆଜି ବି "
        "ସମ୍ମାନିତ।",
        "କୋରାପୁଟର ଆଦିବାସୀ ବୀର, ଭାରତ ଛାଡ଼ ଆନ୍ଦୋଳନର ଶହୀଦ।",
        ["Odisha Review (Government of Odisha), Laxman Nayak articles"],
    ),
    _entry(
        "hirakud", "history",
        "Hirakud Dam", "ହୀରାକୁଦ ବନ୍ଧ",
        "Hirakud Dam on the Mahanadi is among the longest earthen dams in the "
        "world. Inaugurated in 1957, it has shaped Odisha's growth through flood "
        "control, irrigation and power generation.",
        "ମହାନଦୀ ଉପରେ ନିର୍ମିତ ହୀରାକୁଦ ବନ୍ଧ ବିଶ୍ୱର ଦୀର୍ଘତମ ମାଟି ବନ୍ଧମାନଙ୍କ ମଧ୍ୟରୁ "
        "ଅନ୍ୟତମ। ୧୯୫୭ ମସିହାରେ ଏହା ଉଦଘାଟିତ ହୋଇଥିଲା। ବନ୍ୟା ନିୟନ୍ତ୍ରଣ, ଜଳସେଚନ ଓ "
        "ବିଦ୍ୟୁତ ଉତ୍ପାଦନ ମାଧ୍ୟମରେ ଏହା ଓଡ଼ିଶାର ବିକାଶରେ ବଡ଼ ଭୂମିକା ନେଇଛି।",
        "ମହାନଦୀ ଉପରେ ବିଶ୍ୱର ଦୀର୍ଘତମ ମାଟି ବନ୍ଧମାନଙ୍କ ଅନ୍ୟତମ।",
        ["Department of Water Resources, Government of Odisha"],
    ),
    # ── Heritage ─────────────────────────────────────────────────────────
    _entry(
        "konark", "heritage",
        "Konark Sun Temple", "କୋଣାର୍କ ସୂର୍ଯ୍ୟ ମନ୍ଦିର",
        "Built in the 13th century by King Narasimha Deva I of the Eastern Ganga "
        "dynasty, Konark is shaped as the giant chariot of the Sun god — "
        "twenty-four carved stone wheels drawn by seven horses. It was declared a "
        "UNESCO World Heritage Site in 1984.",
        "ତ୍ରୟୋଦଶ ଶତାବ୍ଦୀରେ ଗଙ୍ଗବଂଶର ରାଜା ପ୍ରଥମ ନରସିଂହ ଦେବ ନିର୍ମାଣ କରାଇଥିବା "
        "କୋଣାର୍କ ମନ୍ଦିର ସୂର୍ଯ୍ୟଦେବଙ୍କ ବିଶାଳ ରଥ ଆକାରରେ ଗଢ଼ା — ଚବିଶଟି ଖୋଦିତ ପଥର ଚକ "
        "ଓ ସାତଟି ଘୋଡ଼ା। ୧୯୮୪ ମସିହାରେ ଏହା ୟୁନେସ୍କୋ ବିଶ୍ୱ ଐତିହ୍ୟ ସ୍ଥଳୀ ଭାବେ ଘୋଷିତ "
        "ହୋଇଛି।",
        "ପଥରରେ ଗଢ଼ା ସୂର୍ଯ୍ୟଦେବଙ୍କ ରଥ, ଚବିଶ ଚକ ଓ ସାତ ଘୋଡ଼ା।",
        ["UNESCO World Heritage List, Sun Temple, Konârak (246)"],
    ),
    _entry(
        "srimandira", "heritage",
        "Srimandira, Puri", "ଶ୍ରୀମନ୍ଦିର, ପୁରୀ",
        "The present Jagannath temple at Puri was begun in the 12th century under "
        "Anantavarman Chodaganga Deva of the Ganga dynasty. The Nilachakra and "
        "the Patitapabana flag crown its spire, and the flag is changed every "
        "day. At Ananda Bazar, devotees share the Mahaprasad together without "
        "distinction of caste.",
        "ଦ୍ୱାଦଶ ଶତାବ୍ଦୀରେ ଗଙ୍ଗବଂଶର ଅନନ୍ତବର୍ମା ଚୋଡ଼ଗଙ୍ଗ ଦେବଙ୍କ ସମୟରେ ବର୍ତ୍ତମାନର "
        "ଶ୍ରୀମନ୍ଦିର ନିର୍ମାଣ ଆରମ୍ଭ ହୋଇଥିଲା। ମନ୍ଦିର ଶିଖରରେ ନୀଳଚକ୍ର ଓ ପତିତପାବନ ବାନା "
        "ଶୋଭା ପାଏ, ଏବଂ ବାନା ପ୍ରତିଦିନ ବଦଳାଯାଏ। ଆନନ୍ଦବଜାରରେ ଜାତି ଭେଦ ବିନା ସମସ୍ତେ "
        "ଏକାଠି ମହାପ୍ରସାଦ ସେବନ କରନ୍ତି।",
        "ନୀଳଚକ୍ର ଉପରେ ପ୍ରତିଦିନ ନୂଆ ପତିତପାବନ ବାନା।",
        ["Shree Jagannatha Temple Administration, Puri"],
    ),
    _entry(
        "lingaraj", "heritage",
        "Lingaraj and the Temple City", "ଲିଙ୍ଗରାଜ ଓ ମନ୍ଦିରମାଳିନୀ ଭୁବନେଶ୍ୱର",
        "The 11th-century Lingaraj temple is a crowning example of Kalinga "
        "architecture; the deity is worshipped as Harihara, Shiva and Vishnu in "
        "one. With hundreds of ancient temples, Bhubaneswar is called the Temple "
        "City.",
        "ଏକାଦଶ ଶତାବ୍ଦୀର ଲିଙ୍ଗରାଜ ମନ୍ଦିର କଳିଙ୍ଗ ସ୍ଥାପତ୍ୟର ଶ୍ରେଷ୍ଠ ନିଦର୍ଶନ। ଏଠାରେ "
        "ଶିବ ଓ ବିଷ୍ଣୁ ଏକାଠି ହରିହର ରୂପରେ ପୂଜା ପାଆନ୍ତି। ଶହ ଶହ ପ୍ରାଚୀନ ମନ୍ଦିର ପାଇଁ "
        "ଭୁବନେଶ୍ୱରକୁ ମନ୍ଦିରମାଳିନୀ ନଗରୀ କୁହାଯାଏ।",
        "ହରିହର ରୂପରେ ପୂଜା, କଳିଙ୍ଗ ସ୍ଥାପତ୍ୟର ଶିଖର।",
        ["Archaeological Survey of India, Bhubaneswar circle"],
    ),
    _entry(
        "mukteswar", "heritage",
        "Mukteswar Temple", "ମୁକ୍ତେଶ୍ୱର ମନ୍ଦିର",
        "The 10th-century Mukteswar temple is called the gem of Kalinga "
        "architecture. Its arched stone torana is rare in Odisha's temple art. "
        "Every year the Mukteswar Dance Festival is held here.",
        "ଦଶମ ଶତାବ୍ଦୀର ମୁକ୍ତେଶ୍ୱର ମନ୍ଦିରକୁ କଳିଙ୍ଗ ସ୍ଥାପତ୍ୟର ରତ୍ନ କୁହାଯାଏ। ଏହାର "
        "ଖିଲାନ ଆକାରର ପଥର ତୋରଣ ଓଡ଼ିଶାର ମନ୍ଦିର କଳାରେ ବିରଳ। ପ୍ରତିବର୍ଷ ଏଠାରେ "
        "ମୁକ୍ତେଶ୍ୱର ନୃତ୍ୟ ଉତ୍ସବ ହୁଏ।",
        "କଳିଙ୍ଗ ସ୍ଥାପତ୍ୟର ରତ୍ନ, ଅନନ୍ୟ ପଥର ତୋରଣ।",
        ["Archaeological Survey of India, Bhubaneswar circle",
         "Odisha Tourism, Mukteswar Dance Festival"],
    ),
    _entry(
        "chilika", "heritage",
        "Chilika Lake", "ଚିଲିକା ହ୍ରଦ",
        "Chilika is India's largest brackish-water lagoon. Every winter vast "
        "flocks of migratory birds from Central Asia and beyond arrive at "
        "Nalabana. Seeing Irrawaddy dolphins near Satapada is an unforgettable "
        "experience.",
        "ଚିଲିକା ଭାରତର ସବୁଠାରୁ ବଡ଼ ଲୁଣିଆ ପାଣିର ହ୍ରଦ। ପ୍ରତି ଶୀତରେ ମଧ୍ୟ ଏସିଆ ଓ "
        "ଦୂରଦୂରାନ୍ତରୁ ଲକ୍ଷ ଲକ୍ଷ ପ୍ରବାସୀ ପକ୍ଷୀ ନଳବଣକୁ ଆସନ୍ତି। ସାତପଡ଼ା ନିକଟରେ "
        "ଇରାୱାଡ଼ି ଡଲଫିନ ଦେଖିବା ଏକ ଅବିସ୍ମରଣୀୟ ଅନୁଭୂତି।",
        "ପ୍ରବାସୀ ପକ୍ଷୀ ଓ ଇରାୱାଡ଼ି ଡଲଫିନର ଘର ଚିଲିକା।",
        ["Chilika Development Authority", "Ramsar Sites Information Service"],
    ),
    # ── Culture ──────────────────────────────────────────────────────────
    _entry(
        "odissi", "culture",
        "Odissi dance", "ଓଡ଼ିଶୀ ନୃତ୍ୟ",
        "Odissi is one of India's classical dance forms. Its roots lie in the "
        "temple service of the Maharis and the Gotipua tradition. The tribhangi "
        "and chauka postures are its signature — the same poses carved on our "
        "temple walls.",
        "ଓଡ଼ିଶୀ ଭାରତର ଶାସ୍ତ୍ରୀୟ ନୃତ୍ୟମାନଙ୍କ ମଧ୍ୟରୁ ଅନ୍ୟତମ। ଏହାର ମୂଳ ମନ୍ଦିରର "
        "ମାହାରୀ ସେବା ଓ ଗୋଟିପୁଅ ପରମ୍ପରାରେ। ତ୍ରିଭଙ୍ଗୀ ଓ ଚଉକ ଭଙ୍ଗୀ ଏହାର ବିଶେଷତ୍ୱ, "
        "ଯାହା ଆମ ମନ୍ଦିର କାନ୍ଥର ମୂର୍ତ୍ତିରେ ମଧ୍ୟ ଦେଖାଯାଏ।",
        "ମନ୍ଦିର କାନ୍ଥର ମୂର୍ତ୍ତିରୁ ଜୀବନ୍ତ ହୋଇ ଉଠିଥିବା ନୃତ୍ୟ।",
        ["Sangeet Natak Akademi, Odissi"],
    ),
    _entry(
        "gotipua", "culture",
        "Gotipua", "ଗୋଟିପୁଅ ନାଚ",
        "In Gotipua, young boys dressed as girls dance with demanding, "
        "acrobatic poses. This tradition played a big part in the revival of "
        "Odissi. Raghurajpur near Puri is famous for Gotipua.",
        "ଗୋଟିପୁଅ ନାଚରେ ଛୋଟ ପୁଅ ପିଲାମାନେ ଝିଅ ବେଶ ହୋଇ କଠିନ କସରତ ଭରା ଭଙ୍ଗୀରେ "
        "ନାଚନ୍ତି। ଓଡ଼ିଶୀ ନୃତ୍ୟର ପୁନରୁଦ୍ଧାରରେ ଏହି ପରମ୍ପରାର ବଡ଼ ଭୂମିକା ଥିଲା। ପୁରୀ "
        "ନିକଟ ରଘୁରାଜପୁର ଗୋଟିପୁଅ ପାଇଁ ପ୍ରସିଦ୍ଧ।",
        "ଝିଅ ବେଶରେ ପୁଅ ପିଲାଙ୍କ ଚମତ୍କାର ନାଚ।",
        ["Sangeet Natak Akademi, Gotipua"],
    ),
    _entry(
        "pattachitra", "culture",
        "Pattachitra of Raghurajpur", "ରଘୁରାଜପୁରର ପଟ୍ଟଚିତ୍ର",
        "In Raghurajpur near Puri nearly every home is an artist's studio. "
        "Chitrakaras paint Jagannath and Puranic stories on cloth with natural "
        "colours. During Anasara, painted Pattachitra images of the deities are "
        "worshipped in the Srimandira.",
        "ପୁରୀ ନିକଟ ରଘୁରାଜପୁର ଗାଁର ପ୍ରାୟ ପ୍ରତ୍ୟେକ ଘର ଏକ କଳାଶାଳା। ଏଠାରେ "
        "ଚିତ୍ରକାରମାନେ କପଡ଼ା ଉପରେ ପ୍ରାକୃତିକ ରଙ୍ଗରେ ଜଗନ୍ନାଥ ଓ ପୁରାଣ କାହାଣୀ ଆଙ୍କନ୍ତି। "
        "ଅଣସର ସମୟରେ ଶ୍ରୀମନ୍ଦିରରେ ପଟ୍ଟଚିତ୍ରରେ ଅଙ୍କିତ ଅଣସର ପଟି ପୂଜା ପାଏ।",
        "ଘରେ ଘରେ କଳାଶାଳା, ପ୍ରାକୃତିକ ରଙ୍ଗରେ ଜଗନ୍ନାଥ।",
        ["Odisha Tourism, Raghurajpur heritage village",
         "Orissa Pattachitra, Geographical Indication registry"],
    ),
    _entry(
        "sambalpuri_bandha", "culture",
        "Sambalpuri Bandha", "ସମ୍ବଲପୁରୀ ବାନ୍ଧ",
        "The magic of the Sambalpuri saree lies in 'bandha': the threads are "
        "tied and dyed before weaving. So motifs like the conch, wheel and "
        "flower are hidden in the yarn itself and slowly emerge on the loom — a "
        "skill handed down through generations of western Odisha's weavers.",
        "ସମ୍ବଲପୁରୀ ଶାଢ଼ୀର ଅସଲ ଯାଦୁ ବାନ୍ଧ କଳାରେ — ବୁଣିବା ଆଗରୁ ହିଁ ସୂତାକୁ ବାନ୍ଧି ରଙ୍ଗ "
        "କରାଯାଏ। ତେଣୁ ଶଙ୍ଖ, ଚକ୍ର, ଫୁଲ ଭଳି ନକ୍ସା ସୂତାରେ ହିଁ ଲୁଚି ରହିଥାଏ ଏବଂ ତନ୍ତରେ "
        "ଧୀରେ ଧୀରେ ଫୁଟି ଉଠେ। ପଶ୍ଚିମ ଓଡ଼ିଶାର ବୁଣାକାରଙ୍କ ପିଢ଼ି ପିଢ଼ିର ଦକ୍ଷତା ଏହା।",
        "ବୁଣିବା ଆଗରୁ ସୂତାରେ ଲୁଚି ରହେ ନକ୍ସା।",
        ["Sambalpuri Bandha Saree and Fabrics, Geographical Indication registry"],
    ),
    _entry(
        "pipili", "culture",
        "Pipili appliqué", "ପିପିଲିର ଚାନ୍ଦୁଆ କାମ",
        "In Pipili's colourful appliqué work, cut pieces of cloth are stitched "
        "onto a base cloth to make designs. The craft grew around the canopies, "
        "umbrellas and chariot decorations of Jagannath's festivals.",
        "ପିପିଲିର ରଙ୍ଗବେରଙ୍ଗ ଚାନ୍ଦୁଆ କାମରେ ରଙ୍ଗୀନ କପଡ଼ା କାଟି ଅନ୍ୟ କପଡ଼ା ଉପରେ "
        "ସିଲେଇ କରି ନକ୍ସା ତିଆରି ହୁଏ। ମହାପ୍ରଭୁଙ୍କ ଯାତ୍ରାର ଛତା, ଚାନ୍ଦୁଆ ଓ ରଥ ସଜ୍ଜାକୁ "
        "ନେଇ ଏହି କଳା ବିକଶିତ ହୋଇଛି।",
        "ମହାପ୍ରଭୁଙ୍କ ଛତା ଓ ଚାନ୍ଦୁଆରୁ ଜନ୍ମିତ କଳା।",
        ["Odisha Tourism, Pipili",
         "Pipli Applique Work, Geographical Indication registry"],
    ),
    _entry(
        "bali_jatra", "culture",
        "Bali Jatra and the Sadhabas", "ବାଲିଯାତ୍ରା ଓ ସାଧବ",
        "In ancient times the Sadhaba merchants of Kalinga sailed in boitas to "
        "Bali, Java, Sumatra and Sri Lanka to trade. Remembering that glory, on "
        "Kartika Purnima people float little boats on rivers and ponds, singing "
        "'A Ka Ma Bai'. On the Mahanadi bank at Cuttack the great Bali Jatra fair "
        "is held.",
        "ପ୍ରାଚୀନ କାଳରେ କଳିଙ୍ଗର ସାଧବମାନେ ବୋଇତରେ ବାଲି, ଜାଭା, ସୁମାତ୍ରା ଓ ଶ୍ରୀଲଙ୍କା ଯାଇ "
        "ବାଣିଜ୍ୟ କରୁଥିଲେ। ସେହି ଗୌରବ ମନେ ପକାଇ କାର୍ତ୍ତିକ ପୂର୍ଣ୍ଣିମାରେ ଲୋକେ 'ଆ କା ମା ବୈ' "
        "ଗାଇ ନଦୀ ଓ ପୋଖରୀରେ ଛୋଟ ଡଙ୍ଗା ଭସାନ୍ତି। କଟକର ମହାନଦୀ କୂଳରେ ବିଶାଳ ବାଲିଯାତ୍ରା "
        "ମେଳା ବସେ।",
        "ଆ କା ମା ବୈ, ସାଧବଙ୍କ ସମୁଦ୍ର ଯାତ୍ରାର ସ୍ମୃତି।",
        ["Odisha Tourism, Bali Jatra",
         "Odisha Review, Kalinga maritime trade articles"],
    ),
    _entry(
        "raja_parba", "culture",
        "Raja Parba", "ରଜ ପର୍ବ",
        "Raja is celebrated over three days around Mithuna Sankranti, when "
        "Mother Earth is believed to rest in her menstrual cycle. Farm work "
        "stops; girls wear new clothes, play on swings and eat poda pitha. It is "
        "a unique festival honouring womanhood and fertility.",
        "ମିଥୁନ ସଂକ୍ରାନ୍ତି ଆଗପଛ ତିନି ଦିନ ପାଳିତ ରଜ ପର୍ବରେ ଧରିତ୍ରୀ ମାତା ରଜସ୍ୱଳା "
        "ହୁଅନ୍ତି ବୋଲି ବିଶ୍ୱାସ। ଏହି ସମୟରେ ଚାଷ କାମ ବନ୍ଦ ରହେ; ଝିଅମାନେ ନୂଆ ଲୁଗା ପିନ୍ଧି "
        "ଦୋଳି ଖେଳନ୍ତି ଓ ପୋଡ଼ପିଠା ଖାଆନ୍ତି। ନାରୀତ୍ୱ ଓ ଉର୍ବରତାକୁ ସମ୍ମାନ ଦେଉଥିବା ଏହା ଏକ "
        "ଅନନ୍ୟ ପର୍ବ।",
        "ଦୋଳି, ପୋଡ଼ପିଠା ଓ ଧରିତ୍ରୀ ମାଆଙ୍କ ସମ୍ମାନ।",
        ["Odisha Tourism, Raja Parba"],
    ),
    _entry(
        "nuakhai", "culture",
        "Nuakhai", "ନୂଆଖାଇ",
        "At Nuakhai, the biggest festival of western Odisha, the first rice of "
        "the new harvest is offered to Maa Samaleswari. Then the family eats the "
        "'nabanna' together and greets elders with 'Nuakhai Juhar'. People living "
        "far away try to come home for this day.",
        "ପଶ୍ଚିମ ଓଡ଼ିଶାର ସବୁଠାରୁ ବଡ଼ ପର୍ବ ନୂଆଖାଇରେ ନୂଆ ଧାନର ଅନ୍ନ ପ୍ରଥମେ ମା "
        "ସମଲେଶ୍ୱରୀଙ୍କୁ ଅର୍ପଣ କରାଯାଏ। ତାପରେ ପରିବାର ଏକାଠି ବସି ନବାନ୍ନ ଗ୍ରହଣ କରେ ଏବଂ "
        "ବଡ଼ମାନଙ୍କୁ ନୂଆଖାଇ ଜୁହାର ଜଣାଏ। ଦୂରରେ ରହୁଥିବା ଲୋକେ ବି ଏହି ଦିନ ଘରକୁ ଫେରିବାକୁ "
        "ଚେଷ୍ଟା କରନ୍ତି।",
        "ନୂଆ ଧାନ, ନବାନ୍ନ ଓ ନୂଆଖାଇ ଜୁହାର।",
        ["Odisha Tourism, Nuakhai"],
    ),
    _entry(
        "rasagola", "culture",
        "Odisha Rasagola", "ଓଡ଼ିଶା ରସଗୋଲା",
        "By tradition, on Niladri Bije at the end of Rath Yatra, Lord Jagannath "
        "offers rasagola to placate the upset Maa Lakshmi. The rasagola of Pahala "
        "is famous across the state. In 2019 'Odisha Rasagola' received a "
        "Geographical Indication tag.",
        "ପରମ୍ପରା ଅନୁସାରେ ରଥଯାତ୍ରା ଶେଷରେ ନୀଳାଦ୍ରି ବିଜେ ଦିନ ମହାପ୍ରଭୁ ରୁଷିଥିବା ମା "
        "ଲକ୍ଷ୍ମୀଙ୍କୁ ରସଗୋଲା ଦେଇ ମନାନ୍ତି। ପାହାଳର ରସଗୋଲା ସାରା ରାଜ୍ୟରେ ପ୍ରସିଦ୍ଧ। ୨୦୧୯ "
        "ମସିହାରେ ଓଡ଼ିଶା ରସଗୋଲା ଭୌଗୋଳିକ ସୂଚକ ସ୍ୱୀକୃତି ପାଇଛି।",
        "ମା ଲକ୍ଷ୍ମୀଙ୍କ ରାଗ ଭାଙ୍ଗିବା ମିଠା, ୨୦୧୯ରେ ଜିଆଇ ସ୍ୱୀକୃତି।",
        ["Odisha Rasagola, Geographical Indication registry (2019)"],
    ),
    _entry(
        "mayurbhanj_chhau", "culture",
        "Mayurbhanj Chhau", "ମୟୂରଭଞ୍ଜ ଛଉ",
        "Mayurbhanj Chhau is a powerful dance born from martial practice. Unlike "
        "the Purulia and Seraikela forms, Mayurbhanj Chhau dancers do not wear "
        "masks. In 2010 Chhau dance was inscribed on UNESCO's list of the "
        "Intangible Cultural Heritage of Humanity.",
        "ମୟୂରଭଞ୍ଜ ଛଉ ଯୁଦ୍ଧକଳାରୁ ଜନ୍ମ ନେଇଥିବା ଏକ ଶକ୍ତିଶାଳୀ ନୃତ୍ୟ। ପୁରୁଲିଆ ଓ "
        "ସରାଇକେଲା ଛଉ ଭଳି ନୁହେଁ, ମୟୂରଭଞ୍ଜ ଛଉରେ ନର୍ତ୍ତକମାନେ ମୁଖା ପିନ୍ଧନ୍ତି ନାହିଁ। ୨୦୧୦ "
        "ମସିହାରେ ଛଉ ନୃତ୍ୟ ୟୁନେସ୍କୋର ଅମୂର୍ତ୍ତ ସାଂସ୍କୃତିକ ଐତିହ୍ୟ ତାଲିକାରେ ସ୍ଥାନ ପାଇଛି।",
        "ମୁଖା ବିନା ଯୁଦ୍ଧକଳାର ନୃତ୍ୟ, ୟୁନେସ୍କୋ ସ୍ୱୀକୃତ।",
        ["UNESCO Intangible Cultural Heritage, Chhau dance (2010)"],
    ),
]


def _spread(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order entries so each category is spread evenly across the cycle
    (item i of n in a category sits at position (i + 0.5) / n)."""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        buckets.setdefault(e["category"], []).append(e)
    cat_rank = {c: i for i, c in enumerate(CATEGORIES)}
    placed = [
        ((i + 0.5) / len(items), cat_rank[cat], e)
        for cat, items in buckets.items()
        for i, e in enumerate(items)
    ]
    placed.sort(key=lambda t: (t[0], t[1]))
    return [e for _, _, e in placed]


_ROTATION = _spread(HERITAGE)
_BY_ANNIVERSARY = {e["anniversary"]: e for e in HERITAGE if e["anniversary"]}
assert len({e["key"] for e in HERITAGE}) == len(HERITAGE), "duplicate heritage key"
assert len(_BY_ANNIVERSARY) == sum(1 for e in HERITAGE if e["anniversary"]), (
    "two heritage entries share an anniversary"
)


# Festival name_en (festivals.py) → heritage key. Each pick *adds* to the
# festival's own curated story rather than repeating it — e.g. Salabega on
# Rath Yatra, not a second Rath Yatra retelling.
FESTIVAL_HERITAGE: dict[str, str] = {
    "Rath Yatra": "salabega",
    "Snana Yatra": "pattachitra",
    "Snana Purnima": "pattachitra",
    "Niladri Bije": "srimandira",
    "Pana Sankranti (Odia New Year)": "classical_odia",
    "Maha Shivaratri": "lingaraj",
    "Lingaraj Maha Shivaratri": "lingaraj",
    "Ashokastami — Rukuna Rath Yatra": "lingaraj",
    "Vasanta Panchami / Saraswati Puja": "madhusudan_rao",
    "Dola Purnima": "gita_govinda",
    "Nuakhai": "sambalpuri_bandha",
    "Rama Navami": "upendra_bhanja",
    "Janmashtami": "jagannatha_dasa",
    "Buddha Purnima": "kalinga_war",
}
_BY_KEY = {e["key"]: e for e in HERITAGE}
assert set(FESTIVAL_HERITAGE.values()) <= set(_BY_KEY), "unknown heritage key in FESTIVAL_HERITAGE"


def festival_names(festivals: list[dict] | None) -> list[str]:
    """English festival names from API-shaped or ORM-shaped festival dicts."""
    names = []
    for f in festivals or []:
        name = f.get("name_en") or (f.get("name") or {}).get("en") or ""
        if name:
            names.append(name)
    return names


def _festival_names_on(day: date) -> list[str]:
    """Festivals for a day from the local SQLite store (for tomorrow's
    teaser). Missing DB/row just means no festival match — never an error."""
    try:
        from src.festival_audit import is_verified
        from src.local_day import load_panchang_day

        names = festival_names(load_panchang_day(day).get("festivals"))
        # same verified set tomorrow's post will announce (publication gate)
        return [n for n in names if is_verified(n, day.isoformat())]
    except Exception:  # noqa: BLE001 — teaser falls back to plain rotation
        return []


def heritage_for_date(day: date | str, festivals: list[str] | None = None) -> dict[str, Any]:
    """The day's entry, with `is_anniversary` set when it is a jayanti/divas.

    `festivals` are the day's festival name_en values; None looks them up in
    the local DB (used for tomorrow's teaser)."""
    if isinstance(day, str):
        day = date.fromisoformat(day)
    hit = _BY_ANNIVERSARY.get(day.strftime("%m-%d"))
    if hit:
        return {**hit, "is_anniversary": True}
    if festivals is None:
        festivals = _festival_names_on(day)
    for name in festivals:
        key = FESTIVAL_HERITAGE.get(name)
        if key:
            return {**_BY_KEY[key], "is_anniversary": False}
    entry = _ROTATION[day.toordinal() % len(_ROTATION)]
    return {**entry, "is_anniversary": False}


def heritage_label_or(entry: dict[str, Any]) -> str:
    """Small label above the title: 'ଆଜି ଜୟନ୍ତୀ' on the day, else the category."""
    if entry.get("is_anniversary"):
        return entry["anniversary_or"]
    return CATEGORIES[entry["category"]]["or"]


def tomorrow_heritage(day: date | str) -> dict[str, Any]:
    if isinstance(day, str):
        day = date.fromisoformat(day)
    return heritage_for_date(day + timedelta(days=1))


def heritage_caption_block(day: date | str, festivals: list[str] | None = None) -> str:
    """Caption section for Facebook/Instagram: story + tomorrow's teaser."""
    if isinstance(day, str):
        day = date.fromisoformat(day)
    entry = heritage_for_date(day, festivals)
    tomorrow = tomorrow_heritage(day)
    emoji = CATEGORIES[entry["category"]]["emoji"]
    lines = [
        f"✨ {SERIES_OR} | {heritage_label_or(entry)}",
        f"{emoji} {entry['title']['or']}",
        entry["body"]["or"],
        "💬 ଏ ବିଷୟରେ ଆପଣ ଆଉ କିଛି ଜାଣିଥିଲେ କମେଣ୍ଟରେ ଲେଖନ୍ତୁ।",
        f"👉 ଆସନ୍ତାକାଲି: {tomorrow['title']['or']} — ଫଲୋ କରନ୍ତୁ, ପ୍ରତିଦିନ ଓଡ଼ିଶାକୁ ନୂଆ କରି ଜାଣନ୍ତୁ।",
    ]
    return "\n".join(lines)


def heritage_hashtags(day: date | str, festivals: list[str] | None = None) -> str:
    entry = heritage_for_date(day, festivals)
    return f"{SERIES_TAG} {CATEGORIES[entry['category']]['tag']}"


def validate_all_heritage() -> list[str]:
    """Re-run script checks (import already validated; kept for CI parity
    with `validate_all_stories`)."""
    errors: list[str] = []
    for e in HERITAGE:
        for field, text in (
            ("title", e["title"]["or"]),
            ("body", e["body"]["or"]),
            ("short", e["short_or"]),
        ):
            try:
                validate_odia_text(text, field=f"{e['key']}.{field}")
            except ValueError as exc:
                errors.append(str(exc))
        if not e["sources"]:
            errors.append(f"{e['key']}: no sources")
    return errors
