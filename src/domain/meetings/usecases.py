from datetime import datetime
from .entities import Meeting
from .interfaces import MeetingRepository
from ..teams.interfaces import TeamRepository
from ..users.interfaces import UserRepository


class MeetingUseCases:
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        team_repo: TeamRepository,
        user_repo: UserRepository,
    ):
        self._meeting_repo = meeting_repo
        self._team_repo = team_repo
        self._user_repo = user_repo

    async def schedule_meeting(
        self,
        title: str,
        organizer_id: int,
        team_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Meeting:
        user = await self._user_repo.get_by_id(organizer_id)
        if not user:
            raise ValueError("Пользователь не найден")
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise ValueError("Команда не найдена")

        if await self._meeting_repo.has_conflict(team_id, start_time, end_time):
            raise ValueError("На это время уже назначена встреча")

        meeting = Meeting.create(
            title=title,
            organizer_id=organizer_id,
            team_id=team_id,
            start_time=start_time,
            end_time=end_time,
        )
        await self._meeting_repo.save(meeting)
        return meeting

    async def cancel_meeting(self, meeting_id: int, user_id: int) -> None:
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise ValueError("Встреча не найдена")
        if meeting.organizer_id != user_id:
            raise ValueError("Только организатор может отменить встречу")
        await self._meeting_repo.delete(meeting)

    async def get_team_meetings(self, team_id: int) -> list[Meeting]:
        return await self._meeting_repo.get_by_team(team_id)

    async def get_user_meetings(
        self, user_id: int, start: datetime, end: datetime
    ) -> list[Meeting]:
        return await self._meeting_repo.get_by_user(user_id, start, end)
