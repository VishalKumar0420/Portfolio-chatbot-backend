"""
Section detection utility: infers which resume sections a query targets.
"""

from data import SECTION_KEYWORDS


def detect_sections(query: str) -> list[str]:
    """
    Match a preprocessed query against known section keywords.

    Args:
        query: Lowercased, normalised query string.

    Returns:
        List of section names (e.g. ['SKILLS', 'EXPERIENCE']) that match
        keywords found in the query. Empty list if no match.
    """
    query = query.lower()
    matched_sections = []

    for section, keywords in SECTION_KEYWORDS.items():
        if any(k in query for k in keywords):
            matched_sections.append(section)

    return matched_sections
