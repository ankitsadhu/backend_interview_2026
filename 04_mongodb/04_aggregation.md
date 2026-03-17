# Aggregation Framework

## What is the Aggregation Pipeline?

The aggregation framework processes documents through a **pipeline of stages**. Each stage transforms the data as it passes through.

```
Input Documents
       │
       ▼
┌──────────────┐
│   $match      │  ← Filter documents (like WHERE)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   $group      │  ← Group by fields (like GROUP BY)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   $sort       │  ← Sort results (like ORDER BY)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   $project    │  ← Reshape documents (like SELECT)
└──────┬───────┘
       │
       ▼
  Output Documents
```

```javascript
// Basic syntax
db.collection.aggregate([
  { stage1 },
  { stage2 },
  { stage3 },
  // ...
])
```

---

## Pipeline Stages

### $match — Filter Documents

```javascript
// Equivalent to find() filter — use EARLY in pipeline for performance
db.orders.aggregate([
  { $match: { status: "completed", total: { $gt: 100 } } }
])

// Supports all query operators ($gt, $in, $regex, etc.)
// ⚡ When first in pipeline, can use indexes
```

---

### $project — Reshape Documents

```javascript
db.users.aggregate([
  {
    $project: {
      _id: 0,                              // Exclude _id
      fullName: { $concat: ["$first", " ", "$last"] },  // Computed field
      email: 1,                             // Include
      ageGroup: {
        $switch: {
          branches: [
            { case: { $lt: ["$age", 18] }, then: "minor" },
            { case: { $lt: ["$age", 65] }, then: "adult" }
          ],
          default: "senior"
        }
      },
      // Conditional fields
      isAdult: { $gte: ["$age", 18] },
      displayAge: { $cond: { if: { $gte: ["$age", 18] }, then: "$age", else: "N/A" } }
    }
  }
])
```

---

### $group — Group and Aggregate

```javascript
// Group by status, compute aggregates
db.orders.aggregate([
  {
    $group: {
      _id: "$status",                      // Group key (null = entire collection)
      totalRevenue: { $sum: "$total" },
      avgOrderValue: { $avg: "$total" },
      maxOrder: { $max: "$total" },
      minOrder: { $min: "$total" },
      orderCount: { $sum: 1 },             // Count documents
      customers: { $addToSet: "$customer_id" },  // Unique customers
      allItems: { $push: "$items" },       // Collect all items
      firstOrder: { $first: "$created_at" },
      lastOrder: { $last: "$created_at" }
    }
  }
])

// Group by multiple fields
db.orders.aggregate([
  {
    $group: {
      _id: { status: "$status", year: { $year: "$created_at" } },
      total: { $sum: "$amount" }
    }
  }
])

// Group entire collection (no grouping key)
db.orders.aggregate([
  { $group: { _id: null, total: { $sum: "$amount" }, count: { $sum: 1 } } }
])
```

#### Accumulator Operators Reference

| Operator | Description |
|----------|-------------|
| `$sum` | Sum of values or count (`$sum: 1`) |
| `$avg` | Average |
| `$min` / `$max` | Min / Max value |
| `$first` / `$last` | First / Last value (order-dependent) |
| `$push` | Push all values into array |
| `$addToSet` | Push unique values into array |
| `$stdDevPop` / `$stdDevSamp` | Standard deviation |
| `$mergeObjects` | Merge embedded documents |
| `$accumulator` | Custom JavaScript accumulator |
| `$count` | Count of documents (MongoDB 5.0+) |
| `$top` / `$bottom` | Top/bottom N values (MongoDB 5.2+) |
| `$topN` / `$bottomN` | Top/bottom N values by sort key |

---

### $sort and $limit

```javascript
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { total: -1 } },    // Sort descending
  { $limit: 10 }                // Top 10
])

// ⚡ $sort uses index if it's the first stage (or after $match that uses index)
// ⚠️ $sort has 100 MB memory limit — use { allowDiskUse: true } for large datasets
db.orders.aggregate(pipeline, { allowDiskUse: true })
```

---

### $skip and Pagination

