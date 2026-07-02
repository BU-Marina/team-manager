from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.teams.entities import Team
from src.domain.users.entities import User
from src.domain.teams.value_objects import TeamCode
from src.domain.teams.interfaces import TeamRepository
from src.infra.database.models import TeamModel, UserModel

from .user_converter import UserConverter


class SQLAlchemyTeamRepository(TeamRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_code(self, code: TeamCode) -> Team | None:
        stmt = select(TeamModel).where(TeamModel.code == str(code))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return Team(
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            code=TeamCode(model.code),
            created_at=model.created_at,
        )

    async def save(self, team: Team) -> None:
        model = TeamModel(
            id=team.id,
            name=team.name,
            owner_id=team.owner_id,
            code=str(team.code),
            created_at=team.created_at,
        )
        merged = await self._session.merge(model)
        await self._session.flush()
        await self._session.refresh(merged)
        if team.id is None:
            team.id = merged.id

    async def get_by_id(self, team_id: int) -> Team | None:
        stmt = select(TeamModel).where(TeamModel.id == team_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return Team(
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            code=TeamCode(model.code),
            created_at=model.created_at,
        )

    async def get_by_user(self, user_id: int) -> list[Team]:
        stmt = (
            select(TeamModel)
            .join(UserModel, UserModel.team_id == TeamModel.id)
            .where(UserModel.id == user_id)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def delete(self, team: Team) -> None:
        model = await self._session.get(TeamModel, team.id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: TeamModel) -> Team:
        return Team(
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            code=TeamCode(model.code),
            created_at=model.created_at,
        )

    async def get_members(self, team_id: int) -> list[User]:
        stmt = select(UserModel).where(UserModel.team_id == team_id)
        result = await self._session.execute(stmt)
        return [UserConverter.to_domain(m) for m in result.scalars().all()]
