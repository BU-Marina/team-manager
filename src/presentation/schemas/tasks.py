from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    assignee_id: int
    team_id: int
    deadline: datetime | None = None


class TaskUpdateStatusRequest(BaseModel):
    action: str  # "start" или "complete"


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    assignee_id: int
    creator_id: int
    team_id: int
    deadline: datetime | None = None
    status: str
    created_at: datetime | None = None


class CommentCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    author_id: int
    text: str
    created_at: datetime | None = None
