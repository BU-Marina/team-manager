from dataclasses import dataclass
from datetime import datetime
from .value_objects import TaskStatus


@dataclass
class Task:
    title: str
    description: str
    assignee_id: int
    creator_id: int
    team_id: int
    deadline: datetime | None = None
    status: TaskStatus = TaskStatus.OPEN
    id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        assignee_id: int,
        creator_id: int,
        team_id: int,
        deadline: datetime | None = None,
    ) -> "Task":
        if not title.strip():
            raise ValueError("Название задачи не может быть пустым")
        return cls(
            title=title,
            description=description,
            assignee_id=assignee_id,
            creator_id=creator_id,
            team_id=team_id,
            deadline=deadline,
        )

    def start(self) -> None:
        if self.status != TaskStatus.OPEN:
            raise ValueError(f"Нельзя начать задачу в статусе {self.status}")
        self.status = TaskStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Нельзя завершить задачу в статусе {self.status}")
        self.status = TaskStatus.DONE
