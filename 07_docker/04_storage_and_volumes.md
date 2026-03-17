# Storage & Volumes

## The Storage Problem

Containers are **ephemeral** — when a container is deleted, its writable layer is gone.

```
Container running:                    Container deleted:
┌──────────────────┐                 ┌──────────────────┐
│ Container Layer   │ ← data here    │                  │
│ (R/W)  📝         │                │   ❌ DATA LOST    │
├──────────────────┤                │                  │
│ Image Layers (R/O)│                │                  │
└──────────────────┘                └──────────────────┘
```

**Solution:** Use volumes or bind mounts to persist data outside the container.

---

## Three Types of Mounts

```
┌──────────────────────────────────────────────────────┐
│                    Container                          │
│                                                      │
│  /app/data ← mount point                             │
│                                                      │
└────────┬──────────────┬──────────────┬──────────────┘
         │              │              │
    ┌────┴────┐   ┌─────┴─────┐  ┌────┴────┐
    │  Volume  │   │Bind Mount │  │  tmpfs   │
    │          │   │           │  │          │
    │ Docker-  │   │ Host path │  │ RAM only │
    │ managed  │   │ mapped    │  │ (no disk)│
    │ storage  │   │ directly  │  │          │
    └─────────┘   └───────────┘  └─────────┘
```

| Type | Storage | Managed By | Portability | Use Case |
|------|---------|------------|-------------|----------|
| **Volume** | Docker area (`/var/lib/docker/volumes/`) | Docker | ✅ Cross-platform | Database data, shared data |
| **Bind Mount** | Any host path | User | ❌ Host-specific | Dev: live code reload |
| **tmpfs** | RAM (memory) | OS | ❌ Ephemeral | Sensitive data, temp files |

---

## Volumes

```bash
# Create named volume
docker volume create mydata

# List volumes
docker volume ls

# Inspect volume
docker volume inspect mydata

# Use volume in container
docker run -v mydata:/app/data myapp
docker run --mount source=mydata,target=/app/data myapp

# Anonymous volume (Docker generates name)
docker run -v /app/data myapp

# Read-only volume
docker run -v mydata:/app/data:ro myapp

# Remove volume
docker volume rm mydata

# Remove all unused volumes
docker volume prune
```

### Volume in Dockerfile

```dockerfile
# Declare a volume mount point
VOLUME /app/data

# This creates an anonymous volume at /app/data
# Data written here persists even if container is removed
# (if using named volumes externally)
```

---

## Bind Mounts

Map a **host directory** directly into the container.

```bash
# Bind mount current directory
docker run -v $(pwd):/app myapp
docker run --mount type=bind,source=$(pwd),target=/app myapp

# Read-only bind mount
docker run -v $(pwd)/config:/app/config:ro myapp

# Common dev setup — live reload
docker run -v $(pwd):/app -p 3000:3000 node:18 npm run dev
# Changes on host instantly visible in container!
```

### Volume vs Bind Mount

| Aspect | Volume | Bind Mount |
|--------|--------|-----------|
| Location | Docker-managed (`/var/lib/docker/volumes/`) | Any host path |
| Backup | `docker volume` commands | Standard file tools |
| Portability | Works on any Docker host | Depends on host path |
| Pre-populated | ✅ Container data populates empty volume | ❌ Host directory overlays container |
| Performance | Best on Linux, good with drivers | Native file system speed |
| Security | Isolated from host | Full access to host path |
| Best for | Production, databases | Development, config files |

---

## tmpfs Mounts

Stored in **RAM only** — never written to disk. Removed when container stops.

```bash
docker run --tmpfs /app/temp myapp
docker run --mount type=tmpfs,target=/app/temp,tmpfs-size=100m myapp
```

**Use cases:**
- Sensitive data (passwords, tokens) — no disk trace
- Temporary scratch space
- High-speed I/O for intermediate processing

---

## Sharing Data Between Containers

```bash
# Multiple containers share the same volume
docker volume create shared_data

docker run -d --name writer -v shared_data:/data mywriter
docker run -d --name reader -v shared_data:/data:ro myreader
# writer writes to /data, reader can read it
```

---

## Backup and Restore Volumes

```bash
# Backup a volume to a tar file
docker run --rm \
  -v mydata:/source:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/mydata-backup.tar.gz -C /source .

# Restore from backup
docker run --rm \
  -v mydata:/target \
  -v $(pwd):/backup \
  alpine sh -c "tar xzf /backup/mydata-backup.tar.gz -C /target"
```

---

## Interview Questions — Storage

### Q1: What happens to data when a container is removed?

Data in the **container's writable layer** is lost. Data in **volumes** persists (volumes exist independently of containers). Data in **bind mounts** persists on the host filesystem.

### Q2: When would you use a volume vs a bind mount?

- **Volume:** Production databases, shared data between containers, when you don't need host-path access
- **Bind mount:** Development (live code reload), injecting config files, when you need to access files from the host

### Q3: How do you handle database storage in Docker?

1. Use a **named volume** for data directory (`-v pgdata:/var/lib/postgresql/data`)
2. Never store database data in the container layer
3. Regular volume backups
4. Consider **volume drivers** for cloud-backed storage (EBS, GCE PD)
