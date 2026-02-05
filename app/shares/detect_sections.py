from data import SECTION_KEYWORDS
def detect_sections(query: str) -> list[str]:

    query = query.lower()
    matched_sections = []

    for section, keywords in SECTION_KEYWORDS.items():
        if any(k in query for k in keywords):
            matched_sections.append(section)

    return matched_sections