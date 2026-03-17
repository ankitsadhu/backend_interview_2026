# SQLAlchemy ORM Basics

## Declarative Models (SQLAlchemy 2.0)

### Mapped Class with `DeclarativeBase`

```python
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Base class for all models
class Base(DeclarativeBase):
    pass

# User model
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    age: Mapped[int | None] = mapped_column(Integer, default=None)  # Nullable
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationship (covered in depth in 03_relationships)
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r})"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    total: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="orders")

    def __repr__(self) -> str:
        return f"Order(id={self.id}, total={self.total})"
```

### Key Points — Mapped Types

```python
# Mapped[int]           → NOT NULL integer
# Mapped[int | None]    → NULLABLE integer
# Mapped[str]           → NOT NULL string (needs String(N) in mapped_column)
# Mapped[Optional[str]] → NULLABLE string (pre-3.10 Python)
```

### Create Tables

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://user:pass@localhost/mydb")

# Create all tables defined in Base subclasses
Base.metadata.create_all(engine)
```

---

## Session — Unit of Work

The Session is the **workspace** for ORM operations. It tracks changes and flushes them to the database.

```
Session Lifecycle:
┌──────────────┐
│   new         │  ← object created, added to session
├──────────────┤
│   pending     │  ← in session, not yet flushed (no INSERT sent)
├──────────────┤
│   persistent  │  ← flushed/committed, has a database identity
├──────────────┤
│   detached    │  ← removed from session (after expunge or session close)
├──────────────┤
│   deleted     │  ← marked for deletion, will be DELETEd on commit
└──────────────┘
```

### Creating a Session

```python
from sqlalchemy.orm import Session, sessionmaker

# Option 1: Direct Session (simple scripts)
with Session(engine) as session:
    # ... use session ...
    session.commit()

# Option 2: sessionmaker (recommended for applications)
SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as session:
    # ... use session ...
    session.commit()

# Option 3: Session with begin() — auto-commit/rollback
with Session(engine) as session:
    with session.begin():
        session.add(User(name="Alice", email="alice@test.com"))
        # Auto-commit on exit, auto-rollback on exception
```

### Session in FastAPI / Flask

```python
# FastAPI dependency injection
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Flask pattern
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
```

---

## CRUD Operations

### Create (INSERT)

```python
with Session(engine) as session:
    # Single object
    user = User(name="Alice", email="alice@test.com", age=30)
    session.add(user)
    session.commit()

    print(user.id)  # Auto-generated ID is available after commit

    # Multiple objects
    session.add_all([
        User(name="Bob", email="bob@test.com"),
        User(name="Charlie", email="charlie@test.com"),
    ])
    session.commit()
```

### Flush vs Commit

```python
with Session(engine) as session:
    user = User(name="Alice", email="alice@test.com")
    session.add(user)

    # flush() → sends INSERT to DB, but doesn't commit transaction
    session.flush()
    print(user.id)  # ID is available! (INSERT was sent)

    # commit() → commits the transaction (makes changes permanent)
    session.commit()

    # rollback() → undoes everything since last commit
    session.rollback()
```

| Operation | SQL Sent? | Transaction Committed? | ID Available? |
|-----------|-----------|----------------------|---------------|
| `add()` | No | No | No |
| `flush()` | Yes (INSERT) | No | Yes |
| `commit()` | Yes (if not flushed) | Yes | Yes |
| `rollback()` | ROLLBACK | Transaction undone | No (if not committed) |

> **Auto-flush:** By default, Session auto-flushes before every query. This ensures queries see pending changes.

---

### Read (SELECT)

```python
from sqlalchemy import select

with Session(engine) as session:
    # SQLAlchemy 2.0 style (recommended)
    # Get all users
    stmt = select(User)
    users = session.scalars(stmt).all()

    # Get one user by primary key
    user = session.get(User, 1)  # Returns None if not found

    # Filter
    stmt = select(User).where(User.email == "alice@test.com")
    user = session.scalars(stmt).first()       # First result or None
    user = session.scalars(stmt).one()          # Exactly one (raises if 0 or 2+)
    user = session.scalars(stmt).one_or_none()  # One or None (raises if 2+)

    # Multiple conditions
    stmt = select(User).where(
        User.age > 25,
        User.is_active == True
    )
    users = session.scalars(stmt).all()

    # Ordering
    stmt = select(User).order_by(User.name.desc())

    # Limit / Offset
    stmt = select(User).limit(20).offset(40)

    # Specific columns
    stmt = select(User.name, User.email)
    rows = session.execute(stmt).all()
    for name, email in rows:
        print(name, email)

    # Count
    from sqlalchemy import func
    count = session.scalar(select(func.count()).select_from(User))
