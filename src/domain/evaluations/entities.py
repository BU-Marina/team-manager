from dataclasses import dataclass
from datetime import datetime


@dataclass
class Evaluation:
    task_id: int
    evaluator_id: int
    score: int
    comment: str | None = None
    id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def create(
        cls, task_id: int, evaluator_id: int, score: int, comment: str | None = None
    ) -> "Evaluation":
        if score < 1 or score > 5:
            raise ValueError("Оценка должна быть от 1 до 5")
        return cls(
            task_id=task_id, evaluator_id=evaluator_id, score=score, comment=comment
        )
