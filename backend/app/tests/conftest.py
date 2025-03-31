import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL environment variable is not set")

@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool
    )
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def setup_db(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(async_engine, setup_db):
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_url():
    return "https://www.youtube.com/watch?v=R_wscUcbynk"

@pytest_asyncio.fixture
async def create_url(client, test_url):
    test_obj = {"original_url": test_url, "custom_suffix": "Mario"}
    response = await client.post("/shorten", json=test_obj)
    return response.json()