# Azure Fundamentals

## What is Azure?

**Microsoft Azure** is a cloud computing platform providing **200+ services** including compute, storage, networking, databases, AI, and DevOps tools across **60+ regions** worldwide.

### Cloud Computing Models

| Model | You Manage | Provider Manages | Example |
|-------|-----------|------------------|---------|
| **IaaS** | OS, Runtime, App, Data | Hardware, Networking, Virtualization | Azure VMs |
| **PaaS** | App, Data | Everything else | App Service, Azure SQL |
| **SaaS** | Nothing (just use it) | Everything | Microsoft 365, Dynamics |
| **FaaS** | Just the code | Everything else | Azure Functions |

```
On-Premises     IaaS           PaaS           SaaS
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ App      │   │ App      │   │ App      │   │██████████│
│ Data     │   │ Data     │   │ Data     │   │██████████│
│ Runtime  │   │ Runtime  │   │██████████│   │██████████│
│ OS       │   │ OS       │   │██████████│   │██████████│
│ Virtualize│  │██████████│   │██████████│   │██████████│
│ Servers  │   │██████████│   │██████████│   │██████████│
│ Storage  │   │██████████│   │██████████│   │██████████│
│ Network  │   │██████████│   │██████████│   │██████████│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
 You manage     ████ = Provider manages
```

---

## Azure Global Infrastructure

### Regions & Availability

```
Azure Global Infrastructure
├── Geography (e.g., United States, Europe, Asia)
│   ├── Region (e.g., East US, West Europe)
│   │   ├── Availability Zone 1 (independent datacenter)
│   │   ├── Availability Zone 2
│   │   └── Availability Zone 3
│   └── Region Pair (e.g., East US ↔ West US)
│       └── Used for disaster recovery, geo-replication
```

| Concept | Description | SLA Impact |
|---------|-------------|------------|
| **Region** | Geographic area with 1+ datacenters | Determines latency, compliance |
| **Availability Zone** | Physically separate datacenter within a region | 99.99% SLA (zone-redundant) |
| **Region Pair** | Two regions in same geography, paired for DR | Cross-region replication |
| **Sovereign Cloud** | Azure Government, Azure China (21Vianet) | Meets regulatory requirements |

> **Interview Tip:** Azure has **60+ regions** — more than any cloud provider. Each region has **3 availability zones** (where supported).

---

## Azure Resource Hierarchy

```
Management Group (optional)
    └── Subscription (billing boundary)
        └── Resource Group (logical container)
            ├── Resource (VM, Storage Account, etc.)
            ├── Resource
            └── Resource
```

### Management Groups
- Organize subscriptions into a hierarchy
- Apply policies and RBAC at scale
- Up to 6 levels of depth (excluding root)

### Subscriptions
- **Billing boundary** — each subscription gets its own invoice
- **Access control boundary** — RBAC policies scoped to subscription
- Types: Free, Pay-As-You-Go, Enterprise Agreement, CSP

### Resource Groups
- **Logical container** for related resources
- Resources can only belong to **one** resource group
- Deleting a resource group deletes **all resources** inside it
- Used for lifecycle management, access control, and cost tracking

```bash
# Azure CLI — Working with Resource Groups
az group create --name my-rg --location eastus
az group list --output table
az group delete --name my-rg --yes --no-wait
```

---

## Azure Resource Manager (ARM)

ARM is the **management layer** for all Azure operations. Every request (Portal, CLI, SDK, REST API) goes through ARM.

```
     Portal    CLI    SDK    REST API    PowerShell
        │       │      │        │           │
        └───────┴──────┴────────┴───────────┘
                        │
                ┌───────▼───────┐
                │  Azure Resource│
                │   Manager (ARM)│
                └───────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   Compute          Storage         Networking
   Services         Services        Services
```

### Key ARM Concepts

| Concept | Description |
|---------|-------------|
| **Resource Provider** | Service that supplies resources (e.g., `Microsoft.Compute` for VMs) |
| **Resource Type** | `Microsoft.Compute/virtualMachines`, `Microsoft.Storage/storageAccounts` |
| **ARM Template** | JSON-based Infrastructure as Code (IaC) |
| **Bicep** | DSL that compiles to ARM templates (cleaner syntax) |

### ARM Template Example

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2021-09-01",
      "name": "mystorageaccount",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2"
    }
  ]
}
```

### Bicep Equivalent (Preferred)

```bicep
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-09-01' = {
  name: 'mystorageaccount'
  location: resourceGroup().location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}
