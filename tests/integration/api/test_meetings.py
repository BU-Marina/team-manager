import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.meetings
@pytest.mark.asyncio
class TestMeetingsAPI:
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

    async def test_schedule_meeting(self, client: AsyncClient):
        token = await self._register_and_login(client, "org@test.com", "SecurePass1")

        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {token}"},
        )
        team_id = create_team_resp.json()["id"]
        code = create_team_resp.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {token}"},
        )

        now = datetime.now()
        response = await client.post(
            "/api/meetings/",
            json={
                "title": "Sprint Review",
                "team_id": team_id,
                "start_time": (now + timedelta(days=1)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Sprint Review"

    async def test_schedule_conflict_fails(self, client: AsyncClient):
        token = await self._register_and_login(client, "org2@test.com", "SecurePass1")

        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {token}"},
        )
        team_id = create_team_resp.json()["id"]
        code = create_team_resp.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {token}"},
        )

        now = datetime.now()
        start = now + timedelta(days=2)
        end = start + timedelta(hours=1)

        # Первая встреча
        await client.post(
            "/api/meetings/",
            json={
                "title": "First",
                "team_id": team_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Конфликт
        response = await client.post(
            "/api/meetings/",
            json={
                "title": "Second",
                "team_id": team_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
