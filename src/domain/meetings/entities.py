from dataclasses import dataclass
from datetime import datetime


@dataclass
class Meeting:
    title: str
    organizer_id: int
    team_id: int
    start_time: datetime
    end_time: datetime
    id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def create(
        cls,
        title: str,
        organizer_id: int,
        team_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> "Meeting":
        if not title.strip():
            raise ValueError("Название встречи не может быть пустым")
        if start_time >= end_time:
            raise ValueError("Время начала должно быть раньше времени окончания")
        return cls(
            title=title,
            organizer_id=organizer_id,
            team_id=team_id,
            start_time=start_time,
            end_time=end_time,
        )
