# Alembic Migrations

## What is Alembic?

Alembic is the **database migration tool** for SQLAlchemy — like Django's `makemigrations`/`migrate`, but for SQLAlchemy projects.

It tracks schema changes via **versioned migration scripts** and applies them in order.

```
your-project/
├── alembic/
│   ├── versions/          ← Migration scripts live here
│   │   ├── 001_create_users.py
│   │   ├── 002_add_email_column.py
│   │   └── 003_create_orders.py
│   ├── env.py             ← Environment configuration
│   └── script.py.mako     ← Template for new migrations
├── alembic.ini            ← Alembic configuration
├── models.py              ← SQLAlchemy models
└── app.py
```

---

## Setup

```bash
# Install
pip install alembic

# Initialize (creates alembic/ directory and alembic.ini)
alembic init alembic
```

### Configuration

```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+psycopg2://user:password@localhost/mydb
```

```python
# alembic/env.py — connect Alembic to your models
from models import Base  # Import your Base class

# Find this line and set target_metadata:
target_metadata = Base.metadata
```

### Environment Variables for Database URL

```python
# alembic/env.py — use environment variable instead of hardcoding
import os
from alembic import context

def get_url():
    return os.environ.get("DATABASE_URL", "postgresql://localhost/mydb")

# In run_migrations_online():
connectable = engine_from_config(
    {"sqlalchemy.url": get_url()},
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)
```

---

## Creating Migrations

### Auto-Generate (Recommended)

Alembic compares your models to the database and generates a migration:

```bash
# Auto-generate migration
alembic revision --autogenerate -m "create users table"
```

This creates a file like `alembic/versions/abc123_create_users_table.py`:

```python
"""create users table

Revision ID: abc123def456
Revises: (empty — first migration)
Create Date: 2026-03-16 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

### Manual Migration

```bash
# Create empty migration (for complex changes)
alembic revision -m "add full text search"
```

```python
def upgrade() -> None:
    # Raw SQL for complex operations
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("""
        ALTER TABLE articles
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(body, '')), 'B')
        ) STORED
    """)
    op.execute("CREATE INDEX idx_articles_search ON articles USING gin (search_vector)")

def downgrade() -> None:
    op.drop_index("idx_articles_search")
    op.execute("ALTER TABLE articles DROP COLUMN search_vector")
```

---

## Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply one step forward
alembic upgrade +1

# Rollback one step
alembic downgrade -1

# Rollback to beginning
alembic downgrade base

# Upgrade to specific revision
alembic upgrade abc123def456

# View current revision
alembic current

# View migration history
alembic history --verbose

# Show SQL without executing (for review)
alembic upgrade head --sql > migration.sql
```

---

## Common Operations

### Add Column

```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

### Rename Column

```python
def upgrade():
    op.alter_column('users', 'name', new_column_name='full_name')

def downgrade():
    op.alter_column('users', 'full_name', new_column_name='name')
```

### Add Non-Nullable Column (With Data)

```python
def upgrade():
    # Step 1: Add as nullable
    op.add_column('users', sa.Column('role', sa.String(50), nullable=True))

    # Step 2: Backfill data
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")

    # Step 3: Make non-nullable
    op.alter_column('users', 'role', nullable=False, server_default='user')

def downgrade():
    op.drop_column('users', 'role')
```

### Create Index

```python
def upgrade():
    op.create_index('idx_users_email_lower', 'users', [sa.text('lower(email)')])
    op.create_index(
        'idx_orders_status_date', 'orders', ['status', 'created_at'],
        postgresql_concurrently=True  # Non-blocking!
    )

def downgrade():
    op.drop_index('idx_orders_status_date')
    op.drop_index('idx_users_email_lower')
