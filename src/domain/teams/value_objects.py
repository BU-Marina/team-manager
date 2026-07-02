import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class TeamCode:
    value: str

    @classmethod
    def generate(cls) -> "TeamCode":
        return cls(value=secrets.token_urlsafe(8))

    def __str__(self) -> str:
        return self.value
