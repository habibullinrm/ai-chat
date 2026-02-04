"""Главный роутер API v1."""

from fastapi import APIRouter

from app.api.v1 import auth

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(auth.router, prefix="/auth", tags=["Аутентификация"])