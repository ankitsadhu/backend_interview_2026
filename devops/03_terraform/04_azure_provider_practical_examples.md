# Azure Provider Practical Examples

## Provider Setup

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}
```

Authentication options:

- Azure CLI login for local development
- service principal for CI/CD
- managed identity from Azure-hosted runners
- OIDC federated identity from GitHub Actions/Azure DevOps

## Resource Group

```hcl
resource "azurerm_resource_group" "app" {
  name     = "rg-${var.environment}-app"
  location = var.location

  tags = local.tags
}
```

## VNet, Subnets, and NSG

```hcl
resource "azurerm_virtual_network" "main" {
  name                = "vnet-${var.environment}-main"
  location            = azurerm_resource_group.app.location
  resource_group_name = azurerm_resource_group.app.name
  address_space       = ["10.30.0.0/16"]
}

resource "azurerm_subnet" "app" {
  name                 = "snet-app"
  resource_group_name  = azurerm_resource_group.app.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.30.1.0/24"]
}

resource "azurerm_network_security_group" "app" {
  name                = "nsg-${var.environment}-app"
  location            = azurerm_resource_group.app.location
  resource_group_name = azurerm_resource_group.app.name

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}
```

Interview angle:

```text
Separate subnet creation from NSG association because Azure models that association as a distinct relationship.
```

## Storage Account

```hcl
resource "azurerm_storage_account" "app" {
  name                     = "st${var.environment}app001"
  resource_group_name      = azurerm_resource_group.app.name
  location                 = azurerm_resource_group.app.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true
  }

  tags = local.tags
}
```

Production notes:

- storage account names must be globally unique
- use private endpoints for sensitive workloads
- enable diagnostic logs where required
- avoid storing secrets in plain Terraform variables

## Key Vault

```hcl
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "app" {
  name                = "kv-${var.environment}-app-001"
  location            = azurerm_resource_group.app.location
  resource_group_name = azurerm_resource_group.app.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  purge_protection_enabled   = true
  soft_delete_retention_days = 30
}
```

Interview warning:

```text
Do not put secret values into Terraform state unless you accept the state security implications. Prefer referencing secrets managed outside Terraform or injecting through CI/CD secret stores.
```

## App Service Plan and Web App

```hcl
resource "azurerm_service_plan" "app" {
  name                = "asp-${var.environment}-api"
  location            = azurerm_resource_group.app.location
  resource_group_name = azurerm_resource_group.app.name
  os_type             = "Linux"
  sku_name            = "P1v3"
}

resource "azurerm_linux_web_app" "api" {
  name                = "app-${var.environment}-api-001"
  location            = azurerm_resource_group.app.location
  resource_group_name = azurerm_resource_group.app.name
  service_plan_id     = azurerm_service_plan.app.id

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = true
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE" = "1"
  }
}
```

## Private Endpoint Shape

```hcl
resource "azurerm_private_endpoint" "storage_blob" {
  name                = "pe-${var.environment}-storage-blob"
  location            = azurerm_resource_group.app.location
  resource_group_name = azurerm_resource_group.app.name
  subnet_id           = azurerm_subnet.app.id

  private_service_connection {
    name                           = "psc-storage-blob"
    private_connection_resource_id = azurerm_storage_account.app.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }
}
```

Usually pair this with:

- private DNS zone
- VNet link
- storage firewall restrictions

## AKS Skeleton

```hcl
resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-${var.environment}-main"
  location            = azurerm_resource_group.app.location
  resource_group_name = azurerm_resource_group.app.name
  dns_prefix          = "aks-${var.environment}-main"

  default_node_pool {
    name       = "system"
    node_count = 3
    vm_size    = "Standard_D4s_v5"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
  }
}
```

Production AKS Terraform usually needs more:

- private cluster decision
- node pool separation
- autoscaling
- Azure CNI planning
- managed identities
- Key Vault CSI driver
- logging and monitoring
- network policy
- upgrade strategy

## Cross Questions

### Should Terraform deploy application code?

Usually no. Terraform should provision infrastructure. Application deployment belongs in app CI/CD, Helm, GitOps, or deployment tooling. There are exceptions, but mixing infra and app deploys often creates noisy plans and risky applies.

### Should Terraform create secrets?

Terraform can create secrets, but secret values may end up in state. For production, prefer secret references, Key Vault integration, and tightly secured state.

### Why pin provider versions?

Provider updates can change behavior or resource schemas. Pinning gives reproducible plans and safer upgrades.

