# Docker Security

## Container Isolation Mechanisms

### Linux Namespaces

Namespaces provide **isolated views** of system resources. Each container has its own namespaces.

```
Host System:
  ┌──────────────────────────────────────────────┐
  │  PID namespace (host): PIDs 1, 2, 3, ...    │
  │                                              │
  │  ┌────────────────┐  ┌────────────────┐     │
  │  │  Container A    │  │  Container B    │     │
  │  │  PID ns: 1,2,3  │  │  PID ns: 1,2   │     │
  │  │  NET ns: eth0    │  │  NET ns: eth0   │     │
  │  │  MNT ns: /      │  │  MNT ns: /      │     │
  │  │  UTS ns: hostA   │  │  UTS ns: hostB  │     │
  │  │  IPC ns          │  │  IPC ns          │     │
  │  │  USER ns         │  │  USER ns         │     │
  │  └────────────────┘  └────────────────┘     │
  └──────────────────────────────────────────────┘
```

| Namespace | Isolates | Effect |
|-----------|----------|--------|
| **PID** | Process IDs | Container sees only its own processes (PID 1 = entrypoint) |
| **NET** | Network stack | Own IP, ports, routing table |
| **MNT** | Filesystem mounts | Own root filesystem, mount points |
| **UTS** | Hostname | Own hostname and domain name |
| **IPC** | Inter-process communication | Own shared memory, semaphores |
| **USER** | User/group IDs | Map container UID 0 → host unprivileged UID |
| **Cgroup** | Cgroup membership | Own view of cgroup hierarchy |

---

### Control Groups (cgroups)

Cgroups **limit and account for** resource usage.

```bash
# Memory limit: 512 MB
docker run -m 512m myapp

# CPU limit: 1.5 cores
docker run --cpus 1.5 myapp

# CPU shares (relative weight)
docker run --cpu-shares 512 myapp   # Half of default (1024)

# Block I/O limit
docker run --device-write-bps /dev/sda:10mb myapp

# PID limit (prevent fork bombs)
docker run --pids-limit 100 myapp
```

---

## Root vs Rootless Docker

```
ROOT MODE (default):                 ROOTLESS MODE:
  Docker daemon runs as root         Docker daemon runs as regular user
  Containers run as root by default  Containers run as regular user
  ❌ If container escapes → root     ✅ If container escapes → unprivileged
     on host!                            user on host
```

### Running as Non-Root User

```dockerfile
# ❌ BAD — runs as root inside container
FROM python:3.11-slim
COPY . /app
CMD ["python", "app.py"]

# ✅ GOOD — runs as non-root user
FROM python:3.11-slim
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --chown=appuser:appuser . /app
WORKDIR /app
USER appuser
CMD ["python", "app.py"]

# ✅ ALSO GOOD — use numeric UID (no user creation needed)
FROM python:3.11-slim
COPY . /app
WORKDIR /app
USER 1000:1000
CMD ["python", "app.py"]
```

---

## Security Best Practices

### 1. Image Security

```bash
# Use minimal base images
FROM python:3.11-slim    # Not python:3.11 (includes gcc, make, etc.)
FROM gcr.io/distroless/python3  # Even smaller, no shell

# Pin image versions (never use :latest in production)
FROM python:3.11.8-slim-bookworm  # Exact version + OS

# Scan for vulnerabilities
docker scout quickview myapp:latest
docker scout cves myapp:latest

# Or use tools like:
# - Trivy: trivy image myapp:latest
# - Snyk: snyk container test myapp:latest
# - Grype: grype myapp:latest
```

### 2. Build Security

```dockerfile
# Don't store secrets in image layers!
# ❌ BAD
ENV API_KEY=supersecret123
RUN curl -H "Authorization: $API_KEY" https://api.example.com/package.tar.gz

# ✅ GOOD — use BuildKit secrets
RUN --mount=type=secret,id=api_key \
    curl -H "Authorization: $(cat /run/secrets/api_key)" https://api.example.com/package.tar.gz
```

### 3. Runtime Security

