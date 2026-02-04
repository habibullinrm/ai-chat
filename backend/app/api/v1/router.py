"""Главный роутер API v1."""

from fastapi import APIRouter

from app.api.v1 import auth, chat, conversations, providers, middleware

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(auth.router, prefix="/auth", tags=["Аутентификация"])
api_router.include_router(chat.router, prefix="/chat", tags=["Чат"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Диалоги"])
api_router.include_router(providers.router, prefix="/providers", tags=["Провайдеры"])
api_router.include_router(middleware.router, prefix="/middleware", tags=["Middleware"])