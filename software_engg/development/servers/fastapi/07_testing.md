# Testing FastAPI Applications

misssing
- magic mock
- deps mock
- app.state.

## TestClient (Sync)

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_create_user():
    response = client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com", "age": 30, "password": "Secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "password" not in data  # Filtered by response_model

def test_create_user_invalid():
    response = client.post(
        "/users",
        json={"name": "", "email": "bad-email", "age": -1},
    )
    assert response.status_code == 422  # Validation error

def test_get_user_not_found():
    response = client.get("/users/99999")
    assert response.status_code == 404

def test_list_users_pagination():
    response = client.get("/users?skip=0&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 5
```

---

## AsyncClient (httpx) — For Async Tests

```python
# tests/test_async.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_root(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_and_get_user(async_client: AsyncClient):
    # Create
    response = await async_client.post(
        "/users",
        json={"name": "Bob", "email": "bob@test.com", "age": 25, "password": "Pass1234"},
    )
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Get
    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Bob"
```

---

## Dependency Overrides

```python
# Override database dependency for testing
from db.dependency import get_db

async def get_test_db():
    """Use test database"""
    async with test_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

@pytest.fixture(autouse=True)
def override_deps():
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()

# Override auth dependency
async def mock_current_user():
    return User(id=1, name="Test User", email="test@test.com", role="admin")

@pytest.fixture
def authenticated_client():
    app.dependency_overrides[get_current_user] = mock_current_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
```

---

## Database Testing

```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from db.engine import Base

TEST_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/test_db"

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Create tables once for entire test session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    """Fresh session per test with rollback"""
    async with TestSession() as session:
        async with session.begin():
            yield session
        await session.rollback()  # Rollback after each test

@pytest.fixture
async def async_client(db_session):
    async def override_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
```

---

## Factory Pattern for Test Data

```python
# tests/factories.py
from db.models import User, Post
from faker import Faker

fake = Faker()

class UserFactory:
    @staticmethod
    async def create(session, **kwargs):
        defaults = {
            "name": fake.name(),
            "email": fake.email(),
            "hashed_password": "fakehash123",
            "is_active": True,
        }
        defaults.update(kwargs)
        user = User(**defaults)
        session.add(user)
        await session.flush()
        return user

class PostFactory:
    @staticmethod
    async def create(session, author=None, **kwargs):
        if not author:
            author = await UserFactory.create(session)
        defaults = {
            "title": fake.sentence(),
            "content": fake.text(),
            "author_id": author.id,
        }
        defaults.update(kwargs)
        post = Post(**defaults)
        session.add(post)
        await session.flush()
        return post

# Usage in tests
@pytest.mark.asyncio
async def test_list_users(async_client, db_session):
    # Arrange
    for _ in range(5):
        await UserFactory.create(db_session)
    await db_session.commit()
    
    # Act
    response = await async_client.get("/users?limit=3")
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 3
```

---

## Testing Authentication

```python
def get_auth_headers(user_id: int = 1, role: str = "user") -> dict:
    token = create_access_token(data={"sub": str(user_id), "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_protected_route_no_auth():
    response = client.get("/users/me")
    assert response.status_code == 401

def test_protected_route_with_auth():
    response = client.get("/users/me", headers=get_auth_headers(1))
    assert response.status_code == 200

def test_admin_only_route():
    # Regular user
    response = client.delete("/users/1", headers=get_auth_headers(2, role="user"))
    assert response.status_code == 403
    
    # Admin
    response = client.delete("/users/1", headers=get_auth_headers(1, role="admin"))
    assert response.status_code == 204
```

---

## Testing WebSockets

```python
def test_websocket():
    with client.websocket_connect("/ws/room1") as ws:
        ws.send_text("Hello")
        data = ws.receive_text()
        assert "Hello" in data
```

---

## pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "alembic/*"]

[tool.coverage.report]
fail_under = 80
```

```bash
# Run tests
pytest
pytest -v                     # Verbose
pytest -x                     # Stop on first failure
pytest -k "test_create"       # Run tests matching pattern
pytest --cov=app              # With coverage
pytest --cov=app --cov-report=html  # HTML coverage report
pytest -m "not slow"          # Skip slow tests
```

---

## Interview Questions — Testing

### Q1: How do you test FastAPI endpoints?

1. **TestClient** (sync) — wraps httpx, calls app directly without a server
2. **AsyncClient** (async) — for async tests using `httpx.AsyncClient` with `ASGITransport`
3. **dependency_overrides** — replace DB, auth, etc. with test implementations
4. **Factories** — generate test data consistently

### Q2: How do you isolate database tests?

Each test gets a **fresh session with rollback**: begin a transaction before each test, run the test, rollback after. Tables are created once per session. This ensures tests don't affect each other and are fast.

### Q3: TestClient vs httpx AsyncClient?

- **TestClient**: Synchronous, simple, no `async` needed. Uses httpx internally.
- **AsyncClient**: For async code, needed when fixtures/setup are async. Use when testing `async def` endpoints that interact with async dependencies.
