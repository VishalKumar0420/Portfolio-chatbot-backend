from fastapi import APIRouter
from app.schemas.chat import ChatDelete, ChatInput, ChatQuery
from app.services.chat import add_chat_content, delete_chat_content, search_chat_content


router = APIRouter(prefix="/chat", tags=["CHAT"])


@router.post("/add_chat/")
async def add_chat(chat: ChatInput):
    add_chat_content(chat.chat_id, chat.chat_name, chat.content)
    return {"message": "Chat content added successfully!"}


@router.post("/search_chat/")
async def search_chat(query: ChatQuery):
    results = search_chat_content(query.chat_id, query.query)
    return {"results": results}


@router.delete("/delete_chat/")
async def delete_chat(chat_delete: ChatDelete):
    delete_chat_content(chat_delete.chat_id)
    return {
        "message": f"All data for chat_id '{chat_delete.chat_id}' has been deleted successfully!"
    }
