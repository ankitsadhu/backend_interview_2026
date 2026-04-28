# Terraform Interview Questions

## Beginner

### 1. What is Terraform?

Terraform is an Infrastructure as Code tool that provisions and manages infrastructure from declarative configuration.

### 2. What is a provider?

A provider is a plugin that lets Terraform interact with an API such as Azure, AWS, Kubernetes, or GitHub.

### 3. What is a resource?

A resource is an infrastructure object managed by Terraform, such as an Azure resource group, VNet, storage account, or Kubernetes namespace.

### 4. What is Terraform state?

State is Terraform's mapping between configuration and real infrastructure.

### 5. What does `terraform plan` do?

It compares desired configuration, state, and real infrastructure, then shows the changes Terraform intends to make.

## Intermediate

### 6. Why use remote state?

Remote state enables collaboration, locking, backup, centralized access control, and CI/CD execution.

### 7. Why is state sensitive?

State can contain resource attributes, IDs, dependency information, and secret values.

### 8. What is state locking?

State locking prevents multiple Terraform runs from modifying the same state at the same time.

### 9. `count` vs `for_each`?

`count` is index-based. `for_each` is key-based and usually safer for resources with stable logical identity.

### 10. What is drift?

Drift means real infrastructure differs from Terraform configuration or state, often due to manual changes.

### 11. What is import?

Import maps an existing real resource into Terraform state so Terraform can manage it.

### 12. What are modules?

Modules are reusable Terraform configurations with inputs and outputs.

## Advanced

### 13. How do you rename a Terraform resource without recreating it?

Use a `moved` block or `terraform state mv` to preserve the state mapping between old and new resource addresses.

### 14. How do you recover from a partial apply failure?

Inspect the error, check what was created, run plan again, fix the cause, and apply again. Do not delete state blindly.

### 15. How do you manage secrets with Terraform?

Avoid storing secret values in Terraform where possible, use Key Vault or secret-management workflows, restrict state backend access, and use managed identities/OIDC for authentication.

### 16. How would you structure Terraform for dev/stage/prod?

Use shared modules and separate environment root modules with separate state files and backend keys. Keep production applies gated by CI/CD approval.

### 17. Why can provider upgrades be risky?

Provider upgrades may change schemas, defaults, validation, or replacement behavior. Pin versions and test upgrades in lower environments.

### 18. How do you avoid accidental deletion of critical resources?

Use plan review, `prevent_destroy`, RBAC, policy checks, separate state ownership, backups, and cautious lifecycle design.

### 19. What is `ignore_changes` and when is it dangerous?

`ignore_changes` tells Terraform to ignore drift for selected attributes. It is dangerous when it hides important configuration drift or security changes.

### 20. What is the difference between Terraform and Ansible?

Terraform is primarily for provisioning infrastructure declaratively. Ansible is commonly used for configuration management and procedural automation.

## Azure Questions

### 21. How do you configure Terraform remote state in Azure?

Use the `azurerm` backend with an Azure Storage Account container and unique state key. Enable access control, encryption, and blob versioning where appropriate.

### 22. How should Terraform authenticate to Azure in CI/CD?

Prefer OIDC federated identity or managed identity over long-lived client secrets. Use least-privilege RBAC.

### 23. How would you provision private access to Azure Storage?

Create the storage account, private endpoint, private DNS zone, VNet link, and firewall restrictions. Validate that the storage hostname resolves to a private IP from the workload network.

### 24. Why might Terraform fail creating an Azure subnet?

Possible CIDR overlap, insufficient permissions, subnet delegated incorrectly, provider validation, policy denial, or a dependency/order issue.

### 25. What is the difference between Azure Policy and Terraform validation?

Terraform validation checks code before apply. Azure Policy enforces rules at the Azure control plane and can deny or audit resources even outside Terraform.

## Scenario Questions

### 26. Terraform plan wants to replace a production database. What do you do?

Stop and identify the exact attribute causing replacement. Check provider upgrade, config change, drift, resource address changes, and lifecycle rules. Do not apply until impact and migration/rollback plan are clear.

### 27. Someone manually changed an NSG rule in Azure. What should happen?

Determine whether it was intentional. If intentional, update Terraform code. If accidental, let Terraform revert it. Add process/RBAC/drift detection to prevent recurrence.

