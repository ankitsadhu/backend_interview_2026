# SQLAlchemy Relationships & Joins

## Relationship Types Overview

```
One-to-Many:    User ──< Orders        (one user has many orders)
Many-to-One:    Order >── User         (each order belongs to one user)
One-to-One:     User ──── Profile      (each user has one profile)
Many-to-Many:   Student >──< Course    (students enroll in multiple courses)
Self-Referential: Employee ──< Employee (manager → subordinates)
```

---

## One-to-Many / Many-to-One

The **most common** relationship. The "many" side holds the foreign key.

```python
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # One-to-Many: user.orders → list of Order objects
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",  # Delete orders when user is deleted
        order_by="Order.created_at.desc()",  # Default ordering
    )

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    total: Mapped[int] = mapped_column(Integer)

    # Many-to-One: order.user → single User object
    user: Mapped["User"] = relationship(back_populates="orders")
```

### Usage

```python
with Session(engine) as session:
    # Create with relationship
    user = User(name="Alice", orders=[
        Order(total=200),
        Order(total=150),
    ])
    session.add(user)
    session.commit()

    # Access relationship
    user = session.get(User, 1)
    for order in user.orders:       # Lazy-loads orders (SELECT query fired here)
        print(order.total)

    # Reverse access
    order = session.get(Order, 1)
    print(order.user.name)          # Lazy-loads user
```

---

## One-to-One

Set `uselist=False` on the "one" side.

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # One-to-One
    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        uselist=False,                  # Single object, not a list
        cascade="all, delete-orphan",
    )

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True  # Enforce one-to-one at DB level
    )
    bio: Mapped[str | None] = mapped_column(String)
    avatar_url: Mapped[str | None] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="profile")
```

```python
# Usage
user = User(name="Alice", profile=Profile(bio="Engineer"))
session.add(user)
session.commit()

print(user.profile.bio)     # "Engineer"
print(profile.user.name)    # "Alice"
```

---

## Many-to-Many

Requires an **association table** (junction table).

```python
from sqlalchemy import Table, Column, ForeignKey

# Association table (no ORM model needed for simple many-to-many)
student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    courses: Mapped[list["Course"]] = relationship(
        secondary=student_course,      # Use the association table
        back_populates="students",
    )

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    students: Mapped[list["Student"]] = relationship(
        secondary=student_course,
        back_populates="courses",
    )
```

```python
# Usage
alice = Student(name="Alice")
math = Course(title="Mathematics")
physics = Course(title="Physics")

alice.courses.append(math)
alice.courses.append(physics)
session.add(alice)
session.commit()

# Access
print(alice.courses)       # [Mathematics, Physics]
print(math.students)       # [Alice]
```

### Many-to-Many with Extra Data (Association Object)

When the junction table has **additional columns** (e.g., enrollment date, grade):

```python
class Enrollment(Base):
    __tablename__ = "enrollments"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"), primary_key=True
    )
    grade: Mapped[str | None] = mapped_column(String(2))
    enrolled_at: Mapped[datetime] = mapped_column(server_default=func.now())

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")
```

---

## Self-Referential Relationship

A table that references **itself** (e.g., employee → manager, category → parent).

```python
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), default=None
    )

    # Self-referential relationships
    manager: Mapped["Employee | None"] = relationship(
        back_populates="subordinates",
        remote_side=[id],          # Tells SA which side is "remote"
    )
    subordinates: Mapped[list["Employee"]] = relationship(
        back_populates="manager",
    )

# Usage
ceo = Employee(name="CEO")
vp = Employee(name="VP Engineering", manager=ceo)
dev = Employee(name="Senior Dev", manager=vp)

print(ceo.subordinates)    # [VP Engineering]
print(dev.manager.name)     # "VP Engineering"
```

---

## Cascade Options

Cascades define what happens to related objects when the parent changes.

```python
orders: Mapped[list["Order"]] = relationship(
    cascade="all, delete-orphan",     # Most common for parent-child
)
```

| Cascade | Effect |
|---------|--------|
| `save-update` | Add related objects to session when parent is added (default) |
| `merge` | Merge related objects when parent is merged |
| `delete` | Delete related objects when parent is deleted |
| `delete-orphan` | Delete child if removed from parent's collection |
| `expunge` | Expunge related objects when parent is expunged |
| `refresh-expire` | Refresh/expire related objects with parent |
| `all` | Shorthand for `save-update, merge, refresh-expire, expunge, delete` |

```python
# Common patterns:
cascade="all, delete-orphan"    # Strong ownership (orders belong to user)
cascade="save-update, merge"    # Weak association (default)
cascade="all"                   # Ownership but orphans allowed
```

> **Interview Tip:** `delete-orphan` is NOT included in `"all"`. You must specify it explicitly: `"all, delete-orphan"`.

---

## Loading Strategies — Solving the N+1 Problem

### The N+1 Problem

```python
# This code fires N+1 queries:
users = session.scalars(select(User)).all()      # 1 query: SELECT * FROM users
for user in users:
    print(user.orders)                            # N queries: SELECT * FROM orders WHERE user_id = ?
# Total: 1 + N queries = N+1 problem!
```

### Lazy Loading (Default)

```python
# Relationship is loaded ONLY when accessed
user.orders  # ← SQL query fires HERE

# Good for: accessing relationships rarely
# Bad for: loops over collections
```

### Eager Loading Solutions

#### `selectinload` (Recommended Default)

```python
from sqlalchemy.orm import selectinload

