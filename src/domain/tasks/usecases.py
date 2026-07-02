from datetime import datetime
from .entities import Task
from .interfaces import TaskRepository
from ..users.interfaces import UserRepository
from ..teams.interfaces import TeamRepository


class TaskUseCases:
    def __init__(
        self,
        task_repo: TaskRepository,
        user_repo: UserRepository,
        team_repo: TeamRepository,
    ):
        self._task_repo = task_repo
        self._user_repo = user_repo
        self._team_repo = team_repo

    async def create_task(
        self,
        title: str,
        description: str,
        assignee_id: int,
        creator_id: int,
        team_id: int,
        deadline: datetime | None = None,
    ) -> Task:
        assignee = await self._user_repo.get_by_id(assignee_id)
        if not assignee:
            raise ValueError("Исполнитель не найден")
        creator = await self._user_repo.get_by_id(creator_id)
        if not creator:
            raise ValueError("Создатель не найден")
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise ValueError("Команда не найдена")
        task = Task.create(
            title=title,
            description=description,
            assignee_id=assignee_id,
            creator_id=creator_id,
            team_id=team_id,
            deadline=deadline,
        )
        await self._task_repo.save(task)
        return task

    async def start_task(self, task_id: int, user_id: int) -> Task:
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")
        if task.assignee_id != user_id:
            raise ValueError("Только исполнитель может начать задачу")
        task.start()
        await self._task_repo.save(task)
        return task

    async def complete_task(self, task_id: int, user_id: int) -> Task:
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")
        if task.assignee_id != user_id:
            raise ValueError("Только исполнитель может завершить задачу")
        task.complete()
        await self._task_repo.save(task)
        return task

    async def get_team_tasks(self, team_id: int) -> list[Task]:
        return await self._task_repo.get_by_team(team_id)

    async def get_user_tasks(self, user_id: int) -> list[Task]:
        return await self._task_repo.get_by_assignee(user_id)
