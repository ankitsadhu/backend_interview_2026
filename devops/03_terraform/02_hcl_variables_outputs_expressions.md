# HCL, Variables, Outputs, and Expressions

## HCL

Terraform uses HCL: HashiCorp Configuration Language.

HCL is declarative and structured.

Main block types:

- `terraform`
- `provider`
- `resource`
- `data`
- `variable`
- `locals`
- `output`
- `module`

## Variables

Variables define module inputs.

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment."

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment must be dev, stage, or prod."
  }
}
```

## Locals

Locals define reusable computed values.

```hcl
locals {
  name_prefix = "app-${var.environment}"

  common_tags = {
    environment = var.environment
    owner       = "platform"
    managed_by  = "terraform"
  }
}
```

Use locals for readability, not to hide complex magic.

## Outputs

Outputs expose values from a module.

```hcl
output "resource_group_name" {
  value = azurerm_resource_group.app.name
}
```

Sensitive output:

```hcl
output "key_vault_uri" {
  value     = azurerm_key_vault.app.vault_uri
  sensitive = true
}
```

Important:

```text
sensitive hides output in CLI display, but values can still exist in state.
```

## Types

Common variable types:

```hcl
string
number
bool
list(string)
set(string)
map(string)
object({
  name = string
  size = string
})
```

Example:

```hcl
variable "subnets" {
  type = map(object({
    address_prefix = string
    nsg_enabled    = bool
  }))
}
```

## `count` vs `for_each`

### `count`

```hcl
resource "azurerm_resource_group" "rg" {
  count    = 2
  name     = "rg-${count.index}"
  location = "eastus"
}
```

Problem:

```text
Identity is index-based. Removing item 0 can shift indexes and cause unwanted changes.
```

### `for_each`

```hcl
resource "azurerm_resource_group" "rg" {
  for_each = {
    dev  = "eastus"
    prod = "centralindia"
  }

  name     = "rg-${each.key}"
  location = each.value
}
```

Better because identity is key-based.

Strong interview answer:

```text
Use `for_each` when resources have stable logical names. Use `count` for truly identical resources or optional one-off resources.
```

## Dynamic Blocks

Dynamic blocks generate nested blocks.

Example:

```hcl
dynamic "security_rule" {
  for_each = var.security_rules

  content {
    name                       = security_rule.value.name
    priority                   = security_rule.value.priority
    direction                  = security_rule.value.direction
    access                     = security_rule.value.access
    protocol                   = security_rule.value.protocol
    source_port_range          = "*"
    destination_port_range     = security_rule.value.port
    source_address_prefix      = security_rule.value.source
    destination_address_prefix = "*"
  }
}
```

Use dynamic blocks carefully. They can make modules harder to read.

## Functions

Common functions:

- `lookup`
- `merge`
- `concat`
- `toset`
- `try`
- `coalesce`
- `jsonencode`
- `yamldecode`
- `cidrsubnet`

Example:

```hcl
locals {
  tags = merge(var.default_tags, {
    environment = var.environment
  })
}
```

## CIDR Example

```hcl
locals {
  vnet_cidr = "10.20.0.0/16"
  app_cidr  = cidrsubnet(local.vnet_cidr, 8, 1)
  db_cidr   = cidrsubnet(local.vnet_cidr, 8, 2)
}
```

This can derive `/24` subnets from a `/16`.

## File Organization

Common root module layout:

```text
main.tf
variables.tf
outputs.tf
providers.tf
versions.tf
terraform.tfvars
```

For larger systems:

```text
envs/
  dev/
  prod/
modules/
  network/
  app_service/
  key_vault/
```

## Cross Questions

### Are variables secret by default?

No. Marking a variable `sensitive = true` hides it from some CLI output, but it may still be stored in state if used in resource attributes.

### Why prefer `for_each` over `count`?

`for_each` gives stable identity based on keys. `count` is index-based and can cause unwanted replacements when list order changes.

### Should every repeated block become a dynamic block?

No. Dynamic blocks are useful but can reduce readability. Prefer clarity unless repetition is large or module interface requires it.

