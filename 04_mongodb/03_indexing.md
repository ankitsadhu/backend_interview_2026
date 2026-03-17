# Indexing in MongoDB

## Why Indexes Matter

Without indexes, MongoDB performs a **collection scan** (COLLSCAN) — reads every document to find matches. With indexes, MongoDB uses the index to narrow results dramatically.

```
WITHOUT INDEX:                        WITH INDEX:

Collection (1M docs)                  B-Tree Index
┌──────────────────┐                      ┌─────┐
│ doc 1   ← scan   │                      │  M  │
│ doc 2   ← scan   │                 ┌────┴─────┴────┐
│ doc 3   ← scan   │                 │  E  │    │  R  │
│ ...     ← scan   │              ┌──┴──┐  │ ┌──┴──┐
│ doc 1M  ← scan   │              │A  C │  │ │O  T │
└──────────────────┘              └─────┘  │ └─────┘
                                    ▼      ▼      ▼
Time: O(n)                       Matching documents
                                  Time: O(log n)
```

---

## Index Types

### 1. Single Field Index

```javascript
// Create ascending index on "email"
db.users.createIndex({ email: 1 })

// Descending index — matters for sort operations
db.users.createIndex({ age: -1 })

// Unique index — enforce uniqueness
db.users.createIndex({ email: 1 }, { unique: true })

// Unique + sparse — allow multiple null values
db.users.createIndex(
  { phone: 1 },
  { unique: true, sparse: true }  // documents without "phone" are excluded
)
```

**Query examples that use `{ email: 1 }`:**
```javascript
db.users.find({ email: "alice@example.com" })  // ✅ Exact match
db.users.find({ email: { $gt: "a" } })         // ✅ Range query
db.users.find().sort({ email: 1 })             // ✅ Sort
db.users.find().sort({ email: -1 })            // ✅ Reverse sort (index scanned backwards)
```

---

### 2. Compound Index

Index on **multiple fields**. Field order matters (follows the **ESR rule**).

```javascript
db.orders.createIndex({ status: 1, created_at: -1, total: 1 })
```

#### The ESR Rule (Equality, Sort, Range)

Order fields in a compound index for maximum efficiency:

```
1. Equality  → Fields tested with exact match ($eq, $in)
2. Sort      → Fields used in sort()
3. Range     → Fields tested with range ($gt, $lt, $gte, $lte)

Example query:
db.orders.find({ status: "shipped", total: { $gt: 100 } }).sort({ created_at: -1 })

Ideal index:    { status: 1,   created_at: -1,  total: 1 }
                  ↑ Equality       ↑ Sort         ↑ Range
```

#### Index Prefixes

A compound index supports queries on any **prefix** of its fields:

```javascript
// Index: { a: 1, b: 1, c: 1 }
// Supports:
db.col.find({ a: 1 })              // ✅ prefix {a}
db.col.find({ a: 1, b: 2 })        // ✅ prefix {a, b}
db.col.find({ a: 1, b: 2, c: 3 })  // ✅ full index

// Does NOT efficiently support:
db.col.find({ b: 2 })              // ❌ skips 'a'
db.col.find({ c: 3 })              // ❌ skips 'a' and 'b'
db.col.find({ b: 2, c: 3 })        // ❌ skips 'a'
```

---

### 3. Multikey Index

Automatically created when indexing a field that contains an **array**.

```javascript
db.products.createIndex({ tags: 1 })

// Works for:
db.products.find({ tags: "electronics" })                // ✅ Single value
db.products.find({ tags: { $all: ["electronics", "sale"] } })  // ✅ $all

// Limitation: compound multikey index can only have ONE array field
db.col.createIndex({ arrayField1: 1, arrayField2: 1 })  // ❌ Error!
db.col.createIndex({ arrayField: 1, scalarField: 1 })   // ✅ OK
```

---

### 4. Text Index

Full-text search on string content.

```javascript
// Create text index
db.articles.createIndex({ title: "text", content: "text" })

// With weights (boost certain fields)
db.articles.createIndex(
  { title: "text", content: "text", tags: "text" },
  { weights: { title: 10, tags: 5, content: 1 } }
)

// Search
db.articles.find({ $text: { $search: "mongodb indexing" } })

// With relevance score
db.articles.find(
  { $text: { $search: "mongodb indexing" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })

// Exact phrase
db.articles.find({ $text: { $search: "\"mongodb indexing\"" } })

// Exclude term
db.articles.find({ $text: { $search: "mongodb -tutorial" } })

// Limitation: Only ONE text index per collection
```

> **For production full-text search**, consider **Atlas Search** (Lucene-based) or **Elasticsearch** instead.

---

### 5. Geospatial Indexes

