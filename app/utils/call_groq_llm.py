"""
Groq LLM utility: send a query + context to the Groq API and return an answer.

Includes simple rate limiting, model fallback, and a keyword-based fallback
for when the API is unavailable.
"""

import re
import time

from app.config.groq import groq_client

# Minimum seconds between consecutive Groq API calls
_MIN_INTERVAL = 1.0
_last_api_call: float = 0

# Models tried in order; falls back to the next if one is unavailable
_MODELS = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]


def _context_fallback(query: str, context_chunks: list[str]) -> str:
    """
    Keyword-based fallback when the Groq API is unavailable.

    Scans context for patterns related to the query and returns a
    first-person response. Returns a generic message if nothing matches.
    """
    context = " ".join(context_chunks).lower()
    q = query.lower()

    if any(w in q for w in ("name", "who", "introduce")):
        for pattern in (r"i'm ([^,\.!?]+)", r"i am ([^,\.!?]+)", r"my name is ([^,\.!?]+)"):
            m = re.search(pattern, context)
            if m:
                return f"I am {m.group(1).strip().title()}."

    if any(w in q for w in ("age", "old", "born", "birth")):
        for pattern in (r"(\d+)\s*years?\s*old", r"born\s*in\s*(\d{4})"):
            m = re.search(pattern, context)
            if m:
                if "born" in pattern:
                    age = 2024 - int(m.group(1))
                    return f"I was born in {m.group(1)}, so I'm approximately {age} years old."
                return f"I am {m.group(1)} years old."

    if any(w in q for w in ("education", "degree", "college", "university")):
        return "I have educational background information. What specific details would you like to know?"

    if any(w in q for w in ("skill", "technology", "programming")):
        return "I have experience with various technologies. Feel free to ask about my technical background."

    return "I don't have that specific information available right now. Feel free to ask about other aspects of my background."


def call_groq_llm(
    query: str,
    context_chunks: list[str],
    max_retries: int = 3,
    retry_delay: int = 2,
) -> str:
    """
    Call the Groq chat completion API with the user query and context.

    The LLM responds in first person using only the provided context.
    Falls back to _context_fallback on repeated failure.

    Args:
        query: The user's question.
        context_chunks: Relevant text chunks from the vector store.
        max_retries: Number of retry attempts on rate-limit errors.
        retry_delay: Base delay (seconds) between retries.

    Returns:
        A natural-language answer string.
    """
    global _last_api_call

    # Enforce minimum interval between calls
    elapsed = time.time() - _last_api_call
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_api_call = time.time()

    context_text = "\n\n".join(context_chunks)

    messages = [
        {
            "role": "system",
            "content": (
                 "You are an AI assistant that responds AS the person whose profile "
    "information is provided in the context. Use first-person language (I, me, my).\n\n"
    
    "Formatting Rules:\n"
    "- Always format response in Markdown\n"
    "- Use bullet points for lists\n"
    "- Use **bold** for important info\n"
    "- Keep response clean and readable\n"
    "- Do not use HTML tags\n\n"

    "Other Rules:\n"
    "- Answer only using the provided context\n"
    "- Do not invent information\n"
    "- Be natural and concise\n"
    "- If info missing, say politely"
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nQuestion: {query}",
        },
    ]

    for attempt in range(1, max_retries + 1):
        for model in _MODELS:
            try:
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=800,
                    stream=False,
                )
                return response.choices[0].message.content.strip()

            except Exception as exc:
                err = str(exc).lower()
                if "rate limit" in err or "429" in err:
                    if attempt < max_retries:
                        time.sleep(retry_delay * attempt)
                    break
                continue  # try next model

    return _context_fallback(query, context_chunks)