```javascript
// Simple pagination (inefficient for large offsets)
db.products.aggregate([
  { $sort: { created_at: -1 } },
  { $skip: 20 },   // Skip first 20
  { $limit: 10 }   // Page size 10
])

// Better: range-based pagination
db.products.aggregate([
  { $match: { created_at: { $lt: lastSeenDate } } },
  { $sort: { created_at: -1 } },
  { $limit: 10 }
])
```

---

### $unwind — Flatten Arrays

```javascript
// Document: { name: "Alice", tags: ["dev", "admin", "team-lead"] }

db.users.aggregate([
  { $unwind: "$tags" }
])
// Output:
// { name: "Alice", tags: "dev" }
// { name: "Alice", tags: "admin" }
// { name: "Alice", tags: "team-lead" }

// Preserve documents with empty/missing arrays
{ $unwind: { path: "$tags", preserveNullAndEmptyArrays: true } }

// Include array index
{ $unwind: { path: "$tags", includeArrayIndex: "tagIndex" } }
// Output: { name: "Alice", tags: "dev", tagIndex: 0 }
```

**Common pattern — count tag frequency:**
```javascript
db.articles.aggregate([
  { $unwind: "$tags" },
  { $group: { _id: "$tags", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```

---

### $lookup — Join Collections

```javascript
// Basic lookup (left outer join)
db.orders.aggregate([
  {
    $lookup: {
      from: "users",              // Foreign collection
      localField: "customer_id",  // Field in orders
      foreignField: "_id",        // Field in users
      as: "customer"              // Output array field
    }
  },
  { $unwind: "$customer" }        // Flatten (1:1 relationship)
])

// Pipeline lookup (correlated subquery) — more powerful
db.orders.aggregate([
  {
    $lookup: {
      from: "reviews",
      let: { orderId: "$_id", orderDate: "$created_at" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$order_id", "$$orderId"] },
                { $gte: ["$created_at", "$$orderDate"] }
              ]
            }
          }
        },
        { $sort: { rating: -1 } },
        { $limit: 3 }
      ],
      as: "topReviews"
    }
  }
])

// Uncorrelated lookup (no let, no $expr)
db.orders.aggregate([
  {
    $lookup: {
      from: "holidays",
      pipeline: [
        { $match: { year: 2026 } }
      ],
      as: "holidays"
    }
  }
])
```

---

### $addFields / $set — Add Computed Fields

```javascript
// $addFields and $set are aliases (same behavior)
db.users.aggregate([
  {
    $addFields: {
      fullName: { $concat: ["$first", " ", "$last"] },
      isAdult: { $gte: ["$age", 18] },
      totalScore: { $sum: "$scores" }  // Sum array elements
    }
  }
])
```

---

### $facet — Multiple Pipelines in Parallel

Run multiple aggregation pipelines on the same input, return results in one document.

```javascript
db.products.aggregate([
  {
    $facet: {
      // Pipeline 1: Category counts
      categoryCounts: [
        { $group: { _id: "$category", count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ],
      // Pipeline 2: Price statistics
      priceStats: [
        {
          $group: {
            _id: null,
            avg: { $avg: "$price" },
            min: { $min: "$price" },
            max: { $max: "$price" }
          }
        }
      ],
      // Pipeline 3: Top 5 most expensive
      topProducts: [
        { $sort: { price: -1 } },
        { $limit: 5 },
        { $project: { name: 1, price: 1 } }
      ]
    }
  }
])

// Output:
{
  categoryCounts: [{ _id: "electronics", count: 150 }, ...],
  priceStats: [{ _id: null, avg: 45.99, min: 0.99, max: 999.99 }],
  topProducts: [{ name: "Premium Widget", price: 999.99 }, ...]
}
```

---

### $bucket / $bucketAuto — Histogram Grouping

```javascript
// Manual bucket boundaries
db.users.aggregate([
  {
    $bucket: {
      groupBy: "$age",
      boundaries: [0, 18, 30, 50, 70, 120],  // Bucket ranges
      default: "unknown",                       // For values outside boundaries
      output: {
        count: { $sum: 1 },
        avgIncome: { $avg: "$income" },
        names: { $push: "$name" }
      }
    }
  }
])
// Output: { _id: 18, count: 50, ... }, { _id: 30, count: 80, ... }

// Auto buckets — MongoDB determines boundaries
db.users.aggregate([
  { $bucketAuto: { groupBy: "$age", buckets: 5 } }
])
```

---

