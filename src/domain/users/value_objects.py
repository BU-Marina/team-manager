import re
from dataclasses import dataclass
from enum import StrEnum


class UserRole(StrEnum):
    MEMBER = "member"
    MANAGER = "manager"
    ADMIN = "admin"


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, self.value):
            raise ValueError(f"Некорректный email: {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RawPassword:
    value: str

    def __post_init__(self):
        if len(self.value) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")

    def __str__(self) -> str:
        return self.value
