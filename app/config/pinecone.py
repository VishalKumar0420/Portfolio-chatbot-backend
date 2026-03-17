"""
Pinecone vector store — singleton initialised lazily on first use.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from app.config.settings import get_settings

_INDEX_NAME = "portfolio-chatbot-package"
_vectorstore: PineconeVectorStore | None = None


def get_vectorstore() -> PineconeVectorStore:
    """
    Return the shared Pinecone vector store, creating it on first call.

    Uses sentence-transformers/all-MiniLM-L6-v2 for embeddings.

    Raises:
        RuntimeError: If PINECONE_API_KEY is not configured.
    """
    global _vectorstore

    if _vectorstore is None:
        settings = get_settings()

        if not settings.PINECONE_API_KEY:
            raise RuntimeError("PINECONE_API_KEY is not configured")

        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(_INDEX_NAME)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        _vectorstore = PineconeVectorStore(
            index=index,
            embedding=embeddings,
            text_key="text",
        )

    return _vectorstore
