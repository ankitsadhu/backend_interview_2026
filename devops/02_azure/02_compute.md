# Azure Compute Services

## Compute Service Decision Tree

```
Need to run code on Azure?
    │
    ├── Need full OS control? ──→ Virtual Machines (IaaS)
    │
    ├── Web app / API? ──→ App Service (PaaS)
    │
    ├── Containers?
    │   ├── Simple, single container? ──→ Container Instances (ACI)
    │   ├── Orchestration needed? ──→ Azure Kubernetes Service (AKS)
    │   └── Managed containers, no K8s? ──→ Container Apps
    │
    ├── Event-driven / short tasks? ──→ Azure Functions (FaaS)
    │
    └── Batch processing? ──→ Azure Batch
```

---

## 1. Virtual Machines (VMs)

Full IaaS — you manage OS, patches, runtime, and application.

### VM Sizes (Series)

| Series | Use Case | Example |
|--------|----------|---------|
| **B-series** | Burstable, dev/test, light workloads | B2s (2 vCPU, 4 GB) |
| **D-series** | General purpose, balanced CPU/memory | D4s_v5 (4 vCPU, 16 GB) |
| **E-series** | Memory-optimized (databases, caching) | E8s_v5 (8 vCPU, 64 GB) |
| **F-series** | Compute-optimized (batch, gaming) | F4s_v2 (4 vCPU, 8 GB) |
| **N-series** | GPU-enabled (ML, rendering) | NC6s_v3 (6 vCPU, 112 GB, V100) |
| **L-series** | Storage-optimized (big data, data warehousing) | L8s_v3 |
| **M-series** | Memory ultra (SAP HANA, large in-memory DBs) | M128s (128 vCPU, 2 TB) |

### VM Creation

```bash
# Create a VM
az vm create \
  --resource-group myapp-rg \
  --name myvm \
  --image Ubuntu2204 \
  --size Standard_D2s_v5 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard

# SSH into VM
ssh azureuser@<public-ip>

# List VMs
az vm list --resource-group myapp-rg --output table

# Stop (deallocate) — stops billing for compute
az vm deallocate --resource-group myapp-rg --name myvm

# Start
az vm start --resource-group myapp-rg --name myvm

# Delete
az vm delete --resource-group myapp-rg --name myvm --yes
```

### VM Scale Sets (VMSS)

Auto-scaling group of identical VMs behind a load balancer.

```bash
az vmss create \
  --resource-group myapp-rg \
  --name myScaleSet \
  --image Ubuntu2204 \
  --instance-count 2 \
  --vm-sku Standard_D2s_v5 \
  --upgrade-policy-mode automatic \
  --admin-username azureuser \
  --generate-ssh-keys

# Auto-scale rules
az monitor autoscale create \
  --resource-group myapp-rg \
  --resource myScaleSet \
  --resource-type Microsoft.Compute/virtualMachineScaleSets \
  --min-count 2 \
  --max-count 10 \
  --count 2

# Scale rule: add 1 VM when CPU > 70%
az monitor autoscale rule create \
  --resource-group myapp-rg \
  --autoscale-name myScaleSet \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

### Pricing Models

| Model | Discount | Commitment | Best For |
|-------|----------|------------|----------|
| **Pay-As-You-Go** | 0% | None | Dev/test, unpredictable workloads |
| **Reserved Instances** | Up to 72% | 1 or 3 years | Steady-state production workloads |
| **Spot VMs** | Up to 90% | None (can be evicted) | Batch processing, fault-tolerant workloads |
| **Savings Plans** | Up to 65% | $/hour for 1 or 3 years | Flexible across VM sizes/regions |

---

## 2. App Service (PaaS)

Fully managed platform for web apps, APIs, and mobile backends. Supports .NET, Java, Python, Node.js, PHP, Ruby.

### Key Features

| Feature | Description |
|---------|-------------|
| **Deployment Slots** | Staging environment → swap to production with zero downtime |
| **Custom Domains + SSL** | Map custom domains, free managed SSL certificates |
| **Auto-Scale** | Scale based on CPU, memory, HTTP queue length, schedule |
| **CI/CD Integration** | GitHub Actions, Azure DevOps, local Git |
| **WebSockets** | Support for real-time applications |
| **Always On** | Keep app warm (prevent cold starts on free/shared tiers) |

### App Service Plans (Tiers)

| Tier | Use Case | Features |
|------|----------|----------|
| **Free / Shared** | Dev/test | Shared infra, no SLA, no custom domain |
| **Basic** | Low-traffic apps | Dedicated VMs, manual scale, custom domain |
| **Standard** | Production | Auto-scale, deployment slots, VNet integration |
| **Premium** | High-performance | More cores, more slots, zone redundancy |
| **Isolated** | Compliance | Dedicated environment (ASE), VNet isolation |

```bash
# Create App Service Plan
az appservice plan create \
  --name myPlan \
  --resource-group myapp-rg \
  --sku S1 \
  --is-linux

