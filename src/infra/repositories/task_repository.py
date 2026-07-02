from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.tasks.entities import Task
from src.domain.tasks.value_objects import TaskStatus
from src.domain.tasks.interfaces import TaskRepository
from src.domain.teams.entities import Team
from src.domain.users.entities import User
from src.infra.database.models import TaskModel, TeamModel, UserModel

from .user_converter import UserConverter


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, task_id: int) -> Task | None:
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_team(self, team_id: int) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.team_id == team_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_assignee(self, user_id: int) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.assignee_id == user_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def save(self, task: Task) -> None:
        model = TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id,
            team_id=task.team_id,
            deadline=task.deadline,
            status=str(task.status),
            created_at=task.created_at,
        )
        merged = await self._session.merge(model)
        await self._session.flush()
        await self._session.refresh(merged)
        if task.id is None:
            task.id = merged.id

    async def delete(self, task: Task) -> None:
        model = await self._session.get(TaskModel, task.id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            assignee_id=model.assignee_id,
            creator_id=model.creator_id,
            team_id=model.team_id,
            deadline=model.deadline,
            status=TaskStatus(model.status),
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

    async def get_members(self, team_id: int) -> list[User]:
        stmt = select(UserModel).where(UserModel.team_id == team_id)
        result = await self._session.execute(stmt)
        return [UserConverter.to_domain(m) for m in result.scalars().all()]
