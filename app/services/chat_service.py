
from app.shares.call_groq_llm import call_groq_llm
from app.shares.detect_sections import detect_sections
from app.shares.normalize_text import normalize_text
from app.shares.preprocess_query import preprocess_query
from data import TOP_K, VECTOR_K
from app.core.vectorstore.pinecone_store import _vectorstore
from app.models.chat import Chat
from sqlalchemy.orm import Session
from app.core.vectorstore.pinecone_store import get_vectorstore
import uuid
from pydantic import BaseModel

def add_chat_db(db: Session, chat_id: str, user_id: str, chat_name: str, content: dict):
    try:
        existing_chat = db.query(Chat).filter(Chat.chat_id == uuid.UUID(chat_id)).first()
        

        if existing_chat:
            existing_chat.chat_name = chat_name
            existing_chat.chat_content = content.model_dump()

        else:
            new_chat = Chat(
                chat_id=chat_id,
                user_id=user_id,
                chat_name=chat_name,
                chat_content=content.model_dump()
            )
            db.add(new_chat)

        db.commit()

        

    except Exception as e:
        
        db.rollback()
        raise e


def delete_chat_content(chat_id: str):
    """Delete all data for a specific chat_id from vector store"""
    try:
        # For Pinecone, we need to use the delete method with filter
        # First, let's try to get the index directly and delete by filter
        from src.config.pinecone import index
        
        # Delete all vectors with this chat_id using filter
        delete_response = index.delete(filter={"chat_id": chat_id})
        
        
    except Exception as e:
        
        # Fallback method - try to get documents and delete by IDs
        try:
            results = _vectorstore.similarity_search(
                query="dummy",
                k=1000,
                filter={"chat_id": chat_id}
            )
            
            if results:
                # Extract IDs and delete
                ids_to_delete = []
                for doc in results:
                    section = doc.metadata.get("section", "")
                    block_index = doc.metadata.get("block_index", 0)
                    chunk_index = doc.metadata.get("chunk_index", 0)
                    doc_id = f"{chat_id}_{section}_{block_index}_{chunk_index}"
                    ids_to_delete.append(doc_id)
                
                if ids_to_delete:
                    vectorstore.delete(ids_to_delete)
            
                
        except Exception as fallback_error:
            print(f"Fallback delete also failed: {fallback_error}")

def add_chat_content(chat_id: str, content: dict):
    vectorstore = get_vectorstore()

    if isinstance(content, BaseModel):
        content = content.model_dump()

    delete_chat_content(chat_id)

    texts, metadatas, ids = [], [], []

    for section, value in content.items():
        if not value:
            continue

        if isinstance(value, str):
            texts.append(normalize_text(value))
            ids.append(f"{chat_id}_{section}_0")
            metadatas.append({
                "chat_id": chat_id,
                "section": section
            })

        elif isinstance(value, list):
            for idx, item in enumerate(value):

                if isinstance(item, str):
                    texts.append(normalize_text(item))
                    ids.append(f"{chat_id}_{section}_{idx}")
                    metadatas.append({
                        "chat_id": chat_id,
                        "section": section,
                        "index": idx
                    })

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
                    metadatas.append({
                        "chat_id": chat_id,
                        "section": section,
                        "index": idx
                    })

    if texts:
        vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
def search_chat_content(chat_id: str, query: str):
    processed_query_text = preprocess_query(query)

    inferred_sections = detect_sections(processed_query_text)

    results = _vectorstore.similarity_search_with_score(
        query=processed_query_text, k=VECTOR_K, filter={"chat_id": chat_id}
    )

    ranked_results = []

    for doc, score in results:
        # base similarity score
        final_score = score

        # boost if section matches intent
        if inferred_sections and doc.metadata.get("section") in inferred_sections:
            final_score += 0.3  # Increased boost for better section matching

        ranked_results.append(
            {
                "text": doc.page_content,
                "section": doc.metadata["section"],
                "block_index": doc.metadata.get("block_index"),
                "chunk_index": doc.metadata.get("chunk_index"),
                "score": final_score,
            }
        )

    # sort by final score
    ranked_results.sort(key=lambda x: x["score"], reverse=True)

    # dedupe + pick top 3
    final_chunks = []
    seen = set()

    for r in ranked_results:
        key = (r["section"], r["block_index"], r["chunk_index"])
        if key in seen:
            continue

        final_chunks.append(r["text"])
        seen.add(key)

        if len(final_chunks) == TOP_K:
            break

    answer = call_groq_llm(query, final_chunks)
    return {"answer": answer, "context": final_chunks}