### $graphLookup — Recursive Lookup (Graph Traversal)

```javascript
// Employee hierarchy — find all reports (recursive)
// employees: { _id: "alice", name: "Alice", manager: null }
// employees: { _id: "bob", name: "Bob", manager: "alice" }
// employees: { _id: "charlie", name: "Charlie", manager: "bob" }

db.employees.aggregate([
  { $match: { _id: "alice" } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$_id",            // Start from this value
      connectFromField: "_id",       // Follow this field in results
      connectToField: "manager",     // Match against this field
      as: "allReports",
      maxDepth: 5,                   // Limit recursion depth
      depthField: "level"           // Add depth level to results
    }
  }
])
// Output: alice with allReports = [bob (level 0), charlie (level 1), ...]
```

---

### $merge / $out — Write Pipeline Results

```javascript
// $out — replaces entire collection
db.orders.aggregate([
  { $group: { _id: "$product_id", totalSold: { $sum: "$quantity" } } },
  { $out: "product_sales_summary" }  // Creates/replaces collection
])

// $merge — insert/update/replace (more flexible, since 4.2)
db.orders.aggregate([
  { $group: { _id: "$product_id", totalSold: { $sum: "$quantity" } } },
  {
    $merge: {
      into: "product_sales",
      on: "_id",                        // Match field
      whenMatched: "merge",             // "merge" | "replace" | "keepExisting" | "fail" | pipeline
      whenNotMatched: "insert"          // "insert" | "discard" | "fail"
    }
  }
])
```

---

## Expression Operators Reference

### String Operators

```javascript
{
  upper: { $toUpper: "$name" },
  lower: { $toLower: "$name" },
  concat: { $concat: ["$first", " ", "$last"] },
  substr: { $substr: ["$name", 0, 3] },    // First 3 chars
  length: { $strLenCP: "$name" },
  split: { $split: ["$email", "@"] },       // ["alice", "example.com"]
  regex: { $regexMatch: { input: "$email", regex: /\.com$/ } },
  trim: { $trim: { input: "$name" } },
  replace: { $replaceOne: { input: "$text", find: "foo", replacement: "bar" } }
}
```

### Date Operators

```javascript
{
  year: { $year: "$created_at" },
  month: { $month: "$created_at" },
  day: { $dayOfMonth: "$created_at" },
  hour: { $hour: "$created_at" },
  dayOfWeek: { $dayOfWeek: "$created_at" },  // 1=Sunday
  formatted: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
  diff: { $dateDiff: { startDate: "$start", endDate: "$end", unit: "day" } },
  add: { $dateAdd: { startDate: "$created_at", unit: "month", amount: 1 } }
}
```

### Conditional Operators

```javascript
{
  // if-then-else
  status: { $cond: { if: { $gte: ["$score", 60] }, then: "pass", else: "fail" } },

  // Short form
  status: { $cond: [{ $gte: ["$score", 60] }, "pass", "fail"] },

  // Switch
  tier: {
    $switch: {
      branches: [
        { case: { $gte: ["$spent", 10000] }, then: "platinum" },
        { case: { $gte: ["$spent", 5000] }, then: "gold" },
        { case: { $gte: ["$spent", 1000] }, then: "silver" }
      ],
      default: "bronze"
    }
  },

  // If null (provide default value)
  email: { $ifNull: ["$email", "no-email@default.com"] }
}
```

### Array Operators

```javascript
{
  size: { $size: "$tags" },
  first: { $first: "$items" },          // First element
  last: { $last: "$items" },            // Last element
  slice: { $slice: ["$items", 3] },     // First 3 elements
  reverse: { $reverseArray: "$items" },
  contains: { $in: ["admin", "$roles"] },
  filter: {
    $filter: {
      input: "$scores",
      as: "score",
      cond: { $gte: ["$$score", 60] }
    }
  },
  map: {
    $map: {
      input: "$items",
      as: "item",
      in: { $multiply: ["$$item.price", "$$item.quantity"] }
    }
  },
  reduce: {
    $reduce: {
      input: "$items",
      initialValue: 0,
      in: { $add: ["$$value", { $multiply: ["$$this.price", "$$this.qty"] }] }
    }
  },
  zip: { $zip: { inputs: ["$names", "$scores"] } },
  setUnion: { $setUnion: ["$tags1", "$tags2"] }
}
```

