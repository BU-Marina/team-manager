import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.tasks
@pytest.mark.asyncio
class TestTasksAPI:
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

    async def test_create_task(self, client: AsyncClient):
        token = await self._register_and_login(
            client, "creator@test.com", "SecurePass1"
        )
        member_token = await self._register_and_login(
            client, "member@test.com", "SecurePass1"
        )

        # Создаём команду
        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {token}"},
        )
        team_id = create_team_resp.json()["id"]
        code = create_team_resp.json()["code"]

        # Участник вступает в команду
        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {member_token}"},
        )

        # Получаем id участника
        me_resp = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {member_token}"}
        )
        member_id = me_resp.json()["id"]

        # Создаём задачу
        response = await client.post(
            "/api/tasks/",
            json={
                "title": "Test Task",
                "description": "Description",
                "assignee_id": member_id,
                "team_id": team_id,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["status"] == "open"

    async def test_start_and_complete_task(self, client: AsyncClient):
        token = await self._register_and_login(
            client, "creator2@test.com", "SecurePass1"
        )
        member_token = await self._register_and_login(
            client, "member2@test.com", "SecurePass1"
        )

        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team2"},
            headers={"Authorization": f"Bearer {token}"},
        )
        team_id = create_team_resp.json()["id"]
        code = create_team_resp.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {member_token}"},
        )

        me_resp = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {member_token}"}
        )
        member_id = me_resp.json()["id"]

        create_resp = await client.post(
            "/api/tasks/",
            json={
                "title": "Task",
                "description": "Desc",
                "assignee_id": member_id,
                "team_id": team_id,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["id"]

        # Старт задачи
        start_resp = await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "start"},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert start_resp.status_code == 200
        assert start_resp.json()["status"] == "in_progress"

        # Завершение задачи
        complete_resp = await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "complete"},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "done"
