import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    async def test_register_and_login(self, client: AsyncClient):
        # Регистрация
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "alice@test.com",
                "password": "SecurePass1",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "alice@test.com"

        # Логин
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "alice@test.com",
                "password": "SecurePass1",
            },
        )
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    async def test_register_duplicate_fails(self, client: AsyncClient):
        await client.post(
            "/api/auth/register",
            json={
                "email": "bob@test.com",
                "password": "SecurePass1",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "bob@test.com",
                "password": "SecurePass1",
            },
        )
        assert response.status_code == 400

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/api/auth/register",
            json={
                "email": "eve@test.com",
                "password": "SecurePass1",
            },
        )
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "eve@test.com",
                "password": "WrongPass1",
            },
        )
        assert response.status_code == 401
