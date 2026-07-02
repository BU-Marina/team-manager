import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.evaluations
@pytest.mark.asyncio
class TestEvaluationsAPI:
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

    async def test_create_evaluation(self, client: AsyncClient):
        token = await self._register_and_login(
            client, "eval_creator@test.com", "SecurePass1"
        )
        member_token = await self._register_and_login(
            client, "eval_member@test.com", "SecurePass1"
        )

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

        # Оценка
        response = await client.post(
            "/api/evaluations/",
            json={"task_id": task_id, "score": 4, "comment": "Good work"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 4
        assert data["comment"] == "Good work"

    async def test_invalid_score_fails(self, client: AsyncClient):
        token = await self._register_and_login(
            client, "eval_creator2@test.com", "SecurePass1"
        )
        member_token = await self._register_and_login(
            client, "eval_member2@test.com", "SecurePass1"
        )

        create_team_resp = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {token}"},
        )
        code = create_team_resp.json()["code"]
        team_id = create_team_resp.json()["id"]

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

        response = await client.post(
            "/api/evaluations/",
            json={"task_id": task_id, "score": 10},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    async def test_average_score(self, client: AsyncClient):
        token = await self._register_and_login(client, "avg@test.com", "SecurePass1")

        create_team = await client.post(
            "/api/teams/",
            json={"name": "Team"},
            headers={"Authorization": f"Bearer {token}"},
        )
        team_id = create_team.json()["id"]

        me = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
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
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_task.json()["id"]

        await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "start"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            f"/api/tasks/{task_id}/status",
            json={"action": "complete"},
            headers={"Authorization": f"Bearer {token}"},
        )

        await client.post(
            "/api/evaluations/",
            json={"task_id": task_id, "score": 4},
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = await client.get(
            f"/api/evaluations/average/{my_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["average_score"] == 4.0