```

---

## Azure CLI Essentials

```bash
# Authentication
az login                              # Browser-based login
az login --service-principal \
  --username <app-id> \
  --password <secret> --tenant <id>   # Service principal login

# Account & Subscription
az account show                       # Current subscription
az account list --output table        # All subscriptions
az account set --subscription <id>    # Switch subscription

# Resource Groups
az group create --name myapp-rg --location eastus
az group list --output table

# Common Patterns
az <service> create ...               # Create resource
az <service> list ...                 # List resources
az <service> show --name <n> --resource-group <rg>  # Get details
az <service> delete --name <n> --resource-group <rg> # Delete
az <service> update ...               # Update resource

# Output Formats
az vm list --output table             # Table format
az vm list --output json              # JSON (default)
az vm list --output tsv               # Tab-separated
az vm list --query "[].{Name:name, RG:resourceGroup}" --output table  # JMESPath query
```

---

## Tagging Strategy

Tags are key-value pairs for organizing and tracking resources.

```bash
az resource tag --tags Environment=Production Department=Engineering CostCenter=CC123 \
  --resource-group myapp-rg --name myvm --resource-type Microsoft.Compute/virtualMachines
```

**Recommended Tags:**

| Tag | Purpose | Example |
|-----|---------|---------|
| `Environment` | Deployment stage | Dev, Staging, Production |
| `Owner` | Responsible team/person | platform-team |
| `CostCenter` | Billing allocation | CC-12345 |
| `Project` | Project name | user-service |
| `ManagedBy` | IaC tool | Terraform, Bicep |

---

## Azure vs AWS vs GCP — Quick Comparison

| Category | Azure | AWS | GCP |
|----------|-------|-----|-----|
| Compute (VMs) | Virtual Machines | EC2 | Compute Engine |
| Managed K8s | AKS | EKS | GKE |
| Serverless | Azure Functions | Lambda | Cloud Functions |
| Object Storage | Blob Storage | S3 | Cloud Storage |
| SQL Database | Azure SQL | RDS | Cloud SQL |
| NoSQL | Cosmos DB | DynamoDB | Firestore/Bigtable |
| Message Queue | Service Bus | SQS/SNS | Pub/Sub |
| Event Streaming | Event Hubs | Kinesis | Pub/Sub |
| CDN | Azure CDN / Front Door | CloudFront | Cloud CDN |
| DNS | Azure DNS | Route 53 | Cloud DNS |
| Identity | Azure AD (Entra ID) | IAM | Cloud IAM |
| Key Management | Key Vault | KMS/Secrets Manager | KMS/Secret Manager |
| Monitoring | Azure Monitor | CloudWatch | Cloud Monitoring |
| IaC | ARM/Bicep + Terraform | CloudFormation + Terraform | Deployment Manager + Terraform |

---

## Common Interview Questions — Fundamentals

### Q1: What is the difference between a Region, Availability Zone, and Region Pair?

- **Region**: A set of datacenters deployed within a geographic area (e.g., East US). You choose a region for latency, compliance, and service availability.
- **Availability Zone**: Physically separate datacenters **within a single region**, each with independent power, cooling, and networking. Deploying across zones gives **99.99% SLA**.
- **Region Pair**: Two regions in the same geography paired for disaster recovery. Azure ensures updates roll out to one region at a time. Example: East US ↔ West US.

### Q2: What is a Resource Group? Can a resource belong to multiple resource groups?

A Resource Group is a logical container for related Azure resources. **No** — a resource can only belong to **one** resource group. However, resources in different resource groups can interact with each other. Deleting a resource group deletes all contained resources.

### Q3: What is the difference between ARM and Bicep?

Both are Infrastructure as Code — ARM templates use JSON (verbose, hard to read), while Bicep is a DSL that **compiles down to ARM JSON** but is much cleaner:
- Bicep: No string concatenation, cleaner syntax, modules, type safety
- ARM: Verbose JSON, complex expressions, harder to maintain
- Both achieve the same result — Bicep is the recommended approach

### Q4: How do you choose between IaaS, PaaS, and FaaS?

| Need | Choose | Why |
|------|--------|-----|
| Full OS control, legacy apps | **IaaS** (VMs) | Lift-and-shift, custom software |
| Web apps, APIs, no infra management | **PaaS** (App Service) | Managed platform, auto-scaling |
| Event-driven, short-lived tasks | **FaaS** (Functions) | Pay per execution, auto-scale to zero |
| Containerized microservices | **AKS** | Kubernetes orchestration, portable |
