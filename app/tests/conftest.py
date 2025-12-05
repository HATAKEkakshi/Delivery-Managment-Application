import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
from main import app
from app.database.session import get_session
from app.database.model import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import patch

# Monkey patch ARRAY type for SQLite compatibility in tests
from sqlalchemy.types import TypeDecorator, Text
import json

class ArrayType(TypeDecorator):
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

# Override ARRAY for testing
original_array = postgresql.ARRAY
postgresql.ARRAY = lambda *args, **kwargs: ArrayType()

engine=create_async_engine(
    url="sqlite+aiosqlite:///:memory:",
    echo=False,
)
test_session=async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False)
async def get_session_override():
    async with test_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
    
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    print("🧪 starting tests...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Override the database session
    app.dependency_overrides[get_session] = get_session_override
    
    # Mock email sending for tests
    with patch('app.worker.tasks.send_email_template.delay') as mock_email:
        mock_email.return_value = None
        yield
    
    # Clean up
    app.dependency_overrides.clear()
    print("✅ tests completed!")