# Create Web App
az webapp create \
  --name mywebapp-unique \
  --resource-group myapp-rg \
  --plan myPlan \
  --runtime "PYTHON:3.11"

# Deploy from GitHub
az webapp deployment source config \
  --name mywebapp-unique \
  --resource-group myapp-rg \
  --repo-url https://github.com/user/repo \
  --branch main

# Deployment Slots
az webapp deployment slot create \
  --name mywebapp-unique \
  --resource-group myapp-rg \
  --slot staging

# Swap staging → production (zero downtime)
az webapp deployment slot swap \
  --name mywebapp-unique \
  --resource-group myapp-rg \
  --slot staging \
  --target-slot production

# App Settings (environment variables)
az webapp config appsettings set \
  --name mywebapp-unique \
  --resource-group myapp-rg \
  --settings DATABASE_URL="postgresql://..." SECRET_KEY="abc123"
```

### Deployment Slots — Deep Dive

```
Production Slot ◄───── Swap ─────► Staging Slot
(live traffic)                     (test new version)

Swap Process:
1. Warm up staging slot (pre-swap requests)
2. Swap routing rules (VIP swap — no restart)
3. Old production becomes staging (instant rollback possible)
```

> **Interview Tip:** Deployment slot swap is NOT a re-deployment — it's a routing change. The app is already warmed up, so there's **zero downtime**.

---

## 3. Azure Kubernetes Service (AKS)

Managed Kubernetes — Azure handles the control plane, you manage worker nodes.

### What Azure Manages vs What You Manage

```
┌─────────────────────────────────┐
│         Control Plane            │  ← Azure manages (FREE)
│  API Server, etcd, Scheduler,   │
│  Controller Manager             │
└─────────────┬───────────────────┘
              │
┌─────────────▼───────────────────┐
│         Node Pools               │  ← You manage (you pay for VMs)
│  ┌──────┐ ┌──────┐ ┌──────┐    │
│  │Node 1│ │Node 2│ │Node 3│    │
│  │(VM)  │ │(VM)  │ │(VM)  │    │
│  └──────┘ └──────┘ └──────┘    │
└─────────────────────────────────┘
```

```bash
# Create AKS cluster
az aks create \
  --resource-group myapp-rg \
  --name myAKSCluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v5 \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials (configure kubectl)
az aks get-credentials --resource-group myapp-rg --name myAKSCluster

# Cluster autoscaler
az aks nodepool update \
  --resource-group myapp-rg \
  --cluster-name myAKSCluster \
  --name nodepool1 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10

