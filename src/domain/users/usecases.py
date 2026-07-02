from .entities import User
from .value_objects import Email, RawPassword
from .interfaces import UserRepository, PasswordHasher


class UserUseCases:
    def __init__(self, repo: UserRepository, hasher: PasswordHasher):
        self._repo = repo
        self._hasher = hasher

    async def register(self, email: str, password: str) -> User:
        email_vo = Email(email)
        password_vo = RawPassword(password)

        if await self._repo.get_by_email(email_vo):
            raise ValueError("Пользователь с таким email уже существует")

        hashed = self._hasher.hash(password_vo)
        user = User.create(email=email_vo, hashed_password=hashed)
        await self._repo.save(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        email_vo = Email(email)
        password_vo = RawPassword(password)

        user = await self._repo.get_by_email(email_vo)
        if not user:
            raise ValueError("Неверный email или пароль")

        if not self._hasher.verify(password_vo, user.hashed_password):
            raise ValueError("Неверный email или пароль")

        return user
