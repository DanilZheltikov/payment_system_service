from fastapi import FastAPI

from app.core.config import settings
from app.api.routers import main_router

from contextlib import asynccontextmanager
from app.core.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_title, lifespan=lifespan)

app.include_router(main_router)
