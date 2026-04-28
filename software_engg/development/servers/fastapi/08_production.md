# Production & Deployment

## Project Structure

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app instance, lifespan
│   ├── config.py               # Pydantic Settings
│   ├── dependencies.py         # Shared dependencies
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py           # /auth endpoints
│   │   ├── dependencies.py     # get_current_user
│   │   ├── jwt.py              # Token creation/validation
│   │   └── schemas.py          # TokenResponse, LoginRequest
│   │
│   ├── users/
│   │   ├── __init__.py
│   │   ├── routes.py           # /users endpoints
│   │   ├── schemas.py          # UserCreate, UserResponse
│   │   ├── models.py           # SQLAlchemy User model
│   │   ├── repository.py       # UserRepository
│   │   └── service.py          # Business logic
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py           # Engine, session factory
│   │   ├── base.py             # DeclarativeBase
│   │   └── dependency.py       # get_db
│   │
│   └── core/
│       ├── __init__.py
│       ├── exceptions.py       # Custom exceptions
│       ├── middleware.py        # Custom middleware
│       └── logging.py          # Logging config
│
├── alembic/                    # Migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   └── factories.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
└── .env
```

---

## Uvicorn & Gunicorn

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (single worker)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Production (Gunicorn + Uvicorn workers) — RECOMMENDED
gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile -
```

### Worker Count Formula

```
Workers = (2 × CPU_CORES) + 1

Why:
  - Each worker handles requests independently
  - Extra +1 for handling overhead
  - For I/O-bound apps, can go higher (4 × CPU)
  - For CPU-bound, stick to CPU count
```

---

## Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Non-root user
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
```

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

---

## Structured Logging

```python
# app/core/logging.py
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return json.dumps(log_data)

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

logger = setup_logging()
```

```python
# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    
    response = await call_next(request)
    
    duration = time.perf_counter() - start
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.client.host,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response
```

---

## Health Check Endpoint

```python
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    checks = {}
    
    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
    
    # Redis check
    try:
        await app.state.redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
    
    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={"status": "ready" if all_ok else "not ready", "checks": checks},
    )
```

---

## Error Handling

```python
# Consistent error response format
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url.path),
            }
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "details": exc.errors(),
                "path": str(request.url.path),
            }
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
            }
        },
    )
```

---

## Performance Tips

```python
# 1. Use async database drivers
# ✅ asyncpg (PostgreSQL), aiomysql (MySQL), motor (MongoDB)
# ❌ psycopg2 (sync) — blocks event loop with async def

# 2. Connection pooling
engine = create_async_engine(url, pool_size=20, max_overflow=10)

# 3. Use ORJSONResponse (faster JSON serialization)
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)

# 4. Cache with Redis
from functools import wraps

def cache(ttl: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"cache:{func.__name__}:{hash(args)}"
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# 5. Pagination
@app.get("/items")
async def list_items(page: int = 1, size: int = 20, db=Depends(get_db)):
    query = select(Item).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    total = await db.scalar(select(func.count()).select_from(Item))
    return {
        "items": result.scalars().all(),
        "total": total,
        "page": page,
        "pages": (total + size - 1) // size,
    }
```

---

## Interview Questions — Production

### Q1: How do you deploy FastAPI in production?

```
Gunicorn (process manager)
  └── Uvicorn workers (ASGI server)
        └── FastAPI app

Typically behind Nginx (reverse proxy + TLS + static files)
Containerized with Docker
Orchestrated with Kubernetes or Docker Compose
```

### Q2: How many Uvicorn workers should you use?

`(2 × CPU_CORES) + 1` as a starting point. Each worker is a separate process with its own event loop. More workers = more parallel request handling, but more memory usage. Tune based on load testing.

### Q3: How do you handle errors consistently?

Use **custom exception handlers** for all error types (HTTPException, ValidationError, unhandled Exception). Return a consistent JSON structure with `code`, `message`, and `path`. Log unhandled exceptions with full stack traces for debugging.
