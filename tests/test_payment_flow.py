import pytest
import httpx
import uuid

from app.main import app
from app.models import payment


@pytest.mark.asyncio
async def test_payment_flow():

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        # 1. Register
        test_id = uuid.uuid4().hex[:8]

        email = f"payment_test_{test_id}@gmail.com"
        username = f"payment_test_{test_id}"
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

        # 2. Login
        login_response = await client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password
            }
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        headers = {
            "Authorization": f"Bearer {token}"
        }
                # 3. Create Plan
        plan_response = await client.post(
            "/plans/",
            headers=headers,
            json={
                "name": f"Test Plan {test_id}",
                "description": "Automated payment flow test",
                "price": "1499.00",
                "billing_interval": "monthly",
                "is_active": True
            }
        )

        assert plan_response.status_code == 200

        plan = plan_response.json()
        plan_id = plan["id"]

        # 4. Create Subscription
        subscription_response = await client.post(
            "/subscriptions",
            headers=headers,
            json={
                "plan_id": plan_id
            }
        )

        assert subscription_response.status_code == 200

        subscription = subscription_response.json()
        subscription_id = subscription["id"]

        assert subscription["status"] == "PENDING"
        assert subscription["amount"] == "1499.00"

        # 5. Create Payment
        payment_response = await client.post(
            "/payments",
            headers=headers,
            json={
                "subscription_id": subscription_id,
                "idempotency_key": f"test-{test_id}"
            }
        )

        assert payment_response.status_code == 200

        payment = payment_response.json()

        payment_id = payment["id"]

        assert payment["status"] == "PENDING"
        assert payment["amount"] == 1499.0

        # 5. Create Payment
        payment_response = await client.post(
            "/payments",
            headers=headers,
            json={
                "subscription_id": subscription_id,
                "idempotency_key": f"test-{test_id}"
            }
        )

        assert payment_response.status_code == 200

        payment = payment_response.json()

        payment_id = payment["id"]

        assert payment["status"] == "PENDING"
        assert payment["amount"] == 1499.0

        # 6. Idempotency test
        duplicate_payment_response = await client.post(
            "/payments",
            headers=headers,
            json={
                "subscription_id": subscription_id,
                "idempotency_key": f"test-{test_id}"
            }
        )

        assert duplicate_payment_response.status_code == 200

        duplicate_payment = duplicate_payment_response.json()

        assert duplicate_payment["id"] == payment_id
        assert duplicate_payment["status"] == "PENDING"

        # 7. Mark payment as SUCCESS
        success_response = await client.patch(
            f"/payments/{payment_id}/success",
            headers=headers
        )

        assert success_response.status_code == 200

        success_payment = success_response.json()

        assert success_payment["id"] == payment_id
        assert success_payment["status"] == "SUCCESS"

        # 8. Verify subscription became ACTIVE
        subscription_response = await client.get(
            f"/subscriptions/{subscription_id}",
            headers=headers
        )

        assert subscription_response.status_code == 200

        active_subscription = subscription_response.json()

        assert active_subscription["id"] == subscription_id
        assert active_subscription["status"] == "ACTIVE"
        assert active_subscription["started_at"] is not None
        assert active_subscription["expires_at"] is not None

        
        # 9. Create second user for failed payment test
        failed_test_id = uuid.uuid4().hex[:8]

        failed_email = f"failed_payment_{failed_test_id}@gmail.com"
        failed_username = f"failed_payment_{failed_test_id}"
        failed_password = "test@123"

        failed_register_response = await client.post(
            "/auth/register",
            json={
                "username": failed_username,
                "email": failed_email,
                "password": failed_password
            }
        )

        assert failed_register_response.status_code == 200

        failed_login_response = await client.post(
            "/auth/login",
            data={
                "username": failed_email,
                "password": failed_password
            }
        )

        assert failed_login_response.status_code == 200

        failed_token = failed_login_response.json()["access_token"]

        failed_headers = {
            "Authorization": f"Bearer {failed_token}"
        }
                
                

        # 10. Create subscription for failed payment test
        failed_subscription_response = await client.post(
            "/subscriptions",
            headers=failed_headers,
            json={
                "plan_id": plan_id
            }
        )

        assert failed_subscription_response.status_code == 200

        failed_subscription = failed_subscription_response.json()
        failed_subscription_id = failed_subscription["id"]

        assert failed_subscription["status"] == "PENDING"

        # 11. Create payment for failed payment test
        failed_payment_response = await client.post(
            "/payments",
            headers=failed_headers,
            json={
                "subscription_id": failed_subscription_id,
                "idempotency_key": f"failed-{failed_test_id}"
            }
        )

        assert failed_payment_response.status_code == 200

        failed_payment = failed_payment_response.json()
        failed_payment_id = failed_payment["id"]

        assert failed_payment["status"] == "PENDING"