```javascript
// 2dsphere index (for Earth-like coordinates)
db.places.createIndex({ location: "2dsphere" })

// Store as GeoJSON
db.places.insertOne({
  name: "Central Park",
  location: {
    type: "Point",
    coordinates: [-73.9654, 40.7829]  // [longitude, latitude]
  }
})

// Find places near a point (within 5km)
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.9851, 40.7589] },
      $maxDistance: 5000  // meters
    }
  }
})

// Find places within a polygon
db.places.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [[
          [-74.0, 40.7], [-73.9, 40.7],
          [-73.9, 40.8], [-74.0, 40.8],
          [-74.0, 40.7]  // Must close the ring
        ]]
      }
    }
  }
})
```

---

### 6. Wildcard Index

Index on dynamic or unknown field names (MongoDB 4.2+).

```javascript
// Index ALL fields in a document
db.products.createIndex({ "$**": 1 })

// Index all fields under a specific path
db.products.createIndex({ "attributes.$**": 1 })

// Useful for:
// - Documents with unpredictable field names
// - IoT data with varying sensor fields
// - User-defined metadata

// ⚠️ Limitations:
// - Cannot support compound indexes
// - Cannot support sort efficiently
// - Higher storage and write overhead
```

---

### 7. Hashed Index

For **equality queries only** (not range). Used primarily for **hashed shard keys**.

```javascript
db.users.createIndex({ user_id: "hashed" })

// Supports:
db.users.find({ user_id: "abc123" })  // ✅ Equality

// Does NOT support:
db.users.find({ user_id: { $gt: "a" } })   // ❌ Range
db.users.find().sort({ user_id: 1 })       // ❌ Sort
```

---

### 8. Partial Index

Only index documents that match a filter expression.

```javascript
// Only index active users
db.users.createIndex(
  { email: 1 },
  { partialFilterExpression: { status: "active" } }
)

// Saves space — doesn't index inactive users
// ⚠️ Query must include the filter expression to use the index
db.users.find({ email: "alice@example.com", status: "active" })  // ✅ Uses index
db.users.find({ email: "alice@example.com" })                     // ❌ Cannot use index
```

---

### 9. Sparse Index

Only index documents where the indexed field **exists**.

```javascript
db.users.createIndex({ phone: 1 }, { sparse: true })

// Documents without "phone" field are NOT in the index
// Useful for optional fields with unique constraints
db.users.createIndex({ phone: 1 }, { sparse: true, unique: true })
// Allows multiple documents without "phone" field
```

> **Note:** Partial indexes are more flexible than sparse indexes — prefer partial indexes in new designs.

---

### 10. TTL Index (Time-to-Live)

Automatically delete documents after a specified time.

```javascript
// Delete sessions 30 minutes after createdAt
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 1800 }  // 30 * 60 = 1800 seconds
)

// Insert with date field
db.sessions.insertOne({
  user_id: "alice",
  data: { cart: [...] },
  createdAt: new Date()  // Must be a Date type!
})

// Change expiration time
db.runCommand({
  collMod: "sessions",
  index: { keyPattern: { createdAt: 1 }, expireAfterSeconds: 3600 }
})
```

**How it works:** A background thread runs every 60 seconds and removes expired documents.

> **⚠️ Limitations:**
> - Only works on single date fields (not compound indexes)
> - Not precise — deletions can be delayed by up to 60 seconds
> - Cannot be a compound index or multikey index

---

## Covered Queries

A **covered query** is satisfied entirely by the index — MongoDB doesn't need to read documents at all.

```javascript
db.users.createIndex({ email: 1, name: 1 })

// Covered query — only request indexed fields, exclude _id
db.users.find(
  { email: "alice@example.com" },
  { email: 1, name: 1, _id: 0 }
)
// explain() will show: "totalDocsExamined": 0
```

