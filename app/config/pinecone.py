from fastapi import FastAPI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.config.settings import get_settings

app = FastAPI()

_INDEX_NAME = "portfolio-chatbot-package"
_vectorstore = None


@app.on_event("startup")
async def startup_event():
    global _vectorstore

    print("Starting app...")

    settings = get_settings()

    if not settings.PINECONE_API_KEY:
        raise RuntimeError("Missing PINECONE_API_KEY")

    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(_INDEX_NAME)

    print("Loading embeddings model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    _vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="text",
    )

    print("Vectorstore ready ✅")


def get_vectorstore():
    return _vectorstore