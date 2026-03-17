# Azure Networking

## Networking Building Blocks

```
Internet
    │
    ▼
┌─────────────────────────────────────────────┐
│ Azure Front Door / Application Gateway (L7) │  ← Global/Regional load balancer
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│ Virtual Network (VNet) — 10.0.0.0/16        │
│                                              │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ Subnet A      │  │ Subnet B      │        │
│  │ 10.0.1.0/24  │  │ 10.0.2.0/24  │        │
│  │ ┌──┐ ┌──┐   │  │ ┌──┐ ┌──┐   │        │
│  │ │VM│ │VM│   │  │ │VM│ │VM│   │        │
│  │ └──┘ └──┘   │  │ └──┘ └──┘   │        │
│  │ [NSG]        │  │ [NSG]        │        │
│  └──────────────┘  └──────────────┘         │
│                                              │
│  ┌──────────────┐                            │
│  │ Private       │  ← Private Endpoint       │
│  │ Endpoint      │    for PaaS services       │
│  └──────────────┘                            │
└──────────────────────────────────────────────┘
```

---

## 1. Virtual Network (VNet)

The fundamental building block — an isolated network in Azure.

| Feature | Description |
|---------|-------------|
| **Address Space** | CIDR range (e.g., 10.0.0.0/16 = 65,536 IPs) |
| **Subnets** | Divide VNet into smaller ranges |
| **Region-bound** | VNet exists in one region. Use peering to connect VNets |
| **Free** | No cost for VNets themselves |

```bash
# Create VNet
az network vnet create \
  --resource-group myapp-rg \
  --name myVNet \
  --address-prefix 10.0.0.0/16 \
  --subnet-name frontend \
  --subnet-prefix 10.0.1.0/24

# Add another subnet
az network vnet subnet create \
  --resource-group myapp-rg \
  --vnet-name myVNet \
  --name backend \
  --address-prefix 10.0.2.0/24
```

### VNet Peering

Connect two VNets (same or different regions) — traffic stays on Microsoft backbone.

```bash
# Peer VNet-A → VNet-B (must create in both directions)
az network vnet peering create \
  --name AtoB \
  --resource-group myapp-rg \
  --vnet-name VNetA \
  --remote-vnet /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/VNetB \
  --allow-vnet-access
```

> **Important:** VNet peering is **non-transitive** — if A peers with B and B peers with C, A cannot reach C without a direct peering or a hub-spoke topology.

---

## 2. Network Security Groups (NSG)

Firewall rules for subnets and NICs. Rules are evaluated by **priority** (lower number = higher priority).

```bash
# Create NSG
az network nsg create --resource-group myapp-rg --name myNSG

# Allow HTTP inbound
az network nsg rule create \
  --resource-group myapp-rg \
  --nsg-name myNSG \
  --name AllowHTTP \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --destination-port-ranges 80 443 \
  --source-address-prefixes '*'

# Deny all other inbound (explicit)
az network nsg rule create \
  --resource-group myapp-rg \
  --nsg-name myNSG \
  --name DenyAllInbound \
  --priority 4096 \
  --direction Inbound \
  --access Deny \
  --protocol '*' \
  --source-address-prefixes '*' \
  --destination-port-ranges '*'

# Associate NSG with subnet
az network vnet subnet update \
  --resource-group myapp-rg \
  --vnet-name myVNet \
  --name frontend \
  --network-security-group myNSG
```

### Default NSG Rules (Cannot Be Deleted)

| Priority | Rule | Direction |
|----------|------|-----------|
| 65000 | Allow VNet inbound/outbound | Both |
| 65001 | Allow Azure Load Balancer inbound | Inbound |
| 65500 | Deny all inbound/outbound | Both |

---

## 3. Load Balancing Options

| Service | Layer | Scope | Use Case |
|---------|-------|-------|----------|
| **Azure Load Balancer** | L4 (TCP/UDP) | Regional | VM/VMSS traffic distribution |
| **Application Gateway** | L7 (HTTP/S) | Regional | WAF, SSL termination, URL routing |
| **Azure Front Door** | L7 (HTTP/S) | Global | Global CDN + WAF + load balancing |
| **Traffic Manager** | DNS-based | Global | Multi-region failover (DNS routing) |

### Azure Load Balancer (L4)

