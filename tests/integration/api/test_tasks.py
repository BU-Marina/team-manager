import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.tasks
@pytest.mark.asyncio
class TestTasksAPI:
    async def test_create_task(
        self, client: AsyncClient, manager_token: str, member_token: str
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
        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {member_token}"},
        )

        me_resp = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {member_token}"}
        )
        member_id = me_resp.json()["id"]

        response = await client.post(
            "/api/tasks/",
            json={
                "title": "Test Task",
                "description": "Description",
                "assignee_id": member_id,
                "team_id": team_id,
            },
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["status"] == "open"

    async def test_start_and_complete_task(
        self, client: AsyncClient, manager_token: str, member_token: str
    ):
        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team2"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        team_id = create_team_resp.json()["id"]
        code = create_team_resp.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
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
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        task_id = create_resp.json()["id"]

        start_resp = await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "start"},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert start_resp.status_code == 200
        assert start_resp.json()["status"] == "in_progress"

        complete_resp = await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "complete"},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "done"

    async def test_add_and_get_comments(self, client: AsyncClient, manager_token: str):
        create_team = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        team_id = create_team.json()["id"]
        code = create_team.json()["code"]

        await client.post(
            "/api/teams/join",
            json={"code": code},
            headers={"Authorization": f"Bearer {manager_token}"},
        )

        me = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {manager_token}"}
        )
        my_id = me.json()["id"]

        create_task = await client.post(
            "/api/tasks/",
            json={
                "title": "Task",
                "description": "Desc",
                "assignee_id": my_id,
                "team_id": team_id,
            },
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        task_id = create_task.json()["id"]

        resp = await client.post(
            f"/api/tasks/{task_id}/comments",
            json={"text": "Nice"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["text"] == "Nice"

        comments = await client.get(
            f"/api/tasks/{task_id}/comments",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert len(comments.json()) == 1

    async def test_create_task_as_member_fails(
        self, client: AsyncClient, member_token: str
    ):
        response = await client.post(
            "/api/tasks/",
            json={
                "title": "Task",
                "description": "Desc",
                "assignee_id": 1,
                "team_id": 1,
            },
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 403
        assert "Требуется роль" in response.json()["detail"]