```

### Add Foreign Key

```python
def upgrade():
    op.add_column('orders', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_orders_user_id', 'orders', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    op.drop_constraint('fk_orders_user_id', 'orders', type_='foreignkey')
    op.drop_column('orders', 'user_id')
```

### Rename Table

```python
def upgrade():
    op.rename_table('users', 'accounts')

def downgrade():
    op.rename_table('accounts', 'users')
```

### Create Enum Type (PostgreSQL)

```python
def upgrade():
    status_enum = sa.Enum('pending', 'active', 'suspended', name='user_status')
    status_enum.create(op.get_bind())
    op.add_column('users', sa.Column('status', status_enum, server_default='pending'))

def downgrade():
    op.drop_column('users', 'status')
    sa.Enum(name='user_status').drop(op.get_bind())
```

---

## Data Migrations

Migrate existing data alongside schema changes:

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade():
    # Create reference to table (without importing models!)
    users = table('users',
        column('id', sa.Integer),
        column('full_name', sa.String),
        column('first_name', sa.String),
        column('last_name', sa.String),
    )

    # Step 1: Add new columns
    op.add_column('users', sa.Column('first_name', sa.String(50)))
    op.add_column('users', sa.Column('last_name', sa.String(50)))

    # Step 2: Migrate data
    conn = op.get_bind()
    conn.execute(
        users.update().values(
            first_name=sa.func.split_part(users.c.full_name, ' ', 1),
            last_name=sa.func.split_part(users.c.full_name, ' ', 2),
        )
    )

    # Step 3: Make non-nullable
    op.alter_column('users', 'first_name', nullable=False)
    op.alter_column('users', 'last_name', nullable=False)

    # Step 4: Drop old column
    op.drop_column('users', 'full_name')
```

> **Warning:** Never import your ORM models in migration scripts! Models change over time, but migrations must always work the same way. Use `table()` and `column()` for data operations.

---

## Production Best Practices

### Pre-Deployment Checklist

1. **Always review auto-generated migrations** — they can miss rename operations (shows as drop + create)
2. **Test migrations** — run `upgrade` AND `downgrade` on a staging database
3. **Generate SQL for review**: `alembic upgrade head --sql`
4. **Non-blocking index creation**: Use `postgresql_concurrently=True`
5. **Split large migrations** — schema change in one, data migration in another

### Zero-Downtime Migrations

```
Safe operations (no lock):          Unsafe operations (locks table):
✅ ADD COLUMN (nullable)             ❌ ADD COLUMN NOT NULL (without default)
✅ DROP COLUMN                       ❌ ALTER COLUMN TYPE
✅ CREATE INDEX CONCURRENTLY         ❌ CREATE INDEX (non-concurrent)
✅ ADD CONSTRAINT ... NOT VALID      ❌ ADD CONSTRAINT (validated)
✅ DROP CONSTRAINT                   ❌ RENAME TABLE (breaks queries)
```

### Safe Non-Nullable Column Addition

```python
def upgrade():
    # Step 1: Add nullable column with default
    op.add_column('users', sa.Column('role', sa.String(50), server_default='user'))

    # Step 2: Backfill in batches (for large tables)
    conn = op.get_bind()
    while True:
        result = conn.execute(sa.text(
            "UPDATE users SET role = 'user' WHERE role IS NULL LIMIT 10000"
        ))
        if result.rowcount == 0:
            break

    # Step 3: Make non-nullable
    op.alter_column('users', 'role', nullable=False)
```

---

## Common Interview Questions — Migrations

### Q1: Why not import ORM models in migration scripts?

Models change over time. A migration from 6 months ago expects the model as it was then. If you import current models, the migration may break if columns were renamed or removed.

**Solution:** Use `sa.table()` and `sa.column()` for data operations in migrations.

### Q2: How do you handle a migration that adds a NOT NULL column to a table with existing data?

Three-step process:
1. Add the column as **nullable** (with a `server_default`)
2. **Backfill** existing rows with the default value
3. **ALTER** the column to NOT NULL

This avoids locking and ensures existing rows satisfy the constraint.

### Q3: What's the difference between `alembic upgrade head` and `alembic upgrade +1`?

- `head` — Apply **all** pending migrations
- `+1` — Apply only the **next** migration

In production, `head` is standard. `+1` is useful for step-by-step debugging.
