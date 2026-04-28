# Docker Networking

## Network Drivers

```
┌────────────────────────────────────────────────────────────────┐
│                     Docker Networking                           │
│                                                                │
│  bridge (default)  │  host   │  overlay  │  none   │  macvlan │
│  Container-to-     │  Share  │  Multi-   │  No     │  Physical│
│  container on      │  host   │  host     │  network│  MAC addr│
│  same host         │  network│  (Swarm)  │         │  per     │
│                    │         │           │         │  container│
└────────────────────────────────────────────────────────────────┘
```

| Driver | Scope | Use Case |
|--------|-------|----------|
| **bridge** | Single host | Default. Containers on same host communicate |
| **host** | Single host | Container uses host's network directly (no isolation) |
| **overlay** | Multi-host | Swarm/K8s — containers across different hosts |
| **macvlan** | Single host | Container gets its own MAC address on physical network |
| **none** | Single host | No networking (fully isolated) |

---

## Bridge Network (Default)

```
┌────────────────────────────────────────────────────┐
│                      Host                           │
│                                                    │
│  ┌────────────┐  ┌────────────┐                   │
│  │ Container A│  │ Container B│                   │
│  │ 172.17.0.2 │  │ 172.17.0.3 │                   │
│  └─────┬──────┘  └─────┬──────┘                   │
│        │               │                           │
│  ┌─────┴───────────────┴──────┐                   │
│  │      docker0 (bridge)       │ 172.17.0.1        │
│  └─────────────┬──────────────┘                   │
│                │ NAT                               │
│  ┌─────────────┴──────────────┐                   │
│  │      Host Network (eth0)    │                   │
│  └────────────────────────────┘                   │
└────────────────────────────────────────────────────┘
```

### Default vs User-Defined Bridge

```bash
# Default bridge — containers communicate by IP only
docker run -d --name app1 nginx
docker run -d --name app2 nginx
# app1 can reach app2 by IP (172.17.0.3) but NOT by name

# User-defined bridge — DNS resolution by container name
docker network create mynet
docker run -d --name app1 --network mynet nginx
docker run -d --name app2 --network mynet nginx
# app1 can reach app2 by name: curl http://app2:80 ✅
```

| Feature | Default Bridge | User-Defined Bridge |
|---------|---------------|-------------------|
| DNS resolution | ❌ (IP only) | ✅ (container name) |
| Isolation | All containers on same bridge | Choose which containers join |
| Port mapping | Needed for host access | Needed for host access |
| Connect/disconnect live | ❌ | ✅ |

---

## Port Mapping

```bash
# Map host port to container port
docker run -p 8080:80 nginx
#  Host:8080 → Container:80

# Map specific host IP
docker run -p 127.0.0.1:8080:80 nginx

# Random host port
docker run -p 80 nginx   # Docker assigns random host port
docker port <container>  # See the mapped port

# Map multiple ports
docker run -p 8080:80 -p 8443:443 nginx

# Map UDP port
docker run -p 53:53/udp dns-server
```

---

## Network Commands

```bash
# List networks
docker network ls

# Create network
docker network create mynet
docker network create --driver overlay --attachable myoverlay  # Swarm

# Inspect network
docker network inspect mynet

# Connect/disconnect running container
docker network connect mynet container1
docker network disconnect mynet container1

# Remove network
docker network rm mynet
docker network prune  # Remove all unused networks
```

---

## Container DNS

```
User-defined networks provide automatic DNS:

┌──────────┐     DNS query: "db"     ┌──────────┐
│   app    │ ──────────────────────→ │ Docker   │
│          │ ←── 172.18.0.3 ──────── │ DNS      │
│          │                         │ (127.0.0.11) │
└──────────┘                         └──────────┘
                                          │
                                     ┌────┴─────┐
                                     │   db      │
                                     │ 172.18.0.3│
                                     └──────────┘

# Network aliases (multiple names for same container)
docker run --network mynet --network-alias database --name postgres-primary postgres
# Both "database" and "postgres-primary" resolve to this container
```

---

## Interview Questions — Networking

### Q1: How do containers on the same host communicate?

Via the **bridge network**. On a user-defined bridge, containers can reach each other by name (Docker DNS). On the default bridge, only by IP address.

### Q2: What's the difference between `-p 8080:80` and `EXPOSE 80`?

- `EXPOSE 80` → **documentation** only (metadata in image). Does NOT publish the port.
- `-p 8080:80` → **actually publishes** the port (creates iptables rules for traffic forwarding).

### Q3: When would you use host networking?

When you need **maximum network performance** (no NAT overhead) or the container needs to bind to the host's actual network interfaces. Trade-off: no network isolation between container and host.
