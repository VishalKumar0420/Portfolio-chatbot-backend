from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.config.settings import get_settings

_INDEX_NAME = "portfolio-chatbot-package"
_vectorstore = None


def init_vectorstore():
    global _vectorstore

    print("🚀 Initializing vectorstore...")

    settings = get_settings()

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

    print("✅ Vectorstore ready")


def get_vectorstore():
    if _vectorstore is None:
        raise RuntimeError("Vectorstore not initialized.")
    return _vectorstore