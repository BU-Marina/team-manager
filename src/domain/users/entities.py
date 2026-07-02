from dataclasses import dataclass
from datetime import datetime
from .value_objects import Email, UserRole


@dataclass
class User:
    email: str
    hashed_password: str
    id: int | None = None
    role: UserRole = UserRole.MEMBER
    display_name: str | None = None
    created_at: datetime | None = None

    @classmethod
    def create(cls, email: Email, hashed_password: str) -> "User":
        return cls(
            email=str(email),
            hashed_password=hashed_password,
        )

    def update_profile(self, *, display_name: str | None = None) -> None:
        if display_name is not None:
            self.display_name = display_name
