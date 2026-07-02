import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.meetings
@pytest.mark.asyncio
class TestMeetingsAPI:
    async def test_schedule_meeting(self, client: AsyncClient, manager_token: str):
        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        team_id = create_team_resp.json()["id"]
        code = create_team_resp.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {manager_token}"},
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
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Sprint Review"

    async def test_schedule_conflict_fails(
        self, client: AsyncClient, manager_token: str
    ):
        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        team_id = create_team_resp.json()["id"]
        code = create_team_resp.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {manager_token}"},
        )

        now = datetime.now()
        start = now + timedelta(days=2)
        end = start + timedelta(hours=1)

        await client.post(
            "/api/meetings/",
            json={
                "title": "First",
                "team_id": team_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            headers={"Authorization": f"Bearer {manager_token}"},
        )

        response = await client.post(
            "/api/meetings/",
            json={
                "title": "Second",
                "team_id": team_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 400
