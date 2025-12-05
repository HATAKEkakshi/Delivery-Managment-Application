from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_app(client:AsyncClient):
    response=await client.get("/health")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {"status": "ok server running"}
