from fastapi import APIRouter,Depends,BackgroundTasks,HTTPException
from app.schemas.chat import ChatDelete, ChatInput, ChatQuery
from app.services.chat_service import add_chat_content, delete_chat_content, search_chat_content,add_chat_db
from app.core.db.session import get_db
from app.middleware.authenticate import token_verify
from sqlalchemy.orm import Session
router = APIRouter(prefix="/chat", tags=["CHAT"])


@router.post("/add_chat/")
async def add_chat(chat: ChatInput, background_tasks: BackgroundTasks, db: Session = Depends(get_db),user_id: str = Depends(token_verify)):

    try:
        add_chat_db(
            db,
            chat.chat_id,
            user_id,
            chat.chat_name,
            chat.content
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store chat")

    # Only runs if DB success
    background_tasks.add_task(
        add_chat_content,
        chat.chat_id,
        chat.content
    )

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
