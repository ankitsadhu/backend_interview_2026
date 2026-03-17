# Azure Identity & Security

## Security Model Overview

```
Authentication (Who are you?)
    │
    ▼
Azure AD (Entra ID) ─── Issues tokens (OAuth 2.0 / OIDC)
    │
    ▼
Authorization (What can you do?)
    │
    ├── Azure RBAC (Azure resources — VMs, Storage, etc.)
    ├── Azure AD Roles (Identity plane — users, groups, apps)
    └── Data Plane RBAC (Cosmos DB, Storage data access, etc.)
    │
    ▼
Secrets Management (Protect credentials)
    │
    └── Azure Key Vault (keys, secrets, certificates)
```

---

## 1. Azure AD (Microsoft Entra ID)

Cloud-based **identity and access management** service. Handles authentication for Azure, Microsoft 365, and custom applications.

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Tenant** | An instance of Azure AD representing an organization |
| **User** | A person identity (credentials + profile) |
| **Group** | Collection of users for bulk permission assignment |
| **Service Principal** | Identity for an application/service |
| **Managed Identity** | Auto-managed service principal (no credential management) |
| **App Registration** | Register your app to use Azure AD for auth |
| **Enterprise Application** | Instance of an app within your tenant |

### Authentication Flows (OAuth 2.0)

| Flow | Use Case | Token Type |
|------|----------|------------|
| **Authorization Code** | Web apps (with backend) | Access + Refresh token |
| **Authorization Code + PKCE** | SPAs, Mobile apps | Access + Refresh token |
| **Client Credentials** | Service-to-service (daemon/backend) | Access token only |
| **On-Behalf-Of** | API calls another API on user's behalf | Delegated access token |
| **Device Code** | CLI, IoT devices (no browser) | Access + Refresh token |

### Client Credentials Flow (Service-to-Service)

```
┌────────┐                      ┌──────────┐                    ┌───────────┐
│ Backend │ ── 1. Request token ─→ │ Azure AD │                    │ Target API│
│ Service │                      │          │                    │           │
│         │ ◄─ 2. Access token ── │          │                    │           │
│         │ ── 3. Call API ────────────────────────────────────→ │           │
│         │    (Bearer token)     │          │                    │           │
└────────┘                      └──────────┘                    └───────────┘
```

```python
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient

# Client credentials flow
credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="your-app-id",
    client_secret="your-client-secret"
)

# Use credential to access Azure resources
resource_client = ResourceManagementClient(credential, subscription_id="your-sub-id")

for rg in resource_client.resource_groups.list():
    print(rg.name)
```

---

## 2. Managed Identity

Azure-managed service principal — **no credentials to manage, rotate, or leak**.

### Types

| Type | Lifecycle | Use Case |
|------|-----------|----------|
| **System-assigned** | Tied to resource (created/deleted with it) | Single resource needs access |
| **User-assigned** | Independent lifecycle (you create/delete) | Share identity across resources |

```
App Service (with Managed Identity)
    │
    ▼ (requests token from Azure AD — automatic, no secrets)
Azure AD
    │
    ▼ (returns access token)
App uses token to access:
    ├── Azure SQL
    ├── Key Vault
    ├── Blob Storage
    └── Cosmos DB
```

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# DefaultAzureCredential automatically uses:
# 1. Environment variables (for dev)
# 2. Managed Identity (in Azure)
# 3. Azure CLI credentials (for local dev)
# 4. VS Code credentials
credential = DefaultAzureCredential()

# Access Blob Storage without connection strings!
blob_client = BlobServiceClient(
    account_url="https://mystorageacct.blob.core.windows.net",
    credential=credential
)

# List containers
for container in blob_client.list_containers():
    print(container.name)
```

```bash
# Enable system-assigned managed identity
az webapp identity assign --resource-group myapp-rg --name mywebapp

# Grant access to Key Vault
az keyvault set-policy \
  --name myKeyVault \
  --object-id <managed-identity-principal-id> \
  --secret-permissions get list
```

> **Interview Tip:** `DefaultAzureCredential` is the recommended auth approach. It tries multiple credential sources in order, working seamlessly in both local dev and Azure production.

---

## 3. Azure RBAC (Role-Based Access Control)

Authorization model for **Azure resources** (management plane + data plane).

### How RBAC Works

```
Security Principal (who)  +  Role (what)  +  Scope (where)  =  Permission
      │                        │                  │
      ├── User                 ├── Owner          ├── Management Group
      ├── Group                ├── Contributor     ├── Subscription
      ├── Service Principal    ├── Reader          ├── Resource Group
      └── Managed Identity     ├── Custom Role     └── Resource
                               └── Data Roles
```

### Built-in Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Owner** | Full access + can assign roles | Admins |
| **Contributor** | Full access, cannot assign roles | Developers |
| **Reader** | Read-only | Auditors, viewers |
| **User Access Administrator** | Manage role assignments only | Security team |
| **Storage Blob Data Contributor** | Read/write blob data | Data access |
| **Key Vault Secrets User** | Read secrets | Apps accessing secrets |

```bash
# Assign role
az role assignment create \
  --assignee user@company.com \
  --role "Contributor" \
  --scope /subscriptions/<sub-id>/resourceGroups/myapp-rg

