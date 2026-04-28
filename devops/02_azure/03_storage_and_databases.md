# Azure Storage & Databases

## Storage Decision Tree

```
Need to store data on Azure?
    │
    ├── Unstructured (files, images, videos, backups)?
    │   └── Blob Storage
    │
    ├── Structured / relational?
    │   ├── Fully managed SQL Server → Azure SQL Database
    │   ├── Open-source (PostgreSQL/MySQL) → Azure Database for PostgreSQL/MySQL
    │   └── Massive scale, no limits → Azure SQL Hyperscale
    │
    ├── NoSQL / globally distributed?
    │   └── Cosmos DB (multi-model: Document, Graph, Key-Value, Column, Table)
    │
    ├── Simple key-value (no query need)?
    │   └── Table Storage (cheap) or Cosmos DB Table API
    │
    ├── File shares (SMB/NFS)?
    │   └── Azure Files
    │
    └── Message queue?
        └── Queue Storage (simple) or Service Bus (enterprise)
```

---

## 1. Azure Blob Storage

Object storage for unstructured data — the "S3 of Azure."

### Container Hierarchy

```
Storage Account
    └── Container (like an S3 bucket)
        ├── Blob (Block Blob — files up to 190.7 TB)
        ├── Blob (Append Blob — log files, append-only)
        └── Blob (Page Blob — VHDs, random read/write)
```

### Access Tiers

| Tier | Cost (Storage) | Cost (Access) | Use Case | Min Retention |
|------|---------------|---------------|----------|---------------|
| **Hot** | Highest | Lowest | Frequently accessed | None |
| **Cool** | Lower | Higher | Infrequent (30+ days) | 30 days |
| **Cold** | Even lower | Even higher | Rarely accessed (90+ days) | 90 days |
| **Archive** | Lowest | Highest + rehydration time | Compliance, long-term | 180 days |

> **Archive rehydration** takes **hours** (Standard: up to 15 hours, High Priority: < 1 hour).

### Redundancy Options

| Option | Copies | Durability | Scope |
|--------|--------|-----------|-------|
| **LRS** (Locally Redundant) | 3 | 11 nines | Single datacenter |
| **ZRS** (Zone Redundant) | 3 | 12 nines | 3 availability zones |
| **GRS** (Geo Redundant) | 6 | 16 nines | Primary + paired region |
| **GZRS** (Geo-Zone Redundant) | 6 | 16 nines | 3 zones + paired region |
| **RA-GRS** (Read-Access GRS) | 6 | 16 nines | GRS + read from secondary |
| **RA-GZRS** | 6 | 16 nines | GZRS + read from secondary |

```bash
# Create storage account
az storage account create \
  --name mystorageacct \
  --resource-group myapp-rg \
  --location eastus \
  --sku Standard_ZRS \
  --kind StorageV2 \
  --access-tier Hot

# Create container
az storage container create \
  --name mycontainer \
  --account-name mystorageacct \
  --public-access off

# Upload blob
az storage blob upload \
  --account-name mystorageacct \
  --container-name mycontainer \
  --name myfile.pdf \
  --file ./myfile.pdf

# Generate SAS token (time-limited access)
az storage blob generate-sas \
  --account-name mystorageacct \
  --container-name mycontainer \
  --name myfile.pdf \
  --permissions r \
  --expiry 2026-03-18T00:00:00Z \
  --output tsv
```

### Lifecycle Management

Automatically transition blobs between tiers:

```json
{
  "rules": [
    {
      "name": "move-to-cool",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": { "daysAfterModificationGreaterThan": 30 },
            "tierToArchive": { "daysAfterModificationGreaterThan": 90 },
            "delete": { "daysAfterModificationGreaterThan": 365 }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["logs/"]
        }
      }
    }
  ]
}
```

---

## 2. Azure SQL Database

Fully managed SQL Server — handles patching, backups, HA, scaling.

### Service Tiers

| Tier | Use Case | Compute | Storage |
|------|----------|---------|---------|
| **Basic** | Dev/test, light workloads | 5 DTUs | 2 GB |
| **Standard** | General production | 10-3000 DTUs | 1 TB |
| **Premium** | IO-intensive, OLTP | 125-4000 DTUs | 4 TB |
| **General Purpose** (vCore) | Most workloads | 2-80 vCores | 4 TB |
| **Business Critical** (vCore) | Low latency, HA | 2-128 vCores | 4 TB, local SSD |
| **Hyperscale** | Massive DBs, rapid scale | 2-128 vCores | Up to 100 TB |

### DTU vs vCore Pricing

| Model | How It Works | Best For |
|-------|-------------|----------|
| **DTU** | Bundled CPU + Memory + IO | Simple, predictable workloads |
| **vCore** | Choose CPU, memory, storage independently | Granular control, Azure Hybrid Benefit |

