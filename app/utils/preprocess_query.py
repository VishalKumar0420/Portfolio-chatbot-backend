"""
Query preprocessing utility: lowercase and normalise whitespace.
"""


def preprocess_query(query: str) -> str:
    """
    Lowercase and collapse whitespace in a search query.

    Args:
        query: Raw user query string.

    Returns:
        Cleaned query string ready for vector search.
    """
    return " ".join(query.lower().strip().split())
