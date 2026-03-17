# SQLAlchemy Core Fundamentals

## What is SQLAlchemy?

SQLAlchemy is a **Python SQL toolkit and ORM** — the most widely used database library in the Python ecosystem.

### Two Layers

```
┌──────────────────────────────────────┐
│           ORM (Object Relational)     │  ← High-level: Python classes = DB tables
│  Declarative Models, Session, Query   │
├──────────────────────────────────────┤
│           Core (SQL Expression)       │  ← Mid-level: Pythonic SQL builder
│  Table, Column, select(), insert()    │
├──────────────────────────────────────┤
│           DBAPI (Database API)        │  ← Low-level: psycopg2, asyncpg, etc.
│  Connection pooling, raw SQL          │
└──────────────────────────────────────┘
```

| Layer | When to Use |
|-------|-------------|
| **Core** | Complex queries, ETL pipelines, maximum control, lightweight apps |
| **ORM** | Application development, domain models, CRUD-heavy apps |
| **Both** | Most real-world apps use ORM for models + Core for complex queries |

> **Interview Tip:** SQLAlchemy 2.0 (current) unified the API — Core and ORM use the same `select()` syntax.

---

## Installation

```bash
# SQLAlchemy + PostgreSQL driver
pip install sqlalchemy psycopg2-binary

# For async support
pip install sqlalchemy[asyncio] asyncpg

# With Alembic (migrations)
pip install alembic
```

---

## Engine — The Starting Point

The Engine is the **source of database connectivity**. It manages a **connection pool** and a **dialect** (PostgreSQL, MySQL, SQLite, etc.).

```python
from sqlalchemy import create_engine

# Connection string format:
# dialect+driver://user:password@host:port/database

# PostgreSQL
engine = create_engine(
    "postgresql+psycopg2://user:password@localhost:5432/mydb",
    echo=True,              # Log all SQL (disable in production!)
    pool_size=5,            # Connection pool size
    max_overflow=10,        # Extra connections beyond pool_size
    pool_timeout=30,        # Wait time for available connection
    pool_recycle=1800,      # Recycle connections after 30 min
    pool_pre_ping=True,     # Test connection health before use
)

# SQLite (for testing)
engine = create_engine("sqlite:///local.db")
engine = create_engine("sqlite:///:memory:")  # In-memory
```

### Engine Lifecycle

```python
# Engine is typically created ONCE at application startup
# and shared across the entire application

# DON'T create a new engine per request!
# DO create engine at startup → use it everywhere
```

---

## Connection — Executing SQL

### Core-Style Execution (SQLAlchemy 2.0)

```python
from sqlalchemy import text

# Using connection context manager (auto-closes)
with engine.connect() as conn:
    # Raw SQL with text()
    result = conn.execute(text("SELECT * FROM users WHERE age > :age"), {"age": 25})

    for row in result:
        print(row.name, row.email)

    # Connection doesn't auto-commit in 2.0
    conn.commit()  # Explicit commit required!

# Using begin() — auto-commits on success, auto-rolls-back on exception
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users (name, email) VALUES (:name, :email)"),
                 {"name": "Alice", "email": "alice@test.com"})
    # Auto-commit on exit (no explicit commit needed)
    # Auto-rollback if exception is raised
```

### Result Object

```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, email FROM users"))

    # Fetch methods
    row = result.fetchone()        # Single row (or None)
    rows = result.fetchall()       # All rows as list
    rows = result.fetchmany(10)    # N rows

    # Iterate
    for row in result:
        print(row.id, row.name)    # Access by attribute
        print(row[0], row[1])      # Access by index
        print(row._mapping)         # Dict-like access

    # Scalars
    result = conn.execute(text("SELECT name FROM users"))
    names = result.scalars().all()  # ['Alice', 'Bob', 'Charlie']

    first_name = conn.execute(text("SELECT name FROM users LIMIT 1")).scalar_one()
    # 'Alice'
```

---

## MetaData & Table — Schema Definition (Core Style)

```python
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy import func

metadata = MetaData()

# Define tables
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("email", String(255), unique=True, nullable=False),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, server_default=func.now()),
)

orders = Table(
    "orders", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("total", Integer, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

# Create all tables
metadata.create_all(engine)

# Drop all tables
metadata.drop_all(engine)

# Reflect existing tables from database
metadata.reflect(bind=engine)
existing_users = metadata.tables["users"]
```

---

## Core SQL Expressions

### SELECT

```python
from sqlalchemy import select, and_, or_, not_, func, desc, asc

# Basic select
stmt = select(users)
# SELECT users.id, users.name, users.email, ... FROM users

# Specific columns
stmt = select(users.c.name, users.c.email)
# SELECT users.name, users.email FROM users

# WHERE clause
stmt = select(users).where(users.c.age > 25)
stmt = select(users).where(users.c.name == "Alice")
stmt = select(users).where(users.c.email.like("%@gmail.com"))
stmt = select(users).where(users.c.name.in_(["Alice", "Bob"]))
stmt = select(users).where(users.c.name.is_(None))       # IS NULL
stmt = select(users).where(users.c.name.isnot(None))     # IS NOT NULL

# Multiple conditions
stmt = select(users).where(
    and_(
        users.c.age > 25,
        users.c.is_active == True,
        or_(
            users.c.role == "admin",
            users.c.role == "moderator"
        )
    )
)

# Chaining .where() = AND
stmt = select(users).where(users.c.age > 25).where(users.c.is_active == True)

# ORDER BY
stmt = select(users).order_by(users.c.name)                 # ASC
stmt = select(users).order_by(desc(users.c.created_at))     # DESC
stmt = select(users).order_by(users.c.role, desc(users.c.name))  # Multi-column

# LIMIT / OFFSET
stmt = select(users).limit(20).offset(40)  # Page 3

# DISTINCT
stmt = select(users.c.role).distinct()

# Execute
with engine.connect() as conn:
    result = conn.execute(stmt)
    for row in result:
        print(row.name, row.email)
```

