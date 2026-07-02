from fastapi import APIRouter, Depends, HTTPException, status
from src.domain.users.entities import User
from src.domain.evaluations.usecases import EvaluationUseCases
from src.presentation.api.dependencies import get_current_user, check_role
from src.presentation.schemas.evaluations import (
    EvaluationCreateRequest,
    EvaluationResponse,
)
from src.config.database import get_session
from src.infra.repositories.evaluation_repository import SQLAlchemyEvaluationRepository
from src.infra.repositories.task_repository import SQLAlchemyTaskRepository
from src.infra.repositories.user_repository import SQLAlchemyUserRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


async def get_evaluation_usecases(
    session: AsyncSession = Depends(get_session),
) -> EvaluationUseCases:
    return EvaluationUseCases(
        eval_repo=SQLAlchemyEvaluationRepository(session),
        task_repo=SQLAlchemyTaskRepository(session),
        user_repo=SQLAlchemyUserRepository(session),
    )


@router.post(
    "/", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED
)
async def create_evaluation(
    data: EvaluationCreateRequest,
    current_user: User = Depends(get_current_user),
    usecases: EvaluationUseCases = Depends(get_evaluation_usecases),
):
    check_role(current_user, "manager", "admin")

    try:
        evaluation = await usecases.evaluate_task(
            task_id=data.task_id,
            evaluator_id=current_user.id,
            score=data.score,
            comment=data.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _eval_to_response(evaluation)


@router.get("/my", response_model=list[EvaluationResponse])
async def get_my_evaluations(
    current_user: User = Depends(get_current_user),
    usecases: EvaluationUseCases = Depends(get_evaluation_usecases),
):
    evaluations = await usecases.get_user_evaluations(current_user.id)
    return [_eval_to_response(e) for e in evaluations]


def _eval_to_response(evaluation) -> EvaluationResponse:
    return EvaluationResponse(
        id=evaluation.id,
        task_id=evaluation.task_id,
        evaluator_id=evaluation.evaluator_id,
        score=evaluation.score,
        comment=evaluation.comment,
    )


@router.get("/average/{user_id}", response_model=dict)
async def get_average_score(
    user_id: int,
    current_user: User = Depends(get_current_user),
    usecases: EvaluationUseCases = Depends(get_evaluation_usecases),
):
    avg = await usecases.get_average_score(user_id)
    return {"user_id": user_id, "average_score": avg}
