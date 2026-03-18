"""
Chat service: DB persistence and vector store indexing for chat sessions.
"""

import logging
import uuid

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.pinecone import get_vectorstore
from app.modules.chat.model import Chat
from app.utils.call_groq_llm import call_groq_llm
from app.utils.detect_sections import detect_sections
from app.utils.normalize_text import normalize_text
from app.utils.preprocess_query import preprocess_query
from data import TOP_K, VECTOR_K,SEARCH_FALL_BACK_ANSWER
from collections import defaultdict
logger = logging.getLogger(__name__)


def save_chat(
    db: Session,
    chat_id: str,
    user_id: str,
    chat_name: str,
    content: BaseModel,
) -> None:
    """
    Insert or update a chat record in the database.

    If a chat with the given chat_id already exists, its name and content
    are updated in place. Otherwise a new record is created.

    Raises:
        HTTPException 500: On any database error.
    """
    try:
        chat_uuid = uuid.UUID(chat_id)

        existing = db.query(Chat).filter(Chat.chat_id == chat_uuid).first()

        if existing:
            existing.chat_name = chat_name
            existing.chat_content = content.model_dump()
        else:
            db.add(
                Chat(
                    chat_id=chat_uuid,
                    user_id=user_id,
                    chat_name=chat_name,
                    chat_content= content.model_dump(),
                )
            )

        db.commit()

    except Exception:
        db.rollback()
        logger.exception("Failed to save chat %s to database", chat_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store chat",
        )


def delete_chat_vectors(chat_id: str) -> None:
    """
    Remove all Pinecone vectors associated with the given chat_id.

    Errors are logged but not re-raised so callers can continue safely.
    """
    try:
        vectorstore = get_vectorstore()
        vectorstore._index.delete(filter={"chat_id": chat_id})
    except Exception:
        logger.exception("Failed to delete vectors for chat %s", chat_id)


def index_chat_content(chat_id: str, content: BaseModel) -> None:
    """
    Index resume content into the Pinecone vector store.

    Clears existing vectors for the chat_id first to avoid duplicates,
    then upserts all non-empty sections as text chunks.

    Args:
        chat_id: Unique identifier for the chat session.
        content: ResumeData instance whose fields map to resume sections.
    """
    vectorstore = get_vectorstore()

    if isinstance(content, BaseModel):
        content = content.model_dump()

    delete_chat_vectors(chat_id)

    texts, metadatas, ids = [], [], []

    for section, value in content.items():
        if not value:
            continue

        # 🔹 STRING
        if isinstance(value, str):
            texts.append(normalize_text(value))
            ids.append(f"{chat_id}_{section}_0")
            metadatas.append({"chat_id": chat_id, "section": section})

        # 🔹 LIST
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                if isinstance(item, str):
                    texts.append(normalize_text(item))
                    ids.append(f"{chat_id}_{section}_{idx}")
                    metadatas.append({"chat_id": chat_id, "section": section, "index": idx})

                elif isinstance(item, (dict, BaseModel)):
                    item_dict = (
                        item.model_dump(exclude_none=True)
                        if isinstance(item, BaseModel)
                        else item
                    )

                    text = " ".join(
                        f"{k}: {v}"
                        for k, v in item_dict.items()
                        if isinstance(v, (str, int, bool))
                    )

                    if not text.strip():
                        continue

                    texts.append(normalize_text(text))
                    ids.append(f"{chat_id}_{section}_{idx}")
                    metadatas.append({"chat_id": chat_id, "section": section, "index": idx})

    
        elif isinstance(value, dict):
            for key, val in value.items():
                if not val:
                    continue

                text = f"{key}: {val}"

                texts.append(normalize_text(text))
                ids.append(f"{chat_id}_{section}_{key}")
                metadatas.append({
                    "chat_id": chat_id,
                    "section": section,
                    "field": key
                })
    if texts:
        vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)


