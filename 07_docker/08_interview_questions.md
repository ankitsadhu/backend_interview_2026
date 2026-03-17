# Docker Interview Questions

> Comprehensive question bank covering beginner to advanced topics, rapid-fire Q&A, and troubleshooting scenarios.

---

## 🟢 Beginner Level

### Q1: What is Docker and why use it?

Docker is a platform for packaging, distributing, and running applications in **containers** — lightweight, isolated environments that include everything needed to run the app (code, libraries, system tools).

**Why use it:**
- **Consistency:** "Works on my machine" → works everywhere
- **Isolation:** Each app has its own dependencies (no conflicts)
- **Portability:** Run on any machine with Docker installed
- **Efficiency:** Containers share the host kernel (faster than VMs)
- **Reproducibility:** Dockerfile = code for your environment

---

### Q2: What is the difference between a container and a VM?

| Aspect | Container | VM |
|--------|-----------|-----|
| Isolation | Process-level (namespaces + cgroups) | Hardware-level (hypervisor) |
| OS | Shares host kernel | Full guest OS per VM |
| Size | MBs | GBs |
| Startup | Seconds | Minutes |
| Performance | Near-native | Near-native (with HW virtualization) |
| Density | 100+ per host | ~10 per host |

---

### Q3: What is a Dockerfile?

A text file with instructions for building a Docker image. Each instruction creates a **layer** in the final image.

```dockerfile
FROM python:3.11-slim      # Base image
WORKDIR /app               # Working directory
COPY requirements.txt .    # Copy dependency file
RUN pip install -r requirements.txt  # Install deps (build-time)
COPY . .                   # Copy application code
EXPOSE 8000                # Document port (metadata)
CMD ["python", "app.py"]   # Default runtime command
```

---

### Q4: What are the different Docker network types?

| Network | Description | Use Case |
|---------|-------------|----------|
| **bridge** | Default. Private network on host. | Container-to-container (same host) |
| **host** | Share host's network (no isolation) | Maximum performance |
| **overlay** | Multi-host networking | Swarm/K8s clusters |
| **none** | No networking | Fully isolated containers |

---

### Q5: How do you persist data in Docker?

Three options:
1. **Volumes** — Docker-managed storage (`-v mydata:/data`). Best for production.
2. **Bind mounts** — Map host directory (`-v ./src:/app`). Best for development.
3. **tmpfs** — Store in RAM only. Best for sensitive temp data.

---

## 🟡 Intermediate Level

### Q6: What is multi-stage build and why use it?

A Dockerfile with multiple `FROM` statements. One stage for building, another for the final image.

```dockerfile
FROM node:18 AS builder
RUN npm ci && npm run build

FROM node:18-alpine
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/index.js"]
```

**Why:** Build image might be 800 MB (compiler, SDK). Final image is 50 MB (only runtime + binary). Smaller = faster deploys + less attack surface.

---

### Q7: How does Docker layer caching work?

- Each Dockerfile instruction creates a layer
- Docker caches layers by their content hash
- If instruction + inputs unchanged → reuse cached layer
- If **any** instruction changes → rebuild it AND all subsequent layers

**Optimization:** Put stable instructions (deps) before volatile ones (code): `COPY requirements.txt` → `RUN pip install` → `COPY . .`

---

### Q8: What is the difference between CMD and ENTRYPOINT?

| Feature | CMD | ENTRYPOINT |
|---------|-----|-----------|
| Purpose | Default command + arguments | Main executable |
| Override | Fully replaced by `docker run` args | Not replaced (args appended) |
| Best use | Default args that users might override | Fixed executable, variable args |

```dockerfile
ENTRYPOINT ["python"]      # Always runs python
CMD ["app.py"]             # Default arg (overridable)
# docker run myapp         → python app.py
# docker run myapp test.py → python test.py
```

---

### Q9: How do you handle secrets in Docker?

