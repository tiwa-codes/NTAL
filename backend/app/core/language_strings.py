"""Language strings for USSD interface.
Keeping messages concise (≤160 characters) for USSD compatibility.
"""

LANGUAGES = {
    "en": {
        "consent": "Welcome to NTAL Health! We'll ask about symptoms. Your data is private. Do you consent?\n1. Yes\n2. No",
        "consent_declined": "Thank you. Call us at 0800-HEALTH for assistance.",
        "language": "Choose language:\n1. English\n2. Yoruba",
        "age_group": "Select age group:\n1. Under 5\n2. 5-17 years\n3. 18-49 years\n4. 50+ years",
        "gender": "Select gender:\n1. Male\n2. Female\n3. Other",
        "fever": "Do you have fever?\n1. Yes\n2. No",
        "severe_headache": "Do you have severe headache?\n1. Yes\n2. No",
        "danger_sign": "Any of these: difficulty breathing, chest pain, confusion, severe bleeding?\n1. Yes\n2. No",
        "cough": "Do you have cough?\n1. Yes\n2. No",
        "emergency": "EMERGENCY: Go to nearest clinic NOW or call ambulance. Request callback?\n1. Yes\n2. No",
        "malaria_suspect": "Possible malaria. Visit health center soon. Request callback?\n1. Yes\n2. No",
        "fever_general": "Monitor symptoms. Visit clinic if persists. Request callback?\n1. Yes\n2. No",
        "low_risk": "Low risk. Rest and monitor. Request callback?\n1. Yes\n2. No",
        "callback_queued": "Callback requested. Provider will call soon. Stay safe!",
        "goodbye": "Thank you. Stay healthy!",
        "invalid_input": "Invalid input. Please try again.",
        "rate_limit": "Limit reached. Try again tomorrow.",
    },
    "yo": {  # Yoruba
        "consent": "Kaabo si NTAL Health! A o beere nipa aisan. Data re wa ni aabo. Se o gba?\n1. Beeni\n2. Rara",
        "consent_declined": "O se. Pe wa ni 0800-HEALTH fun iranlowo.",
        "language": "Yan ede:\n1. English\n2. Yoruba",
        "age_group": "Yan ojo ori:\n1. O din 5\n2. 5-17\n3. 18-49\n4. 50+",
        "gender": "Yan abo/ako:\n1. Okunrin\n2. Obinrin\n3. Omiran",
        "fever": "Nje o ni iba?\n1. Beeni\n2. Rara",
        "severe_headache": "Nje ori nfo e pupoju?\n1. Beeni\n2. Rara",
        "danger_sign": "Nje o ni wahala mimi, okan dun, idamu, tabi eje njade pupoju?\n1. Beeni\n2. Rara",
        "cough": "Nje o ni iko?\n1. Beeni\n2. Rara",
        "emergency": "PAJAWIRI: Lo si ile iwosan tabi pe ambulance. Request callback?\n1. Beeni\n2. Rara",
        "malaria_suspect": "O le je iba. Lo si ile iwosan laipe. Request callback?\n1. Beeni\n2. Rara",
        "fever_general": "Wo aisan na. Lo si ile iwosan ti o ba tesi. Request callback?\n1. Beeni\n2. Rara",
        "low_risk": "Ewu kekere. Sinmi ki o wo. Request callback?\n1. Beeni\n2. Rara",
        "callback_queued": "A o pe o laipe. Duro ni aabo!",
        "goodbye": "O se. Wa ni ilera!",
        "invalid_input": "Idahun ko tọ. Gbiyanju lẹẹkansi.",
        "rate_limit": "O ti po ju. Gbiyanju lọla.",
    }
}


def get_message(language: str, key: str) -> str:
    """Get localized message, fallback to English if not found."""
    lang = LANGUAGES.get(language, LANGUAGES["en"])
    return lang.get(key, LANGUAGES["en"].get(key, f"Message not found: {key}"))