def search_chat(chat_id: str, query: str) -> dict:
    """
    Semantic search over the chat's indexed content, answered by the LLM.

    Steps:
      1. Preprocess the query.
      2. Infer relevant resume sections from the query.
      3. Run vector similarity search filtered by chat_id.
      4. Boost scores for section-matched results.
      5. Deduplicate and pick top-K chunks.
      6. Pass chunks to Groq LLM for a natural-language answer.

    Returns:
        dict with 'answer' (str) and 'context' (list[str]).
    """
    vectorstore = get_vectorstore()
    processed_query_text = preprocess_query(query)
    inferred_sections = detect_sections(processed_query_text)
    metadata_filter = {"chat_id": chat_id}
    if inferred_sections:
        # If vector DB supports $in operator
        metadata_filter["section"] = {"$in": inferred_sections}

    results = vectorstore.similarity_search_with_score(
        query=processed_query_text,
        k=VECTOR_K,
        filter=metadata_filter
    )
    if not results:
        return {
            "answer":SEARCH_FALL_BACK_ANSWER
        }

    # Boost scores for results whose section matches the inferred intent
    grouped = group_results_by_section(results)
    context_chunks = build_context_chunks(grouped)
    answer = call_groq_llm(query, context_chunks)
    return {
        "answer": answer,
    }



def group_results_by_section(results):
    grouped = defaultdict(list)

    for doc, score in results:
        section = doc.metadata.get("section")
        grouped[section].append({
            "text": doc.page_content,
            "score": score,
            "index": doc.metadata.get("index")
        })

    return grouped


def build_context_chunks(grouped_results):
    context_chunks = []

    def sort_by_score(items):
        return sorted(items, key=lambda x: x["score"], reverse=True)

    # 🔹 ABOUT ME
    if "aboutMe" in grouped_results:
        about = sort_by_score(grouped_results["aboutMe"])
        context_chunks.append(
            "ABOUT ME:\n" + about[0]["text"]
        )

    # 🔹 SKILLS
    if "skills" in grouped_results:
        skills = sort_by_score(grouped_results["skills"])
        skill_list = [s["text"] for s in skills]
        context_chunks.append(
            "SKILLS:\n" + ", ".join(skill_list)
        )

    # 🔹 EXPERIENCE
    if "experience" in grouped_results:
        experiences = sort_by_score(grouped_results["experience"])
        exp_texts = [
            f"- {e['text']}"
            for e in experiences
        ]
        context_chunks.append(
            "EXPERIENCE:\n" + "\n".join(exp_texts)
        )

    # 🔹 EDUCATIONS
    if "educations" in grouped_results:
        educations = sort_by_score(grouped_results["educations"])
        edu_texts = [
            f"- {e['text']}"
            for e in educations
        ]
        context_chunks.append(
            "EDUCATION:\n" + "\n".join(edu_texts)
        )

    # 🔹 CERTIFICATIONS
    if "certifications" in grouped_results:
        certs = sort_by_score(grouped_results["certifications"])
        cert_texts = [
            f"- {c['text']}"
            for c in certs
        ]
        context_chunks.append(
            "CERTIFICATIONS:\n" + "\n".join(cert_texts)
        )

    # 🔹 ACHIEVEMENTS
    if "achievements" in grouped_results:
        achievements = sort_by_score(grouped_results["achievements"])
        ach_texts = [
            f"- {a['text']}"
            for a in achievements
        ]
        context_chunks.append(
            "ACHIEVEMENTS:\n" + "\n".join(ach_texts)
        )

    # 🔹 PERSONAL INFO
    if "personalInfo" in grouped_results:
        info = sort_by_score(grouped_results["personalInfo"])
        info_texts = [
            f"- {i['text']}"
            for i in info
        ]
        context_chunks.append(
            "PERSONAL INFORMATION:\n" + "\n".join(info_texts)
        )

    return context_chunks
