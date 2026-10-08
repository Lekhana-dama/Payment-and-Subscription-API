import pytest
import httpx
from app.main import app
import uuid


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.get("/payments/")

        assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_and_login():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        test_id = uuid.uuid4().hex[:8]

        email = f"auth_login_{test_id}@gmail.com"
        username = f"auth_login_{test_id}"
        password = "test@123"

        register_response = await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )

        assert register_response.status_code == 200

        login_response = await client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password
            }
        )

        assert login_response.status_code == 200
@pytest.mark.asyncio
async def test_jwt_protected_endpoint():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        test_id = uuid.uuid4().hex[:8]

        email = f"jwt_protected_{test_id}@gmail.com"
        username = f"jwt_protected_{test_id}"
        password = "test@123"

        register_response = await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )

        assert register_response.status_code == 200

        login_response = await client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password
            }
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        response = await client.get(
            "/payments/",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 200