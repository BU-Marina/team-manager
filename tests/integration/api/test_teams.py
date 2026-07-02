import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.teams
@pytest.mark.asyncio
class TestTeams:
    async def test_create_team(self, client: AsyncClient, manager_token: str):
        response = await client.post(
            "/api/teams/",
            json={"name": "Dream Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Dream Team"
        assert "code" in data

    async def test_join_team(
        self, client: AsyncClient, manager_token: str, member_token: str
    ):
        create_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        code = create_resp.json()["code"]

        join_resp = await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert join_resp.status_code == 200

    async def test_remove_member(
        self, client: AsyncClient, manager_token: str, member_token: str
    ):
        create_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        team_id = create_resp.json()["id"]
        code = create_resp.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {member_token}"},
        )

        me_resp = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {member_token}"}
        )
        member_id = me_resp.json()["id"]

        response = await client.delete(
            f"/api/teams/{team_id}/members/{member_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 204

    async def test_access_foreign_team_forbidden(
        self, client: AsyncClient, manager_token: str, member_token: str
    ):
        create_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        team_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/teams/{team_id}/members",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 403
