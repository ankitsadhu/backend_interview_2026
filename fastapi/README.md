# FastAPI Study Guide

> Comprehensive FastAPI learning path from fundamentals to production-grade applications, organized for interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | ASGI, path/query params, request body, response model, status codes, Pydantic basics | 🟢 Beginner |
| 02 | [Dependency Injection](./02_dependency_injection.md) | `Depends`, nested deps, class-based deps, DB sessions, auth deps, yield deps, scopes | 🟡 Intermediate |
| 03 | [Pydantic & Validation](./03_pydantic_and_validation.md) | Models, validators, field types, nested models, discriminated unions, settings, serialization | 🟡 Intermediate |
| 04 | [Authentication & Security](./04_authentication.md) | OAuth2, JWT, password hashing, API keys, scopes, CORS, rate limiting, HTTPS | 🟡 Intermediate |
| 05 | [Database Integration](./05_database.md) | SQLAlchemy async, Alembic, repository pattern, transactions, connection pooling, testing | 🟡🔴 Intermediate-Advanced |
| 06 | [Advanced Features](./06_advanced_features.md) | Middleware, background tasks, WebSockets, SSE, file uploads, streaming, lifespan events | 🔴 Advanced |
| 07 | [Testing](./07_testing.md) | `TestClient`, `httpx.AsyncClient`, fixtures, mocking deps, DB testing, factory patterns | 🔴 Advanced |
| 08 | [Production & Deployment](./08_production.md) | Project structure, Uvicorn/Gunicorn, Docker, logging, monitoring, error handling, performance | 🔴 Advanced |
| 09 | [Interview Questions](./09_interview_questions.md) | 25+ questions (beginner → advanced) + rapid-fire Q&A + design scenarios | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Core
1. `01_fundamentals.md` — routing, params, request/response
2. `02_dependency_injection.md` — the DI system
3. `03_pydantic_and_validation.md` — data validation

### Week 2: Security & Data
4. `04_authentication.md` — JWT, OAuth2, security
5. `05_database.md` — async SQLAlchemy, Alembic

### Week 3: Production
6. `06_advanced_features.md` — middleware, WebSockets, background tasks
7. `07_testing.md` — testing strategies
8. `08_production.md` — deployment and monitoring

### Final Review
9. `09_interview_questions.md` — test yourself
