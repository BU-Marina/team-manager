from datetime import datetime
from pydantic import BaseModel


class CalendarEvent(BaseModel):
    type: str  # "task" или "meeting"
    title: str
    start: datetime
    end: datetime | None = None
    status: str | None = None  # только для задач


class CalendarResponse(BaseModel):
    events: list[CalendarEvent]
