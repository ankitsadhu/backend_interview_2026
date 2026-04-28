# Dependency Injection

## What is Dependency Injection in FastAPI?

FastAPI's **DI system** lets you declare shared logic (DB sessions, auth, config) as reusable dependencies that are automatically resolved and injected.

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# A dependency is any callable that returns a value
def get_db():
    db = SessionLocal()
    try:
        yield db          # Provide DB session
    finally:
        db.close()        # Cleanup after request

# Inject with Depends()
@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

---

## Function Dependencies

```python
from fastapi import Depends, Query

# Simple dependency
def common_parameters(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
):
    return {"skip": skip, "limit": limit, "search": search}

@app.get("/items")
async def list_items(params: dict = Depends(common_parameters)):
    return {"params": params}

@app.get("/users")
async def list_users(params: dict = Depends(common_parameters)):
    return {"params": params}
# Both endpoints share the same pagination logic!
```

---

## Class-Based Dependencies

```python
from fastapi import Depends

class Pagination:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
    
    @property
    def limit(self):
        return self.size

@app.get("/items")
async def list_items(pagination: Pagination = Depends()):
    # Depends() with no args uses the class __init__ as the callable
    items = db.query(Item).offset(pagination.skip).limit(pagination.limit).all()
    return {"page": pagination.page, "items": items}
```

---

## Nested Dependencies

Dependencies can depend on other dependencies — FastAPI resolves the full chain.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user = authenticate(token, db)
    if not user:
        raise HTTPException(status_code=401)
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=403, detail="User is disabled")
    return current_user

@app.get("/me")
async def read_me(user: User = Depends(get_current_active_user)):
    # Resolution chain:
    #   get_db() → get_current_user(token, db) → get_current_active_user(user)
    return user
```

```
Dependency Tree:
  read_me
    └── get_current_active_user
            └── get_current_user
                    ├── oauth2_scheme (extracts token from header)
                    └── get_db (database session)
```

---

## Yield Dependencies (with Cleanup)

`yield` dependencies run **setup code** before the endpoint and **cleanup code** after.

```python
from contextlib import asynccontextmanager

# Sync yield dependency
def get_db():
    db = SessionLocal()
    try:
        yield db              # ← Endpoint runs here
    finally:
        db.close()            # ← Always runs after (cleanup)

# Async yield dependency
async def get_async_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()     # Commit on success
        except Exception:
            await session.rollback()   # Rollback on error
            raise

# Dependency with external resource
async def get_redis():
    redis = await aioredis.from_url("redis://localhost")
    try:
        yield redis
    finally:
        await redis.close()

@app.get("/cached")
async def get_cached(
    db: AsyncSession = Depends(get_async_db),
    redis: Redis = Depends(get_redis),
):
    cached = await redis.get("key")
    if cached:
        return json.loads(cached)
    result = await db.execute(select(Item))
    return result.scalars().all()
```

---

## Dependency Scopes

```python
# Per-request (default) — new instance per request
@app.get("/")
async def endpoint(db: Session = Depends(get_db)):
    pass  # get_db() called for each request

# Per-router — apply to all routes in a router
router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("/protected")
async def protected():
    return {"status": "ok"}  # verify_api_key runs automatically

# Global — apply to ALL routes
app = FastAPI(dependencies=[Depends(log_request)])
```

---

## Dependency Overrides (for Testing)

```python
# production dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# test override
def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# In tests:
app.dependency_overrides[get_db] = get_test_db

# Now all endpoints using Depends(get_db) will get the test DB!
client = TestClient(app)
response = client.get("/users")

# Cleanup
app.dependency_overrides.clear()
```

---

## Common Dependency Patterns

### Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### Permission Dependency

```python
from functools import wraps

class PermissionChecker:
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions
    
    def __call__(self, user: User = Depends(get_current_user)):
        for perm in self.required_permissions:
            if perm not in user.permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing permission: {perm}",
                )
        return user

# Usage
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    user: User = Depends(PermissionChecker(["admin", "user:delete"])),
):
    return {"deleted": user_id}
```

### Settings/Config Dependency

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool = False
    
    model_config = {"env_file": ".env"}

@lru_cache
def get_settings() -> Settings:
    return Settings()

@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```

---

## Interview Questions — Dependency Injection

### Q1: How does FastAPI's DI differ from Django's approach?

| Aspect | FastAPI DI | Django |
|--------|-----------|-------|
| Style | Explicit (Depends) | Implicit (middleware, decorators) |
| Scope | Per-request, per-router, global | Per-request (middleware) |
| Testing | `dependency_overrides` | Mock/patch |
| Type safety | ✅ (type hints) | ❌ (runtime) |
| Async support | ✅ Native | Limited |

### Q2: What is a yield dependency?

A dependency using `yield` — code before `yield` runs as setup (e.g., open DB), code after `yield` runs as cleanup (e.g., close DB). Similar to a context manager. FastAPI ensures cleanup runs even if the endpoint raises an exception.

### Q3: How do you override dependencies in tests?

Use `app.dependency_overrides[original_dep] = mock_dep`. This replaces the dependency globally for all endpoints. Clean up with `app.dependency_overrides.clear()` after tests.
