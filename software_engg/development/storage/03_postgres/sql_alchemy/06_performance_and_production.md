# Performance & Production

## Connection Pooling

### Built-in Pool (create_engine)

SQLAlchemy includes a connection pool by default.

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost/mydb",
    pool_size=10,            # Maintained connections
    max_overflow=20,         # Extra connections under load (total max = 30)
    pool_timeout=30,         # Wait time for connection (raises TimeoutError)
    pool_recycle=1800,       # Recycle connections after 30 min (prevent stale)
    pool_pre_ping=True,      # Health check before checkout (prevents errors)
)
```

### Pool Types

```python
from sqlalchemy.pool import QueuePool, NullPool, StaticPool

# QueuePool (default) — connection pool with queue
engine = create_engine(url, poolclass=QueuePool)

# NullPool — no pooling (new connection every time)
# Use for: short-lived scripts, when using external pooler (PgBouncer)
engine = create_engine(url, poolclass=NullPool)

# StaticPool — single connection reused by all threads
# Use for: testing with SQLite in-memory
engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)
```

### Pool Events

```python
from sqlalchemy import event

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    """Called when a connection is checked out from the pool."""
    print("Connection checked out")

@event.listens_for(engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    """Called when a connection is returned to the pool."""
    print("Connection returned")
```

---

## Bulk Operations

### Bulk Insert (Fast)

```python
from sqlalchemy import insert

with Session(engine) as session:
    # Method 1: ORM bulk insert (SQLAlchemy 2.0)
    session.execute(
        insert(User),
        [
            {"name": "Alice", "email": "alice@test.com"},
            {"name": "Bob", "email": "bob@test.com"},
            {"name": "Charlie", "email": "charlie@test.com"},
        ]
    )
    session.commit()

    # Method 2: Core insert (bypasses ORM, fastest)
    with engine.begin() as conn:
        conn.execute(
            User.__table__.insert(),
            [{"name": f"user_{i}", "email": f"user_{i}@test.com"} for i in range(10000)]
        )

    # Method 3: COPY (fastest for PostgreSQL — via psycopg2)
    import csv, io

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for i in range(100000):
        writer.writerow([f"user_{i}", f"user_{i}@test.com"])
    buffer.seek(0)

    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()
    cursor.copy_from(buffer, 'users', columns=('name', 'email'), sep=',')
    raw_conn.commit()
```

### Performance Comparison

| Method | 10K rows | 100K rows |
|--------|----------|-----------|
| `session.add()` loop | ~5s | ~50s |
| `session.add_all()` | ~3s | ~30s |
| `session.execute(insert(...), [...])` | ~0.5s | ~3s |
| Core `conn.execute(table.insert(), [...])` | ~0.3s | ~2s |
| `COPY` via psycopg2 | ~0.1s | ~0.5s |

### Bulk Update

```python
from sqlalchemy import update

# Method 1: ORM bulk update
session.execute(
    update(User).where(User.is_active == False).values(is_active=True)
)

# Method 2: Bulk update with different values per row
from sqlalchemy.dialects.postgresql import insert as pg_insert

stmt = pg_insert(User).values([
    {"id": 1, "name": "Alice Updated"},
    {"id": 2, "name": "Bob Updated"},
])
stmt = stmt.on_conflict_do_update(
    index_elements=["id"],
    set_={"name": stmt.excluded.name}
)
session.execute(stmt)
```

### Bulk Delete

```python
from sqlalchemy import delete

# Bulk delete (no loading objects)
session.execute(
    delete(User).where(User.is_active == False)
)
session.commit()
```

---

## Async SQLAlchemy

### Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Use asyncpg driver (not psycopg2)
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/mydb",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Usage

```python
from sqlalchemy import select

async def get_users():
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.is_active == True)
        result = await session.scalars(stmt)
        return result.all()

