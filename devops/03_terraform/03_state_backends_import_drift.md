# State, Backends, Import, and Drift

## Why State Exists

Terraform state maps configuration to real infrastructure.

Example:

```text
azurerm_resource_group.app -> /subscriptions/.../resourceGroups/rg-prod-app
```

Without state, Terraform would not know which real resource belongs to which code block.

## What State Contains

State may contain:

- resource IDs
- resource attributes
- dependencies
- provider metadata
- sensitive values

Important:

```text
Terraform state must be protected like a secret.
```

## Local vs Remote State

### Local State

State stored on your machine.

Good for:

- quick experiments
- local learning

Bad for:

- team collaboration
- production
- CI/CD

### Remote State

State stored in a shared backend.

Benefits:

- collaboration
- locking
- central backup
- CI/CD compatibility

## Azure Remote Backend Example

Terraform backend using Azure Storage:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate-prod"
    storage_account_name = "sttfstateprod001"
    container_name       = "tfstate"
    key                  = "network/prod.tfstate"
  }
}
```

Bootstrap note:

```text
The storage account for remote state must exist before Terraform can use it as a backend. Teams often bootstrap it manually or with a separate bootstrap stack.
```

## State Locking

Locking prevents multiple applies from modifying state at the same time.

Why it matters:

```text
Two concurrent applies can corrupt state or create conflicting infrastructure changes.
```

Azure backend supports locking through blob leases.

## Drift

Drift means real infrastructure no longer matches Terraform configuration/state.

Causes:

- manual portal changes
- emergency hotfixes
- another IaC tool
- provider-side defaults changed
- failed partial apply

## Detecting Drift

```bash
terraform plan
terraform plan -refresh-only
```

Production pattern:

```text
Run scheduled drift detection and alert on unexpected changes.
```

## Handling Drift

Options:

1. Accept the manual change by updating code.
2. Revert the manual change through Terraform.
3. Import unmanaged resources into Terraform.
4. Ignore specific provider-managed fields only when justified.

Use `ignore_changes` sparingly:

```hcl
lifecycle {
  ignore_changes = [
    tags["last_modified_by"]
  ]
}
```

Interview warning:

```text
ignore_changes can hide real drift if overused.
```

## Import

Import brings an existing resource into Terraform state.

Modern import block:

```hcl
import {
  to = azurerm_resource_group.app
  id = "/subscriptions/<sub>/resourceGroups/rg-prod-app"
}
```

Then:

```bash
terraform plan
terraform apply
```

Older command style:

```bash
terraform import azurerm_resource_group.app /subscriptions/<sub>/resourceGroups/rg-prod-app
```

Import does not automatically write perfect configuration. You must write configuration that matches the existing resource.

## Moving State

When refactoring code, use moved blocks:

```hcl
moved {
  from = azurerm_resource_group.app
  to   = module.resource_group.azurerm_resource_group.this
}
```

This tells Terraform:

```text
same real resource, new address in code
```

Without this, Terraform may plan to destroy and recreate.

## State Commands

```bash
terraform state list
terraform state show azurerm_resource_group.app
terraform state mv old.address new.address
terraform state rm azurerm_resource_group.app
```

Use state commands carefully. They change Terraform's understanding of the world.

## Partial Apply Failure

Terraform may create some resources and fail on later ones.

Recovery steps:

1. Read the error.
2. Check what was actually created.
3. Run `terraform plan` again.
4. Fix config or permissions.
5. Apply again.

Do not blindly delete state.

## Cross Questions

### Why should state not be committed to Git?

It can contain secrets, is environment-specific, and creates collaboration conflicts.

### What happens if state is lost?

Terraform loses the mapping between code and real resources. You may need to recover from backend backup or re-import resources.

### Does `terraform refresh` change infrastructure?

Refresh updates Terraform's view of real infrastructure in state. It does not intentionally change infrastructure.

### How do you safely rename a resource block?

Use a `moved` block or `terraform state mv` so Terraform preserves the mapping instead of recreating the resource.

