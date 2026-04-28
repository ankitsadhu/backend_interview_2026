# Advanced MANG Terraform Scenarios

## 1. Safely Refactor a Production Resource Into a Module

Problem:

```text
You have azurerm_storage_account.app in root module.
You want to move it into module.storage without recreating it.
```

Bad outcome:

```text
Terraform plans to destroy old storage account and create a new one.
```

Safe approach:

```hcl
moved {
  from = azurerm_storage_account.app
  to   = module.storage.azurerm_storage_account.this
}
```

Then:

```bash
terraform plan
```

Expected plan should show address move, not destroy/create.

Interview answer:

```text
Refactoring Terraform code changes resource addresses. I would preserve state mapping using moved blocks or state mv, then review the plan carefully before apply.
```

## 2. Import a Manually Created Azure Resource

Scenario:

```text
A production resource group was created manually during an incident.
Now it must be managed by Terraform.
```

Steps:

1. Write matching Terraform configuration.
2. Add an import block or run `terraform import`.
3. Run plan.
4. Adjust config until plan does not try to replace the resource.
5. Apply to persist import state.

Import block:

```hcl
import {
  to = azurerm_resource_group.incident
  id = "/subscriptions/<sub>/resourceGroups/rg-prod-incident"
}
```

Key warning:

```text
Import maps the resource into state. It does not magically create perfect HCL.
```

## 3. Handle Drift Without Causing an Outage

Scenario:

```text
Someone changed an App Gateway rule manually in Azure Portal.
Terraform now wants to revert it.
```

Decision path:

```text
Was the manual change intentional emergency fix?
  |
  +-- yes -> update Terraform code to match, plan, review, apply
  |
  +-- no  -> use Terraform to revert drift
```

Do not blindly apply. Understand why drift happened.

Prevention:

- RBAC restricts manual changes
- change process
- drift detection
- Azure Activity Log alerts

## 4. Partial Apply Failure

Scenario:

```text
Terraform created VNet and subnets, then failed creating Private Endpoint.
```

Recovery:

1. Read exact error.
2. Check state and real Azure resources.
3. Fix cause: permissions, DNS zone, provider config, subnet policy.
4. Run `terraform plan` again.
5. Apply again.

Avoid:

```text
Deleting state file or manually deleting random resources.
```

## 5. Zero-Downtime Infrastructure Change

Scenario:

```text
Change App Service Plan SKU or move traffic to new App Service.
```

Safer design:

```text
create new infra
deploy app
run health checks
shift traffic at Front Door/App Gateway/DNS
monitor
decommission old infra later
```

Terraform concerns:

- `create_before_destroy`
- resource naming uniqueness
- dependencies
- traffic manager/load balancer config
- health probes
- rollback path

Interview nuance:

```text
Terraform can provision both old and new infrastructure, but traffic shifting and application readiness need explicit rollout design.
```

## 6. Multi-Team Terraform Ownership

Problem:

```text
Platform team owns network.
App teams own service infrastructure.
Security team owns policy and Key Vault access.
```

Better state split:

```text
network-prod.tfstate
security-prod.tfstate
app-a-prod.tfstate
app-b-prod.tfstate
```

Why:

- smaller blast radius
- clearer ownership
- fewer lock conflicts
- least-privilege CI credentials

Risk:

```text
Too many tiny states create dependency management overhead.
```

Use remote state outputs carefully. Prefer explicit published outputs or platform data sources where possible.

## 7. Azure Landing Zone With Terraform

Landing zone includes:

- management groups
- subscriptions
- policies
- RBAC
- hub-spoke network
- logging
- security baseline
- private DNS
- connectivity to on-prem

Interview framing:

```text
Landing zone Terraform should be owned by platform/security teams, heavily reviewed, and separated from application workload state.
```

## 8. Provider Upgrade Strategy

Provider upgrades can introduce:

- deprecated arguments
- behavior changes
- forced replacements
- schema changes
- new default values

Safe process:

```text
upgrade in dev -> run plan -> read changelog -> fix warnings -> test -> promote to prod
```

Pin versions:

```hcl
version = "~> 3.100"
```

Avoid unbounded:

```hcl
version = ">= 3.0"
```

## 9. Handling Secrets in Terraform

Problem:

```text
Terraform state may store secret values in plain or recoverable form.
```

Safer patterns:

- manage Key Vault container, not secret values
- inject secrets outside Terraform
- use managed identities instead of passwords
- use OIDC for CI/CD cloud auth
- restrict state backend access
- enable state backend versioning and audit logs

Interview answer:

```text
Marking a variable sensitive is not enough. If the value is stored in a resource attribute, it can still be in state.
```

## 10. Terraform vs ARM/Bicep on Azure

Terraform:

- multi-cloud
- broad ecosystem
- mature module workflows
- state managed by Terraform

Bicep/ARM:

- Azure-native
- no separate state file
- day-one support for Azure features
- integrates directly with ARM deployments

Strong answer:

```text
For Azure-only teams needing fastest feature support, Bicep can be attractive. For multi-cloud or standardized platform modules across tools, Terraform is often preferred.
```

## 11. Debugging a Plan That Wants to Replace Production

Checklist:

- which attribute forces replacement?
- did provider version change?
- did resource address change?
- did `count` index shift?
- did module source/version change?
- did remote object drift?
- is lifecycle rule missing?
- is name immutable?

Command:

```bash
terraform plan
terraform state show <address>
```

If address changed, use `moved` block or `terraform state mv`.

## 12. Final MANG Checklist

Before approving a Terraform design, cover:

- remote state and locking
- state access security
- environment separation
- module boundaries
- least-privilege CI identity
- plan review and apply gates
- drift detection
- policy checks
- provider version pinning
- import/refactor strategy
- protection for critical resources
- rollback or forward-recovery plan

