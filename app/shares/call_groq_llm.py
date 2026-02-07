import time
import re
from groq import Groq
from app.core.llm.groq_client import client

# ==============================
# Simple rate limiting
# ==============================
_last_api_call = 0
_min_interval = 1  # Groq has good rate limits; 1s is enough


def simple_context_answer(
    user_query: str,
    context_chunks: list[str],
) -> str:
    """
    Simple fallback when LLM API is unavailable.
    Extracts relevant information from context based on query keywords.
    Responds as the person (first person).
    """

    context_text = " ".join(context_chunks).lower()
    query_lower = user_query.lower()

    # ------------------------------
    # Name extraction
    # ------------------------------
    if any(word in query_lower for word in ["name", "who", "introduce"]):
        name_patterns = [
            r"i'm ([^,\.!?]+)",
            r"i am ([^,\.!?]+)",
            r"my name is ([^,\.!?]+)",
            r"name is ([^,\.!?]+)",
            r"called ([^,\.!?]+)",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, context_text)
            if match:
                name = match.group(1).strip()
                return f"I am {name.title()}."

    # ------------------------------
    # Age-related queries
    # ------------------------------
    if any(word in query_lower for word in ["age", "old", "born", "birth"]):
        age_patterns = [
            r"(\d+)\s*years?\s*old",
            r"age\s*(?:is|:)?\s*(\d+)",
            r"born\s*in\s*(\d{4})",
        ]

        for pattern in age_patterns:
            match = re.search(pattern, context_text)
            if match:
                if "born" in pattern:
                    birth_year = int(match.group(1))
                    current_year = 2024
                    age = current_year - birth_year
                    return (
                        f"I was born in {birth_year}, "
                        f"so I'm approximately {age} years old."
                    )
                return f"I am {match.group(1)} years old."

        return (
            "I don't have my age information available right now, "
            "but I can share other details about myself."
        )

    # ------------------------------
    # Education queries
    # ------------------------------
    if any(
        word in query_lower
        for word in ["education", "degree", "college", "qualification", "study", "university"]
    ):
        if any(
            edu_word in context_text
            for edu_word in ["degree", "college", "university", "education", "graduated"]
        ):
            return (
                "I do have educational background information. "
                "Let me know what specific details you'd like to know."
            )

    # ------------------------------
    # Skills queries
    # ------------------------------
    if any(
        word in query_lower
        for word in ["skill", "technology", "tech", "programming", "development"]
    ):
        if any(
            skill_word in context_text
            for skill_word in ["developer", "programming", "technology", "skill"]
        ):
            return (
                "I have experience with various technologies and skills. "
                "I'd be happy to share more about my technical background."
            )

    # ------------------------------
    # Default response
    # ------------------------------
    return (
        "I don't have that specific information available right now, "
        "but feel free to ask about other aspects of my background."
    )


def call_groq_llm(
    user_query: str,
    context_chunks: list[str],
    max_retries: int = 3,
    retry_delay: int = 2,
) -> str:
    """
    Calls Groq API for chat completion with retry logic.
    Falls back to context-based response if API fails.
    """

    global _last_api_call

    # ------------------------------
    # Rate limiting
    # ------------------------------
    current_time = time.time()
    time_since_last = current_time - _last_api_call

    if time_since_last < _min_interval:
        sleep_time = _min_interval - time_since_last
        time.sleep(sleep_time)

    _last_api_call = time.time()

    # ------------------------------
    # Combine context
    # ------------------------------
    context_text = "\n\n".join(context_chunks)

    # ------------------------------
    # Build chat messages
    # ------------------------------
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that responds AS the person whose "
                "profile information is provided in the context. "
                "Use first-person language (I, me, my).\n\n"
                "Rules:\n"
                "- Answer only using the context\n"
                "- Do not invent information\n"
                "- Be natural and concise (2–4 sentences)\n"
                "- If info is missing, say so politely\n\n"
                "Example:\n"
                "Say 'I am Ankit Kumar Pandey' instead of "
                "'This person is Ankit Kumar Pandey'."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Context information:\n{context_text}\n\n"
                f"User Question: {user_query}\n\n"
                "Please provide a helpful response:"
            ),
        },
    ]

    # ------------------------------
    # Models to try
    # ------------------------------
    models_to_try = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]

    # ------------------------------
    # Retry logic
    # ------------------------------
    for attempt in range(1, max_retries + 1):
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=800,
                    top_p=1,
                    stream=False,
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                error_msg = str(e).lower()

                if "rate limit" in error_msg or "429" in error_msg:
                    wait_time = retry_delay * attempt
                    if attempt < max_retries:
                        time.sleep(wait_time)
                        break
                    return simple_context_answer(user_query, context_chunks)

                if "model" in error_msg and "not found" in error_msg:
                    continue

                continue

    # ------------------------------
    # Final fallback
    # ------------------------------
    return simple_context_answer(user_query, context_chunks)
