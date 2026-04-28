# Azure Networking Examples

## Azure Network Building Blocks

```text
Internet
  |
  v
Azure Front Door
  |
  v
Application Gateway / WAF
  |
  v
VNet
  |
  +-- frontend subnet
  +-- backend subnet
  +-- private endpoint subnet
  +-- AzureFirewallSubnet
```

Core services:

- Virtual Network
- Subnet
- Network Security Group
- Route Table
- NAT Gateway
- Azure Load Balancer
- Application Gateway
- Azure Front Door
- Private Endpoint
- Private DNS Zone
- VPN Gateway / ExpressRoute

## VNet and Subnet Example

```bash
az group create \
  --name rg-network-demo \
  --location eastus

az network vnet create \
  --resource-group rg-network-demo \
  --name vnet-prod-eastus \
  --address-prefix 10.10.0.0/16 \
  --subnet-name snet-app \
  --subnet-prefix 10.10.1.0/24

az network vnet subnet create \
  --resource-group rg-network-demo \
  --vnet-name vnet-prod-eastus \
  --name snet-db \
  --address-prefix 10.10.2.0/24
```

Interview explanation:

```text
The VNet provides private address space. Subnets separate app and database tiers so security and routing can be controlled independently.
```

## NSG Example

Allow HTTPS to app subnet, deny direct database access from internet.

```bash
az network nsg create \
  --resource-group rg-network-demo \
  --name nsg-app

az network nsg rule create \
  --resource-group rg-network-demo \
  --nsg-name nsg-app \
  --name AllowHTTPS \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --destination-port-ranges 443

az network vnet subnet update \
  --resource-group rg-network-demo \
  --vnet-name vnet-prod-eastus \
  --name snet-app \
  --network-security-group nsg-app
```

Important:

```text
NSG rules are stateful. If inbound traffic is allowed, the response traffic is automatically allowed.
```

## NAT Gateway for Outbound Internet

Use NAT Gateway when private subnets need stable outbound internet IPs.

```bash
az network public-ip create \
  --resource-group rg-network-demo \
  --name pip-nat-prod \
  --sku Standard

az network nat gateway create \
  --resource-group rg-network-demo \
  --name nat-prod \
  --public-ip-addresses pip-nat-prod

az network vnet subnet update \
  --resource-group rg-network-demo \
  --vnet-name vnet-prod-eastus \
  --name snet-app \
  --nat-gateway nat-prod
```

Use case:

```text
Third-party payment provider allows only requests from your fixed outbound IP.
```

## Private Endpoint Example

Private Endpoint gives a private IP inside your VNet for an Azure PaaS service.

Use cases:

- Azure Storage private access
- Azure SQL private access
- Key Vault private access
- Cosmos DB private access

Mental model:

```text
App subnet -> private IP in VNet -> Azure PaaS service
```

You usually also need Private DNS so the public service hostname resolves to the private endpoint IP from inside the VNet.

Interview trap:

```text
Creating a private endpoint without correct private DNS often leads to confusing connectivity failures.
```

## Application Gateway vs Front Door

| Feature | Application Gateway | Azure Front Door |
|---------|---------------------|------------------|
| Scope | Regional | Global edge |
| Layer | L7 HTTP/S | L7 HTTP/S |
| Common Use | Regional WAF and routing | Global routing, CDN, WAF |
| Backend | VMs, AKS, App Service, private backends | global apps, multi-region |

Typical design:

```text
Global users -> Front Door -> regional App Gateway -> AKS/App Service
```

## Hub-Spoke Network

```text
          on-prem
             |
        VPN/ExpressRoute
             |
          hub VNet
       /     |      \
 spoke A  spoke B  spoke C
```

Hub contains shared services:

- firewall
- VPN/ExpressRoute gateway
- DNS resolver
- bastion
- monitoring

Spokes contain workloads.

Why:

- centralized security
- easier connectivity
- shared network services
- scalable team isolation

## AKS Networking Interview View

AKS networking choices include:

- Azure CNI
- kubenet
- overlay networking
- internal load balancer
- ingress controller
- private cluster

Common production pattern:

```text
Front Door -> Application Gateway Ingress Controller -> private AKS services -> private database endpoint
```

Questions to expect:

- how pods get IPs
- how services are exposed
- how ingress differs from service
- how private AKS reaches Azure Container Registry
- how NSG and Kubernetes NetworkPolicy differ

## Azure Troubleshooting Commands

```bash
# Effective routes for a NIC
az network nic show-effective-route-table \
  --resource-group rg-network-demo \
  --name myNic

# Effective NSG rules for a NIC
az network nic list-effective-nsg \
  --resource-group rg-network-demo \
  --name myNic

# Network Watcher connectivity test
az network watcher test-connectivity \
  --source-resource <source-resource-id> \
  --dest-address api.example.com \
  --dest-port 443

# Check DNS records in private zone
az network private-dns record-set a list \
  --resource-group rg-network-demo \
  --zone-name privatelink.blob.core.windows.net
```

## Cross Questions

### NSG vs Azure Firewall?

NSG is subnet/NIC-level filtering. Azure Firewall is a managed centralized firewall with richer L3-L7 filtering, threat intelligence, logging, and forced tunneling patterns.

### Private Endpoint vs Service Endpoint?

Private Endpoint gives the service a private IP in your VNet. Service Endpoint keeps the public endpoint but restricts access to selected VNets.

### Front Door vs Traffic Manager?

Front Door is a global L7 reverse proxy. Traffic Manager is DNS-based routing and does not proxy traffic.

### Why might an Azure VM have internet access one day and fail the next?

Possible causes: route table change, NAT Gateway issue, NSG change, Azure Firewall policy, DNS change, public IP removal, or exhausted SNAT ports.

