from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config.settings import settings
from src.config.database import engine
from src.infra.database.models import Base
from src.presentation.api.users import router as users_router
from src.presentation.api.teams import router as teams_router
from src.presentation.api.tasks import router as tasks_router
from src.presentation.api.evaluations import router as evaluations_router
from src.presentation.api.meetings import router as meetings_router
from src.presentation.api.calendar import router as calendar_router
from src.presentation.api.frontend import router as frontend_router


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

    # Роуты
    app.include_router(users_router)
    app.include_router(teams_router)
    app.include_router(tasks_router)
    app.include_router(evaluations_router)
    app.include_router(meetings_router)
    app.include_router(calendar_router)
    app.include_router(frontend_router)

    return app


app = create_app()