# List role assignments
az role assignment list --resource-group myapp-rg --output table

# Custom role
az role definition create --role-definition '{
  "Name": "VM Operator",
  "Description": "Can start and stop VMs",
  "Actions": [
    "Microsoft.Compute/virtualMachines/start/action",
    "Microsoft.Compute/virtualMachines/restart/action",
    "Microsoft.Compute/virtualMachines/deallocate/action",
    "Microsoft.Compute/virtualMachines/read"
  ],
  "AssignableScopes": ["/subscriptions/<sub-id>"]
}'
```

### Principle of Least Privilege

```
❌ Bad:  Assign "Owner" at subscription level to all developers
✅ Good: Assign "Contributor" at resource group level to team
✅ Best: Assign specific data roles per resource (e.g., "Storage Blob Data Reader")
```

---

## 4. Azure Key Vault

Centralized secrets management — keys, secrets, and certificates.

| Object Type | Use Case | Example |
|-------------|----------|---------|
| **Secrets** | Connection strings, API keys, passwords | `DatabaseConnectionString` |
| **Keys** | Encryption keys (RSA, EC) | Disk encryption, signing |
| **Certificates** | SSL/TLS certificates | Custom domain certs |

```bash
# Create Key Vault
az keyvault create \
  --name myKeyVault \
  --resource-group myapp-rg \
  --location eastus \
  --enable-rbac-authorization true

# Store a secret
az keyvault secret set \
  --vault-name myKeyVault \
  --name "DatabasePassword" \
  --value "P@ssw0rd!"

# Get a secret
az keyvault secret show \
  --vault-name myKeyVault \
  --name "DatabasePassword" \
  --query value --output tsv
```

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://myKeyVault.vault.azure.net",
    credential=credential
)

# Get secret
db_password = client.get_secret("DatabasePassword")
print(f"DB Password: {db_password.value}")

# Set secret
client.set_secret("ApiKey", "sk-abc123xyz")

# List secrets
for secret in client.list_properties_of_secrets():
    print(f"{secret.name}: enabled={secret.enabled}")
```

### Key Vault Best Practices

1. **Use RBAC** over Access Policies (newer, more granular)
2. **Enable soft-delete** (on by default, 90-day recovery)
3. **Enable purge protection** for production (prevents permanent deletion)
4. **Use Managed Identity** to access Key Vault (no secrets to access secrets!)
5. **Reference secrets from App Service** using `@Microsoft.KeyVault(SecretUri=...)`
6. **Enable logging** with Azure Monitor for audit trail

### App Service Key Vault Reference

```bash
# Instead of storing secrets in app settings:
# DATABASE_URL=postgresql://user:password@server/db

# Reference Key Vault:
az webapp config appsettings set \
  --name mywebapp \
  --resource-group myapp-rg \
  --settings "DATABASE_URL=@Microsoft.KeyVault(VaultName=myKeyVault;SecretName=DatabaseURL)"
```

---

## 5. Zero Trust Security Model

```
Never trust, always verify.

Principles:
1. Verify explicitly — Always authenticate and authorize
2. Least privilege access — Just-in-time, just-enough access
3. Assume breach — Minimize blast radius, segment access, encrypt
```

| Layer | Azure Implementation |
|-------|---------------------|
| Identity | Azure AD + MFA + Conditional Access |
| Devices | Intune / Endpoint Manager |
| Applications | App proxy, RBAC, Managed Identity |
| Data | Encryption at rest + in transit, data classification |
| Infrastructure | NSGs, Azure Firewall, Private Endpoints |
| Network | VNet isolation, micro-segmentation |

---

## Common Interview Questions — Security

### Q1: What is the difference between a Service Principal and a Managed Identity?

Both are identities for applications/services, but:
- **Service Principal**: You create it, you manage its credentials (client secret or certificate), you rotate secrets. Used when Managed Identity isn't available.
- **Managed Identity**: Azure auto-manages the credentials — no secrets to store, rotate, or leak. System-assigned is tied to a resource lifecycle; user-assigned can be shared. **Always prefer Managed Identity.**

### Q2: How does DefaultAzureCredential work?

It tries authenticated credential sources in order: Environment variables → Managed Identity → Azure CLI → VS Code → Interactive browser. This means the same code works in local dev (uses CLI/VS Code credentials) and production (uses Managed Identity) without changes.

### Q3: How would you securely connect an App Service to Azure SQL?

1. Enable **Managed Identity** on App Service
2. Grant the managed identity **SQL Database Reader/Writer** role or create a contained DB user
3. Use `DefaultAzureCredential` for token-based auth (no password)
4. Create a **Private Endpoint** for Azure SQL
5. Disable public access on Azure SQL
6. Store no connection string secrets — use `Authentication=Active Directory Default` in connection string