async def create_user(name: str, email: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = User(name=name, email=email)
            session.add(user)
        # Auto-commit on exit

# Eager loading (lazy loading doesn't work in async!)
async def get_user_with_orders(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .options(selectinload(User.orders))  # MUST eager-load!
            .where(User.id == user_id)
        )
        user = await session.scalar(stmt)
        return user
```

### FastAPI Integration

```python
from fastapi import Depends, FastAPI

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    user = await db.scalar(stmt)
    if not user:
        raise HTTPException(status_code=404)
    return {"id": user.id, "name": user.name}
```

> **Critical:** Lazy loading raises errors in async context! Always use eager loading (`selectinload`, `joinedload`) with async sessions.

---

## Testing Patterns

### Test Database Setup

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

@pytest.fixture
def engine():
    """In-memory SQLite for fast tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Fresh session per test with rollback."""
    with Session(engine) as session:
        yield session
        session.rollback()
```

### Using a Real PostgreSQL Database

```python
import pytest
from sqlalchemy import create_engine, event

TEST_DB_URL = "postgresql://user:pass@localhost/test_db"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine):
    """Transactional test — each test runs in a savepoint."""
    conn = engine.connect()
    trans = conn.begin()
    session = Session(bind=conn)

    # Nested transaction (savepoint)
    nested = conn.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        nonlocal nested
        if transaction.nested and not transaction._parent.nested:
            nested = conn.begin_nested()

    yield session

    session.close()
    trans.rollback()
    conn.close()
```

### Query Count Assertion

```python
from contextlib import contextmanager
from sqlalchemy import event

@contextmanager
def assert_query_count(engine, expected_count):
    """Assert exact number of SQL queries executed."""
    queries = []

    def track(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(engine, "before_cursor_execute", track)
    try:
        yield queries
    finally:
        event.remove(engine, "before_cursor_execute", track)
    assert len(queries) == expected_count, \
        f"Expected {expected_count} queries, got {len(queries)}:\n" + \
        "\n".join(queries)

# Usage in test
def test_no_n_plus_one(session, engine):
    with assert_query_count(engine, 2):  # 1 for users, 1 for orders
        users = session.scalars(
            select(User).options(selectinload(User.orders))
        ).all()
        for user in users:
            _ = user.orders  # Should NOT fire additional queries
```

---

## Common Anti-Patterns

### 1. Creating Engine Per Request

```python
# ❌ BAD: new engine per request (creates new connection pool!)
@app.get("/users")
def get_users():
    engine = create_engine(DB_URL)
    ...

# ✅ GOOD: create once, reuse
engine = create_engine(DB_URL)

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    ...
```

### 2. Forgetting to Commit

```python
# ❌ BAD: changes lost
with Session(engine) as session:
    session.add(User(name="Alice"))
    # Forgot session.commit()!

# ✅ GOOD: use begin() context manager
with Session(engine) as session:
    with session.begin():
        session.add(User(name="Alice"))
    # Auto-commits
```

### 3. Long-Running Sessions

```python
# ❌ BAD: session stays open during slow operations
with Session(engine) as session:
    user = session.get(User, 1)
    send_email(user.email)   # 5-second network call, session held open!
    session.commit()

# ✅ GOOD: load data, close session, then do slow work
with Session(engine) as session:
    user = session.get(User, 1)
    email = user.email

send_email(email)  # Session already closed
```

### 4. Catching Exceptions Without Rollback

```python
# ❌ BAD: session in broken state
try:
    session.add(user)
    session.commit()
except IntegrityError:
    pass  # Session is now in invalid state!

# ✅ GOOD: rollback on error
try:
    session.add(user)
    session.commit()
except IntegrityError:
    session.rollback()
    raise
```

---

## Common Interview Questions — Performance

### Q1: How does SQLAlchemy's connection pool work?

SQLAlchemy maintains a **pool of database connections** (`QueuePool` by default):
1. When you need a connection, one is **checked out** from the pool
2. When you're done, the connection is **returned** (not closed)
3. If pool is full, new requests **wait** up to `pool_timeout` seconds
4. `pool_pre_ping` validates connections before use (avoids stale connection errors)

### Q2: How do you handle database connections in a FastAPI application?

```python
# 1. Create engine ONCE at startup
engine = create_engine(DB_URL, pool_size=10, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

# 2. Use dependency injection with a generator
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. Inject into route handlers
@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User)).all()
```

### Q3: When should you use Core vs ORM?

| Scenario | Use |
|----------|-----|
| CRUD operations on domain models | ORM |
| Complex analytical queries | Core |
| Bulk data processing (ETL) | Core |
| Simple web app with models | ORM |
| Performance-critical queries | Core |
| Prototyping | ORM |
| Both in same app | Yes! Use ORM for models, Core for complex queries |
