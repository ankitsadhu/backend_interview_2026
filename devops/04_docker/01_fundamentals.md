# Docker Fundamentals

## What is Docker?

**Docker** is a platform for building, shipping, and running applications inside **containers** — lightweight, isolated environments that package code with all its dependencies.

> *"It works on my machine"* → *"It works in the container"* → It works everywhere.

---

## Containers vs Virtual Machines

```
VIRTUAL MACHINES:                       CONTAINERS:
┌─────────────────────────┐            ┌─────────────────────────┐
│  App A │  App B │ App C │            │  App A │  App B │ App C │
├────────┼────────┼───────┤            ├────────┼────────┼───────┤
│Guest OS│Guest OS│GuestOS│            │  Libs  │  Libs  │ Libs  │
├────────┴────────┴───────┤            ├────────┴────────┴───────┤
│       Hypervisor         │            │    Container Runtime     │
│    (VMware, KVM, etc.)  │            │    (Docker Engine)       │
├─────────────────────────┤            ├─────────────────────────┤
│       Host OS            │            │       Host OS            │
├─────────────────────────┤            ├─────────────────────────┤
│       Hardware           │            │       Hardware           │
└─────────────────────────┘            └─────────────────────────┘

Each VM: full OS (GB)                  Each container: just app + libs (MB)
Boot time: minutes                     Start time: seconds
```

| Aspect | Virtual Machine | Container |
|--------|----------------|-----------|
| **Isolation** | Full OS isolation (strongest) | Process-level isolation (namespaces + cgroups) |
| **Size** | GBs (includes full OS) | MBs (just app + dependencies) |
| **Startup** | Minutes | Seconds (or less) |
| **Performance** | Near-native (hardware virtualization) | Native (shares host kernel) |
| **Density** | ~10 VMs per host | ~100+ containers per host |
| **OS** | Any OS (Windows on Linux host via hypervisor) | Must match host kernel (Linux on Linux) |
| **Use case** | Strong isolation, different OS | Microservices, CI/CD, consistent environments |

---

## Docker Architecture

```
┌──────────────────────────────────────────────────────┐
│                     Docker Client                     │
│                  (docker CLI / API)                    │
│                                                      │
│  docker build    docker pull    docker run            │
└──────────────┬───────────────────────────────────────┘
               │ REST API (unix socket or TCP)
               ▼
┌──────────────────────────────────────────────────────┐
│                   Docker Daemon (dockerd)              │
│                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Images      │  │  Containers  │  │  Networks    │ │
│  │  Manager     │  │  Manager     │  │  Manager     │ │
│  └──────┬──────┘  └──────┬───────┘  └─────────────┘ │
│         │                │                            │
│         ▼                ▼                            │
│  ┌──────────────────────────────┐                    │
│  │        containerd             │  ← Container runtime│
│  │  ┌────────────────────────┐  │                    │
│  │  │        runc             │  │  ← OCI runtime     │
│  │  │  (creates containers)  │  │    (creates Linux   │
│  │  └────────────────────────┘  │     processes)       │
│  └──────────────────────────────┘                    │
└──────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│                   Host OS (Linux Kernel)               │
│                                                      │
│  Namespaces (isolation) + Cgroups (resource limits)   │
└──────────────────────────────────────────────────────┘
```

### Key Components

| Component | Role |
|-----------|------|
| **Docker Client** | CLI tool (`docker` command) — sends commands to daemon |
| **Docker Daemon** (`dockerd`) | Background service managing images, containers, networks, volumes |
| **containerd** | Industry-standard container runtime (manages container lifecycle) |
| **runc** | Low-level OCI runtime (creates actual Linux processes with namespaces) |
| **Docker Registry** | Stores and distributes images (Docker Hub, ECR, GCR, ACR) |

---

## Images

An **image** is a read-only template for creating containers. Built from a **Dockerfile** — a series of instructions that produce **layers**.

