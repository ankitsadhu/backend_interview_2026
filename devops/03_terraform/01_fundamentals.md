# Terraform Fundamentals

## What Is Terraform?

Terraform is an Infrastructure as Code tool.

You declare the desired infrastructure in configuration files, and Terraform plans and applies changes to make real infrastructure match that desired state.

Example:

```hcl
resource "azurerm_resource_group" "app" {
  name     = "rg-prod-app"
  location = "eastus"
}
```

## Why Infrastructure as Code?

IaC gives you:

- repeatability
- reviewable infrastructure changes
- version control
- faster environment creation
- less manual drift
- safer collaboration

Interview answer:

```text
IaC turns infrastructure changes into code changes, so they can be reviewed, tested, versioned, and rolled out consistently.
```

## Terraform Core Concepts

### Provider

A provider is a plugin that knows how to manage a platform.

Examples:

- `azurerm`
- `aws`
- `google`
- `kubernetes`
- `helm`

### Resource

A resource is something Terraform creates or manages.

Examples:

- Azure resource group
- virtual network
- storage account
- Kubernetes namespace

### Data Source

A data source reads existing information.

Example:

```hcl
data "azurerm_client_config" "current" {}
```

### State

State is Terraform's record of managed infrastructure.

Terraform uses state to map:

```text
resource block in code -> real cloud resource
```

State is not optional trivia. It is central to how Terraform works.

## Plan and Apply

### `terraform init`

Downloads providers and configures backend.

### `terraform plan`

Shows what Terraform intends to change.

### `terraform apply`

Applies the plan.

### `terraform destroy`

Destroys managed infrastructure.

Basic flow:

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

## Declarative vs Imperative

Terraform is declarative.

You say:

```text
I want this infrastructure.
```

You do not usually say:

```text
First click this, then create that, then update this field.
```

Terraform decides the required operations using the provider and state.

## Dependency Graph

Terraform builds a graph of dependencies.

Explicit dependency:

```hcl
resource "azurerm_subnet" "app" {
  name                 = "snet-app"
  resource_group_name  = azurerm_resource_group.app.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}
```

Because the subnet references the VNet and resource group, Terraform knows the order.

Manual dependency:

```hcl
depends_on = [azurerm_network_security_group.app]
```

Use `depends_on` only when Terraform cannot infer the relationship.

## First Azure Example

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

resource "azurerm_resource_group" "app" {
  name     = "rg-dev-app"
  location = "eastus"
}
```

## Terraform Is Not a Configuration Management Tool

Terraform is best at provisioning infrastructure.

It is not ideal for:

- installing packages inside servers repeatedly
- managing application runtime configuration on hosts
- patching OS packages

Tools like Ansible, cloud-init, Kubernetes, or image baking may fit those better.

## Common Mistakes

- storing state locally for team projects
- committing secrets or `.tfstate`
- running applies manually from laptops for production
- using one huge root module for everything
- overusing workspaces
- ignoring plan output
- using `count` where `for_each` gives safer identity

## Cross Questions

### Is Terraform idempotent?

Terraform aims to be idempotent. If config and real infrastructure already match state, a new plan should show no changes. Provider bugs, drift, timestamps, and external changes can break this expectation.

### Does Terraform replace all resources when config changes?

No. Some fields update in place. Some force replacement. The provider schema decides this behavior.

### Why is `terraform plan` important?

It shows intended changes before execution. In production, plan review is a safety gate.

### Can Terraform manage resources created manually?

Yes, but you need to import them into state and write matching configuration.