```bash
# Read-only filesystem
docker run --read-only myapp
docker run --read-only --tmpfs /tmp myapp  # Allow writes to /tmp only

# Drop all capabilities, add only what's needed
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp

# No new privileges
docker run --security-opt no-new-privileges myapp

# Prevent container from gaining additional access
docker run --security-opt no-new-privileges --cap-drop ALL --read-only myapp
```

### 4. Linux Capabilities

```
Root has ALL capabilities. Containers get a SUBSET by default.

Default capabilities:
  CHOWN, DAC_OVERRIDE, FSETID, FOWNER, MKNOD, NET_RAW,
  SETGID, SETUID, SETFCAP, SETPCAP, NET_BIND_SERVICE,
  SYS_CHROOT, KILL, AUDIT_WRITE

Dangerous capabilities (NOT default):
  SYS_ADMIN    → almost root (mount, cgroups, etc.)
  NET_ADMIN    → configure network
  SYS_PTRACE   → debug other processes
```

```bash
# Drop ALL capabilities, add only needed
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp

# Check container capabilities
docker exec myapp cat /proc/1/status | grep Cap
```

### 5. Seccomp and AppArmor

```bash
# Seccomp — restricts system calls
# Docker applies a default seccomp profile (blocks ~40 syscalls)
docker run --security-opt seccomp=default.json myapp
docker run --security-opt seccomp=unconfined myapp  # ⚠️ Disable (don't!)

# AppArmor — mandatory access control
docker run --security-opt apparmor=docker-default myapp
```

---

## Docker Secrets (Swarm Mode)

```bash
# Create a secret
echo "my-db-password" | docker secret create db_password -

# Use in a Swarm service
docker service create \
  --name myapp \
  --secret db_password \
  myapp:latest

# In container: secret available at /run/secrets/db_password
cat /run/secrets/db_password  # → my-db-password
```

```yaml
# docker-compose.yml (Swarm mode)
services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    external: true      # Created beforehand
  api_key:
    file: ./api_key.txt # From file
```

---

## Docker Content Trust (Image Signing)

```bash
# Enable content trust
export DOCKER_CONTENT_TRUST=1

# Now docker pull/push will verify/sign images
docker pull nginx:latest  # Verifies signature
docker push myapp:v1.0    # Signs the image

# Without valid signature → pull fails
```

---

## Security Checklist

```
Image:
  ☐ Use minimal base images (slim, distroless, alpine)
  ☐ Pin image versions (never :latest in production)
  ☐ Scan for CVEs regularly (Trivy, Snyk, Docker Scout)
  ☐ Don't store secrets in layers (use BuildKit secrets)
  ☐ Use multi-stage builds (separate build/runtime)

Runtime:
  ☐ Run as non-root user (USER instruction)
  ☐ Drop ALL capabilities, add only needed
  ☐ Use read-only filesystem where possible
  ☐ Set resource limits (memory, CPU, PIDs)
  ☐ Enable no-new-privileges
  ☐ Use default seccomp/AppArmor profiles

Network:
  ☐ Don't expose unnecessary ports
  ☐ Use user-defined networks (not default bridge)
  ☐ Use TLS/mTLS between services

Supply Chain:
  ☐ Use signed images (Docker Content Trust)
  ☐ Use private registries for internal images
  ☐ Regularly update base images
```

---

## Interview Questions — Security

### Q1: How does Docker isolate containers?

Using Linux kernel features:
- **Namespaces:** Isolate PID, network, filesystem, hostname, IPC, users — each container gets its own view
- **Cgroups:** Limit CPU, memory, I/O, PIDs — prevent resource hogging
- **seccomp:** Block dangerous system calls
- **AppArmor/SELinux:** Mandatory access control

### Q2: Why should containers run as non-root?

If a container running as root has a vulnerability or escape, the attacker gets **root access on the host**. Running as non-root (unprivileged user) limits the blast radius — even if they escape the container, they're an unprivileged user on the host.

### Q3: What are Linux capabilities?

Instead of all-or-nothing root, Linux splits root privileges into ~40 **capabilities** (e.g., `NET_BIND_SERVICE` to bind ports < 1024). Containers get a subset by default. Best practice: drop ALL, add only what's needed.
