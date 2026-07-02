import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.evaluations
@pytest.mark.asyncio
class TestEvaluationsAPI:
    async def test_create_evaluation(
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

        response = await client.post(
            "/api/evaluations/",
            json={"task_id": task_id, "score": 4, "comment": "Good work"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 4
        assert data["comment"] == "Good work"

    async def test_invalid_score_fails(
        self, client: AsyncClient, manager_token: str, member_token: str
    ):
        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        code = create_team_resp.json()["code"]
        team_id = create_team_resp.json()["id"]

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

        response = await client.post(
            "/api/evaluations/",
            json={"task_id": task_id, "score": 10},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 422

    async def test_average_score(self, client: AsyncClient, manager_token: str):
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

        await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "start"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "complete"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )

        await client.post(
            "/api/evaluations/",
            json={"task_id": task_id, "score": 4},
            headers={"Authorization": f"Bearer {manager_token}"},
        )

        resp = await client.get(
            f"/api/evaluations/average/{my_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["average_score"] == 4.0
