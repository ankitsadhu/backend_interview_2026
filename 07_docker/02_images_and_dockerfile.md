# Images & Dockerfile Deep Dive

## Build Process

```
┌──────────────────────────────────────────────────────┐
│  docker build -t myapp:1.0 .                          │
│                                                      │
│  1. Docker client sends build context to daemon       │
│     (all files in . minus .dockerignore)             │
│                                                      │
│  2. Daemon reads Dockerfile line by line              │
│                                                      │
│  3. Each instruction creates a layer:                 │
│     FROM  → pull base image                          │
│     RUN   → create temp container, execute, commit    │
│     COPY  → add files to layer                        │
│                                                      │
│  4. Each layer is cached (hash-based)                 │
│     If instruction + context unchanged → use cache    │
│                                                      │
│  5. Final image = stack of all layers                 │
└──────────────────────────────────────────────────────┘
```

---

## Layer Caching

Docker caches each layer. If an instruction and its inputs haven't changed, the cached layer is reused.

```dockerfile
# ❌ BAD — cache busted on every code change
FROM python:3.11-slim
WORKDIR /app
COPY . .                              # Any file change invalidates cache
RUN pip install -r requirements.txt   # Re-installs ALL deps every time!
CMD ["python", "app.py"]

# ✅ GOOD — dependencies cached separately
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .              # Only changes if deps change
RUN pip install -r requirements.txt   # Cached unless requirements.txt changes
COPY . .                              # Only app code layer changes
CMD ["python", "app.py"]
```

### Cache Rules

| Instruction | Cache Key |
|-------------|----------|
| `FROM` | Image digest |
| `RUN` | Command string (same string = cache hit) |
| `COPY` / `ADD` | File content checksums |
| `ENV`, `ARG` | String value |

**Cache is invalidated** from the first changed instruction onward — all subsequent layers are rebuilt.

---

## .dockerignore

Exclude files from the build context (like `.gitignore`).

```
# .dockerignore
.git
.gitignore
node_modules
__pycache__
*.pyc
.env
.venv
docker-compose*.yml
Dockerfile
README.md
tests/
.coverage
*.log
```

**Why it matters:**
- Reduces build context size → faster builds
- Prevents sensitive files from being copied into images
- Prevents unnecessary cache invalidation

---

## Multi-Stage Builds

Use **multiple `FROM` statements** to create intermediate build stages and copy only what's needed into the final image.

```dockerfile
# Stage 1: Build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production (only what's needed)
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

```dockerfile
# Go example — final image is just the binary!
# Stage 1: Build
FROM golang:1.21 AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# Stage 2: Minimal runtime
FROM alpine:3.18
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]

