"""
Text normalisation utility: collapses extra whitespace.
"""


def normalize_text(text: str) -> str:
    """
    Strip leading/trailing whitespace and collapse internal whitespace to single spaces.

    Args:
        text: Raw text string.

    Returns:
        Normalised text string.
    """
    return " ".join(text.strip().split())
