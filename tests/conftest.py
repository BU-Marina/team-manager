import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import ASGITransport, AsyncClient

from src.presentation.api.factory import create_app
from src.config.database import get_session
from src.infra.database.models import Base

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def client(session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def member_token(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "member@test.com", "password": "SecurePass1"},
    )
    resp = await client.post(
        "/api/auth/login", json={"email": "member@test.com", "password": "SecurePass1"}
    )
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def manager_token(session, client: AsyncClient):
    from src.domain.users.value_objects import Email, UserRole
    from src.infra.repositories.user_repository import SQLAlchemyUserRepository

    await client.post(
        "/api/auth/register",
        json={"email": "manager@test.com", "password": "SecurePass1"},
    )

    repo = SQLAlchemyUserRepository(session)
    user = await repo.get_by_email(Email("manager@test.com"))
    user.role = UserRole.MANAGER
    await repo.save(user)

    resp = await client.post(
        "/api/auth/login", json={"email": "manager@test.com", "password": "SecurePass1"}
    )
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(session, client: AsyncClient):
    from src.domain.users.value_objects import Email, UserRole
    from src.infra.repositories.user_repository import SQLAlchemyUserRepository

    await client.post(
        "/api/auth/register",
        json={"email": "admin@test.com", "password": "SecurePass1"},
    )

    repo = SQLAlchemyUserRepository(session)
    user = await repo.get_by_email(Email("admin@test.com"))
    user.role = UserRole.ADMIN
    await repo.save(user)

    resp = await client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "SecurePass1"}
    )
    return resp.json()["access_token"]
