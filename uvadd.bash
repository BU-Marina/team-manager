uv add fastapi uvicorn[standard]
uv add sqlalchemy[asyncio] aiosqlite alembic
uv add pydantic pydantic-settings pydantic[email]
uv add python-jose[cryptography] bcrypt
uv add python-multipart jinja2
uv add pytest pytest-asyncio pytest-mock httpx
uv add asyncpg
uv add sqladmin

uv add --dev mypy ruff pre-commit
uv run pre-commit install