# Upgrade cluster
az aks upgrade --resource-group myapp-rg --name myAKSCluster --kubernetes-version 1.28.0
```

### AKS Key Features

| Feature | Description |
|---------|-------------|
| **Node Pools** | System pool (K8s system pods) + User pools (your apps) |
| **Autoscaler** | Cluster autoscaler (add/remove nodes) + HPA (pod replicas) |
| **Azure CNI** | Pods get VNet IP addresses directly |
| **Azure AD Integration** | RBAC with Azure AD identities |
| **Managed Identity** | No service principal credentials needed |
| **Azure Monitor** | Container Insights for logs, metrics, alerts |

---

## 4. Azure Container Instances (ACI)

Run containers **without managing VMs or orchestrators**. Fastest way to run a container in Azure.

```bash
az container create \
  --resource-group myapp-rg \
  --name mycontainer \
  --image mcr.microsoft.com/azuredocs/aci-helloworld \
  --ports 80 \
  --cpu 1 --memory 1.5 \
  --dns-name-label my-container-app \
  --restart-policy OnFailure

# Check logs
az container logs --resource-group myapp-rg --name mycontainer

# Attach to running container
az container attach --resource-group myapp-rg --name mycontainer
```

**Best For:** CI/CD build agents, batch jobs, sidecar containers, quick demos, event-driven tasks.

---

## 5. Azure Container Apps

Serverless container platform built on Kubernetes + KEDA + Envoy. **No Kubernetes knowledge needed.**

| Feature | Container Apps | AKS | ACI |
|---------|---------------|-----|-----|
| K8s knowledge needed | ❌ | ✅ | ❌ |
| Auto-scale to zero | ✅ | ❌ | ❌ |
| Built-in Dapr | ✅ | Manual | ❌ |
| Ingress/traffic splitting | ✅ | Manual (Ingress) | ❌ |
| Microservices | ✅ | ✅ | Single container |
| Cost model | Per-second | Per-node VM | Per-second |

```bash
az containerapp create \
  --name mycontainerapp \
  --resource-group myapp-rg \
  --environment my-env \
  --image myregistry.azurecr.io/myapp:latest \
  --target-port 8080 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 10
```

---

## Compute Service Comparison Matrix

| Criteria | VMs | App Service | AKS | ACI | Container Apps | Functions |
|----------|-----|-------------|-----|-----|----------------|-----------|
| Abstraction Level | IaaS | PaaS | CaaS | CaaS | Serverless CaaS | FaaS |
| OS Access | Full | No | Node level | No | No | No |
| Auto-scale | VMSS | Built-in | Cluster + HPA | Manual | KEDA | Built-in |
| Scale to Zero | No | No (keep-alive) | No | Yes | Yes | Yes (Consumption) |
| Cold Start | No | Possible | No | ~30s | ~5s | ~1-3s |
| Max Execution | Unlimited | Unlimited | Unlimited | Unlimited | Unlimited | 10 min (Consumption) |
| Pricing | Per VM-hour | Per plan | Per node-hour | Per second | Per second | Per execution |
| Best For | Legacy, full control | Web apps, APIs | Microservices | Jobs, sidecars | Event-driven services | Event processing |

---

## Common Interview Questions — Compute

### Q1: When would you choose AKS over App Service?

Use **AKS** when you need:
- **Multi-container microservices** with complex networking (service mesh)
- **Cross-platform portability** (same K8s manifests work anywhere)
- **Fine-grained control** over scaling, networking, storage
- **Custom operators** or specialized workloads (ML pipelines, data streaming)

Use **App Service** when:
- Simple web apps or REST APIs
- Don't want to manage K8s operational complexity
- Need quick deployment with CI/CD integration
- Team doesn't have Kubernetes expertise

### Q2: What are Deployment Slots in App Service, and how do they enable zero-downtime deployments?

Deployment slots are **separate instances** of the same app with their own hostnames. You deploy to a staging slot, test it, then **swap** it with production. The swap is a **VIP swap** (routing change, not re-deployment), so the staging slot is already warmed up → zero downtime. You can also route a percentage of traffic to staging for canary testing.

### Q3: What is the difference between Azure Container Instances and Container Apps?

**ACI** is a bare-bones container runtime — good for single-container jobs and quick tasks. **Container Apps** is a serverless platform **built on Kubernetes** that adds auto-scaling (including to zero), Dapr integration, traffic splitting, and revision management — ideal for microservices without K8s complexity.
