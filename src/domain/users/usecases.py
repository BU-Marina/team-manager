from .entities import User
from .value_objects import Email, RawPassword, UserRole
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

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._repo.get_by_id(user_id)

    async def update_profile(self, user_id: int, **kwargs) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        user.update_profile(**kwargs)
        await self._repo.save(user)
        return user

    async def delete_account(self, user_id: int) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        await self._repo.delete(user)

    async def change_role(self, admin_id: int, user_id: int, new_role: str) -> User:
        admin = await self._repo.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise ValueError("Только админ может менять роли")
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        user.role = UserRole(new_role)
        await self._repo.save(user)
        return user

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        if not self._hasher.verify(RawPassword(old_password), user.hashed_password):
            raise ValueError("Неверный текущий пароль")
        user.hashed_password = self._hasher.hash(RawPassword(new_password))
        await self._repo.save(user)
