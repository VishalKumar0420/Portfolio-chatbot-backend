def split_large_section(text: str):
    return [p.strip() for p in text.split("\n\n") if p.strip()]