```bash
# Create SQL Server
az sql server create \
  --name myserver \
  --resource-group myapp-rg \
  --location eastus \
  --admin-user sqladmin \
  --admin-password 'P@ssw0rd!'

# Create Database
az sql db create \
  --resource-group myapp-rg \
  --server myserver \
  --name mydb \
  --service-objective S0

# Configure firewall
az sql server firewall-rule create \
  --resource-group myapp-rg \
  --server myserver \
  --name AllowMyIP \
  --start-ip-address 203.0.113.0 \
  --end-ip-address 203.0.113.0

# Enable Azure services access
az sql server firewall-rule create \
  --resource-group myapp-rg \
  --server myserver \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

---

## 3. Azure Cosmos DB

Globally distributed, multi-model NoSQL database with **single-digit millisecond latency** at any scale.

### Cosmos DB APIs

| API | Data Model | When to Use |
|-----|-----------|-------------|
| **NoSQL** (native) | JSON documents | New apps, flexible schema, recommended default |
| **MongoDB** | BSON documents | Migrating from MongoDB |
| **PostgreSQL** | Relational (Citus) | Distributed PostgreSQL |
| **Cassandra** | Wide-column | Migrating from Cassandra |
| **Table** | Key-value | Migrating from Table Storage |
| **Gremlin** | Graph | Social networks, recommendations |

### Request Units (RUs) — Cosmos Pricing Model

Everything in Cosmos DB is measured in **Request Units (RUs)**:

| Operation | Cost |
|-----------|------|
| Point read (1 KB doc by ID) | 1 RU |
| Simple query | 3-10 RUs |
| Insert (1 KB doc) | 5 RUs |
| Complex query (cross-partition) | 10-100+ RUs |

> **Think of RUs as a currency** — you provision a budget (e.g., 400 RU/s) and every operation spends from that budget.

### Consistency Levels (Unique to Cosmos DB)

```
Strong ◄─── Bounded Staleness ◄─── Session ◄─── Consistent Prefix ◄─── Eventual

Strongest                                                              Weakest
(highest latency,                                                      (lowest latency,
 highest cost)                                                          lowest cost)
```

| Level | Guarantee | Use Case |
|-------|-----------|----------|
| **Strong** | Linearizable reads, always latest | Financial transactions |
| **Bounded Staleness** | Reads lag by at most K versions or T time | Leaderboards with slight delay |
| **Session** | Within a session, reads see own writes | **Default, recommended for most apps** |
| **Consistent Prefix** | Reads never see out-of-order writes | Social feeds |
| **Eventual** | No ordering guarantees | Likes counter, analytics |

```bash
# Create Cosmos DB account
az cosmosdb create \
  --name mycosmosdb \
  --resource-group myapp-rg \
  --kind GlobalDocumentDB \
  --default-consistency-level Session \
  --locations regionName=eastus failoverPriority=0 \
  --locations regionName=westus failoverPriority=1

# Create database
az cosmosdb sql database create \
  --account-name mycosmosdb \
  --resource-group myapp-rg \
  --name mydb

# Create container with partition key
az cosmosdb sql container create \
  --account-name mycosmosdb \
  --resource-group myapp-rg \
  --database-name mydb \
  --name users \
  --partition-key-path /userId \
  --throughput 400
```

### Partition Key — Critical Design Decision

| Good Partition Key | Bad Partition Key |
|-------------------|-------------------|
| High cardinality (many distinct values) | Low cardinality (few values like `status`) |
| Evenly distributes data | Creates hot partitions |
| Included in most queries | Rarely in queries (causes cross-partition) |
| Examples: `userId`, `tenantId`, `deviceId` | Examples: `country`, `isActive`, `date` |

> **Interview Tip:** Choosing the wrong partition key is the #1 mistake in Cosmos DB. It cannot be changed after container creation.

---

## 4. Azure Database for PostgreSQL

Fully managed PostgreSQL with built-in HA, backups, and security.

### Deployment Options

| Option | Use Case | Scale |
|--------|----------|-------|
| **Single Server** (retiring) | Simple workloads | Up to 64 vCores |
| **Flexible Server** (recommended) | Production workloads | 1-96 vCores, zone-redundant HA |
| **Cosmos DB PostgreSQL** (Citus) | Hyperscale, distributed queries | Horizontally scalable |

```bash
az postgres flexible-server create \
  --resource-group myapp-rg \
  --name mypgsql \
  --location eastus \
  --admin-user pgadmin \
  --admin-password 'P@ssw0rd!' \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose \
  --storage-size 128 \
  --version 16 \
  --high-availability ZoneRedundant
```

---

## SQL vs Cosmos DB Decision Matrix

| Factor | Azure SQL | Cosmos DB |
|--------|-----------|-----------|
| Data Model | Relational (tables, joins) | NoSQL (documents, key-value, graph) |
| Schema | Fixed schema | Schema-less / flexible |
| Scaling | Vertical (scale up) | Horizontal (partition + replicate) |
| Global Distribution | Geo-replication (async) | Multi-region writes (built-in) |
| Consistency | Strong (ACID) | 5 levels (Strong → Eventual) |
| Latency | <10ms (single region) | <10ms (any region) |
| Pricing | DTU or vCore | Request Units (RU/s) |
| Best For | Complex queries, joins, transactions | High-scale, low-latency, global apps |

---

## Common Interview Questions — Storage & Databases

### Q1: When would you choose Cosmos DB over Azure SQL?

Choose **Cosmos DB** when you need:
- **Global distribution** with multi-region writes (< 10ms anywhere)
- **Massive scale** without worrying about sharding
- **Flexible schema** (JSON documents that evolve without migrations)
- **Guaranteed low latency** at any scale

Choose **Azure SQL** when:
- Complex **joins and transactions** (ACID)
- Existing relational schema or SQL expertise
- BI/reporting with complex queries
- Single-region application

### Q2: Explain Cosmos DB consistency levels. When is Session consistency enough?

Session consistency guarantees **read-your-own-writes** within a session. It's the **default and recommended level** because:
- A user will always see their own updates immediately
- Other users may see slightly stale data (acceptable for most apps)
- Much lower RU cost and latency than Strong consistency
- Perfect for user-facing apps (profiles, feeds, carts)

### Q3: What's the difference between Blob Storage access tiers?

Hot = frequently accessed (low access cost, high storage cost). Cool = infrequent access, 30-day minimum. Cold = rare access, 90-day minimum. Archive = compliance data, hours to rehydrate, 180-day minimum. Use **lifecycle management** to auto-tier blobs based on age.