| Method | Security | Use Case |
|--------|----------|----------|
| Environment variables | ⚠️ Visible in `docker inspect` | Dev/staging |
| Docker secrets (Swarm) | ✅ Encrypted, mounted as files | Swarm production |
| BuildKit `--secret` | ✅ Never in image layers | Build-time secrets |
| External (Vault, AWS SM) | ✅ Best | Enterprise production |
| `.env` file | ⚠️ Don't commit to git | Local development |

---

### Q10: How does `depends_on` work in Docker Compose?

`depends_on` controls **startup order**, not readiness. Options:

```yaml
depends_on:
  db:
    condition: service_started               # Default — just started
    condition: service_healthy               # Wait for health check
    condition: service_completed_successfully # Wait for exit code 0
```

Without `service_healthy`, the app may start before the database is ready to accept connections.

---

### Q11: What is the Docker build context?

The set of files sent to the Docker daemon when you run `docker build .` The `.` is the context directory. All files in it are sent (can be slow for large directories).

**Optimization:** Use `.dockerignore` to exclude unnecessary files (`.git`, `node_modules`, `__pycache__`).

---

### Q12: What is the difference between `docker stop` and `docker kill`?

- `docker stop`: Sends **SIGTERM** (graceful). Waits 10 seconds. Then SIGKILL.
- `docker kill`: Sends **SIGKILL** immediately (no graceful shutdown).

Always prefer `docker stop` → allows app to close connections, flush buffers.

---

## 🔴 Advanced Level

### Q13: How do Linux namespaces provide container isolation?

Docker uses 7 Linux namespaces:
- **PID:** Isolated process tree (container's PID 1 ≠ host's PID 1)
- **NET:** Own IP, ports, routing table
- **MNT:** Own filesystem view and mount points
- **UTS:** Own hostname
- **IPC:** Own shared memory and semaphores
- **USER:** Map container root to unprivileged host user
- **Cgroup:** Own view of resource limits

Together they create the **illusion** of a separate machine.

---

### Q14: What are cgroups and how does Docker use them?

**Control Groups (cgroups)** limit and account for resource usage:
- **Memory:** `--memory 512m` (OOM killed if exceeded)
- **CPU:** `--cpus 2` (limit to 2 cores)
- **PIDs:** `--pids-limit 100` (prevent fork bombs)
- **Block I/O:** `--device-write-bps` (limit disk write speed)

Without cgroups, a container could consume all host resources → crash other containers.

---

### Q15: What is Copy-on-Write and how does the overlay filesystem work?

```
Image Layers (read-only):       Container Layer (read-write):
  Layer 3 ─┐                      ┌──────────────────┐
  Layer 2 ─┤ Merged view (union)  │ Modified files    │
  Layer 1 ─┘                      │ New files         │
                                  │ Deleted (whiteout)│
                                  └──────────────────┘

When container reads a file: Walk layers top-down, use first found
When container modifies a file: Copy from image layer → container layer → modify
When container deletes: Create "whiteout" marker in container layer
```

**overlay2** is Docker's default storage driver. It efficiently merges layers using Linux overlay filesystem.

---

### Q16: How would you debug a container that keeps crashing?

```bash
# 1. Check logs
docker logs myapp --tail 100

# 2. Check exit code
docker inspect myapp --format='{{.State.ExitCode}}'
# Exit 0: normal, 1: app error, 137: OOM killed (SIGKILL), 143: SIGTERM

# 3. Check OOM (Out of Memory)
docker inspect myapp --format='{{.State.OOMKilled}}'

# 4. Run interactively (override CMD)
docker run -it --entrypoint sh myapp:latest

# 5. Check resource usage
docker stats myapp

# 6. Inspect events
docker events --filter container=myapp

# 7. Start with minimal command
docker run --rm -it myapp:latest /bin/sh -c "ls -la /app && cat /app/config"
```

---

### Q17: How does Docker networking work under the hood?

```
1. Bridge network uses Linux bridge (virtual switch)
2. Each container gets a veth pair (virtual ethernet):
   - One end in container namespace (eth0)
   - Other end attached to docker0 bridge
3. iptables rules handle:
   - NAT for outbound traffic (container → internet)
   - Port forwarding for published ports (host:port → container:port)
4. DNS resolution via embedded DNS server (127.0.0.11)
```

