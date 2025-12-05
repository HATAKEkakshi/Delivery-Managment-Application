import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.tests.conftest import client


@pytest_asyncio.fixture
async def seller_data():
    return {
        "name": "Test Seller",
        "email": "seller@test.com",
        "password": "testpass123"
    }


@pytest_asyncio.fixture
async def registered_seller(client: AsyncClient, seller_data):
    response = await client.post("/seller/signup", json=seller_data)
    return response.json()


class TestSellerAuth:
    async def test_seller_signup(self, client: AsyncClient, seller_data):
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == seller_data["name"]
        assert data["email"] == seller_data["email"]
        assert "password" not in data

    async def test_seller_signup_duplicate_email(self, client: AsyncClient, seller_data):
        # First signup
        await client.post("/seller/signup", json=seller_data)
        # Second signup with same email
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 400

    async def test_seller_login_valid_credentials(self, client: AsyncClient, registered_seller, seller_data):
        login_data = {
            "username": seller_data["email"],
            "password": seller_data["password"]
        }
        response = await client.post("/seller/token", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["type"] == "jwt"

    async def test_seller_login_invalid_credentials(self, client: AsyncClient):
        login_data = {
            "username": "wrong@email.com",
            "password": "wrongpass"
        }
        response = await client.post("/seller/token", data=login_data)
        assert response.status_code == 401

    async def test_seller_login_wrong_password(self, client: AsyncClient, registered_seller, seller_data):
        login_data = {
            "username": seller_data["email"],
            "password": "wrongpassword"
        }
        response = await client.post("/seller/token", data=login_data)
        assert response.status_code == 401


class TestSellerValidation:
    async def test_seller_signup_invalid_email(self, client: AsyncClient):
        seller_data = {
            "name": "Test Seller",
            "email": "invalid-email",
            "password": "testpass123"
        }
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 422

    async def test_seller_signup_missing_fields(self, client: AsyncClient):
        seller_data = {
            "name": "Test Seller"
            # Missing email and password
        }
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 422

    async def test_seller_signup_empty_password(self, client: AsyncClient):
        seller_data = {
            "name": "Test Seller",
            "email": "seller@test.com",
            "password": ""
        }
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 422