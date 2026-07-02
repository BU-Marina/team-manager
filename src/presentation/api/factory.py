# src/presentation/api/factory.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config.settings import settings
from src.config.database import engine
from src.infra.database.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.mount(
        "/static", StaticFiles(directory="src/presentation/static"), name="static"
    )
    # TODO Роутеры будем подключать по мере готовности:
    # app.include_router(users_router, prefix="/api")
    return app


app = create_app()  # для uvicorn
