from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class MeetingCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    team_id: int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("Время начала должно быть раньше времени окончания")
        return self


class MeetingResponse(BaseModel):
    id: int
    title: str
    organizer_id: int
    team_id: int
    start_time: datetime
    end_time: datetime
