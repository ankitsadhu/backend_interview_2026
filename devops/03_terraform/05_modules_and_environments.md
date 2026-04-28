# Modules and Environments

## What Is a Module?

A module is a reusable Terraform configuration package.

Every Terraform directory is a module.

The root module is the directory where you run Terraform.

Child modules are called with:

```hcl
module "network" {
  source = "../../modules/network"

  environment = "prod"
  location    = "eastus"
  vnet_cidr   = "10.50.0.0/16"
}
```

## Why Use Modules?

Modules help with:

- reuse
- consistency
- standardization
- team ownership
- reducing copy-paste

But modules can hurt when:

- they hide too much
- they expose too many variables
- they become universal mega-modules
- they make simple resources hard to understand

Strong interview answer:

```text
Good modules encode stable platform decisions while still exposing the few inputs application teams genuinely need.
```

## Module Interface Design

A module should have:

- clear inputs
- useful outputs
- reasonable defaults
- validation
- examples
- versioning

Bad variable:

```hcl
variable "all_settings" {
  type = any
}
```

Better:

```hcl
variable "subnets" {
  type = map(object({
    address_prefix = string
    nsg_rules      = optional(list(string), [])
  }))
}
```

## Environment Layouts

### Directory Per Environment

```text
envs/
  dev/
    main.tf
    backend.tf
    terraform.tfvars
  prod/
    main.tf
    backend.tf
    terraform.tfvars
modules/
  network/
  app_service/
  key_vault/
```

Pros:

- explicit separation
- separate state
- easier approvals

Cons:

- some duplication

### Workspaces

Workspaces allow multiple state files for one configuration.

```bash
terraform workspace new dev
terraform workspace select prod
```

Good for:

- small similar environments

Risky for:

- complex production differences
- accidental apply to wrong workspace

Interview answer:

```text
For serious production environments, I prefer separate directories and separate backend keys because the boundary is explicit and easier to review.
```

## Module Versioning

For shared modules, pin versions:

```hcl
module "network" {
  source  = "app.terraform.io/company/network/azurerm"
  version = "1.4.2"
}
```

Or Git tag:

```hcl
module "network" {
  source = "git::https://github.com/company/tf-modules.git//network?ref=v1.4.2"
}
```

Do not point production directly at a moving branch unless the workflow intentionally handles that risk.

## Composition Pattern

Root module wires together child modules.

```hcl
module "network" {
  source      = "../../modules/network"
  environment = var.environment
  location    = var.location
  vnet_cidr   = var.vnet_cidr
}

module "app" {
  source              = "../../modules/app_service"
  environment         = var.environment
  location            = var.location
  resource_group_name = module.network.resource_group_name
  subnet_id           = module.network.app_subnet_id
}
```

Root module owns orchestration. Child modules own a clear resource boundary.

## Environment Variables vs tfvars

Input options:

- `terraform.tfvars`
- `*.auto.tfvars`
- `-var`
- `-var-file`
- `TF_VAR_name`

Production pattern:

```text
Keep non-secret environment config in tfvars. Keep secrets in CI/CD secret store or Key Vault references.
```

## Cross Questions

### What makes a bad Terraform module?

Too many knobs, unclear ownership, hidden dependencies, weak outputs, no examples, no versioning, and abstractions that leak provider details badly.

### How do you avoid duplicating code across environments?

Use shared modules and thin environment root modules. Keep environment-specific values in tfvars or explicit inputs.

### When would you not create a module?

When the abstraction is used once, the resource is simple, or the module would hide important behavior without reducing real complexity.

