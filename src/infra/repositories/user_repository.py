from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.users.entities import User
from src.domain.users.value_objects import Email
from src.domain.users.interfaces import UserRepository
from src.infra.database.models import UserModel
from src.infra.repositories.user_converter import UserConverter


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._converter = UserConverter()

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._converter.to_domain(model)

    async def save(self, user: User) -> None:
        model = self._converter.to_model(user)
        await self._session.merge(model)
        await self._session.flush()
        # Обновляем id у доменной сущности после сохранения
        if user.id is None:
            user.id = model.id

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._converter.to_domain(model)

    async def delete(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
