import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.teams
@pytest.mark.asyncio
class TestTeams:
    async def _register_and_login(
        self, client: AsyncClient, email: str, password: str
    ) -> str:
        await client.post(
            "/api/auth/register", json={"email": email, "password": password}
        )
        response = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        return response.json()["access_token"]

    async def test_create_team(self, client: AsyncClient):
        token = await self._register_and_login(client, "owner@test.com", "SecurePass1")

        response = await client.post(
            "/api/teams/",
            json={"name": "Dream Team"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Dream Team"
        assert "code" in data

    async def test_join_team(self, client: AsyncClient):
        owner_token = await self._register_and_login(
            client, "owner2@test.com", "SecurePass1"
        )
        member_token = await self._register_and_login(
            client, "member@test.com", "SecurePass1"
        )

        create_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        code = create_resp.json()["code"]

        join_resp = await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert join_resp.status_code == 200
