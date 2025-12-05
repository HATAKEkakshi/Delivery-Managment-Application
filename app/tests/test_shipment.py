import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.tests.conftest import client


@pytest_asyncio.fixture
async def seller_token(client: AsyncClient):
    # Create and login seller
    seller_data = {
        "name": "Test Seller",
        "email": "seller@test.com",
        "password": "testpass123"
    }
    await client.post("/seller/signup", json=seller_data)
    
    login_data = {
        "username": seller_data["email"],
        "password": seller_data["password"]
    }
    response = await client.post("/seller/token", data=login_data)
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def partner_token(client: AsyncClient):
    # Create and login partner
    partner_data = {
        "name": "Test Partner",
        "email": "partner@test.com",
        "password": "testpass123",
        "serviceable_zip_codes": [11001, 11002, 11003],
        "max_handling_capacity": 5
    }
    await client.post("/partner/signup", json=partner_data)
    
    login_data = {
        "username": partner_data["email"],
        "password": partner_data["password"]
    }
    response = await client.post("/partner/token", data=login_data)
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def shipment_data():
    return {
        "content": "Test Package",
        "weight": 2.5,
        "destination": 11002,
        "client_email_id": "client@test.com",
        "client_contact_phone": "+1234567890"
    }


@pytest_asyncio.fixture
async def created_shipment(client: AsyncClient, seller_token, shipment_data):
    headers = {"Authorization": f"Bearer {seller_token}"}
    response = await client.post("/shipment/", json=shipment_data, headers=headers)
    return response.json()


class TestShipmentCreation:
    async def test_create_shipment_success(self, client: AsyncClient, seller_token, shipment_data):
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = await client.post("/shipment/", json=shipment_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == shipment_data["content"]
        assert data["weight"] == shipment_data["weight"]
        assert data["destination"] == shipment_data["destination"]
        assert "id" in data
        assert "timeline" in data
        assert "seller" in data

    async def test_create_shipment_unauthorized(self, client: AsyncClient, shipment_data):
        response = await client.post("/shipment/", json=shipment_data)
        assert response.status_code == 401

    async def test_create_shipment_invalid_data(self, client: AsyncClient, seller_token):
        headers = {"Authorization": f"Bearer {seller_token}"}
        invalid_data = {
            "content": "",  # Empty content
            "weight": -1,   # Negative weight
            "destination": 0,  # Invalid destination
            "client_email_id": "invalid-email"  # Invalid email
        }
        response = await client.post("/shipment/", json=invalid_data, headers=headers)
        assert response.status_code == 422

    async def test_create_shipment_missing_fields(self, client: AsyncClient, seller_token):
        headers = {"Authorization": f"Bearer {seller_token}"}
        incomplete_data = {
            "content": "Test Package"
            # Missing required fields
        }
        response = await client.post("/shipment/", json=incomplete_data, headers=headers)
        assert response.status_code == 422


class TestShipmentRetrieval:
    async def test_get_shipment_success(self, client: AsyncClient, created_shipment):
        shipment_id = created_shipment["id"]
        response = await client.get(f"/shipment/?id={shipment_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == shipment_id
        assert data["content"] == created_shipment["content"]

    async def test_get_shipment_not_found(self, client: AsyncClient):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/shipment/?id={fake_id}")
        assert response.status_code == 404

    async def test_get_shipment_invalid_id(self, client: AsyncClient):
        response = await client.get("/shipment/?id=invalid-uuid")
        assert response.status_code == 422


class TestShipmentTracking:
    async def test_track_shipment_success(self, client: AsyncClient, created_shipment):
        shipment_id = created_shipment["id"]
        response = await client.get(f"/shipment/track?id={shipment_id}")
        
        assert response.status_code == 200
        # This endpoint returns HTML, so we check content type
        assert "text/html" in response.headers.get("content-type", "")

    async def test_track_shipment_not_found(self, client: AsyncClient):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/shipment/track?id={fake_id}")
        assert response.status_code == 404


class TestShipmentUpdate:
    async def test_update_shipment_success(self, client: AsyncClient, created_shipment, partner_token):
        shipment_id = created_shipment["id"]
        headers = {"Authorization": f"Bearer {partner_token}"}
        
        update_data = {
            "location": 11001,
            "description": "Package picked up",
            "status": "IN_TRANSIT"
        }
        
        response = await client.patch(f"/shipment/?id={shipment_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["timeline"]) > len(created_shipment["timeline"])

    async def test_update_shipment_unauthorized(self, client: AsyncClient, created_shipment):
        shipment_id = created_shipment["id"]
        update_data = {
            "location": 11001,
            "description": "Unauthorized update"
        }
        
        response = await client.patch(f"/shipment/?id={shipment_id}", json=update_data)
        assert response.status_code == 401

    async def test_update_shipment_not_found(self, client: AsyncClient, partner_token):
        fake_id = "00000000-0000-0000-0000-000000000000"
        headers = {"Authorization": f"Bearer {partner_token}"}
        
        update_data = {
            "location": 11001,
            "description": "Update non-existent shipment"
        }
        
        response = await client.patch(f"/shipment/?id={fake_id}", json=update_data, headers=headers)
        assert response.status_code == 404


class TestShipmentCancellation:
    async def test_cancel_shipment_success(self, client: AsyncClient, created_shipment, seller_token):
        shipment_id = created_shipment["id"]
        headers = {"Authorization": f"Bearer {seller_token}"}
        
        response = await client.get(f"/shipment/cancel?id={shipment_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # Check if cancellation was recorded in timeline
        assert any(event["status"] == "CANCELLED" for event in data["timeline"])

    async def test_cancel_shipment_unauthorized(self, client: AsyncClient, created_shipment):
        shipment_id = created_shipment["id"]
        response = await client.get(f"/shipment/cancel?id={shipment_id}")
        assert response.status_code == 401

    async def test_cancel_shipment_not_found(self, client: AsyncClient, seller_token):
        fake_id = "00000000-0000-0000-0000-000000000000"
        headers = {"Authorization": f"Bearer {seller_token}"}
        
        response = await client.get(f"/shipment/cancel?id={fake_id}", headers=headers)
        assert response.status_code == 404