uv add fastapi uvicorn[standard]
uv add sqlalchemy[asyncio] aiosqlite alembic
uv add pydantic pydantic-settings
uv add python-jose[cryptography] passlib[bcrypt]
uv add python-multipart jinja2
uv add pytest pytest-asyncio pytest-mock httpx

uv add --dev mypy ruff pre-commit
uv run pre-commit install
