from .entities import Team
from .value_objects import TeamCode
from .interfaces import TeamRepository
from ..users.interfaces import UserRepository
from ..users.entities import User


class TeamUseCases:
    def __init__(self, team_repo: TeamRepository, user_repo: UserRepository):
        self._team_repo = team_repo
        self._user_repo = user_repo

    async def create_team(self, name: str, owner_id: int) -> Team:
        user = await self._user_repo.get_by_id(owner_id)
        if not user:
            raise ValueError("Пользователь не найден")
        team = Team.create(name=name, owner_id=owner_id)
        await self._team_repo.save(team)
        return team

    async def join_team(self, user_id: int, code: str) -> Team:
        team_code = TeamCode(code)
        team = await self._team_repo.get_by_code(team_code)
        if not team:
            raise ValueError("Команда с таким кодом не найдена")
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        user.join_team(team.id)
        await self._user_repo.save(user)
        return team

    async def get_user_teams(self, user_id: int) -> list[Team]:
        return await self._team_repo.get_by_user(user_id)

    async def get_team_members(self, team_id: int) -> list[User]:
        return await self._team_repo.get_members(team_id)
