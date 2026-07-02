from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.meetings.entities import Meeting
from src.domain.meetings.interfaces import MeetingRepository
from src.infra.database.models import MeetingModel


class SQLAlchemyMeetingRepository(MeetingRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, meeting_id: int) -> Meeting | None:
        stmt = select(MeetingModel).where(MeetingModel.id == meeting_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_team(self, team_id: int) -> list[Meeting]:
        stmt = select(MeetingModel).where(MeetingModel.team_id == team_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_user(
        self, user_id: int, start: datetime, end: datetime
    ) -> list[Meeting]:
        stmt = select(MeetingModel).where(
            and_(
                MeetingModel.organizer_id == user_id,
                MeetingModel.start_time >= start,
                MeetingModel.end_time <= end,
            )
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def has_conflict(
        self,
        team_id: int,
        start: datetime,
        end: datetime,
        exclude_id: int | None = None,
    ) -> bool:
        stmt = select(MeetingModel).where(
            and_(
                MeetingModel.team_id == team_id,
                MeetingModel.start_time < end,
                MeetingModel.end_time > start,
            )
        )
        if exclude_id is not None:
            stmt = stmt.where(MeetingModel.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def save(self, meeting: Meeting) -> None:
        model = MeetingModel(
            id=meeting.id,
            title=meeting.title,
            organizer_id=meeting.organizer_id,
            team_id=meeting.team_id,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            created_at=meeting.created_at,
        )
        merged = await self._session.merge(model)
        await self._session.flush()
        await self._session.refresh(merged)
        if meeting.id is None:
            meeting.id = merged.id

    async def delete(self, meeting: Meeting) -> None:
        model = await self._session.get(MeetingModel, meeting.id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: MeetingModel) -> Meeting:
        return Meeting(
            id=model.id,
            title=model.title,
            organizer_id=model.organizer_id,
            team_id=model.team_id,
            start_time=model.start_time,
            end_time=model.end_time,
            created_at=model.created_at,
        )
