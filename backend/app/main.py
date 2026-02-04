"""Главный модуль FastAPI приложения."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.config import get_settings
from app.core.exceptions import AppException
from app.core.rate_limit import rate_limiter

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    yield
    # Shutdown
    from app.providers import close_all_providers
    await close_all_providers()
    await rate_limiter.close()


app = FastAPI(
    title=settings.app_name,
    description="Веб-приложение для асинхронного общения с LLM",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Обработчик кастомных исключений приложения."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": exc.code,
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик непредвиденных исключений."""
    if settings.debug:
        detail = str(exc)
    else:
        detail = "Внутренняя ошибка сервера"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "code": "INTERNAL_ERROR",
        },
    )


# Подключаем API роутер
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/api/health")
async def health_check():
    """Проверка состояния сервиса."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": f"Добро пожаловать в {settings.app_name}"}