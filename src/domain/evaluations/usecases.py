from .entities import Evaluation
from .interfaces import EvaluationRepository
from ..tasks.interfaces import TaskRepository
from ..users.interfaces import UserRepository


class EvaluationUseCases:
    def __init__(
        self,
        eval_repo: EvaluationRepository,
        task_repo: TaskRepository,
        user_repo: UserRepository,
    ):
        self._eval_repo = eval_repo
        self._task_repo = task_repo
        self._user_repo = user_repo

    async def evaluate_task(
        self, task_id: int, evaluator_id: int, score: int, comment: str | None = None
    ) -> Evaluation:
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")
        user = await self._user_repo.get_by_id(evaluator_id)
        if not user:
            raise ValueError("Пользователь не найден")
        evaluation = Evaluation.create(
            task_id=task_id, evaluator_id=evaluator_id, score=score, comment=comment
        )
        await self._eval_repo.save(evaluation)
        return evaluation

    async def get_user_evaluations(self, user_id: int) -> list[Evaluation]:
        return await self._eval_repo.get_by_user(user_id)