### Aggregates & GROUP BY

```python
from sqlalchemy import func

stmt = (
    select(
        users.c.role,
        func.count().label("count"),
        func.avg(users.c.age).label("avg_age"),
        func.max(users.c.age).label("max_age"),
    )
    .group_by(users.c.role)
    .having(func.count() > 5)
)
```

### JOIN

```python
# Explicit join
stmt = (
    select(users.c.name, orders.c.total)
    .join(orders, users.c.id == orders.c.user_id)            # INNER JOIN
)

stmt = (
    select(users.c.name, orders.c.total)
    .join(orders, users.c.id == orders.c.user_id, isouter=True)  # LEFT JOIN
)

stmt = (
    select(users.c.name, orders.c.total)
    .join(orders, users.c.id == orders.c.user_id, full=True)     # FULL OUTER JOIN
)

# Auto-join (if ForeignKey is defined)
stmt = select(users.c.name, orders.c.total).join(orders)
```

### INSERT

```python
# Single insert
stmt = users.insert().values(name="Alice", email="alice@test.com")

# Multiple inserts
stmt = users.insert().values([
    {"name": "Bob", "email": "bob@test.com"},
    {"name": "Charlie", "email": "charlie@test.com"},
])

# Insert with RETURNING
stmt = users.insert().values(name="Dave", email="dave@test.com").returning(users.c.id)

with engine.begin() as conn:
    result = conn.execute(stmt)
    new_id = result.scalar_one()
```

### UPDATE

```python
stmt = (
    users.update()
    .where(users.c.id == 1)
    .values(name="Alice Updated", is_active=False)
)

# Update with RETURNING
stmt = (
    users.update()
    .where(users.c.is_active == False)
    .values(is_active=True)
    .returning(users.c.id, users.c.name)
)
```

### DELETE

```python
stmt = users.delete().where(users.c.id == 42)

# Delete with RETURNING
stmt = users.delete().where(users.c.is_active == False).returning(users.c.id)
```

### Subqueries

```python
# Subquery: users with above-average age
avg_age = select(func.avg(users.c.age)).scalar_subquery()

stmt = select(users).where(users.c.age > avg_age)

# Subquery in FROM
subq = (
    select(
        orders.c.user_id,
        func.sum(orders.c.total).label("total_spent")
    )
    .group_by(orders.c.user_id)
    .subquery()
)

stmt = (
    select(users.c.name, subq.c.total_spent)
    .join(subq, users.c.id == subq.c.user_id)
)

# EXISTS
from sqlalchemy import exists

has_orders = exists().where(orders.c.user_id == users.c.id)
stmt = select(users).where(has_orders)
```

---

## Common Interview Questions — Core

### Q1: What is the difference between `engine.connect()` and `engine.begin()`?

```python
# connect() — manual transaction control
with engine.connect() as conn:
    conn.execute(...)
    conn.commit()    # Must commit explicitly
    # If exception → must handle rollback yourself (auto-rollback on context exit)

# begin() — automatic transaction management
with engine.begin() as conn:
    conn.execute(...)
    # Auto-commit on successful exit
    # Auto-rollback on exception
```

**Best practice:** Use `engine.begin()` for write operations (ensures atomicity). Use `engine.connect()` when you need fine-grained transaction control.

---

### Q2: What is `text()` and when do you use it?

`text()` wraps raw SQL strings with **parameterized binding**:

```python
from sqlalchemy import text

# Safe: parameterized (prevents SQL injection)
conn.execute(text("SELECT * FROM users WHERE name = :name"), {"name": user_input})

# NEVER do this (SQL injection vulnerability!):
conn.execute(text(f"SELECT * FROM users WHERE name = '{user_input}'"))  # ❌ DANGER
```

**Use `text()` when:**
- Running raw SQL that's too complex for the expression language
- Calling stored procedures
- Performance-critical queries where you want exact SQL control

---

### Q3: What is the difference between `create_engine()` parameters `echo` and `pool_pre_ping`?

| Parameter | Purpose | Production Setting |
|-----------|---------|-------------------|
| `echo=True` | Logs all SQL to stdout | `False` (use logging instead) |
| `pool_pre_ping=True` | Tests connection health before checkout | `True` (prevents stale connections) |
| `pool_size` | Permanent connections in pool | 5-20 depending on workload |
| `max_overflow` | Extra connections beyond pool_size | 10-20 |
| `pool_recycle` | Seconds before connection is recycled | 1800 (30 min) |
