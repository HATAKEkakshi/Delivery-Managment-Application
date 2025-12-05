import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.tests.conftest import client


class TestHealthEndpoint:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok server running"

    async def test_health_check_method_not_allowed(self, client: AsyncClient):
        response = await client.post("/health")
        assert response.status_code == 405

    async def test_health_check_response_format(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert isinstance(data["status"], str)