### 28. Two engineers run apply at the same time. What prevents corruption?

Remote state locking. Without locking, concurrent applies can corrupt state or cause conflicting infrastructure changes.

### 29. You moved resources into a module and Terraform wants to recreate them. Why?

Resource addresses changed. Use `moved` blocks or `terraform state mv` to tell Terraform the new address maps to the same real resource.

### 30. How would you design Terraform for multiple app teams?

Use platform-owned modules, separate states by ownership boundary, least-privilege CI identities, plan review, policy checks, and clear outputs/contracts between platform and app teams.

### 31. How do you reduce Terraform blast radius?

Split state by domain/environment, avoid mega-root modules, use least privilege, review plans, protect critical resources, and gate production applies.

### 32. How do you detect and handle drift in production?

Run scheduled `terraform plan -refresh-only` or normal plans in CI, alert on unexpected drift, investigate cause, then either update code or revert the manual change.

## MANG Follow-Up Chains

### 33. Is Terraform declarative or imperative?

Terraform is declarative. You define desired state, and Terraform decides operations to reach that state.

Follow-up:

```text
Provisioners are imperative escape hatches and should be used sparingly.
```

### 34. Does Terraform know real infrastructure without state?

Not enough to safely manage it. Terraform can read APIs, but state maps resource addresses to real object IDs.

### 35. Why is one huge Terraform state risky?

It increases blast radius, lock contention, plan time, permission scope, and accidental coupling between unrelated systems.

### 36. Why are too many tiny states also risky?

They increase dependency complexity, output sharing, ordering problems, and operational overhead.

### 37. Should Terraform manage Kubernetes resources?

It can, but be careful. Terraform is good for cluster infrastructure and stable platform resources. Fast-changing app deployments may be better handled by Helm, GitOps, or app deployment pipelines.

### 38. Should Terraform run database migrations?

Usually no. Database migrations are application lifecycle changes and need app-aware rollback/forward recovery.

### 39. What is a saved plan and why use it?

A saved plan is generated with `terraform plan -out=tfplan` and later applied with `terraform apply tfplan`. It ensures the reviewed plan is what gets applied.

### 40. Can a saved plan become stale?

Yes. If real infrastructure or state changes after the plan, apply may fail or behave unexpectedly. Keep plan/apply close and use locking.

### 41. Why pin module versions?

To avoid unreviewed changes from a moving module source affecting production plans.

### 42. Why should provider versions be upgraded intentionally?

Provider upgrades can change behavior and replacement logic. Upgrade through lower environments with reviewed plans.

### 43. How do you enforce tagging standards?

Use module defaults, variable validation, policy-as-code checks, and Azure Policy to deny or audit missing tags.

### 44. How do you debug a Terraform dependency issue?

Check references, graph-inferred dependencies, provider behavior, missing `depends_on`, and whether eventual consistency in the cloud API is involved.

### 45. What is eventual consistency in Terraform context?

Cloud APIs may report a resource as created before all dependent operations can use it, causing transient failures. Providers often handle this, but not always.

### 46. How do you handle emergency manual changes?

Document the change, update Terraform code or import/state as needed, run a plan, and restore Terraform as the source of truth.

### 47. What should be reviewed in a Terraform plan?

Creates, updates, destroys, replacements, sensitive values, IAM/RBAC changes, network exposure, public access, SKU/cost changes, and unexpected tag or lifecycle changes.

### 48. What is the safest answer when plan shows `-/+` on production?

Stop and investigate because `-/+` means replacement. Understand downtime/data-loss impact before applying.

## Rapid Fire

### Should `.terraform/` be committed?

No.

### Should `.tfstate` be committed?

No.

### Should `.terraform.lock.hcl` be committed?

Yes, generally commit it to pin provider selections for reproducibility.

### What command formats Terraform files?

`terraform fmt`

### What command checks syntax and internal consistency?

`terraform validate`

### What command shows managed resources in state?

`terraform state list`

### What is the biggest Terraform interview mistake?

Talking only about writing resource blocks and ignoring state, drift, review workflow, and blast radius.

## Final Interview Tip

For senior Terraform answers, connect:

```text
desired state -> state mapping -> dependency graph -> plan safety -> CI/CD controls -> production blast radius
```

