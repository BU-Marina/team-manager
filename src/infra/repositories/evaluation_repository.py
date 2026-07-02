from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.evaluations.entities import Evaluation
from src.domain.evaluations.interfaces import EvaluationRepository
from src.infra.database.models import EvaluationModel


class SQLAlchemyEvaluationRepository(EvaluationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_task(self, task_id: int) -> list[Evaluation]:
        stmt = select(EvaluationModel).where(EvaluationModel.task_id == task_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_user(self, user_id: int) -> list[Evaluation]:
        stmt = select(EvaluationModel).where(EvaluationModel.evaluator_id == user_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def save(self, evaluation: Evaluation) -> None:
        model = EvaluationModel(
            id=evaluation.id,
            task_id=evaluation.task_id,
            evaluator_id=evaluation.evaluator_id,
            score=evaluation.score,
            comment=evaluation.comment,
            created_at=evaluation.created_at,
        )
        merged = await self._session.merge(model)
        await self._session.flush()
        await self._session.refresh(merged)
        if evaluation.id is None:
            evaluation.id = merged.id

    def _to_domain(self, model: EvaluationModel) -> Evaluation:
        return Evaluation(
            id=model.id,
            task_id=model.task_id,
            evaluator_id=model.evaluator_id,
            score=model.score,
            comment=model.comment,
            created_at=model.created_at,
        )
