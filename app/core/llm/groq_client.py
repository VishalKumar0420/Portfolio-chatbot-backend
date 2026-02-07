import os
from groq import Groq
from app.core.config.setting import settings

GROQ_API_KEY = settings.GROQ_API_KEY

if not GROQ_API_KEY:
    raise RuntimeError(
        "❌ GROQ_API_KEY not found in environment variables. Please set GROQ_API_KEY in your .env file"
    )

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    raise RuntimeError(f"❌ Failed to initialize Groq client: {e}")
