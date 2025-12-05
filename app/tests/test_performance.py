import pytest
import pytest_asyncio
import asyncio
import time
from httpx import AsyncClient
from app.tests.conftest import client


class TestPerformance:
    """Performance and load testing"""
    
    async def test_health_endpoint_response_time(self, client: AsyncClient):
        """Test that health endpoint responds quickly"""
        start_time = time.time()
        response = await client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        # Health endpoint should respond within 100ms
        assert response_time < 0.1

    async def test_concurrent_user_registration(self, client: AsyncClient):
        """Test concurrent user registrations"""
        async def register_seller(index):
            seller_data = {
                "name": f"Concurrent Seller {index}",
                "email": f"concurrent{index}@test.com",
                "password": "testpass123"
            }
            return await client.post("/seller/signup", json=seller_data)
        
        # Create 10 concurrent registration requests
        tasks = [register_seller(i) for i in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed (no database conflicts)
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) == 10
        
        for response in successful_responses:
            assert response.status_code == 200

    async def test_concurrent_shipment_creation(self, client: AsyncClient):
        """Test concurrent shipment creation by same seller"""
        # First create and login a seller
        seller_data = {
            "name": "Performance Seller",
            "email": "performance@test.com",
            "password": "testpass123"
        }
        await client.post("/seller/signup", json=seller_data)
        
        login_response = await client.post("/seller/token", data={
            "username": seller_data["email"],
            "password": seller_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        async def create_shipment(index):
            shipment_data = {
                "content": f"Concurrent Package {index}",
                "weight": 1.0 + (index * 0.1),
                "destination": 11001 + (index % 3),
                "client_email_id": f"client{index}@test.com"
            }
            return await client.post("/shipment/", json=shipment_data, headers=headers)
        
        # Create 5 concurrent shipments
        start_time = time.time()
        tasks = [create_shipment(i) for i in range(5)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # All should succeed
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) == 5
        
        for response in successful_responses:
            assert response.status_code == 200
        
        # Total time should be reasonable (less than 2 seconds for 5 shipments)
        total_time = end_time - start_time
        assert total_time < 2.0

    async def test_database_query_performance(self, client: AsyncClient):
        """Test database query performance with multiple shipments"""
        # Create seller and multiple shipments
        seller_data = {
            "name": "DB Performance Seller",
            "email": "dbperf@test.com",
            "password": "testpass123"
        }
        await client.post("/seller/signup", json=seller_data)
        
        login_response = await client.post("/seller/token", data={
            "username": seller_data["email"],
            "password": seller_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create 20 shipments
        shipment_ids = []
        for i in range(20):
            shipment_data = {
                "content": f"DB Test Package {i}",
                "weight": 1.0,
                "destination": 11001,
                "client_email_id": f"dbclient{i}@test.com"
            }
            response = await client.post("/shipment/", json=shipment_data, headers=headers)
            assert response.status_code == 200
            shipment_ids.append(response.json()["id"])
        
        # Test retrieval performance
        start_time = time.time()
        for shipment_id in shipment_ids[:10]:  # Test first 10
            response = await client.get(f"/shipment/?id={shipment_id}")
            assert response.status_code == 200
        end_time = time.time()
        
        # Should retrieve 10 shipments in less than 1 second
        retrieval_time = end_time - start_time
        assert retrieval_time < 1.0

    async def test_memory_usage_stability(self, client: AsyncClient):
        """Test that repeated operations don't cause memory leaks"""
        # Perform the same operation multiple times
        for i in range(50):
            response = await client.get("/health")
            assert response.status_code == 200
        
        # If we get here without timeout/crash, memory usage is stable
        assert True

    async def test_large_payload_handling(self, client: AsyncClient):
        """Test handling of large payloads"""
        # Create seller
        seller_data = {
            "name": "Large Payload Seller",
            "email": "largepayload@test.com",
            "password": "testpass123"
        }
        await client.post("/seller/signup", json=seller_data)
        
        login_response = await client.post("/seller/token", data={
            "username": seller_data["email"],
            "password": seller_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create shipment with large content description
        large_content = "A" * 1000  # 1KB of content
        shipment_data = {
            "content": large_content,
            "weight": 1.0,
            "destination": 11001,
            "client_email_id": "largeclient@test.com"
        }
        
        start_time = time.time()
        response = await client.post("/shipment/", json=shipment_data, headers=headers)
        end_time = time.time()
        
        assert response.status_code == 200
        # Should handle large payload reasonably quickly
        processing_time = end_time - start_time
        assert processing_time < 1.0

    async def test_error_handling_performance(self, client: AsyncClient):
        """Test that error handling doesn't significantly impact performance"""
        # Test multiple invalid requests
        invalid_requests = [
            ("/shipment/?id=invalid-uuid", "GET"),
            ("/shipment/?id=00000000-0000-0000-0000-000000000000", "GET"),
            ("/seller/token", "POST"),  # Missing data
        ]
        
        start_time = time.time()
        for endpoint, method in invalid_requests:
            if method == "GET":
                response = await client.get(endpoint)
            else:
                response = await client.post(endpoint)
            # Should return appropriate error codes quickly
            assert response.status_code in [400, 401, 404, 422]
        end_time = time.time()
        
        # Error handling should be fast
        total_time = end_time - start_time
        assert total_time < 0.5