from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_session
from src.domain.users.usecases import UserUseCases
from src.domain.users.entities import User
from src.infra.repositories.user_repository import SQLAlchemyUserRepository
from src.infra.auth.password_hasher import BcryptPasswordHasher
from src.infra.auth.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_user_usecases(
    session: AsyncSession = Depends(get_session),
) -> UserUseCases:
    repo = SQLAlchemyUserRepository(session)
    hasher = BcryptPasswordHasher()
    return UserUseCases(repo=repo, hasher=hasher)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    usecases: UserUseCases = Depends(get_user_usecases),
):
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )

    user = await usecases.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )

    return user


def require_team(team_id: int, current_user: User = Depends(get_current_user)):
    """Проверяет, что текущий пользователь принадлежит команде team_id."""
    if current_user.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не состоите в этой команде",
        )
