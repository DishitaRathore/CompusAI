import re

from rapidfuzz import fuzz, process


DOMAIN_WORDS = [
    "attendance",
    "fees",
    "fee",
    "ticket",
    "phishing",
    "security",
    "policy",
    "history",
    "password",
    "privacy",
    "course",
    "payment",
    "department",
    "timetable",
    "announcement",
]


COMMON_TYPOS = {
    "attendence": "attendance",
    "atendance": "attendance",
    "attandance": "attendance",
    "feees": "fees",
    "fess": "fees",
    "phising": "phishing",
    "pishing": "phishing",
    "tikcet": "ticket",
    "ticet": "ticket",
    "polciy": "policy",
    "polcy": "policy",
    "histroy": "history",
    "hisory": "history",
    "passwrod": "password",
    "privcy": "privacy",
}


def normalize_query(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)

    words = []

    for word in text.split():
        clean_word = re.sub(r"[^a-z0-9]", "", word)

        if clean_word in COMMON_TYPOS:
            corrected_word = COMMON_TYPOS[clean_word]

        elif len(clean_word) >= 4:
            match = process.extractOne(
                clean_word,
                DOMAIN_WORDS,
                scorer=fuzz.ratio,
                score_cutoff=88
            )

            if match:
                corrected_word = match[0]
            else:
                corrected_word = clean_word

        else:
            corrected_word = clean_word

        words.append(corrected_word)

    return " ".join(words)