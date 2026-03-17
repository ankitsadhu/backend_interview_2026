# Docker Compose

## What is Docker Compose?

**Docker Compose** defines and runs **multi-container** applications using a YAML file.

```
Without Compose (manual):                With Compose:
  docker network create mynet             docker compose up -d
  docker volume create dbdata             
  docker run -d --name db \               # That's it!
    --network mynet \                     # All defined in
    -v dbdata:/var/lib/postgresql/data \   # docker-compose.yml
    -e POSTGRES_PASSWORD=secret \
    postgres:16
  docker run -d --name app \
    --network mynet \
    -p 8000:8000 \
    -e DB_HOST=db \
    myapp:latest
```

---

## docker-compose.yml Structure

```yaml
# docker-compose.yml

services:
  # Service 1: Web application
  app:
    build: ./app                     # Build from Dockerfile in ./app
    # OR
    image: myapp:latest              # Use pre-built image
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy   # Wait for health check
      cache:
        condition: service_started
    volumes:
      - ./app:/app                   # Bind mount (dev)
    networks:
      - frontend
      - backend
    restart: unless-stopped

  # Service 2: Database
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: secret
    volumes:
      - dbdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # Init script
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # Service 3: Cache
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - cachedata:/data
    networks:
      - backend
    command: redis-server --appendonly yes

  # Service 4: Worker (background)
  worker:
    build: ./app
    command: python worker.py
    environment:
      - DB_HOST=db
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    networks:
      - backend
    deploy:
      replicas: 3                    # Run 3 worker instances

# Named volumes (persist across restarts)
volumes:
  dbdata:
  cachedata:

# Custom networks
networks:
  frontend:
  backend:
```

---

## Compose Commands

```bash
# Start all services
docker compose up                    # Foreground (see logs)
docker compose up -d                 # Detached (background)

# Build and start
docker compose up --build            # Rebuild images before starting

# Stop services
docker compose stop                  # Stop (keep containers)
docker compose down                  # Stop and remove containers + networks
docker compose down -v               # Also remove volumes
docker compose down --rmi all        # Also remove images

# Restart
docker compose restart
docker compose restart app           # Restart specific service

# Logs
docker compose logs                  # All services
docker compose logs -f app           # Follow specific service
docker compose logs --tail 50 app    # Last 50 lines

# Scale services
docker compose up -d --scale worker=5

# Execute command in service
docker compose exec app bash
docker compose exec db psql -U user -d mydb

# Run one-off command
docker compose run --rm app python manage.py migrate

# List containers
docker compose ps

# View config (resolved)
docker compose config
```

---

## Environment Variables

```yaml
services:
  app:
    # Method 1: Direct values
    environment:
      - DB_HOST=db
      - DB_PORT=5432

    # Method 2: From .env file
    env_file:
      - .env
      - .env.local

    # Method 3: Variable substitution from host
    environment:
      - DB_PASSWORD=${DB_PASSWORD}    # from host env or .env
      - APP_PORT=${APP_PORT:-8000}    # with default value
```

```bash
# .env file (auto-loaded by compose)
DB_HOST=db
DB_PORT=5432
DB_PASSWORD=supersecret
APP_PORT=8000

# Override at runtime
DB_PASSWORD=different docker compose up
```

---

## depends_on and Service Health

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy    # Wait for health check to pass
      cache:
        condition: service_started    # Just wait for container to start
      migrations:
        condition: service_completed_successfully  # Wait for exit code 0

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  migrations:
    build: ./app
    command: python manage.py migrate
    depends_on:
      db:
        condition: service_healthy
```

---

## Profiles (Conditional Services)

```yaml
services:
  app:
    build: ./app
    # No profile — always runs

  db:
    image: postgres:16
    # No profile — always runs

  debug:
    image: busybox
    profiles: ["debug"]              # Only runs with --profile debug

  monitoring:
    image: prometheus
    profiles: ["monitoring"]

  grafana:
    image: grafana/grafana
    profiles: ["monitoring"]
```

```bash
docker compose up                         # Only app + db
docker compose --profile debug up         # app + db + debug
docker compose --profile monitoring up    # app + db + prometheus + grafana
docker compose --profile debug --profile monitoring up  # Everything
```

---

## Override Files

```
docker-compose.yml          ← Base configuration
docker-compose.override.yml ← Auto-applied overrides (dev defaults)
docker-compose.prod.yml     ← Production overrides (manual)
```

```yaml
# docker-compose.yml (base)
services:
  app:
    build: ./app
    ports:
      - "8000:8000"

# docker-compose.override.yml (dev — auto-applied)
services:
  app:
    volumes:
      - ./app:/app           # Live reload
    environment:
      - DEBUG=true

# docker-compose.prod.yml (production)
services:
  app:
    image: registry.com/myapp:v1.2.3   # Pre-built image
    environment:
      - DEBUG=false
    deploy:
      replicas: 3
```

```bash
# Dev (uses base + override automatically)
docker compose up

# Production (explicit files)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Real-World Compose Example: Full Stack

```yaml
# Full-stack app: React + FastAPI + PostgreSQL + Redis + Nginx
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - frontend
      - api
    networks:
      - frontend

  frontend:
    build: ./frontend
    expose:
      - "3000"
    networks:
      - frontend

  api:
    build: ./backend
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - frontend
      - backend

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      retries: 5

  cache:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data
    networks:
      - backend

  worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    networks:
      - backend

volumes:
  pgdata:
  redisdata:

networks:
  frontend:
  backend:
```

---

## Interview Questions — Compose

### Q1: What is the difference between `docker compose up` and `docker compose run`?

- `up`: Starts **all services** defined in the compose file
- `run`: Runs a **one-off command** against a service (creates a new container, useful for migrations, tests)

### Q2: How do you handle secrets in Docker Compose?

1. **Environment variables** from `.env` file (simple, but visible in `docker inspect`)
2. **Docker secrets** (Swarm mode — encrypted at rest and in transit)
3. **External secret managers** (Vault, AWS Secrets Manager) injected at runtime
4. **Never** hardcode secrets in `docker-compose.yml` or Dockerfiles

### Q3: How does networking work in Compose?

Compose automatically creates a **user-defined bridge network** for the project. All services are on this network and can reach each other **by service name** (Docker DNS). You can define additional custom networks for isolation.
