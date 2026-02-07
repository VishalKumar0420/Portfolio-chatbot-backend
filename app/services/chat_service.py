from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.shares import call_groq_llm, detect_sections, normalize_text, preprocess_query, split_large_section
from data import TOP_K, VECTOR_K
from app.core.vectorstore.pinecone_store import _vectorstore



# Delete all data for a specific chat_id from vector store
def delete_chat_content(chat_id: str):
    try:
        from app.core.vectorstore.pinecone_store import index

        # Delete all vectors with this chat_id using filter
        delete_response = index.delete(filter={"chat_id": chat_id})
        print(f"Pinecone delete response: {delete_response}")
        print(f"Attempted to delete all data for chat_id: {chat_id}")

    # Fallback method - try to get documents and delete by IDs
    except Exception as e:
        print(f"Error deleting chat content for {chat_id}: {e}")
        try:
            results = _vectorstore.similarity_search(
                query="dummy", k=1000, filter={"chat_id": chat_id}
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
                    _vectorstore.delete(ids_to_delete)
                    print(
                        f"Fallback: Deleted {len(ids_to_delete)} documents for chat_id: {chat_id}"
                    )
            else:
                print(f"No documents found for chat_id: {chat_id}")

        except Exception as fallback_error:
            print(f"Fallback delete also failed: {fallback_error}")


# First, delete existing data for this chat_id if it exists
def add_chat_content(chat_id: str, chat_name: str, content: dict):
    print(f"Checking for existing data for chat_id: {chat_id}")
    delete_chat_content(chat_id)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", ".", " ", ""]
    )

    texts, metadatas, ids = [], [], []

    for section, text in content.items():
        if not text or not text.strip():
            continue

        text = normalize_text(text)

        sub_blocks = split_large_section(text) if len(text) > 1000 else [text]

        for block_index, block in enumerate(sub_blocks):
            chunks = splitter.split_text(block)

            for chunk_index, chunk in enumerate(chunks):
                texts.append(chunk)
                ids.append(f"{chat_id}_{section}_{block_index}_{chunk_index}")
                metadatas.append(
                    {
                        "chat_id": chat_id,
                        "chat_name": chat_name,
                        "section": section,
                        "block_index": block_index,
                        "chunk_index": chunk_index,
                    }
                )

    if texts:
        _vectorstore.add_texts(texts, metadatas, ids)
        print(f"Added {len(texts)} new chunks for chat_id: {chat_id}")
    else:
        print(f"No valid content to add for chat_id: {chat_id}")


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