```
Image Layers:
  ┌──────────────────────────┐
  │  Layer 5: CMD ["python"] │  ← Metadata (no disk change)
  ├──────────────────────────┤
  │  Layer 4: COPY app.py    │  ← Application code
  ├──────────────────────────┤
  │  Layer 3: RUN pip install│  ← Dependencies
  ├──────────────────────────┤
  │  Layer 2: RUN apt update │  ← System packages
  ├──────────────────────────┤
  │  Layer 1: FROM python:3.11│  ← Base image (OS + Python)
  └──────────────────────────┘
  
  Each layer:
    - Read-only
    - Shared across images (deduplication)
    - Cached during builds (unchanged layers reused)
```

### Image Commands

```bash
# Pull image from registry
docker pull python:3.11-slim

# List local images
docker images
docker image ls

# Image details
docker inspect python:3.11-slim

# Image history (layers)
docker history python:3.11-slim

# Remove image
docker rmi python:3.11-slim
docker image rm python:3.11-slim

# Remove unused images
docker image prune         # Dangling images only
docker image prune -a      # All unused images

# Tag an image
docker tag myapp:latest myregistry.com/myapp:v1.0

# Push to registry
docker push myregistry.com/myapp:v1.0

# Save/load images (offline transfer)
docker save myapp:latest > myapp.tar
docker load < myapp.tar
```

---

## Containers

A **container** is a running instance of an image, with its own writable layer on top.

```
Container = Image (read-only layers) + Container Layer (read-write)

┌──────────────────────────┐
│  Container Layer (R/W)   │  ← Changes, new files, modified files
├──────────────────────────┤
│  Image Layer 4 (R/O)     │
├──────────────────────────┤
│  Image Layer 3 (R/O)     │  ← Shared with other containers
├──────────────────────────┤
│  Image Layer 2 (R/O)     │    using the same image
├──────────────────────────┤
│  Image Layer 1 (R/O)     │
└──────────────────────────┘

Copy-on-Write (CoW):
  When container modifies a file from the image:
  1. File is copied to container layer
  2. Modification happens on the copy
  3. Original image layer unchanged
```

### Container Lifecycle Commands

```bash
# Run a container
docker run -d --name myapp -p 8080:80 nginx:latest
#  -d        : detached (background)
#  --name    : container name
#  -p 8080:80: map host:container port
#  nginx     : image to use

# Run interactively
docker run -it ubuntu:22.04 bash
#  -i  : interactive (stdin)
#  -t  : allocate TTY

# Run with auto-remove (ephemeral)
docker run --rm -it python:3.11 python -c "print('hello')"

# List containers
docker ps           # Running only
docker ps -a        # All (including stopped)

# Container info
docker inspect myapp
docker logs myapp
docker logs -f myapp   # Follow (tail)
docker stats           # Live resource usage

# Execute command in running container
docker exec -it myapp bash
docker exec myapp ls /app

# Stop / Start / Restart
docker stop myapp      # Graceful (SIGTERM → 10s → SIGKILL)
docker start myapp
docker restart myapp
docker kill myapp      # Force kill (SIGKILL)

# Remove container
docker rm myapp
docker rm -f myapp     # Force remove (even if running)

# Remove all stopped containers
docker container prune
```

### Resource Limits

```bash
# Memory limit
docker run -m 512m myapp            # 512 MB max
docker run --memory-swap 1g myapp   # Memory + swap limit

# CPU limit
docker run --cpus 2 myapp           # Max 2 CPU cores
docker run --cpu-shares 512 myapp   # Relative weight (default=1024)

# Combined
docker run -m 1g --cpus 1.5 -d myapp
```

### Environment Variables

```bash
# Set env vars
docker run -e DB_HOST=localhost -e DB_PORT=5432 myapp

# From file
docker run --env-file .env myapp

# .env file format:
# DB_HOST=localhost
# DB_PORT=5432
# DB_PASSWORD=secret
```

---

## Docker CLI Cheat Sheet

### System Commands

