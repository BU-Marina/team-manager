from fastapi import APIRouter, Depends, HTTPException, status
from src.domain.users.entities import User
from src.presentation.api.dependencies import get_current_user, check_role
from src.presentation.schemas.teams import (
    TeamCreateRequest,
    TeamJoinRequest,
    TeamResponse,
)
from src.presentation.schemas.users import UserResponse
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
    check_role(current_user, "manager", "admin")

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


@router.get("/my", response_model=list[TeamResponse])
async def get_my_teams(
    current_user: User = Depends(get_current_user),
    usecases: TeamUseCases = Depends(get_team_usecases),
):
    teams = await usecases.get_user_teams(current_user.id)
    return [
        TeamResponse(id=t.id, name=t.name, owner_id=t.owner_id, code=str(t.code))
        for t in teams
    ]


@router.get("/{team_id}/members", response_model=list[UserResponse])
async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    usecases: TeamUseCases = Depends(get_team_usecases),
):
    if current_user.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не состоите в этой команде",
        )
    members = await usecases.get_team_members(team_id)
    return [
        UserResponse(
            id=m.id, email=m.email, role=str(m.role), display_name=m.display_name
        )
        for m in members
    ]


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    team_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    usecases: TeamUseCases = Depends(get_team_usecases),
):
    check_role(current_user, "manager", "admin")

    try:
        await usecases.remove_member(team_id, member_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