# Result:
# Build image: ~800 MB (Go SDK + build tools)
# Final image: ~15 MB (Alpine + single binary)
```

```dockerfile
# Python example
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
USER 1000
CMD ["python", "app.py"]
```

---

## Image Optimization

### Size Reduction Strategies

| Strategy | Impact | Example |
|----------|--------|---------|
| **Use slim/alpine base** | 50-90% smaller | `python:3.11-slim` instead of `python:3.11` |
| **Multi-stage builds** | Remove build tools | Separate builder and runtime stages |
| **Minimize layers** | Fewer layers | Combine related `RUN` commands |
| **Clean up in same layer** | Smaller layer | `RUN apt install && rm -rf /var/lib/apt/lists/*` |
| **No cache dirs** | Smaller pip/npm | `pip install --no-cache-dir`, `npm ci --omit=dev` |
| **Use .dockerignore** | Faster builds | Exclude `.git`, `node_modules`, etc. |

### Combine RUN Commands

```dockerfile
# ❌ BAD — 3 layers (cleanup doesn't shrink previous layers!)
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ GOOD — 1 layer (cleanup happens in same layer)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

### Base Image Comparison

| Base Image | Size | Includes | Use Case |
|-----------|------|----------|----------|
| `ubuntu:22.04` | ~77 MB | Full Ubuntu | When you need apt packages |
| `debian:bookworm-slim` | ~80 MB | Minimal Debian | General purpose |
| `python:3.11` | ~900 MB | Full Python + Debian | Development |
| `python:3.11-slim` | ~150 MB | Python + minimal Debian | Production |
| `python:3.11-alpine` | ~50 MB | Python + Alpine Linux | Smallest (but musl libc) |
| `node:18-alpine` | ~175 MB | Node.js + Alpine | Production Node.js |
| `alpine:3.18` | ~7 MB | Minimal Linux | Base for custom images |
| `gcr.io/distroless/base` | ~20 MB | Almost nothing (no shell!) | Highest security |
| `scratch` | 0 MB | Empty | Static binaries (Go, Rust) |

> **⚠️ Alpine gotcha:** Alpine uses `musl libc` instead of `glibc`. Some Python packages with C extensions may fail. Use `slim` for reliability.

---

## Docker Registries

```
┌──────────────┐          ┌──────────────────┐
│  docker push  │ ────────→│  Registry         │
│  docker pull  │ ←────────│  (Docker Hub,     │
│               │          │   ECR, GCR, ACR,  │
└──────────────┘          │   Harbor)          │
                           └──────────────────┘

Image naming convention:
  registry/namespace/repository:tag
  
  docker.io/library/nginx:1.25     (Docker Hub official)
  docker.io/myuser/myapp:v2.0      (Docker Hub user)
  123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest  (AWS ECR)
  gcr.io/my-project/myapp:v1.0     (Google GCR)
```

```bash
# Login to registry
docker login
docker login myregistry.com

# Tag for registry
docker tag myapp:latest myregistry.com/myapp:v1.0

# Push
docker push myregistry.com/myapp:v1.0

# Pull
docker pull myregistry.com/myapp:v1.0
```

---

## BuildKit (Modern Build Engine)

```bash
# Enable BuildKit (default in Docker 23.0+)
DOCKER_BUILDKIT=1 docker build .

# BuildKit features:
#   - Parallel build stages
#   - Better caching (mount cache)
#   - Secret mounts (no secrets in layers!)
#   - SSH agent forwarding
```

### Cache Mounts

```dockerfile
# Cache pip downloads across builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache apt downloads
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl
```

### Secret Mounts

```dockerfile
# Secret never appears in any layer!
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    npm install --registry https://private.registry.com

# Build with:
docker build --secret id=api_key,src=./api_key.txt .
```

---

## Image Tagging Strategy

```
Semantic Versioning:
  myapp:1.0.0    ← Exact version (immutable, for production)
  myapp:1.0      ← Minor version (may update patch)
  myapp:1        ← Major version (may update minor)
  myapp:latest   ← Latest build (⚠️ mutable, avoid in production!)

Environment-based:
  myapp:dev
  myapp:staging
  myapp:production

Git-based:
  myapp:abc1234         ← Git commit SHA (immutable, traceable)
  myapp:main-abc1234    ← Branch + commit
  myapp:v1.2.3          ← Git tag

Best Practice:
  ✅ Use immutable tags in production (v1.2.3 or SHA)
  ❌ Never use :latest in production (you don't know what you'll get)
```

---

## Interview Questions — Images

### Q1: How does Docker layer caching work?

Each Dockerfile instruction creates a layer. Docker caches layers by checking:
- `RUN`: same command string?
- `COPY`/`ADD`: same file checksums?
- If unchanged → reuse cached layer (skip rebuild)
- If changed → rebuild this layer AND all subsequent layers

**Optimization:** Put rarely-changing instructions (deps) before frequently-changing ones (code).

### Q2: Why use multi-stage builds?

1. Separate **build** dependencies from **runtime**
2. Build image: large (compilers, SDKs, dev tools)
3. Final image: small (only app + runtime deps)
4. **Smaller images** = faster deploys, less attack surface, less storage

### Q3: What's the difference between `COPY` and `ADD`?

| Feature | `COPY` | `ADD` |
|---------|--------|-------|
| Copy files | ✅ | ✅ |
| URL download | ❌ | ✅ (not recommended, use `curl` in `RUN`) |
| Auto-extract tar | ❌ | ✅ |
| Recommended | ✅ Always prefer `COPY` | Only for tar extraction |

### Q4: What are distroless images?

Images by Google that contain **only the application and its runtime dependencies** — no package manager, no shell, no OS utilities.

**Benefits:** Minimal attack surface, smaller images, no shell for attackers to use.
**Drawback:** Can't `docker exec bash` for debugging (no shell!). Use debug variants for troubleshooting.