```bash
# System info
docker info           # Docker system-wide information
docker version        # Docker client and server version

# Disk usage
docker system df      # Show docker disk usage

# Clean up everything
docker system prune      # Remove stopped containers, dangling images, unused networks
docker system prune -a   # Also remove all unused images (not just dangling)
docker system prune --volumes  # Also remove volumes
```

---

## Dockerfile Basics

```dockerfile
# FROM — base image
FROM python:3.11-slim

# WORKDIR — set working directory (created if not exists)
WORKDIR /app

# COPY — copy files from host to image
COPY requirements.txt .
COPY . .

# RUN — execute commands during build (creates layer)
RUN pip install --no-cache-dir -r requirements.txt

# ENV — set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_PORT=8000

# EXPOSE — document which port the app listens on (metadata only!)
EXPOSE 8000

# CMD — default command when container starts
CMD ["python", "app.py"]
```

### Key Dockerfile Instructions

| Instruction | Build-time | Run-time | Description |
|-------------|-----------|----------|-------------|
| `FROM` | ✅ | | Base image |
| `RUN` | ✅ | | Execute command (creates layer) |
| `COPY` | ✅ | | Copy files from host |
| `ADD` | ✅ | | Like COPY + URL download + tar extraction |
| `WORKDIR` | ✅ | | Set working directory |
| `ENV` | ✅ | ✅ | Set environment variable |
| `ARG` | ✅ | | Build-time variable (not in final image) |
| `EXPOSE` | ✅ | | Document exposed port (metadata only) |
| `CMD` | | ✅ | Default command (overridden by `docker run` args) |
| `ENTRYPOINT` | | ✅ | Main executable (CMD becomes arguments) |
| `VOLUME` | | ✅ | Create anonymous volume mount point |
| `USER` | ✅ | ✅ | Set user for subsequent instructions |
| `LABEL` | ✅ | | Add metadata (author, version) |
| `HEALTHCHECK` | | ✅ | Define health check command |

### CMD vs ENTRYPOINT

```dockerfile
# CMD only — easily overridden
CMD ["python", "app.py"]
# docker run myapp              → python app.py
# docker run myapp bash         → bash (CMD overridden)

# ENTRYPOINT only — always runs
ENTRYPOINT ["python"]
# docker run myapp              → python
# docker run myapp app.py       → python app.py (args appended)

# ENTRYPOINT + CMD — best practice
ENTRYPOINT ["python"]
CMD ["app.py"]
# docker run myapp              → python app.py
# docker run myapp test.py      → python test.py (CMD overridden, ENTRYPOINT stays)
```

---

## Build & Run Example

```bash
# Project structure
myapp/
├── app.py
├── requirements.txt
└── Dockerfile

# Build image
docker build -t myapp:1.0 .
#  -t myapp:1.0  : tag (name:version)
#  .             : build context (current directory)

# Build with build args
docker build --build-arg VERSION=2.0 -t myapp:2.0 .

# Run
docker run -d -p 8000:8000 --name myapp myapp:1.0

# Check logs
docker logs -f myapp

# Stop and cleanup
docker stop myapp && docker rm myapp
```

---

## Interview Questions — Fundamentals

### Q1: What is the difference between a Docker image and a container?

| Aspect | Image | Container |
|--------|-------|-----------|
| State | Immutable (read-only) | Mutable (read-write layer) |
| Analogy | Class | Instance of a class |
| Lifecycle | Built once, shared | Created, started, stopped, deleted |
| Storage | Layers on disk | Image layers + writable container layer |

### Q2: What happens when you run `docker run`?

1. Docker checks if image exists locally → if not, `docker pull`
2. Creates a new container (writable layer on top of image)
3. Allocates a network interface and IP address
4. Starts the container process (CMD/ENTRYPOINT)
5. Captures stdout/stderr for `docker logs`

### Q3: What is Copy-on-Write (CoW)?

When a container modifies a file from the image:
1. File is **copied** from the read-only image layer to the container's writable layer
2. Modification happens on the **copy** only
3. Original image layer is **unchanged**

This means multiple containers can share the same image layers efficiently.
