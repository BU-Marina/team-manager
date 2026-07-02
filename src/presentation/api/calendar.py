from datetime import datetime
from fastapi import APIRouter, Depends, Query
from src.domain.users.entities import User
from src.domain.tasks.usecases import TaskUseCases
from src.domain.meetings.usecases import MeetingUseCases
from src.presentation.api.dependencies import get_current_user
from src.presentation.schemas.calendar import CalendarEvent, CalendarResponse
from src.config.database import get_session
from src.infra.repositories.task_repository import SQLAlchemyTaskRepository
from src.infra.repositories.meeting_repository import SQLAlchemyMeetingRepository
from src.infra.repositories.team_repository import SQLAlchemyTeamRepository
from src.infra.repositories.user_repository import SQLAlchemyUserRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


async def get_task_usecases(
    session: AsyncSession = Depends(get_session),
) -> TaskUseCases:
    return TaskUseCases(
        task_repo=SQLAlchemyTaskRepository(session),
        user_repo=SQLAlchemyUserRepository(session),
        team_repo=SQLAlchemyTeamRepository(session),
    )


async def get_meeting_usecases(
    session: AsyncSession = Depends(get_session),
) -> MeetingUseCases:
    return MeetingUseCases(
        meeting_repo=SQLAlchemyMeetingRepository(session),
        team_repo=SQLAlchemyTeamRepository(session),
        user_repo=SQLAlchemyUserRepository(session),
    )


@router.get("/", response_model=CalendarResponse)
async def get_calendar(
    start: datetime = Query(...),
    end: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    task_uc: TaskUseCases = Depends(get_task_usecases),
    meeting_uc: MeetingUseCases = Depends(get_meeting_usecases),
):
    events: list[CalendarEvent] = []

    # Задачи пользователя
    tasks = await task_uc.get_user_tasks(current_user.id)
    for task in tasks:
        if task.deadline and start <= task.deadline <= end:
            events.append(
                CalendarEvent(
                    type="task",
                    title=task.title,
                    start=task.deadline,
                    end=task.deadline,
                    status=str(task.status),
                )
            )

    # Встречи пользователя
    meetings = await meeting_uc.get_user_meetings(current_user.id, start, end)
    for meeting in meetings:
        events.append(
            CalendarEvent(
                type="meeting",
                title=meeting.title,
                start=meeting.start_time,
                end=meeting.end_time,
            )
        )

    return CalendarResponse(events=events)
