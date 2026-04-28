# Terraform Study Guide

> Beginner-to-advanced Terraform learning path for DevOps, backend, cloud, and MANG-level interviews.

Terraform interviews test whether you can safely manage infrastructure changes, reason about state, design reusable modules, debug drift, and build reliable CI/CD workflows.

## Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | IaC, providers, resources, state, plan/apply/destroy, dependency graph | Beginner |
| 02 | [HCL, Variables, Outputs, and Expressions](./02_hcl_variables_outputs_expressions.md) | HCL syntax, variables, locals, outputs, functions, validation, dynamic blocks | Beginner-Intermediate |
| 03 | [State, Backends, Import, and Drift](./03_state_backends_import_drift.md) | state internals, remote backend, locking, import, refresh, drift handling | Intermediate-Advanced |
| 04 | [Azure Provider Practical Examples](./04_azure_provider_practical_examples.md) | resource groups, VNet, NSG, App Service, Storage, Key Vault, AKS patterns | Intermediate |
| 05 | [Modules and Environments](./05_modules_and_environments.md) | reusable modules, module interface design, environments, workspaces, composition | Intermediate-Advanced |
| 06 | [CI/CD, Security, and Production Patterns](./06_cicd_security_production_patterns.md) | pipelines, approvals, policy, secrets, least privilege, testing, rollbacks | Advanced |
| 07 | [Advanced MANG Scenarios](./07_advanced_mang_scenarios.md) | refactoring state, zero-downtime changes, multi-team design, Azure landing zones, incident handling | Advanced |
| 08 | [Interview Questions](./08_interview_questions.md) | cross questions, scenario questions, rapid fire, system design prompts | All Levels |

## Study Path

1. Learn Terraform's execution model: config, state, providers, plan, apply.
2. Practice HCL with variables, locals, outputs, `for_each`, and validation.
3. Understand state deeply. This is where many interview questions become serious.
4. Build Azure resources with `azurerm`.
5. Learn module design and environment separation.
6. Add CI/CD, policy, security, and review workflows.
7. Finish with advanced scenarios and cross-question drills.

## Core Mental Model

```text
Terraform configuration
  |
  v
Terraform builds dependency graph
  |
  v
Provider reads real infrastructure
  |
  v
Terraform compares config + state + real world
  |
  v
Plan
  |
  v
Apply
  |
  v
Updated infrastructure + updated state
```

## Why This Matters for MANG Interviews

Many candidates can write a resource block.

Stronger candidates can explain:

- why Terraform state is sensitive and critical
- how to recover from drift or partial apply failure
- how to design modules without over-abstracting
- how to safely refactor resources without destroying production
- how to run Terraform in CI/CD with approvals and locking
- how to manage Azure identities, networking, and secrets safely
- how to design infrastructure ownership across many teams

