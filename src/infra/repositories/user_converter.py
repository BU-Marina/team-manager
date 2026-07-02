from src.domain.users.entities import User
from src.domain.users.value_objects import UserRole
from src.infra.database.models import UserModel


class UserConverter:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            display_name=model.display_name,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            role=str(entity.role),
            display_name=entity.display_name,
            created_at=entity.created_at,
        )
