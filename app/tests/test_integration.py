import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.tests.conftest import client


class TestIntegrationWorkflow:
    """Integration tests that test complete workflows"""
    
    async def test_complete_shipment_workflow(self, client: AsyncClient):
        """Test complete workflow: seller signup -> partner signup -> create shipment -> update -> track"""
        
        # 1. Create seller
        seller_data = {
            "name": "Integration Seller",
            "email": "integration_seller@test.com",
            "password": "testpass123"
        }
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 200
        
        # 2. Login seller
        login_data = {
            "username": seller_data["email"],
            "password": seller_data["password"]
        }
        response = await client.post("/seller/token", data=login_data)
        assert response.status_code == 200
        seller_token = response.json()["access_token"]
        
        # 3. Create delivery partner
        partner_data = {
            "name": "Integration Partner",
            "email": "integration_partner@test.com",
            "password": "testpass123",
            "serviceable_zip_codes": [11001, 11002, 11003],
            "max_handling_capacity": 10
        }
        response = await client.post("/partner/signup", json=partner_data)
        assert response.status_code == 200
        
        # 4. Login partner
        login_data = {
            "username": partner_data["email"],
            "password": partner_data["password"]
        }
        response = await client.post("/partner/token", data=login_data)
        assert response.status_code == 200
        partner_token = response.json()["access_token"]
        
        # 5. Create shipment
        shipment_data = {
            "content": "Integration Test Package",
            "weight": 3.0,
            "destination": 11002,
            "client_email_id": "client@integration.com",
            "client_contact_phone": "+1234567890"
        }
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = await client.post("/shipment/", json=shipment_data, headers=headers)
        assert response.status_code == 200
        shipment = response.json()
        shipment_id = shipment["id"]
        
        # 6. Update shipment status (partner)
        update_data = {
            "location": 11001,
            "description": "Package picked up from seller",
            "status": "IN_TRANSIT"
        }
        headers = {"Authorization": f"Bearer {partner_token}"}
        response = await client.patch(f"/shipment/?id={shipment_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_shipment = response.json()
        
        # 7. Verify timeline was updated
        assert len(updated_shipment["timeline"]) > len(shipment["timeline"])
        latest_event = updated_shipment["timeline"][-1]
        assert latest_event["location"] == 11001
        assert latest_event["description"] == "Package picked up from seller"
        
        # 8. Track shipment (public endpoint)
        response = await client.get(f"/shipment/?id={shipment_id}")
        assert response.status_code == 200
        tracked_shipment = response.json()
        assert tracked_shipment["id"] == shipment_id
        
        # 9. Cancel shipment (seller)
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = await client.get(f"/shipment/cancel?id={shipment_id}", headers=headers)
        assert response.status_code == 200
        cancelled_shipment = response.json()
        
        # 10. Verify cancellation
        assert any(event["status"] == "CANCELLED" for event in cancelled_shipment["timeline"])

    async def test_unauthorized_access_workflow(self, client: AsyncClient):
        """Test that unauthorized access is properly blocked"""
        
        # Try to create shipment without authentication
        shipment_data = {
            "content": "Unauthorized Package",
            "weight": 1.0,
            "destination": 11001,
            "client_email_id": "client@test.com"
        }
        response = await client.post("/shipment/", json=shipment_data)
        assert response.status_code == 401
        
        # Try to update shipment without authentication
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {
            "location": 11001,
            "description": "Unauthorized update"
        }
        response = await client.patch(f"/shipment/?id={fake_id}", json=update_data)
        assert response.status_code == 401
        
        # Try to cancel shipment without authentication
        response = await client.get(f"/shipment/cancel?id={fake_id}")
        assert response.status_code == 401

    async def test_cross_user_access_prevention(self, client: AsyncClient):
        """Test that users cannot access each other's resources inappropriately"""
        
        # Create two sellers
        seller1_data = {
            "name": "Seller One",
            "email": "seller1@test.com",
            "password": "testpass123"
        }
        seller2_data = {
            "name": "Seller Two",
            "email": "seller2@test.com",
            "password": "testpass123"
        }
        
        await client.post("/seller/signup", json=seller1_data)
        await client.post("/seller/signup", json=seller2_data)
        
        # Login both sellers
        response = await client.post("/seller/token", data={
            "username": seller1_data["email"],
            "password": seller1_data["password"]
        })
        seller1_token = response.json()["access_token"]
        
        response = await client.post("/seller/token", data={
            "username": seller2_data["email"],
            "password": seller2_data["password"]
        })
        seller2_token = response.json()["access_token"]
        
        # Seller 1 creates a shipment
        shipment_data = {
            "content": "Seller 1 Package",
            "weight": 1.0,
            "destination": 11001,
            "client_email_id": "client1@test.com"
        }
        headers = {"Authorization": f"Bearer {seller1_token}"}
        response = await client.post("/shipment/", json=shipment_data, headers=headers)
        assert response.status_code == 200
        shipment_id = response.json()["id"]
        
        # Seller 2 tries to cancel Seller 1's shipment (should fail)
        headers = {"Authorization": f"Bearer {seller2_token}"}
        response = await client.get(f"/shipment/cancel?id={shipment_id}", headers=headers)
        # This should either be 403 (forbidden) or 404 (not found for this user)
        assert response.status_code in [403, 404]

    async def test_data_validation_workflow(self, client: AsyncClient):
        """Test various data validation scenarios"""
        
        # Create and login seller
        seller_data = {
            "name": "Validation Seller",
            "email": "validation@test.com",
            "password": "testpass123"
        }
        await client.post("/seller/signup", json=seller_data)
        
        response = await client.post("/seller/token", data={
            "username": seller_data["email"],
            "password": seller_data["password"]
        })
        seller_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {seller_token}"}
        
        # Test various invalid shipment data
        invalid_shipments = [
            {
                "content": "",  # Empty content
                "weight": 1.0,
                "destination": 11001,
                "client_email_id": "client@test.com"
            },
            {
                "content": "Valid Content",
                "weight": -1.0,  # Negative weight
                "destination": 11001,
                "client_email_id": "client@test.com"
            },
            {
                "content": "Valid Content",
                "weight": 1.0,
                "destination": 0,  # Invalid destination
                "client_email_id": "client@test.com"
            },
            {
                "content": "Valid Content",
                "weight": 1.0,
                "destination": 11001,
                "client_email_id": "invalid-email"  # Invalid email
            }
        ]
        
        for invalid_data in invalid_shipments:
            response = await client.post("/shipment/", json=invalid_data, headers=headers)
            assert response.status_code == 422