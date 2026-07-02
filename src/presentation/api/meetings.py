from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.users.entities import User
from src.domain.meetings.usecases import MeetingUseCases
from src.presentation.api.dependencies import (
    get_current_user,
    require_team,
    check_role,
)
from src.presentation.schemas.meetings import MeetingCreateRequest, MeetingResponse
from src.config.database import get_session
from src.infra.repositories.meeting_repository import SQLAlchemyMeetingRepository
from src.infra.repositories.team_repository import SQLAlchemyTeamRepository
from src.infra.repositories.user_repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


async def get_meeting_usecases(
    session: AsyncSession = Depends(get_session),
) -> MeetingUseCases:
    return MeetingUseCases(
        meeting_repo=SQLAlchemyMeetingRepository(session),
        team_repo=SQLAlchemyTeamRepository(session),
        user_repo=SQLAlchemyUserRepository(session),
    )


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def schedule_meeting(
    data: MeetingCreateRequest,
    current_user: User = Depends(get_current_user),
    usecases: MeetingUseCases = Depends(get_meeting_usecases),
):
    check_role(current_user, "manager", "admin")

    if current_user.team_id != data.team_id:
        raise HTTPException(status_code=403, detail="Вы не состоите в этой команде")

    try:
        meeting = await usecases.schedule_meeting(
            title=data.title,
            organizer_id=current_user.id,
            team_id=data.team_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _meeting_to_response(meeting)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    usecases: MeetingUseCases = Depends(get_meeting_usecases),
):
    check_role(current_user, "manager", "admin")

    try:
        await usecases.cancel_meeting(meeting_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/team/{team_id}", response_model=list[MeetingResponse])
async def get_team_meetings(
    team_id: int,
    _: None = Depends(require_team),
    usecases: MeetingUseCases = Depends(get_meeting_usecases),
):
    meetings = await usecases.get_team_meetings(team_id)
    return [_meeting_to_response(m) for m in meetings]


@router.get("/my", response_model=list[MeetingResponse])
async def get_my_meetings(
    start: datetime = Query(...),
    end: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    usecases: MeetingUseCases = Depends(get_meeting_usecases),
):
    meetings = await usecases.get_user_meetings(current_user.id, start, end)
    return [_meeting_to_response(m) for m in meetings]


def _meeting_to_response(meeting) -> MeetingResponse:
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        organizer_id=meeting.organizer_id,
        team_id=meeting.team_id,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
    )
