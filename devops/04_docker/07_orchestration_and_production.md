# Orchestration & Production

## Docker Swarm

Docker's built-in **container orchestration**. Simpler than Kubernetes but less feature-rich.

```
┌──────────────────────────────────────────────────────┐
│                    Swarm Cluster                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Manager Node  │  │ Manager Node  │  (Raft consensus│
│  │ (Leader)      │  │ (Follower)    │   for HA)       │
│  └──────────────┘  └──────────────┘                 │
│        │                  │                          │
│  ┌─────┴──────────────────┴──────┐                  │
│  │        Worker Nodes            │                  │
│  │  ┌────────┐  ┌────────┐       │                  │
│  │  │ Task 1 │  │ Task 1 │       │ ← Service "web"  │
│  │  │(web.1) │  │(web.2) │       │   (2 replicas)    │
│  │  └────────┘  └────────┘       │                  │
│  │  ┌────────┐                   │                  │
│  │  │ Task 1 │                   │ ← Service "api"  │
│  │  │(api.1) │                   │   (1 replica)     │
│  │  └────────┘                   │                  │
│  └───────────────────────────────┘                  │
└──────────────────────────────────────────────────────┘
```

```bash
# Initialize Swarm
docker swarm init

# Join worker node
docker swarm join --token <worker-token> <manager-ip>:2377

# Create a service
docker service create --name web --replicas 3 -p 80:80 nginx

# Scale service
docker service scale web=5

# Update service (rolling update)
docker service update --image nginx:1.25 web

# List services and tasks
docker service ls
docker service ps web

# Remove service
docker service rm web
```

---

## Docker Swarm vs Kubernetes

| Feature | Docker Swarm | Kubernetes |
|---------|-------------|-----------|
| **Complexity** | Simple (built into Docker) | Complex (steep learning curve) |
| **Setup** | `docker swarm init` | Install cluster (kubeadm, EKS, GKE) |
| **Scaling** | `docker service scale` | HPA (auto-scaling) |
| **Networking** | Overlay (built-in) | CNI plugins (Calico, Cilium, Flannel) |
| **Service mesh** | None built-in | Istio, Linkerd |
| **Config/Secrets** | Docker configs/secrets | ConfigMaps, Secrets (+ external tools) |
| **Load balancing** | Built-in (routing mesh) | Ingress controllers |
| **Community** | Smaller | Very large, industry standard |
| **Use case** | Small-medium deployments | Production at any scale |

---

## Kubernetes Basics (Docker's Next Step)

```
┌──────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                    │
│                                                      │
│  Control Plane:                                      │
│    API Server, Scheduler, Controller Manager, etcd   │
│                                                      │
│  Worker Nodes:                                       │
│  ┌────────────────────────────────────────────┐     │
│  │  Node 1                                    │     │
│  │  ┌──────────┐  ┌──────────┐              │     │
│  │  │  Pod      │  │  Pod      │              │     │
│  │  │ ┌──────┐ │  │ ┌──────┐ │              │     │
│  │  │ │ app  │ │  │ │ api  │ │              │     │
│  │  │ │ :8000│ │  │ │ :3000│ │              │     │
│  │  │ └──────┘ │  │ └──────┘ │              │     │
│  │  └──────────┘  └──────────┘              │     │
│  │  kubelet + kube-proxy + container runtime │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
```

### Key Kubernetes Concepts

| Concept | Docker Equivalent | Description |
|---------|------------------|-------------|
| **Pod** | Container (roughly) | Smallest deployable unit (1+ containers) |
| **Deployment** | Service (swarm) | Manages pod replicas, rolling updates |
| **Service** | Port mapping + DNS | Stable network endpoint for pods |
| **ConfigMap** | `docker config` | Configuration data |
| **Secret** | `docker secret` | Sensitive data (base64 encoded) |
| **Namespace** | N/A | Logical cluster partitioning |
| **Ingress** | Port publishing | HTTP routing from outside cluster |
| **PersistentVolume** | Volume | Persistent storage |

---

## Health Checks

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
  CMD curl -f http://localhost:8000/health || exit 1

# Health check states:
#   starting  → within start-period, health check ignored
#   healthy   → health check passing
#   unhealthy → health check failing (after retries)
```

```yaml
# In docker-compose.yml
services:
  app:
    image: myapp:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

### Health Check Endpoints

