# Querying & Advanced ORM

## Advanced Query Patterns

### Aggregations

```python
from sqlalchemy import select, func

with Session(engine) as session:
    # Count
    count = session.scalar(select(func.count()).select_from(User))

    # Group by with aggregates
    stmt = (
        select(
            User.role,
            func.count().label("count"),
            func.avg(User.age).label("avg_age"),
            func.max(User.age).label("max_age"),
        )
        .group_by(User.role)
        .having(func.count() > 5)
    )
    results = session.execute(stmt).all()
    for role, count, avg_age, max_age in results:
        print(f"{role}: {count} users, avg age {avg_age:.1f}")
```

### Subqueries

```python
# Subquery: users with above-average order total
avg_total = select(func.avg(Order.total)).scalar_subquery()

stmt = (
    select(User)
    .join(User.orders)
    .where(Order.total > avg_total)
)

# Correlated subquery: total spent per user
total_spent = (
    select(func.sum(Order.total))
    .where(Order.user_id == User.id)
    .correlate(User)
    .scalar_subquery()
)

stmt = select(User.name, total_spent.label("total_spent"))

# Subquery in FROM
user_totals = (
    select(
        Order.user_id,
        func.sum(Order.total).label("total_spent")
    )
    .group_by(Order.user_id)
    .subquery()
)

stmt = (
    select(User.name, user_totals.c.total_spent)
    .join(user_totals, User.id == user_totals.c.user_id)
    .order_by(user_totals.c.total_spent.desc())
)
```

### EXISTS / NOT EXISTS

```python
from sqlalchemy import exists

# Users who have at least one order
has_orders = exists().where(Order.user_id == User.id)
stmt = select(User).where(has_orders)

# Users with NO orders
stmt = select(User).where(~has_orders)

# Also via relationship (more "ORM-like"):
stmt = select(User).where(User.orders.any())
stmt = select(User).where(~User.orders.any())

# Users with an order above 100
stmt = select(User).where(User.orders.any(Order.total > 100))
```

### CASE Expressions

```python
from sqlalchemy import case

stmt = select(
    User.name,
    case(
        (User.age < 18, "minor"),
        (User.age < 65, "adult"),
        else_="senior"
    ).label("age_group")
)
```

### UNION / INTERSECT / EXCEPT

```python
from sqlalchemy import union, union_all, intersect, except_

stmt1 = select(User.name).where(User.role == "admin")
stmt2 = select(User.name).where(User.is_active == True)

combined = union(stmt1, stmt2)        # UNION (deduplicated)
combined = union_all(stmt1, stmt2)    # UNION ALL (with duplicates)
combined = intersect(stmt1, stmt2)    # INTERSECT
combined = except_(stmt1, stmt2)      # EXCEPT

results = session.execute(combined).all()
```

### Window Functions

```python
from sqlalchemy import func, over

# ROW_NUMBER()
stmt = select(
    User.name,
    User.department,
    User.salary,
    func.row_number().over(
        partition_by=User.department,
        order_by=User.salary.desc()
    ).label("rank")
)

# Running total
stmt = select(
    Order.id,
    Order.total,
    func.sum(Order.total).over(
        order_by=Order.created_at
    ).label("running_total")
)

# LAG / LEAD
stmt = select(
    Order.id,
    Order.total,
    func.lag(Order.total, 1).over(
        order_by=Order.created_at
    ).label("prev_total")
)
```

### CTEs (Common Table Expressions)

```python
# Define CTE
high_spenders = (
    select(
        Order.user_id,
        func.sum(Order.total).label("total_spent")
    )
    .group_by(Order.user_id)
    .having(func.sum(Order.total) > 1000)
    .cte("high_spenders")
)

# Use CTE in main query
stmt = (
    select(User.name, high_spenders.c.total_spent)
    .join(high_spenders, User.id == high_spenders.c.user_id)
    .order_by(high_spenders.c.total_spent.desc())
)

# Recursive CTE
from sqlalchemy import literal

org_chart = (
    select(
        Employee.id,
        Employee.name,
        Employee.manager_id,
        literal(1).label("depth"),
    )
    .where(Employee.manager_id.is_(None))
    .cte("org_chart", recursive=True)
)

org_chart = org_chart.union_all(
    select(
        Employee.id,
        Employee.name,
        Employee.manager_id,
        (org_chart.c.depth + 1).label("depth"),
    )
    .join(org_chart, Employee.manager_id == org_chart.c.id)
)

stmt = select(org_chart)
```

---

## Hybrid Properties

Computed properties that work **both in Python and in SQL**.

