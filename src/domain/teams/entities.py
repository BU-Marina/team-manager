from dataclasses import dataclass, field
from datetime import datetime
from .value_objects import TeamCode


@dataclass
class Team:
    name: str
    owner_id: int
    code: TeamCode = field(default_factory=TeamCode.generate)
    id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def create(cls, name: str, owner_id: int) -> "Team":
        return cls(name=name, owner_id=owner_id, code=TeamCode.generate())
