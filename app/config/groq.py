"""
Groq LLM client — singleton initialised at import time.

Raises RuntimeError on startup if GROQ_API_KEY is missing so
misconfiguration is caught before the first request.
"""

from groq import Groq

from app.config.settings import get_settings

_settings = get_settings()

if not _settings.GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured. Add it to your .env file.")

try:
    groq_client = Groq(api_key=_settings.GROQ_API_KEY)
except Exception as exc:
    raise RuntimeError(f"Failed to initialise Groq client: {exc}")
