# FastAPI Interview Questions

> Comprehensive question bank covering beginner to advanced, rapid-fire, and design scenarios.

---

## 🟢 Beginner Level

### Q1: What is FastAPI and what are its key features?

FastAPI is a modern Python web framework built on **Starlette** (ASGI) and **Pydantic** (validation). Key features:
1. **Async support** — native `async`/`await`
2. **Auto-validation** — Pydantic models validate request data automatically
3. **Auto-documentation** — OpenAPI docs at `/docs` (Swagger) and `/redoc`
4. **Type hints** — Python type annotations drive routing, validation, and docs
5. **High performance** — comparable to Node.js and Go

---

### Q2: How does FastAPI differ from Flask and Django?

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| Async | ✅ Native | ❌ (needs extensions) | Partial (3.1+) |
| Validation | ✅ Pydantic (auto) | ❌ Manual | Forms/serializers |
| Auto docs | ✅ OpenAPI | ❌ (needs Swagger ext) | ❌ (DRF has it) |
| ORM | None (bring your own) | None (use SQLAlchemy) | Built-in Django ORM |
| DI system | ✅ `Depends()` | ❌ | ❌ |
| Learning curve | Low-Medium | Low | High |
| Best for | APIs, microservices | Simple apps, prototypes | Full-stack web apps |

---

### Q3: What is Pydantic and how does FastAPI use it?

Pydantic defines **data models** with type annotations. FastAPI uses them to:
1. **Validate** request bodies, query params, path params
2. **Serialize** response data (filter fields via `response_model`)
3. **Generate** OpenAPI schema (auto-docs)
4. **Parse** environment variables (`BaseSettings`)

Invalid data → automatic **422 Unprocessable Entity** response.

---

### Q4: What is the difference between path and query parameters?

```python
# Path parameter — part of the URL path
@app.get("/users/{user_id}")    # /users/42
async def get_user(user_id: int): ...

# Query parameter — after ? in the URL
@app.get("/users")              # /users?skip=0&limit=10
async def list_users(skip: int = 0, limit: int = 10): ...
```

Path params identify **specific resources**. Query params **filter/paginate** collections.

---

### Q5: How does FastAPI auto-generate API documentation?

FastAPI reads your type hints, Pydantic models, route decorators, and `Field()` metadata to generate an **OpenAPI 3.0 schema** (`/openapi.json`). Swagger UI (`/docs`) and ReDoc (`/redoc`) render this schema as interactive, testable documentation — zero manual effort.

---

## 🟡 Intermediate Level

### Q6: Explain FastAPI's dependency injection system.

`Depends()` declares reusable logic that FastAPI resolves automatically:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db         # Setup
    finally:
        db.close()       # Cleanup

@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    ...
```

**Features:**
- Nested dependencies (deps that depend on other deps)
- Class-based dependencies
- Yield dependencies (setup + cleanup)
- Override in tests (`app.dependency_overrides`)
- Scopes: per-request, per-router, global

---

### Q7: What's the difference between `async def` and `def` endpoints?

| Type | Execution | Use When |
|------|-----------|----------|
| `async def` | Runs on event loop (main thread) | Using async libraries (asyncpg, aiohttp) |
| `def` (sync) | Runs in **thread pool** (won't block loop) | Using blocking libraries (requests, psycopg2) |

**⚠️ Common mistake:** Using blocking calls inside `async def` → freezes the entire event loop!

---

### Q8: How do you handle authentication in FastAPI?

1. **OAuth2PasswordBearer** — extracts `Bearer <token>` from Authorization header
2. **JWT creation** — `python-jose` to encode/decode tokens
3. **Password hashing** — `passlib` with bcrypt
4. **Auth dependency** — `get_current_user` decodes token, fetches user from DB
5. **RBAC** — `RoleChecker` class dependency with required roles

```python
@app.get("/admin-only")
async def admin(user: User = Depends(RoleChecker(["admin"]))):
    return {"message": "Welcome, admin!"}
```

---

### Q9: How do you test FastAPI applications?

1. **TestClient** — sync testing (wraps httpx)
2. **AsyncClient** — async testing with `httpx.ASGITransport`
3. **dependency_overrides** — swap DB, auth, etc. for test versions
4. **Transaction rollback** — each test gets a fresh DB state
5. **Factories** — generate test data with `faker` or custom factories

---

### Q10: What is `response_model` and why use it?

`response_model` tells FastAPI which Pydantic model to use for the **response**:
- **Filters** fields (only include what's in the model)
- **Validates** the response data
- **Documents** the response schema in OpenAPI docs

```python
@app.post("/users", response_model=UserResponse)  # Excludes password, internal fields
async def create_user(data: UserCreate):
    return user  # Even if user has extra fields, response only includes UserResponse fields
```

---

### Q11: How does CORS work in FastAPI?

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],  # Allowed origins
    allow_methods=["*"],                   # Allowed HTTP methods
    allow_headers=["*"],                   # Allowed headers
    allow_credentials=True,                # Allow cookies/auth
)
```

CORS prevents browsers from making requests to a different origin unless the server explicitly allows it. FastAPI handles CORS via Starlette's `CORSMiddleware`.

---

## 🔴 Advanced Level

### Q12: How do you structure a large FastAPI project?

Feature-based structure: each feature (`users/`, `auth/`, `posts/`) has its own `routes.py`, `schemas.py`, `models.py`, `repository.py`, and `service.py`. Shared code goes in `core/` and `db/`. Use `APIRouter` per feature and include in the main app.

