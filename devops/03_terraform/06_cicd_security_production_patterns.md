# CI/CD, Security, and Production Patterns

## Production Terraform Workflow

Recommended flow:

```text
developer opens PR
  |
  v
terraform fmt / validate
  |
  v
security and policy checks
  |
  v
terraform plan
  |
  v
human review of plan
  |
  v
approved apply from CI/CD
```

Avoid ad-hoc production applies from laptops.

## CI/CD Pipeline Steps

```bash
terraform fmt -check
terraform init
terraform validate
terraform plan -out=tfplan
terraform show -json tfplan
```

Apply should usually be gated:

```bash
terraform apply tfplan
```

Using the saved plan reduces the chance of applying something different from what was reviewed.

## Azure Authentication in CI/CD

Options:

- service principal with client secret
- service principal with certificate
- OIDC federated identity
- managed identity on self-hosted Azure runner

Better modern pattern:

```text
Use OIDC/federated credentials so CI does not store long-lived cloud secrets.
```

## Least Privilege

Terraform identity should have only the permissions required.

Examples:

- network pipeline can manage VNets, subnets, route tables, NSGs
- app pipeline can manage App Service and app-specific resources
- security-owned pipeline manages Key Vault policies and firewall rules

Avoid:

```text
Every pipeline gets Owner on the subscription.
```

## Policy Checks

Tools:

- Terraform `validate`
- `tflint`
- `tfsec`
- Checkov
- OPA/Conftest
- Sentinel in Terraform Cloud
- Azure Policy

Example policies:

- storage accounts must not allow public access
- Key Vault purge protection must be enabled
- NSG cannot expose SSH to internet
- resources must have required tags
- production resources must use approved regions

## Secrets and State Security

Protect state:

- remote backend
- encryption at rest
- restricted access
- audit logs
- state locking
- backup/versioning

Avoid putting secret values into resources when possible.

Bad:

```hcl
resource "azurerm_key_vault_secret" "db_password" {
  name         = "db-password"
  value        = var.db_password
  key_vault_id = azurerm_key_vault.app.id
}
```

This stores the value in state.

Better pattern:

```text
Provision Key Vault and access policy with Terraform. Inject secret value through a secret-management workflow outside Terraform.
```

## Testing Terraform

Levels:

- formatting: `terraform fmt`
- syntax: `terraform validate`
- linting: `tflint`
- security scan: Checkov/tfsec
- unit-like module tests: `terraform test`
- integration tests: deploy to test subscription
- policy checks: OPA/Sentinel/Azure Policy

## Rollbacks

Terraform rollback is not always easy.

Why:

- cloud operations may be destructive
- provider replacement behavior may lose data
- state changes after apply
- previous config may not reverse data migrations

Production approach:

- review plans carefully
- use deletion protection where possible
- backup state
- use lifecycle controls for critical resources
- design resource changes for forward recovery

## Lifecycle Controls

```hcl
lifecycle {
  prevent_destroy = true
}
```

Useful for critical resources:

- production databases
- state storage accounts
- key vaults
- core networks

But:

```text
prevent_destroy can block legitimate changes. It is a guardrail, not a substitute for review.
```

## `create_before_destroy`

```hcl
lifecycle {
  create_before_destroy = true
}
```

Useful for some zero-downtime replacements.

Risks:

- names may need to be unique
- extra capacity needed
- dependencies may still cause downtime

## Cross Questions

### Why run Terraform from CI/CD?

For consistency, auditability, controlled credentials, locking, review gates, and repeatable execution.

### Is `terraform plan` enough as a security review?

No. It shows changes, but policy and security tools are needed to detect risky patterns systematically.

### Can Terraform roll back automatically?

Not reliably. You can apply previous config, but infrastructure changes may not be perfectly reversible.

### Why save the plan artifact?

So the reviewed plan is the exact plan applied, reducing race conditions and surprises.

