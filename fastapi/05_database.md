# Database Integration

## Async SQLAlchemy Setup

```python
# db/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/mydb"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,                    # SQL logging (True for debug)
    pool_size=20,                  # Max connections in pool
    max_overflow=10,               # Extra connections beyond pool_size
    pool_timeout=30,               # Seconds to wait for connection
    pool_recycle=1800,             # Recycle connections after 30 min
    pool_pre_ping=True,            # Check connection before use
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,        # Don't expire objects after commit
)

class Base(DeclarativeBase):
    pass
```

---

## Models

```python
# db/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from db.engine import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    posts: Mapped[list["Post"]] = relationship(back_populates="author", lazy="selectin")

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    author: Mapped["User"] = relationship(back_populates="posts")
```

---

## Database Dependency

```python
# db/dependency.py
from db.engine import async_session

async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

## Repository Pattern

```python
# repositories/user_repo.py
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list(self, skip: int = 0, limit: int = 20) -> list[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, data: UserCreate, hashed_password: str) -> User:
        user = User(
            email=data.email,
            name=data.name,
            hashed_password=hashed_password,
        )
        self.session.add(user)
        await self.session.flush()       # Get ID without committing
        await self.session.refresh(user) # Refresh to load defaults
        return user
    
    async def update(self, user_id: int, data: UserUpdate) -> User | None:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(user_id)
        
        await self.session.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: int) -> bool:
        result = await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        return result.rowcount > 0

# Dependency
def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)
```

---

## Using in Routes

```python
# routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from repositories.user_repo import UserRepository, get_user_repo

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    repo: UserRepository = Depends(get_user_repo),
):
    return await repo.list(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repo),
):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    repo: UserRepository = Depends(get_user_repo),
):
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    hashed = hash_password(data.password)
    return await repo.create(data, hashed)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    repo: UserRepository = Depends(get_user_repo),
):
    user = await repo.update(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repo),
):
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
```

---

## Alembic Migrations

```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Configure alembic/env.py for async
```

```python
# alembic/env.py (async version)
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from db.engine import Base, DATABASE_URL

target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()

import asyncio
asyncio.run(run_async_migrations())
```

```bash
# Create migration
alembic revision --autogenerate -m "create users table"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View current version
alembic current

# View history
alembic history
```

---

## Transactions

```python
# Explicit transaction control
async def transfer_funds(
    db: AsyncSession,
    from_id: int,
    to_id: int,
    amount: float,
):
    async with db.begin():  # Auto-rollback on exception
        from_account = await db.get(Account, from_id)
        to_account = await db.get(Account, to_id)
        
        if from_account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        from_account.balance -= amount
        to_account.balance += amount
        # Commits automatically at end of 'async with db.begin()'

# Nested savepoints
async def complex_operation(db: AsyncSession):
    async with db.begin():
        # Operation 1
        db.add(User(name="Alice"))
        
        async with db.begin_nested():  # SAVEPOINT
            try:
                db.add(User(name="Duplicate"))  # Might fail
            except IntegrityError:
                pass  # Savepoint rolled back, outer transaction continues
        
        # Operation 3 (still in outer transaction)
        db.add(User(name="Bob"))
```

---

## Interview Questions — Database

### Q1: Why use async SQLAlchemy with FastAPI?

FastAPI is built on ASGI (async). Using sync SQLAlchemy would **block the event loop** during queries (unless you use `def` endpoints, which run in a thread pool). Async SQLAlchemy (`asyncpg`) → non-blocking queries → better throughput under load.

### Q2: What is the Repository pattern?

Abstracts data access into a class with methods like `get`, `create`, `update`, `delete`. Benefits:
- **Separation of concerns:** Routes don't know about SQL
- **Testability:** Mock the repository instead of the database
- **Reusability:** Same repo used across routes

### Q3: How do you handle database connection pooling?

SQLAlchemy's `create_async_engine` manages a connection pool:
- `pool_size=20` — keep 20 connections ready
- `max_overflow=10` — up to 30 total under high load
- `pool_pre_ping=True` — verify connections before use (prevents stale connections)
- `pool_recycle=1800` — replace connections every 30 min (prevents timeouts)
