# Azure Study Guide

> Comprehensive Azure learning path for backend engineers, organized for MANG-level interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | Azure architecture, regions, resource groups, ARM, subscriptions, management hierarchy, Azure CLI/Portal | 🟢 Beginner |
| 02 | [Compute Services](./02_compute.md) | VMs, App Service, AKS, Container Instances, Azure Functions, VM Scale Sets, comparison matrix | 🟢🟡 Beginner-Intermediate |
| 03 | [Storage & Databases](./03_storage_and_databases.md) | Blob Storage, Table Storage, Queue Storage, Cosmos DB vs SQL, storage tiers, redundancy | 🟡 Intermediate |
| 04 | [Networking](./04_networking.md) | VNet, subnets, NSG, Load Balancer, Application Gateway, Azure Front Door, Private Endpoints, DNS | 🟡 Intermediate |
| 05 | [Messaging & Events](./05_messaging_and_events.md) | Service Bus, Event Hubs, Event Grid, Storage Queues, Kafka on Azure, comparison and patterns | 🟡🔴 Intermediate-Advanced |
| 06 | [Identity & Security](./06_identity_and_security.md) | Azure AD (Entra ID), RBAC, Managed Identity, Key Vault, OAuth flows, Zero Trust | 🟡🔴 Intermediate-Advanced |
| 07 | [Serverless & Integration](./07_serverless_and_integration.md) | Azure Functions deep dive, Durable Functions, Logic Apps, API Management, Function triggers | 🔴 Advanced |
| 08 | [Monitoring & DevOps](./08_monitoring_and_devops.md) | Application Insights, Azure Monitor, Log Analytics, Azure DevOps, ARM templates, Bicep, Terraform | 🔴 Advanced |
| 09 | [Architecture Patterns](./09_architecture_patterns.md) | Microservices on Azure, CQRS, event sourcing, saga pattern, circuit breaker, Azure Well-Architected | 🔴 Advanced |
| 10 | [Interview Questions](./10_interview_questions.md) | 30+ categorized questions (beginner → advanced) + scenario-based + rapid-fire | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_fundamentals.md` — understand Azure hierarchy, ARM, resource groups
2. Read `02_compute.md` — master compute service selection
3. Read `03_storage_and_databases.md` — storage tiers, Cosmos DB vs SQL

### Week 2: Networking & Messaging
4. Read `04_networking.md` — VNet design, load balancing, private endpoints
5. Read `05_messaging_and_events.md` — Service Bus vs Event Hubs decision tree
6. Read `06_identity_and_security.md` — Managed Identity, RBAC, Key Vault

### Week 3: Advanced & Architecture
7. Read `07_serverless_and_integration.md` — Functions, Durable Functions, APIM
8. Read `08_monitoring_and_devops.md` — observability, IaC
9. Read `09_architecture_patterns.md` — production-grade design patterns

### Final Review
10. Go through `10_interview_questions.md` — test yourself across all levels