```bash
# Create public load balancer
az network lb create \
  --resource-group myapp-rg \
  --name myLB \
  --sku Standard \
  --frontend-ip-name myFrontEnd \
  --backend-pool-name myBackEnd \
  --public-ip-address myPublicIP

# Health probe
az network lb probe create \
  --resource-group myapp-rg \
  --lb-name myLB \
  --name healthProbe \
  --protocol tcp \
  --port 80

# Load balancing rule
az network lb rule create \
  --resource-group myapp-rg \
  --lb-name myLB \
  --name httpRule \
  --frontend-ip myFrontEnd \
  --backend-pool myBackEnd \
  --protocol tcp \
  --frontend-port 80 \
  --backend-port 80 \
  --probe healthProbe
```

### Application Gateway (L7)

```
Client → AppGW → Backend Pool (VMs/App Service/AKS)
              │
         Features:
         ├── SSL/TLS termination
         ├── URL-based routing (/api → backend1, /web → backend2)
         ├── Cookie-based session affinity
         ├── Web Application Firewall (WAF)
         ├── Auto-scaling
         └── WebSocket support
```

### Azure Front Door (Global L7)

```
Users worldwide → Front Door edge POPs → Nearest healthy backend
                  │
             Features:
             ├── Global HTTP load balancing
             ├── SSL offloading
             ├── WAF (DDoS protection)
             ├── Caching (CDN built-in)
             ├── URL rewrite & redirect
             └── Session affinity
```

---

## 4. Private Endpoints

Access PaaS services (Storage, SQL, Cosmos DB) **privately** over your VNet — traffic never leaves Microsoft backbone.

```
Without Private Endpoint:
App (VNet) →→→ Internet →→→ Azure SQL (public endpoint)

With Private Endpoint:
App (VNet) ──── Private Endpoint (10.0.3.4) ──── Azure SQL
              (traffic stays on Azure backbone)
```

```bash
# Create private endpoint for Azure SQL
az network private-endpoint create \
  --resource-group myapp-rg \
  --name mySqlPrivateEndpoint \
  --vnet-name myVNet \
  --subnet backend \
  --private-connection-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Sql/servers/myserver \
  --group-id sqlServer \
  --connection-name mySqlConnection
```

> **Interview Tip:** Private Endpoints assign a **private IP** from your VNet to the PaaS service. Combined with disabling public access, this is the standard security pattern for production.

---

## 5. Azure DNS

| Type | Purpose |
|------|---------|
| **Public DNS Zone** | Manage DNS records for public domains |
| **Private DNS Zone** | Name resolution within VNets (e.g., for Private Endpoints) |

```bash
# Create private DNS zone
az network private-dns zone create \
  --resource-group myapp-rg \
  --name privatelink.database.windows.net

# Link to VNet
az network private-dns link vnet create \
  --resource-group myapp-rg \
  --zone-name privatelink.database.windows.net \
  --name myDNSLink \
  --virtual-network myVNet \
  --registration-enabled false
```

---

## Common Interview Questions — Networking

### Q1: Explain the hub-spoke network topology.

A **hub VNet** acts as a central point of connectivity. **Spoke VNets** peer with the hub but not with each other. Traffic between spokes flows through the hub (via a firewall/NVA). Benefits:
- Centralized security (Azure Firewall in hub)
- Shared services (DNS, monitoring) in hub
- Isolation between workloads (spokes)
- Cost savings (shared ExpressRoute/VPN gateway)

### Q2: What's the difference between NSG and Azure Firewall?

**NSG**: Basic L3/L4 filtering (IP, port, protocol) at subnet/NIC level — free, stateful.
**Azure Firewall**: Managed L4-L7 firewall with FQDN filtering, threat intelligence, TLS inspection, centralized logging — fully managed, paid service. Use NSG for micro-segmentation within a VNet; use Azure Firewall as a centralized edge firewall.

### Q3: When would you use Private Endpoints vs Service Endpoints?

**Private Endpoints** assign a private IP from your VNet — traffic is fully private. **Service Endpoints** extend VNet identity to PaaS services (traffic still goes to public IP but through Microsoft backbone). Private Endpoints are preferred because:
- Works across VNet peering and on-premises
- PaaS service gets actual private IP (visible in DNS)
- Can disable public access entirely