**Requirements for covered query:**
1. All query filter fields are in the index
2. All returned fields are in the index
3. No fields in the query are arrays or embedded documents
4. `_id` must be explicitly excluded (unless it's part of the index)

---

## Using `explain()` to Analyze Queries

```javascript
// Three verbosity levels
db.users.find({ age: { $gt: 25 } }).explain("queryPlanner")       // Default — shows plan
db.users.find({ age: { $gt: 25 } }).explain("executionStats")     // Shows actual execution
db.users.find({ age: { $gt: 25 } }).explain("allPlansExecution")  // All candidate plans

// Key fields in executionStats:
{
  "executionStats": {
    "nReturned": 500,          // Documents returned
    "executionTimeMillis": 15, // Time taken
    "totalKeysExamined": 500,  // Index entries scanned
    "totalDocsExamined": 500,  // Documents read from disk
    "executionStages": {
      "stage": "IXSCAN",      // Using index scan (good!)
      // vs "COLLSCAN"        // Collection scan (bad!)
      "indexName": "age_1",
      "direction": "forward"
    }
  }
}
```

### What to Look For

| Metric | Good | Bad |
|--------|------|-----|
| `stage` | `IXSCAN`, `COVERED` | `COLLSCAN` |
| `totalKeysExamined` / `nReturned` | Close to 1:1 | Much higher than nReturned |
| `totalDocsExamined` / `nReturned` | Close to 1:1 (or 0 for covered) | Much higher than nReturned |
| `executionTimeMillis` | Low | High (> 100ms for simple queries) |
| `needYield` | Low | High (memory pressure) |

### Reading the Query Plan

```javascript
// Common stage names
"COLLSCAN"    // Collection scan — NO index used (full scan)
"IXSCAN"      // Index scan — using an index
"FETCH"       // Retrieving documents (after index scan)
"SORT"        // In-memory sort (bad if large dataset)
"SORT_KEY_GENERATOR" // Preparing to sort
"PROJECTION"  // Applying field projection
"LIMIT"       // Limiting results
"SKIP"        // Skipping results
"SHARD_MERGE" // Merging from multiple shards

// Ideal: IXSCAN → FETCH → (no SORT stage)
// Bad:    COLLSCAN → SORT
```

---

## Index Management

```javascript
// List all indexes
db.users.getIndexes()

// Drop index
db.users.dropIndex("email_1")        // by name
db.users.dropIndex({ email: 1 })     // by specification

// Drop all indexes (except _id)
db.users.dropIndexes()

// Create index in background (non-blocking) — default in 4.2+
db.users.createIndex({ field: 1 })
// Pre-4.2: db.users.createIndex({ field: 1 }, { background: true })

// Index name
db.users.createIndex({ email: 1 }, { name: "idx_users_email" })

// Check index size
db.users.stats().indexSizes
db.users.totalIndexSize()

// Hide index (test impact without dropping)
db.users.hideIndex("email_1")
db.users.unhideIndex("email_1")
```

---

## Index Strategy Best Practices

### 1. Use the ESR Rule

```
Equality → Sort → Range

// Query: find active users, sort by age, filter score > 80
db.users.find({ status: "active", score: { $gt: 80 } }).sort({ age: 1 })

// Best index:
db.users.createIndex({ status: 1, age: 1, score: 1 })
//                      ↑ Equality   ↑ Sort   ↑ Range
```

### 2. Create Indexes for Your Queries, Not Your Collections

```javascript
// Don't index every field — index based on actual query patterns
// Bad: create index on every field "just in case"
// Good: analyze slow query log, create targeted indexes
```

### 3. Limit Number of Indexes

```
Each index:
- Uses RAM (must fit in memory for performance)
- Slows down writes (every insert/update must update all indexes)
- Increases storage

Rule of thumb: ≤ 5–10 indexes per collection for write-heavy workloads
```

### 4. Compound Indexes Replace Multiple Single-Field Indexes

```javascript
// If you need:
db.col.find({ a: 1 })           // Query on a
db.col.find({ a: 1, b: 2 })     // Query on a + b
db.col.find({ a: 1 }).sort({ b: 1 })

// Single compound index handles all three:
db.col.createIndex({ a: 1, b: 1 })
// No need for separate { a: 1 } — it's a prefix!
```

### 5. Monitor Index Usage

```javascript
// Check which indexes are actually used
db.users.aggregate([{ $indexStats: {} }])

// Result shows:
{
  "name": "email_1",
  "accesses": {
    "ops": 12345,              // Number of times used
    "since": ISODate("2026-01-01")
  }
}

// Drop unused indexes to save resources
```

---

## Interview Questions — Indexing

### Q1: What is the difference between a single-field and compound index?

| Aspect | Single-Field | Compound |
|--------|-------------|----------|
| Fields | 1 field | 2+ fields |
| Prefix support | N/A | Yes (left-to-right prefixes) |
| Sort support | Both directions | Depends on index key direction |
| Use case | Simple queries | Multi-field queries, complex sorting |

---

### Q2: Why does field order matter in compound indexes?

Because MongoDB uses **index prefixes**. An index `{ a: 1, b: 1, c: 1 }` can satisfy queries on `{a}`, `{a, b}`, or `{a, b, c}` — but NOT `{b}`, `{c}`, or `{b, c}`.

Also, the order determines sort optimization:
- `{ a: 1, b: -1 }` supports `.sort({ a: 1, b: -1 })` and `.sort({ a: -1, b: 1 })` (reversed)
- But NOT `.sort({ a: 1, b: 1 })` (mixed directions can't reverse)

---

### Q3: How would you debug a slow query?

1. Use `.explain("executionStats")` to see the plan
2. Look for `COLLSCAN` (full scan) — add an index
3. Check `totalKeysExamined` vs `nReturned` ratio (high = inefficient)
4. Check for in-memory `SORT` stage — add sort field to index
5. Check if index is **in RAM** (`db.col.stats().indexSizes`)
6. Use `db.setProfilingLevel(1, { slowms: 100 })` to log slow queries
7. Check `$indexStats` for index usage patterns

---

### Q4: What is an index intersection and why is it rarely better than compound indexes?

**Index intersection** is when MongoDB combines results from multiple single-field indexes:

```javascript
// With indexes: { a: 1 } and { b: 1 }
db.col.find({ a: 5, b: 10 })
// MongoDB MAY intersect the two indexes

// But a compound index { a: 1, b: 1 } is almost always faster:
// - Single index scan vs two + intersection
// - Less memory usage
// - Predictable performance
```

MongoDB prefers compound indexes; intersection is a fallback.
