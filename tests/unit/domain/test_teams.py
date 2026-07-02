import pytest
from src.domain.teams.entities import Team
from src.domain.teams.value_objects import TeamCode
from src.domain.teams.interfaces import TeamRepository
from src.domain.users.entities import User
from src.domain.users.value_objects import Email
from src.domain.users.interfaces import UserRepository
from src.domain.teams.usecases import TeamUseCases


# --- Fakes ---


class FakeTeamRepository(TeamRepository):
    def __init__(self):
        self._teams: dict[int, Team] = {}
        self._by_code: dict[str, Team] = {}
        self._next_id = 1

    async def get_by_id(self, team_id: int) -> Team | None:
        return self._teams.get(team_id)

    async def get_by_code(self, code: TeamCode) -> Team | None:
        return self._by_code.get(str(code))

    async def save(self, team: Team) -> None:
        if team.id is None:
            team.id = self._next_id
            self._next_id += 1
        self._teams[team.id] = team
        self._by_code[str(team.code)] = team

    async def delete(self, team: Team) -> None:
        self._teams.pop(team.id, None)
        self._by_code.pop(str(team.code), None)


class FakeUserRepository(UserRepository):
    def __init__(self):
        self._users: dict[int, User] = {}
        self._by_email: dict[str, User] = {}
        self._next_id = 1

    async def get_by_email(self, email: Email) -> User | None:
        return self._by_email.get(str(email))

    async def save(self, user: User) -> None:
        if user.id is None:
            user.id = self._next_id
            self._next_id += 1
        self._users[user.id] = user
        self._by_email[user.email] = user

    async def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    async def delete(self, user: User) -> None:
        self._users.pop(user.id, None)
        self._by_email.pop(user.email, None)


# --- Fixtures ---


@pytest.fixture
def user_repo():
    return FakeUserRepository()


@pytest.fixture
def team_repo():
    return FakeTeamRepository()


@pytest.fixture
def usecases(team_repo, user_repo):
    return TeamUseCases(team_repo=team_repo, user_repo=user_repo)


# --- Tests ---


@pytest.mark.unit
@pytest.mark.teams
@pytest.mark.asyncio
class TestCreateTeam:
    async def test_create_team_success(self, usecases, team_repo, user_repo):
        owner = User.create(email=Email("owner@test.com"), hashed_password="hashed")
        await user_repo.save(owner)

        team = await usecases.create_team(name="Dream Team", owner_id=owner.id)

        assert team.name == "Dream Team"
        assert team.owner_id == owner.id
        assert str(team.code)  # код сгенерирован

    async def test_create_team_user_not_found(self, usecases):
        with pytest.raises(ValueError, match="Пользователь не найден"):
            await usecases.create_team(name="Team", owner_id=999)


@pytest.mark.unit
@pytest.mark.teams
@pytest.mark.asyncio
class TestJoinTeam:
    async def test_join_team_success(self, usecases, team_repo, user_repo):
        owner = User.create(email=Email("owner@test.com"), hashed_password="hashed")
        member = User.create(email=Email("member@test.com"), hashed_password="hashed")
        await user_repo.save(owner)
        await user_repo.save(member)

        team = await usecases.create_team(name="Team", owner_id=owner.id)

        joined = await usecases.join_team(user_id=member.id, code=str(team.code))

        assert joined.id == team.id
        updated_member = await user_repo.get_by_id(member.id)
        assert updated_member.team_id == team.id

    async def test_join_team_invalid_code(self, usecases, user_repo):
        member = User.create(email=Email("member@test.com"), hashed_password="hashed")
        await user_repo.save(member)

        with pytest.raises(ValueError, match="Команда с таким кодом не найдена"):
            await usecases.join_team(user_id=member.id, code="WRONGCODE")
