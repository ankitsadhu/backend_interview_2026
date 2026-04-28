# SQLAlchemy Study Guide

> Comprehensive SQLAlchemy learning path — from Core to ORM, organized for interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Core Fundamentals](./01_core_fundamentals.md) | Engine, Connection, MetaData, Table, Column, raw SQL, Core expressions | 🟢 Beginner |
| 02 | [ORM Basics](./02_orm_basics.md) | Declarative models, Session, CRUD, relationships, lazy loading | 🟢🟡 Beginner-Intermediate |
| 03 | [Relationships & Joins](./03_relationships_and_joins.md) | One-to-many, many-to-many, self-referential, polymorphic, eager/lazy loading, N+1 problem | 🟡 Intermediate |
| 04 | [Querying & Advanced ORM](./04_querying_and_advanced.md) | Query API, filters, aggregates, subqueries, hybrid properties, events, mixins | 🟡🔴 Intermediate-Advanced |
| 05 | [Migrations (Alembic)](./05_alembic_migrations.md) | Alembic setup, autogenerate, upgrade/downgrade, production workflows | 🟡🔴 Intermediate-Advanced |
| 06 | [Performance & Production](./06_performance_and_production.md) | Connection pooling, N+1 solutions, bulk operations, async SQLAlchemy, testing patterns | 🔴 Advanced |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_core_fundamentals.md` — understand Engine, Connection, MetaData
2. Read `02_orm_basics.md` — build models, master Session lifecycle

### Week 2: Relationships & Queries
3. Read `03_relationships_and_joins.md` — all relationship types, N+1 problem
4. Read `04_querying_and_advanced.md` — complex queries, hybrid properties

### Week 3: Production
5. Read `05_alembic_migrations.md` — schema migrations with Alembic
6. Read `06_performance_and_production.md` — pooling, bulk ops, async
