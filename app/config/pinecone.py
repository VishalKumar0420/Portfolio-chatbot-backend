import requests
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.config.settings import get_settings

_INDEX_NAME = "portfolio-chatbot-package"
_vectorstore = None


# 🔥 Google Embeddings (Gemini API)
class GoogleEmbedding:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        response = requests.post(
            f"{self.url}?key={self.api_key}",
            json={
                "content": {
                    "parts": [{"text": text}]
                }
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        # ✅ IMPORTANT: extract correct vector
        return data["embedding"]["values"]


def init_vectorstore():
    global _vectorstore

    print("🚀 Initializing vectorstore (Google API)...")

    settings = get_settings()

    # ✅ Pinecone
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(_INDEX_NAME)

    # ✅ Google embeddings
    embeddings = GoogleEmbedding(settings.GOOGLE_API_KEY)

    _vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="text",
    )

    print("✅ Vectorstore ready (Google Embedding API)")


def get_vectorstore():
    if _vectorstore is None:
        raise RuntimeError("Vectorstore not initialized.")
    return _vectorstore