```

### Legacy Query API (1.x style — still works but deprecated)

```python
# These still work but should be migrated to 2.0 select() style
users = session.query(User).filter(User.age > 25).all()
user = session.query(User).filter_by(email="alice@test.com").first()
count = session.query(User).count()
```

---

### Update

```python
with Session(engine) as session:
    # Method 1: Load → Modify → Commit (ORM-tracked)
    user = session.get(User, 1)
    user.name = "Alice Updated"
    user.age = 31
    session.commit()  # SQLAlchemy detects changes automatically

    # Method 2: Bulk update (no object loading — faster)
    stmt = (
        update(User)
        .where(User.is_active == False)
        .values(is_active=True)
    )
    session.execute(stmt)
    session.commit()

    # Update with RETURNING (PostgreSQL)
    from sqlalchemy import update
    stmt = (
        update(User)
        .where(User.role == "admin")
        .values(role="superadmin")
        .returning(User.id, User.name)
    )
    result = session.execute(stmt)
    updated_users = result.all()
    session.commit()
```

---

### Delete

```python
with Session(engine) as session:
    # Method 1: Load → Delete
    user = session.get(User, 42)
    if user:
        session.delete(user)
        session.commit()

    # Method 2: Bulk delete (faster, no loading)
    from sqlalchemy import delete
    stmt = delete(User).where(User.is_active == False)
    session.execute(stmt)
    session.commit()

    # Delete with RETURNING
    stmt = (
        delete(User)
        .where(User.is_active == False)
        .returning(User.id, User.email)
    )
    result = session.execute(stmt)
    deleted = result.all()
    session.commit()
```

---

## Identity Map

The Session maintains an **identity map** — each database row is represented by **exactly one** Python object.

```python
with Session(engine) as session:
    user1 = session.get(User, 1)
    user2 = session.get(User, 1)  # No new SQL query!

    assert user1 is user2  # Same Python object!

    # This is a key feature:
    # 1. Prevents duplicate objects in memory
    # 2. Tracks all changes to the object
    # 3. Avoids unnecessary SELECT queries
```

---

## Model Configuration Patterns

### Table Arguments

```python
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # Composite unique constraint
        UniqueConstraint("tenant_id", "email", name="uq_tenant_email"),
        # Composite index
        Index("idx_users_role_active", "role", "is_active"),
        # Table-level check constraint
        CheckConstraint("age >= 0 AND age <= 150", name="ck_users_age"),
        # Schema
        {"schema": "public"},
    )
```

### Column Configuration

```python
from sqlalchemy import String, text
from sqlalchemy.orm import mapped_column

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String, default=None)
    stock: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()       # DEFAULT now() in DDL
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()             # Updated on every UPDATE
    )
```

### Mixins (Reusable Column Groups)

```python
from sqlalchemy.orm import Mapped, mapped_column

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

class User(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    # Inherits: created_at, updated_at, is_deleted, deleted_at
```

---

## Common Interview Questions — ORM Basics

### Q1: What is the difference between `session.flush()` and `session.commit()`?

- **`flush()`** — Sends pending SQL (INSERT/UPDATE/DELETE) to the database but **keeps the transaction open**. Objects get their IDs. Can be rolled back.
- **`commit()`** — Calls `flush()` first, then **commits the transaction** (makes changes permanent). Cannot be undone.

**When flush is useful:** Getting auto-generated IDs before commit, or ensuring queries in the same transaction see pending changes.

---

### Q2: What is the Session identity map?

The identity map ensures **one Python object per database row** within a Session:
- `session.get(User, 1)` returns the **same object** on repeated calls
- Prevents duplicate in-memory representations
- Session tracks all attribute changes for dirty checking

**Implication:** Don't share objects across sessions without merging — objects are bound to their originating session.

---

### Q3: What is the difference between `session.execute()` and `session.scalars()`?

```python
# execute() → returns Row objects (tuples)
result = session.execute(select(User))
rows = result.all()  # List of Row objects → access via row.User or row[0]

# scalars() → returns the first column of each row
users = session.scalars(select(User)).all()  # List of User objects directly

# Use scalars() when selecting a single entity/column
# Use execute() when selecting multiple columns or entities
```

---

### Q4: How do you handle the "detached instance" error?

```python
# This error occurs when accessing a lazy-loaded relationship
# on an object that's been detached from its session:

user = session.get(User, 1)
session.close()
print(user.orders)  # DetachedInstanceError!

# Solutions:
# 1. Eagerly load relationships before closing session
stmt = select(User).options(selectinload(User.orders))

# 2. Keep session open while accessing relationships

# 3. Use expire_on_commit=False
Session(engine, expire_on_commit=False)
# Objects retain their data after commit (but may be stale)
```
