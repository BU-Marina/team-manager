from pydantic import BaseModel


class TeamCreateRequest(BaseModel):
    name: str


class TeamJoinRequest(BaseModel):
    code: str


class TeamResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    code: str