---

### Q13: How do you handle database transactions?

```python
# Option 1: Session-per-request with auto-commit
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()    # Auto-commit
        except Exception:
            await session.rollback()  # Auto-rollback
            raise

# Option 2: Explicit transactions
async with db.begin():    # Begins transaction
    # All operations here are in one transaction
    pass                  # Auto-commit at end, rollback on exception

# Option 3: Savepoints (nested transactions)
async with db.begin_nested():
    # Savepoint — can rollback without affecting outer transaction
```

---

### Q14: How do you handle background tasks vs Celery?

| Feature | BackgroundTasks | Celery |
|---------|----------------|--------|
| Runs in | Same process (after response) | Separate worker process |
| Use case | Quick tasks (email, log) | Heavy tasks (reports, ML, video) |
| Retries | ❌ | ✅ |
| Scheduling | ❌ | ✅ (Celery Beat) |
| Monitoring | ❌ | ✅ (Flower) |
| Broker | None | Redis/RabbitMQ |

Rule: If the task is < 1 second, use `BackgroundTasks`. Otherwise, use Celery/RQ.

---

### Q15: How do you deploy FastAPI in production?

```
Internet → Nginx (reverse proxy, TLS, static) 
           → Gunicorn (process manager, workers=(2×CPU)+1)
              → Uvicorn workers (ASGI server)
                 → FastAPI app
```

Containerized with Docker, orchestrated with Kubernetes or Docker Compose. Health checks at `/health` and `/health/ready`.

---

### Q16: How do you optimize FastAPI performance?

1. **ORJSONResponse** — faster JSON serialization
2. **Async DB drivers** — asyncpg, motor
3. **Connection pooling** — `pool_size=20, max_overflow=10`
4. **Redis caching** — cache frequent queries
5. **Pagination** — never return unbounded result sets
6. **Gunicorn workers** — `(2 × CPU) + 1`
7. **Indexes** — proper DB indexes for query patterns
8. **CDN** — for static assets

---

## ⚡ Rapid-Fire Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | What is ASGI? | Async Server Gateway Interface (async version of WSGI) |
| 2 | Default docs URL? | `/docs` (Swagger UI) and `/redoc` |
| 3 | How to run FastAPI? | `uvicorn main:app --reload` |
| 4 | Pydantic v1 `.dict()` → v2? | `.model_dump()` |
| 5 | How to mark a field required? | `Field(...)` or no default |
| 6 | 422 status code means? | Validation error (invalid request data) |
| 7 | `Depends()` with no args? | Uses the class `__init__` as the dependency callable |
| 8 | `yield` in a dependency does what? | Setup before yield, cleanup after yield |
| 9 | How to override deps in tests? | `app.dependency_overrides[dep] = mock_dep` |
| 10 | `response_model` purpose? | Filter/validate response, generate docs |
| 11 | Blocking call in `async def`? | Freezes event loop! Use `def` or `run_in_executor` |
| 12 | FastAPI built on? | Starlette (ASGI) + Pydantic (validation) |
| 13 | How to handle file uploads? | `UploadFile = File(...)` |
| 14 | What is `from_attributes`? | Allows Pydantic to read ORM objects (SQLAlchemy models) |
| 15 | How to add middleware? | `app.add_middleware()` or `@app.middleware("http")` |
| 16 | WebSocket support? | Yes, via `@app.websocket("/path")` |
| 17 | How to set response status code? | `status_code=201` in decorator |
| 18 | How to group routes? | `APIRouter(prefix="/users", tags=["users"])` |
| 19 | Workers for production? | `(2 × CPU_CORES) + 1` Gunicorn + Uvicorn workers |
| 20 | `BackgroundTasks` runs when? | After the response is sent to the client |

---

## 🔧 Design Scenarios

### Scenario 1: Design a REST API for a Blog App

```
Endpoints:
  POST   /auth/register        — Create account
  POST   /auth/login           — Get JWT token
  
  GET    /posts                 — List posts (paginated, filterable)
  POST   /posts                 — Create post (auth required)
  GET    /posts/{id}            — Get post by ID
  PATCH  /posts/{id}            — Update post (author only)
  DELETE /posts/{id}            — Delete post (author or admin)
  
  POST   /posts/{id}/comments   — Add comment (auth required)
  GET    /posts/{id}/comments   — List comments

Key decisions:
  - JWT auth with refresh tokens
  - Repository pattern for DB access
  - Pagination with cursor-based for feeds
  - Rate limiting on auth endpoints
  - Background task for email notifications
```

### Scenario 2: Design an API Rate Limiter

```
Requirements:
  - 100 requests per minute per user
  - Different limits per endpoint/plan
  
Implementation:
  1. Redis sliding window counter
  2. Middleware or dependency
  3. Return 429 with Retry-After header
  4. Key: user_id + endpoint
  5. Response headers: X-RateLimit-Remaining, X-RateLimit-Reset
```

### Scenario 3: Design File Upload Service

```
Requirements:
  - Accept images (JPEG, PNG) up to 10 MB
  - Generate thumbnails
  - Store in S3/MinIO
  
Implementation:
  1. UploadFile with content_type validation
  2. Size check before reading full file
  3. Stream upload to S3 (don't load entire file in memory)
  4. Background task for thumbnail generation
  5. Return presigned URL for download
  6. Store metadata in PostgreSQL
```