```python
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    salary: Mapped[int] = mapped_column(Integer)
    bonus: Mapped[int] = mapped_column(Integer, default=0)

    @hybrid_property
    def full_name(self) -> str:
        """Works in Python"""
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        """Works in SQL"""
        return cls.first_name + " " + cls.last_name

    @hybrid_property
    def total_compensation(self) -> int:
        return self.salary + self.bonus

    @total_compensation.expression
    def total_compensation(cls):
        return cls.salary + cls.bonus

    @hybrid_method
    def earns_more_than(self, amount: int) -> bool:
        return self.total_compensation > amount

    @earns_more_than.expression
    def earns_more_than(cls, amount: int):
        return cls.salary + cls.bonus > amount

# Usage — works in Python AND SQL!
user = session.get(User, 1)
print(user.full_name)                    # Python: "Alice Smith"
print(user.total_compensation)           # Python: 155000

# In query (generates SQL)
stmt = select(User).where(User.full_name == "Alice Smith")
# SELECT * FROM users WHERE first_name || ' ' || last_name = 'Alice Smith'

stmt = select(User).where(User.earns_more_than(100000))
# SELECT * FROM users WHERE salary + bonus > 100000

stmt = select(User).order_by(User.total_compensation.desc())
```

---

## Column Properties and Computed Columns

```python
from sqlalchemy.orm import column_property
from sqlalchemy import select, func

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))

    # Computed on every load (SQL expression)
    full_name = column_property(first_name + " " + last_name)

    # Correlated subquery as a column
    order_count = column_property(
        select(func.count(Order.id))
        .where(Order.user_id == id)
        .correlate_except(Order)
        .scalar_subquery()
    )

# Usage
user = session.get(User, 1)
print(user.full_name)     # Loaded from SQL, not Python
print(user.order_count)   # Loaded as part of the SELECT query
```

---

## Event Listeners

Hook into ORM lifecycle events for auditing, validation, or side effects.

```python
from sqlalchemy import event

# Before insert hook
@event.listens_for(User, "before_insert")
def user_before_insert(mapper, connection, target):
    target.email = target.email.lower()
    target.created_at = datetime.utcnow()

# Before update hook
@event.listens_for(User, "before_update")
def user_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()

# After delete hook
@event.listens_for(User, "after_delete")
def user_after_delete(mapper, connection, target):
    print(f"User {target.id} deleted — audit log created")

# Session-level events
@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    for obj in session.new:
        if isinstance(obj, User):
            obj.email = obj.email.lower()

    for obj in session.dirty:
        if isinstance(obj, User):
            obj.updated_at = datetime.utcnow()
```

### Attribute Events

```python
# Validate on set
@event.listens_for(User.email, "set")
def validate_email(target, value, oldvalue, initiator):
    if value and "@" not in value:
        raise ValueError(f"Invalid email: {value}")
    return value.lower()
```

---

## Polymorphic Inheritance

### Single Table Inheritance (STI)

All subclasses in **one table**, differentiated by a discriminator column.

```python
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))  # Discriminator

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "employee",
    }

class Manager(Employee):
    department: Mapped[str | None] = mapped_column(String(100))

    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }

class Engineer(Employee):
    language: Mapped[str | None] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }

# Query returns correct types automatically
employees = session.scalars(select(Employee)).all()
# Returns mix of Employee, Manager, Engineer objects

managers = session.scalars(select(Manager)).all()
# Only Manager objects
```

### Joined Table Inheritance

Base table + subclass tables with foreign keys.

```python
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))
    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "employee"}

class Manager(Employee):
    __tablename__ = "managers"
    id: Mapped[int] = mapped_column(ForeignKey("employees.id"), primary_key=True)
    department: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {"polymorphic_identity": "manager"}
```

---

## Common Interview Questions — Advanced ORM

### Q1: What is a hybrid property and when would you use it?

A hybrid property works as a **Python property** on instances and as a **SQL expression** in queries. Use when:

1. You need a computed field that should be filterable/sortable in SQL
2. You want consistent logic between Python and database
3. Examples: `full_name`, `total_compensation`, `is_expired`, `age_in_years`

### Q2: How do you prevent SELECT N+1 in a codebase?

1. **Set `raiseload("*")`** as default → forces explicit loading declarations
2. **Code review** for any relationship access in loops
3. **Use `selectinload`** for collections, `joinedload` for single objects
4. **Monitor** with SQLAlchemy logging (`echo=True`) or query counting in tests
5. **Automated tests** that assert query count:

```python
# Test that listing users fires exactly 2 queries
from sqlalchemy import event

query_count = 0

@event.listens_for(engine, "before_cursor_execute")
def count_queries(*args):
    nonlocal query_count
    query_count += 1

users = list_users()  # Your function
assert query_count == 2, f"Expected 2 queries, got {query_count}"
```

### Q3: What is the difference between `column_property` and `hybrid_property`?

| Feature | `column_property` | `hybrid_property` |
|---------|-------------------|-------------------|
| SQL on load | Yes (included in SELECT) | No (computed in Python) |
| Filterable | Yes | Yes (with `.expression`) |
| Python computation | Not easily | Yes (via getter) |
| Use case | Always-needed SQL computation | Conditional or complex logic |
