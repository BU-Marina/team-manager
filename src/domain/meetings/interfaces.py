from typing import Protocol
from datetime import datetime
from .entities import Meeting


class MeetingRepository(Protocol):
    async def get_by_id(self, meeting_id: int) -> Meeting | None: ...
    async def get_by_team(self, team_id: int) -> list[Meeting]: ...
    async def get_by_user(
        self, user_id: int, start: datetime, end: datetime
    ) -> list[Meeting]: ...
    async def has_conflict(
        self,
        team_id: int,
        start: datetime,
        end: datetime,
        exclude_id: int | None = None,
    ) -> bool: ...
    async def save(self, meeting: Meeting) -> None: ...
    async def delete(self, meeting: Meeting) -> None: ...
