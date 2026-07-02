import pytest

from src.domain.users.entities import User
from src.domain.users.value_objects import Email, RawPassword, UserRole
from src.domain.users.interfaces import UserRepository, PasswordHasher
from src.domain.users.usecases import UserUseCases


# --- Fakes (лёгкие реализации для тестов) ---


class FakeUserRepository(UserRepository):
    """Хранилище в памяти для тестов"""

    def __init__(self):
        self._users: dict[str, User] = {}

    async def get_by_email(self, email: Email) -> User | None:
        return self._users.get(str(email))

    async def save(self, user: User) -> None:
        self._users[user.email] = user

    async def get_by_id(self, user_id: int) -> User | None:
        for u in self._users.values():
            if u.id == user_id:
                return u
        return None

    async def delete(self, user: User) -> None:
        self._users.pop(user.email, None)


class FakePasswordHasher(PasswordHasher):
    """Хешер для тестов (без bcrypt, быстро)"""

    def hash(self, password: RawPassword) -> str:
        return f"hashed_{str(password)}"

    def verify(self, password: RawPassword, hashed: str) -> bool:
        return hashed == f"hashed_{str(password)}"


# --- Fixtures ---


@pytest.fixture
def repo():
    return FakeUserRepository()


@pytest.fixture
def hasher():
    return FakePasswordHasher()


@pytest.fixture
def usecases(repo, hasher):
    return UserUseCases(repo=repo, hasher=hasher)


# --- Tests: Register ---


@pytest.mark.unit
@pytest.mark.users
@pytest.mark.asyncio
class TestRegister:
    async def test_register_creates_user(self, usecases, repo):
        user = await usecases.register("test@example.com", "SecurePass1")

        assert user.email == "test@example.com"
        assert user.role == UserRole.MEMBER
        assert user.hashed_password == "hashed_SecurePass1"

        # Проверяем, что пользователь реально сохранён
        saved = await repo.get_by_email(Email("test@example.com"))
        assert saved is not None
        assert saved.email == "test@example.com"

    async def test_register_duplicate_email_fails(self, usecases):
        await usecases.register("test@example.com", "SecurePass1")

        with pytest.raises(ValueError, match="уже существует"):
            await usecases.register("test@example.com", "AnotherPass1")

    async def test_register_invalid_email_fails(self, usecases):
        with pytest.raises(ValueError):
            await usecases.register("not-an-email", "SecurePass1")

    async def test_register_weak_password_fails(self, usecases):
        with pytest.raises(ValueError):
            await usecases.register("test@example.com", "123")


# --- Tests: Authenticate ---


@pytest.mark.unit
@pytest.mark.users
@pytest.mark.asyncio
class TestAuthenticate:
    async def test_authenticate_success(self, usecases):
        await usecases.register("test@example.com", "SecurePass1")

        user = await usecases.authenticate("test@example.com", "SecurePass1")

        assert user is not None
        assert user.email == "test@example.com"

    async def test_authenticate_wrong_password_fails(self, usecases):
        await usecases.register("test@example.com", "SecurePass1")

        with pytest.raises(ValueError, match="Неверный email или пароль"):
            await usecases.authenticate("test@example.com", "WrongPass1")

    async def test_authenticate_unknown_email_fails(self, usecases):
        with pytest.raises(ValueError, match="Неверный email или пароль"):
            await usecases.authenticate("unknown@example.com", "SecurePass1")
