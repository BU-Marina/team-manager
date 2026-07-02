import pytest

from src.domain.users.entities import User
from src.domain.users.value_objects import Email
from src.infra.repositories.user_repository import SQLAlchemyUserRepository


@pytest.mark.asyncio
class TestUserRepository:
    async def test_save_and_retrieve(self, session):
        repo = SQLAlchemyUserRepository(session)
        user = User.create(
            email=Email("test@example.com"), hashed_password="hashed_123"
        )

        await repo.save(user)
        retrieved = await repo.get_by_email(Email("test@example.com"))

        assert retrieved is not None
        assert retrieved.email == "test@example.com"
        assert retrieved.hashed_password == "hashed_123"

    async def test_get_by_email_not_found(self, session):
        repo = SQLAlchemyUserRepository(session)
        result = await repo.get_by_email(Email("unknown@example.com"))
        assert result is None
