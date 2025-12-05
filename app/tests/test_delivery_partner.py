import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.tests.conftest import client


@pytest_asyncio.fixture
async def partner_data():
    return {
        "name": "Test Partner",
        "email": "partner@test.com",
        "password": "testpass123",
        "serviceable_zip_codes": [11001, 11002, 11003],
        "max_handling_capacity": 5
    }


@pytest_asyncio.fixture
async def registered_partner(client: AsyncClient, partner_data):
    response = await client.post("/partner/signup", json=partner_data)
    return response.json()


class TestDeliveryPartnerAuth:
    async def test_partner_signup(self, client: AsyncClient, partner_data):
        response = await client.post("/partner/signup", json=partner_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == partner_data["name"]
        assert data["email"] == partner_data["email"]
        assert data["serviceable_zip_codes"] == partner_data["serviceable_zip_codes"]
        assert data["max_handling_capacity"] == partner_data["max_handling_capacity"]
        assert "password" not in data

    async def test_partner_signup_duplicate_email(self, client: AsyncClient, partner_data):
        # First signup
        await client.post("/partner/signup", json=partner_data)
        # Second signup with same email
        response = await client.post("/partner/signup", json=partner_data)
        assert response.status_code == 400

    async def test_partner_login_valid_credentials(self, client: AsyncClient, registered_partner, partner_data):
        login_data = {
            "username": partner_data["email"],
            "password": partner_data["password"]
        }
        response = await client.post("/partner/token", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["type"] == "jwt"

    async def test_partner_login_invalid_credentials(self, client: AsyncClient):
        login_data = {
            "username": "wrong@email.com",
            "password": "wrongpass"
        }
        response = await client.post("/partner/token", data=login_data)
        assert response.status_code == 401


class TestDeliveryPartnerValidation:
    async def test_partner_signup_invalid_email(self, client: AsyncClient):
        partner_data = {
            "name": "Test Partner",
            "email": "invalid-email",
            "password": "testpass123",
            "serviceable_zip_codes": [11001],
            "max_handling_capacity": 5
        }
        response = await client.post("/partner/signup", json=partner_data)
        assert response.status_code == 422

    async def test_partner_signup_empty_zip_codes(self, client: AsyncClient):
        partner_data = {
            "name": "Test Partner",
            "email": "partner@test.com",
            "password": "testpass123",
            "serviceable_zip_codes": [],
            "max_handling_capacity": 5
        }
        response = await client.post("/partner/signup", json=partner_data)
        assert response.status_code == 422

    async def test_partner_signup_invalid_capacity(self, client: AsyncClient):
        partner_data = {
            "name": "Test Partner",
            "email": "partner@test.com",
            "password": "testpass123",
            "serviceable_zip_codes": [11001],
            "max_handling_capacity": 0
        }
        response = await client.post("/partner/signup", json=partner_data)
        assert response.status_code == 422

    async def test_partner_signup_missing_fields(self, client: AsyncClient):
        partner_data = {
            "name": "Test Partner",
            "email": "partner@test.com"
            # Missing password, serviceable_zip_codes, max_handling_capacity
        }
        response = await client.post("/partner/signup", json=partner_data)
        assert response.status_code == 422