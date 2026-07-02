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
    team_id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def create(
        cls, email: Email, hashed_password: str, team_id: int | None = None
    ) -> "User":
        return cls(
            email=str(email),
            hashed_password=hashed_password,
            team_id=team_id,
        )

    def update_profile(self, *, display_name: str | None = None) -> None:
        if display_name is not None:
            self.display_name = display_name

    def join_team(self, team_id: int) -> None:
        self.team_id = team_id

    def is_manager_or_admin(self) -> bool:
        return self.role in (UserRole.MANAGER, UserRole.ADMIN)

    def leave_team(self) -> None:
        self.team_id = None
