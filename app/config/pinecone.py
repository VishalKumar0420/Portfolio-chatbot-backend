import requests
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.config.settings import get_settings

_INDEX_NAME = "portfolio-chatbot-package"
_vectorstore = None


# 🔥 Custom Embeddings class (API based)
class HFAPIEmbeddings:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()


def init_vectorstore():
    global _vectorstore

    print("🚀 Initializing vectorstore...")

    settings = get_settings()

    # ✅ Pinecone
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(_INDEX_NAME)

    # ✅ HF API embeddings (NO local model load)
    embeddings = HFAPIEmbeddings(settings.HF_TOKEN)

    _vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="text",
    )

    print("✅ Vectorstore ready (API mode)")


def get_vectorstore():
    if _vectorstore is None:
        raise RuntimeError("Vectorstore not initialized.")
    return _vectorstore