---

## Pipeline Optimization

### 1. $match Early

```javascript
// ✅ GOOD — filter first (uses index, reduces data)
[
  { $match: { status: "active" } },      // Filter 1M → 10K docs
  { $group: { _id: "$category", count: { $sum: 1 } } }
]

// ❌ BAD — group first, filter later
[
  { $group: { _id: "$category", count: { $sum: 1 } } },  // Groups ALL 1M docs
  { $match: { count: { $gt: 100 } } }
]
```

### 2. $project Early (Reduce Document Size)

```javascript
// ✅ Remove unused fields early to reduce memory usage
[
  { $match: { status: "active" } },
  { $project: { name: 1, category: 1, price: 1 } },  // Drop unused fields
  { $group: { _id: "$category", avgPrice: { $avg: "$price" } } }
]
```

### 3. MongoDB Auto-Optimizations

MongoDB automatically applies these optimizations:

| Optimization | Description |
|-------------|-------------|
| `$match` + `$match` | Coalesced into single `$match` |
| `$match` before `$project` | Moved before project when possible |
| `$sort` + `$limit` | Combined into top-k sort (memory efficient) |
| `$skip` + `$limit` | Reordered for efficiency |
| `$lookup` + immediate `$unwind` | Combined into more efficient operation |

### 4. Use `allowDiskUse` for Large Datasets

```javascript
// Default: each pipeline stage limited to 100 MB of RAM
// For large aggregations:
db.orders.aggregate(pipeline, { allowDiskUse: true })
```

---

## Real-World Aggregation Examples

### Monthly Revenue Report

```javascript
db.orders.aggregate([
  { $match: { status: "completed", created_at: { $gte: ISODate("2026-01-01") } } },
  {
    $group: {
      _id: {
        year: { $year: "$created_at" },
        month: { $month: "$created_at" }
      },
      revenue: { $sum: "$total" },
      orders: { $sum: 1 },
      avgOrderValue: { $avg: "$total" },
      uniqueCustomers: { $addToSet: "$customer_id" }
    }
  },
  {
    $addFields: {
      uniqueCustomerCount: { $size: "$uniqueCustomers" }
    }
  },
  { $project: { uniqueCustomers: 0 } },
  { $sort: { "_id.year": 1, "_id.month": 1 } }
])
```

### Product Recommendation (Customers Also Bought)

```javascript
db.orders.aggregate([
  // Find orders containing product X
  { $match: { "items.product_id": ObjectId("productX") } },
  // Get all items from those orders
  { $unwind: "$items" },
  // Exclude product X itself
  { $match: { "items.product_id": { $ne: ObjectId("productX") } } },
  // Count co-occurrences
  { $group: { _id: "$items.product_id", count: { $sum: 1 } } },
  // Sort by frequency
  { $sort: { count: -1 } },
  { $limit: 5 },
  // Get product details
  {
    $lookup: {
      from: "products",
      localField: "_id",
      foreignField: "_id",
      as: "product"
    }
  },
  { $unwind: "$product" },
  { $project: { name: "$product.name", price: "$product.price", coOccurrences: "$count" } }
])
```

---

## Interview Questions — Aggregation

### Q1: What's the difference between `$match` in aggregation and `find()`?

Functionally similar, but:
- `$match` is a **pipeline stage** — can be placed anywhere in the pipeline
- `find()` is a **standalone query method** — only filters, cannot transform
- `$match` at the **start** uses indexes (like find)
- `$match` after `$group` or `$project` **cannot use indexes** (operates on transformed data)

### Q2: How does `$unwind` affect performance?

`$unwind` can **multiply documents** (one per array element), which:
- Increases memory usage
- Increases downstream processing time
- Can blow past the 100 MB stage limit

**Optimization:** Filter with `$match` before `$unwind`, and use `$limit` after when possible.

### Q3: When would you use `$facet`?

When you need **multiple independent aggregations** on the same dataset in a single query:
- Dashboard pages (counts, averages, top-N, all in one call)
- Search results with faceted filters (price ranges, categories, ratings)
- Reports with multiple metrics

**Limitation:** Each sub-pipeline starts from the same input, and `$facet` output is a single document (must be < 16 MB).
