
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore 
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config.setting import settings


INDEX_NAME = "portfolio-chatbot-package"


if not settings.PINECONE_API_KEY:
    raise RuntimeError("❌ PINECONE_API_KEY not found in environment")

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    text_key="text"
)
