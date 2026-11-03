from fastapi import APIRouter
from app.api.v1.endpoints import conversations, chat, documents, translate

api_v1_router = APIRouter()

api_v1_router.include_router(conversations.router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(documents.router)
api_v1_router.include_router(translate.router)
