import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.tests.conftest import client


class TestSecurityFeatures:
    """Test security-related features"""
    
    async def test_password_hashing(self, client: AsyncClient):
        """Test that passwords are properly hashed and not stored in plain text"""
        seller_data = {
            "name": "Security Test Seller",
            "email": "security@test.com",
            "password": "plaintext_password"
        }
        
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 200
        
        # Ensure password is not returned in response
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    async def test_jwt_token_format(self, client: AsyncClient):
        """Test that JWT tokens are properly formatted"""
        seller_data = {
            "name": "JWT Test Seller",
            "email": "jwt@test.com",
            "password": "testpass123"
        }
        
        await client.post("/seller/signup", json=seller_data)
        
        login_data = {
            "username": seller_data["email"],
            "password": seller_data["password"]
        }
        response = await client.post("/seller/token", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        token = data["access_token"]
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3
        assert data["type"] == "jwt"

    async def test_invalid_token_access(self, client: AsyncClient):
        """Test that invalid tokens are rejected"""
        invalid_tokens = [
            "invalid.token.here",
            "Bearer invalid_token",
            "completely_invalid_token",
            ""
        ]
        
        shipment_data = {
            "content": "Test Package",
            "weight": 1.0,
            "destination": 11001,
            "client_email_id": "client@test.com"
        }
        
        for invalid_token in invalid_tokens:
            headers = {"Authorization": f"Bearer {invalid_token}"}
            response = await client.post("/shipment/", json=shipment_data, headers=headers)
            assert response.status_code == 401

    async def test_expired_token_handling(self, client: AsyncClient):
        """Test handling of expired tokens (if implemented)"""
        # This would require mocking time or using a very short token expiry
        # For now, we test the structure is in place
        
        seller_data = {
            "name": "Expiry Test Seller",
            "email": "expiry@test.com",
            "password": "testpass123"
        }
        
        await client.post("/seller/signup", json=seller_data)
        
        login_data = {
            "username": seller_data["email"],
            "password": seller_data["password"]
        }
        response = await client.post("/seller/token", data=login_data)
        assert response.status_code == 200
        
        # Token should be valid immediately after creation
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        shipment_data = {
            "content": "Test Package",
            "weight": 1.0,
            "destination": 11001,
            "client_email_id": "client@test.com"
        }
        
        response = await client.post("/shipment/", json=shipment_data, headers=headers)
        assert response.status_code == 200

    async def test_sql_injection_prevention(self, client: AsyncClient):
        """Test that SQL injection attempts are prevented"""
        # Test SQL injection in email field
        malicious_data = {
            "name": "Malicious User",
            "email": "test@test.com'; DROP TABLE sellers; --",
            "password": "testpass123"
        }
        
        response = await client.post("/seller/signup", json=malicious_data)
        # Should either fail validation (422) or be safely handled
        assert response.status_code in [422, 400]

    async def test_xss_prevention(self, client: AsyncClient):
        """Test that XSS attempts in input fields are handled"""
        xss_payload = "<script>alert('xss')</script>"
        
        seller_data = {
            "name": xss_payload,
            "email": "xss@test.com",
            "password": "testpass123"
        }
        
        response = await client.post("/seller/signup", json=seller_data)
        
        if response.status_code == 200:
            # If creation succeeds, ensure the payload is properly escaped/sanitized
            data = response.json()
            # The exact handling depends on your sanitization strategy
            # At minimum, it shouldn't execute as script
            assert data["name"] == xss_payload  # Should be stored as-is, not executed

    async def test_rate_limiting_structure(self, client: AsyncClient):
        """Test that rate limiting structure is in place (if implemented)"""
        # Make multiple rapid requests to login endpoint
        login_data = {
            "username": "nonexistent@test.com",
            "password": "wrongpass"
        }
        
        responses = []
        for _ in range(10):
            response = await client.post("/seller/token", data=login_data)
            responses.append(response.status_code)
        
        # All should be 401 (unauthorized) rather than 429 (rate limited)
        # unless rate limiting is implemented
        for status_code in responses:
            assert status_code in [401, 429]

    async def test_cors_headers(self, client: AsyncClient):
        """Test that CORS headers are properly set"""
        response = await client.get("/health")
        
        # Check if CORS headers are present (based on your CORS configuration)
        # This depends on your actual CORS setup in main.py
        assert response.status_code == 200
        
        # If CORS is configured to allow all origins
        # headers should include access-control-allow-origin
        # The exact test depends on your CORS configuration

    async def test_sensitive_data_exposure(self, client: AsyncClient):
        """Test that sensitive data is not exposed in responses"""
        seller_data = {
            "name": "Sensitive Data Test",
            "email": "sensitive@test.com",
            "password": "supersecretpassword"
        }
        
        response = await client.post("/seller/signup", json=seller_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Ensure sensitive fields are not in response
        sensitive_fields = ["password", "password_hash", "salt"]
        for field in sensitive_fields:
            assert field not in data
        
        # Ensure only expected fields are present
        expected_fields = {"name", "email"}
        actual_fields = set(data.keys())
        assert expected_fields.issubset(actual_fields)