```python
# Python (FastAPI) health check endpoint
from fastapi import FastAPI
import asyncpg

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/health/ready")
async def ready():
    """Readiness check — verify all dependencies"""
    try:
        # Check database
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        
        # Check Redis
        await redis_client.ping()
        
        return {"status": "ready", "checks": {"db": "ok", "redis": "ok"}}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "not ready", "error": str(e)})
```

---

## Logging

```bash
# Docker logging drivers
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 myapp

# Available drivers:
#   json-file (default) — logs stored as JSON files
#   syslog              — sends to syslog
#   fluentd             — sends to Fluentd
#   awslogs             — sends to CloudWatch
#   gcplogs             — sends to Google Cloud Logging
#   none                — discard logs
```

```yaml
# docker-compose.yml
services:
  app:
    image: myapp
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        tag: "{{.Name}}/{{.ID}}"
```

### Best Practices

```
1. Log to stdout/stderr (not files inside container)
   → Docker captures stdout/stderr
   → Log driver handles routing

2. Use structured logging (JSON)
   → Easy to parse and search

3. Set log rotation (max-size, max-file)
   → Prevent disk full

4. Centralize logs (ELK, Loki, CloudWatch)
   → Enable search, alerts
```

---

## CI/CD with Docker

```yaml
# GitHub Actions — build and push Docker image
name: Docker CI/CD

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            myuser/myapp:latest
            myuser/myapp:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myuser/myapp:${{ github.sha }}
          severity: 'HIGH,CRITICAL'
```

---

## Production Best Practices

### Container Configuration

```yaml
# Production docker-compose.yml patterns
services:
  app:
    image: registry.com/myapp:v1.2.3      # Pinned version
    restart: unless-stopped                # Auto-restart
    read_only: true                        # Read-only filesystem
    tmpfs:
      - /tmp                               # Writable temp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### Production Checklist

```
Image:
  ☐ Use specific version tags (not :latest)
  ☐ Multi-stage build (minimal final image)
  ☐ Non-root user
  ☐ Scanned for vulnerabilities
  ☐ .dockerignore configured

Runtime:
  ☐ Resource limits (memory, CPU, PIDs)
  ☐ Health checks configured
  ☐ Restart policy set
  ☐ Read-only filesystem (if possible)
  ☐ Capabilities dropped
  ☐ Log rotation configured

Data:
  ☐ Named volumes for persistent data
  ☐ Volume backup strategy
  ☐ Secrets managed properly (not in env vars)

Networking:
  ☐ Only necessary ports exposed
  ☐ TLS for external communication
  ☐ User-defined networks

Operations:
  ☐ CI/CD pipeline for building/pushing images
  ☐ Monitoring (Prometheus, Datadog)
  ☐ Centralized logging
  ☐ Graceful shutdown handling (SIGTERM)
```

### Graceful Shutdown

```python
# Python — handle SIGTERM for graceful shutdown
import signal
import sys

def handle_sigterm(signum, frame):
    print("Received SIGTERM, shutting down gracefully...")
    # Close database connections
    # Finish current requests
    # Flush buffers
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
```

```dockerfile
# Important: Use exec form so PID 1 receives signals
# ✅ GOOD — exec form (receives SIGTERM)
CMD ["python", "app.py"]
ENTRYPOINT ["python", "app.py"]

# ❌ BAD — shell form (shell is PID 1, app doesn't get SIGTERM)
CMD python app.py
```

---

## Interview Questions — Orchestration & Production

### Q1: Docker Swarm vs Kubernetes — when to use each?

- **Swarm:** Small teams, simple deployments, already using Docker, don't need advanced features
- **Kubernetes:** Production at scale, need auto-scaling, service mesh, advanced networking, large team, industry standard

### Q2: How do you handle rolling updates with zero downtime?

1. **Health checks** → new containers must pass health check before receiving traffic
2. **Rolling update policy** → replace containers one at a time (or in batches)
3. **Graceful shutdown** → handle SIGTERM, finish in-flight requests
4. **Readiness check** → don't send traffic until container is fully ready
5. **Connection draining** → stop sending new requests before stopping old container

### Q3: Why should containers write logs to stdout instead of files?

1. Docker captures stdout/stderr automatically
2. Log driver handles routing (CloudWatch, ELK, etc.)
3. No need to manage log files inside container
4. Works with `docker logs` command
5. Container filesystem is ephemeral — files are lost on restart
