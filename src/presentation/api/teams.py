from fastapi import APIRouter, Depends, HTTPException, status
from src.domain.users.entities import User
from src.presentation.api.dependencies import get_current_user
from src.presentation.schemas.teams import (
    TeamCreateRequest,
    TeamJoinRequest,
    TeamResponse,
)
from src.domain.teams.usecases import TeamUseCases
from src.infra.repositories.user_repository import SQLAlchemyUserRepository
from src.infra.repositories.team_repository import SQLAlchemyTeamRepository
from src.config.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/teams", tags=["teams"])


async def get_team_usecases(
    session: AsyncSession = Depends(get_session),
) -> TeamUseCases:
    return TeamUseCases(
        team_repo=SQLAlchemyTeamRepository(session),
        user_repo=SQLAlchemyUserRepository(session),
    )


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    usecases: TeamUseCases = Depends(get_team_usecases),
):
    try:
        team = await usecases.create_team(name=data.name, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return TeamResponse(
        id=team.id, name=team.name, owner_id=team.owner_id, code=str(team.code)
    )


@router.post("/join", response_model=TeamResponse)
async def join_team(
    data: TeamJoinRequest,
    current_user: User = Depends(get_current_user),
    usecases: TeamUseCases = Depends(get_team_usecases),
):
    try:
        team = await usecases.join_team(user_id=current_user.id, code=data.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return TeamResponse(
        id=team.id, name=team.name, owner_id=team.owner_id, code=str(team.code)
    )