# 2 queries total (regardless of N users)
stmt = select(User).options(selectinload(User.orders))
users = session.scalars(stmt).all()
# Query 1: SELECT * FROM users
# Query 2: SELECT * FROM orders WHERE user_id IN (1, 2, 3, ...)
```

#### `joinedload`

```python
from sqlalchemy.orm import joinedload

# 1 query with LEFT JOIN
stmt = select(User).options(joinedload(User.orders))
users = session.scalars(stmt).unique().all()  # unique() required!
# SELECT users.*, orders.* FROM users LEFT JOIN orders ON ...
```

> **Gotcha:** `joinedload` can produce duplicate parent rows → must call `.unique()`.

#### `subqueryload`

```python
from sqlalchemy.orm import subqueryload

# 2 queries (uses subquery instead of IN clause)
stmt = select(User).options(subqueryload(User.orders))
# Query 1: SELECT * FROM users
# Query 2: SELECT * FROM orders WHERE user_id IN (SELECT id FROM users)
```

#### `contains_eager` (with explicit join)

```python
from sqlalchemy.orm import contains_eager

# When you've already joined and want to populate the relationship
stmt = (
    select(User)
    .join(User.orders)
    .options(contains_eager(User.orders))
    .where(Order.total > 100)
)
users = session.scalars(stmt).unique().all()
```

### Loading Strategy Comparison

| Strategy | Queries | Best For |
|----------|---------|----------|
| `lazy` (default) | N+1 | Single object access, rarely traversed relationships |
| `selectinload` | 2 | **Most common choice**, collections |
| `joinedload` | 1 | Many-to-one (single object), small result sets |
| `subqueryload` | 2 | Large collections with complex base query |
| `contains_eager` | 1 | When you already JOIN for filtering |
| `raiseload` | Error | Prevent accidental lazy loading |

#### `raiseload` — Prevent Accidental Lazy Loading

```python
from sqlalchemy.orm import raiseload

# Raise error if any relationship is accessed without explicit loading
stmt = select(User).options(raiseload("*"))
user = session.scalars(stmt).first()
user.orders  # raises InvalidRequestError!

# Per-relationship
stmt = select(User).options(
    selectinload(User.orders),
    raiseload(User.profile),
)
```

### Nested Eager Loading

```python
# Load user → orders → order_items → product
stmt = select(User).options(
    selectinload(User.orders)
    .selectinload(Order.items)
    .joinedload(OrderItem.product)
)
```

---

## ORM Joins

### Relationship-Based Joins

```python
from sqlalchemy import select

# Join using relationship
stmt = (
    select(User.name, Order.total)
    .join(User.orders)              # Uses the relationship definition
)

# Explicit join condition
stmt = (
    select(User.name, Order.total)
    .join(Order, User.id == Order.user_id)
)

# LEFT JOIN
stmt = (
    select(User.name, Order.total)
    .join(User.orders, isouter=True)
)

# Multiple joins
stmt = (
    select(User.name, Order.total, OrderItem.quantity)
    .join(User.orders)
    .join(Order.items)
)
```

### Filtering on Relationships

```python
# Users who have at least one order > 100
stmt = select(User).where(User.orders.any(Order.total > 100))

# Users where ALL orders are > 100
stmt = select(User).where(~User.orders.any(Order.total <= 100))

# Users who have NO orders
stmt = select(User).where(~User.orders.any())

# Orders belonging to active users
stmt = select(Order).where(Order.user.has(User.is_active == True))
```

---

## Common Interview Questions — Relationships

### Q1: What is the N+1 query problem and how do you solve it in SQLAlchemy?

**Problem:** Loading a collection of objects, then accessing a lazy-loaded relationship on each → 1 query for the collection + N queries for relationships.

**Solutions:**
1. **`selectinload()`** — 2 queries total using `IN` clause (best default)
2. **`joinedload()`** — 1 query with LEFT JOIN (good for many-to-one)
3. **`raiseload()`** — Prevent accidental lazy loading (use in production)
4. **`contains_eager()`** — Use when you already have an explicit join

---

### Q2: When do you use `selectinload` vs `joinedload`?

| | `selectinload` | `joinedload` |
|---|----------------|--------------|
| Queries | 2 (SELECT + SELECT ... IN) | 1 (LEFT JOIN) |
| Best for | One-to-many (collections) | Many-to-one (single object) |
| Duplicates? | No | Yes (must call `.unique()`) |
| Collection size | Handles large collections well | Cartesian product risk |
| Default choice | ✅ Yes | For single-object relationships |

---

### Q3: Explain `cascade="all, delete-orphan"`.

- **`all`** = `save-update` + `merge` + `refresh-expire` + `expunge` + `delete`
- **`delete-orphan`** = If a child is removed from the parent's collection, delete it

```python
user.orders.remove(order)    # With delete-orphan → DELETE FROM orders WHERE id = ?
                              # Without → order stays in DB with NULL user_id
```

**Use for:** Strong parent-child ownership where children can't exist without parent.

---

### Q4: What is `back_populates` vs `backref`?

```python
# back_populates (explicit — recommended in SQLAlchemy 2.0)
class User(Base):
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    user: Mapped["User"] = relationship(back_populates="orders")

# backref (implicit — creates reverse relationship automatically)
class User(Base):
    orders: Mapped[list["Order"]] = relationship(backref="user")

# class Order doesn't need to define the relationship — it's auto-created
```

**`back_populates`** is preferred because both sides are **explicitly defined**, making the code more readable and IDE-friendly.
