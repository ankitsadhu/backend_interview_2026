# Docker Study Guide

> Comprehensive Docker learning path from beginner to advanced, organized for interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | What is Docker, containers vs VMs, architecture, images, containers, Docker CLI, Dockerfile | 🟢 Beginner |
| 02 | [Images & Dockerfile](./02_images_and_dockerfile.md) | Build process, layers, caching, multi-stage builds, best practices, image optimization, registries | 🟢🟡 Beginner-Intermediate |
| 03 | [Networking](./03_networking.md) | Bridge, host, overlay, macvlan networks, DNS, port mapping, container communication | 🟡 Intermediate |
| 04 | [Storage & Volumes](./04_storage_and_volumes.md) | Volumes, bind mounts, tmpfs, storage drivers, backup/restore, stateful containers | 🟡 Intermediate |
| 05 | [Docker Compose](./05_docker_compose.md) | Multi-container apps, services, networks, volumes, environment, depends_on, profiles, overrides | 🟡 Intermediate |
| 06 | [Security](./06_security.md) | Root vs rootless, namespaces, cgroups, seccomp, AppArmor, image scanning, secrets, read-only FS | 🟡🔴 Intermediate-Advanced |
| 07 | [Orchestration & Production](./07_orchestration_and_production.md) | Docker Swarm, Kubernetes intro, health checks, logging, monitoring, CI/CD, production best practices | 🔴 Advanced |
| 08 | [Interview Questions](./08_interview_questions.md) | 25+ categorized questions (beginner → advanced) + rapid-fire Q&A + troubleshooting scenarios | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_fundamentals.md` — understand containers and the Docker architecture
2. Practice building images and running containers
3. Read `02_images_and_dockerfile.md` — master multi-stage builds

### Week 2: Networking, Storage & Compose
4. Read `03_networking.md` — understand bridge vs overlay networks
5. Read `04_storage_and_volumes.md` — volumes and persistent data
6. Read `05_docker_compose.md` — multi-container applications

### Week 3: Security & Production
7. Read `06_security.md` — namespaces, cgroups, scanning
8. Read `07_orchestration_and_production.md` — Swarm, K8s, CI/CD

### Final Review
9. Go through `08_interview_questions.md` — test yourself across all levels
