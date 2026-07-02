from fastapi import APIRouter, Depends, HTTPException, status
from src.domain.users.entities import User
from src.domain.tasks.usecases import TaskUseCases
from src.presentation.api.dependencies import get_current_user, require_team
from src.presentation.schemas.tasks import (
    TaskCreateRequest,
    TaskUpdateStatusRequest,
    TaskResponse,
    CommentCreateRequest,
    CommentResponse,
)
from src.config.database import get_session
from src.infra.repositories.task_repository import SQLAlchemyTaskRepository
from src.infra.repositories.user_repository import SQLAlchemyUserRepository
from src.infra.repositories.team_repository import SQLAlchemyTeamRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


async def get_task_usecases(
    session: AsyncSession = Depends(get_session),
) -> TaskUseCases:
    return TaskUseCases(
        task_repo=SQLAlchemyTaskRepository(session),
        user_repo=SQLAlchemyUserRepository(session),
        team_repo=SQLAlchemyTeamRepository(session),
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    usecases: TaskUseCases = Depends(get_task_usecases),
):
    if current_user.team_id != data.team_id:
        raise HTTPException(status_code=403, detail="Вы не состоите в этой команде")

    try:
        task = await usecases.create_task(
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
            creator_id=current_user.id,
            team_id=data.team_id,
            deadline=data.deadline,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _task_to_response(task)


@router.post("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    data: TaskUpdateStatusRequest,
    current_user: User = Depends(get_current_user),
    usecases: TaskUseCases = Depends(get_task_usecases),
):
    try:
        if data.action == "start":
            task = await usecases.start_task(task_id, current_user.id)
        elif data.action == "complete":
            task = await usecases.complete_task(task_id, current_user.id)
        else:
            raise HTTPException(status_code=400, detail="Неизвестное действие")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _task_to_response(task)


@router.get("/team/{team_id}", response_model=list[TaskResponse])
async def get_team_tasks(
    team_id: int,
    _: None = Depends(require_team),
    usecases: TaskUseCases = Depends(get_task_usecases),
):
    tasks = await usecases.get_team_tasks(team_id)
    return [_task_to_response(t) for t in tasks]


@router.get("/my", response_model=list[TaskResponse])
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    usecases: TaskUseCases = Depends(get_task_usecases),
):
    tasks = await usecases.get_user_tasks(current_user.id)
    return [_task_to_response(t) for t in tasks]


def _task_to_response(task) -> TaskResponse:
    return TaskResponse(
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


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    task_id: int,
    data: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    usecases: TaskUseCases = Depends(get_task_usecases),
):
    try:
        comment = await usecases.add_comment(task_id, current_user.id, data.text)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _comment_to_response(comment)


@router.get("/{task_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    usecases: TaskUseCases = Depends(get_task_usecases),
):
    comments = await usecases.get_comments(task_id)
    return [_comment_to_response(c) for c in comments]


def _comment_to_response(comment) -> CommentResponse:
    return CommentResponse(
        id=comment.id,
        author_id=comment.author_id,
        text=comment.text,
        created_at=comment.created_at,
    )