---

### Q18: What is the difference between `ADD` vs `COPY`?

Both copy files into the image, but `ADD` has extra features:
- `ADD` can download from URLs (not recommended — use `curl` in `RUN`)
- `ADD` auto-extracts `.tar` files

**Best practice:** Always use `COPY` unless you specifically need tar extraction.

---

## ⚡ Rapid-Fire Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Default Docker network driver? | `bridge` |
| 2 | Where are Docker volumes stored? | `/var/lib/docker/volumes/` (Linux) |
| 3 | What is PID 1 in a container? | The entrypoint process (must handle SIGTERM) |
| 4 | `EXPOSE` publishes a port? | No, it's documentation only. Use `-p` to publish. |
| 5 | Default Docker storage driver? | `overlay2` |
| 6 | What format are Docker images? | OCI (Open Container Initiative) image specification |
| 7 | Docker image vs container? | Image = blueprint (class). Container = running instance (object). |
| 8 | What does `docker system prune` do? | Removes stopped containers, unused networks, dangling images |
| 9 | Max memory exceeded → what happens? | Container is OOM killed (exit code 137) |
| 10 | `docker run --rm` does what? | Auto-removes container when it exits |
| 11 | What is a dangling image? | An image not tagged and not referenced by any container |
| 12 | `docker exec` vs `docker attach`? | `exec`: new process in container. `attach`: attach to PID 1's stdin/stdout. |
| 13 | Can you `docker commit` in production? | Technically yes, but **never** do — use Dockerfiles for reproducibility |
| 14 | What is BuildKit? | Modern build engine with parallel builds, cache mounts, secrets |
| 15 | What is a distroless image? | Google images with no OS tools, shell, or package manager — just the app |
| 16 | How to pass build-time variables? | `ARG` in Dockerfile + `--build-arg` in build command |
| 17 | Swarm vs Compose? | Compose = dev multi-container. Swarm = production orchestration. |
| 18 | What is `docker scout`? | Docker's built-in vulnerability scanning tool |
| 19 | How to make filesystem read-only? | `docker run --read-only myapp` |
| 20 | Container gets own IP? | Yes, from the Docker network subnet (e.g., 172.17.0.x) |

---

## 🔧 Troubleshooting Scenarios

### Scenario 1: Container starts but immediately exits

```bash
# Check exit code
docker inspect myapp --format='{{.State.ExitCode}}'

# Check logs
docker logs myapp

Common causes:
  - Exit 0: CMD/ENTRYPOINT completed (e.g., ran a script, not a server)
  - Exit 1: Application error (check logs)
  - Exit 127: Command not found (wrong ENTRYPOINT/CMD)
  - Exit 137: OOM killed (increase memory limit)
  - Exit 143: SIGTERM received (another process stopped it)

Fix for "exits immediately":
  - Ensure CMD runs a long-lived process (server, not script)
  - Check if running in shell form (sh -c wraps and may exit)
```

### Scenario 2: Cannot connect to containerized service

```bash
# Is the container running?
docker ps

# Is the port published correctly?
docker port myapp
# Expected: 0.0.0.0:8080->80/tcp

# Is the app listening on 0.0.0.0 (not 127.0.0.1)?
docker exec myapp netstat -tlnp
# App must listen on 0.0.0.0 inside container
# Listening on 127.0.0.1 = only reachable from inside container

# Check firewall
# Windows/Mac: Docker Desktop handles port forwarding
# Linux: Check iptables rules
```

### Scenario 3: Docker image keeps getting larger

```bash
# Analyze image layers
docker history myapp:latest

# Find large layers
docker history --no-trunc myapp:latest | sort -k7 -h

Solutions:
  1. Multi-stage build (separate build and runtime)
  2. Combine RUN commands (cleanup in same layer)
  3. Use .dockerignore (exclude unnecessary files)
  4. Use slim/alpine base images
  5. Remove cache (pip --no-cache-dir, npm cache clean)
  6. Use dive tool: dive myapp:latest (interactive layer explorer)
```
