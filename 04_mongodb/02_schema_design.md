# Schema Design in MongoDB

## The Core Decision: Embed vs Reference

The most important design decision in MongoDB is whether to **embed** related data within a document or **reference** it in a separate collection.

```
EMBEDDING:                              REFERENCING:
┌─────────────────────┐                 ┌──────────────────┐     ┌──────────────────┐
│ User                │                 │ User             │     │ Address          │
│ ┌─────────────────┐ │                 │                  │     │                  │
│ │ name: "Alice"   │ │                 │ _id: ObjectId()  │──┐  │ _id: ObjectId()  │
│ │ address: {      │ │                 │ name: "Alice"    │  │  │ user_id: ref     │
│ │   city: "NYC"   │ │                 │                  │  └─▶│ city: "NYC"      │
│ │   zip: "10001"  │ │                 │                  │     │ zip: "10001"     │
│ │ }               │ │                 │                  │     │                  │
│ └─────────────────┘ │                 └──────────────────┘     └──────────────────┘
└─────────────────────┘                         Separate collections
    Single document
```

### Decision Matrix

| Factor | Embed | Reference |
|--------|-------|-----------|
| **Read pattern** | Data always read together | Data read independently |
| **Data size** | Sub-document is small (< few KB) | Sub-document is large or grows unboundedly |
| **Write pattern** | Data updated together | Data updated independently |
| **Cardinality** | One-to-few, One-to-many (bounded) | One-to-many (unbounded), Many-to-many |
| **Data duplication** | Acceptable or beneficial | Must avoid (data integrity critical) |
| **Document size** | Within 16 MB limit | Would exceed 16 MB |
| **Atomicity** | Need atomic updates across related data | Eventual consistency acceptable |

> **Rule of thumb:** *Embed when the relationship is "contains" — Reference when the relationship is "refers to"*

---

## Relationship Patterns

### One-to-One: Embed

```javascript
// ✅ GOOD — embed address in user
{
  _id: ObjectId("..."),
  name: "Alice",
  email: "alice@example.com",
  address: {
    street: "123 Main St",
    city: "NYC",
    state: "NY",
    zip: "10001"
  }
}

// ❌ AVOID — separate collection for 1:1 (unnecessary overhead)
// users: { _id: 1, name: "Alice", address_id: ObjectId("...") }
// addresses: { _id: ObjectId("..."), street: "123 Main St", ... }
```

**When to reference 1:1:** If the embedded document is large and rarely accessed (e.g., user profile + medical_history).

---

### One-to-Few (< ~20): Embed as Array

```javascript
// User with phone numbers (1-to-few)
{
  _id: ObjectId("..."),
  name: "Alice",
  phones: [
    { type: "home", number: "555-1234" },
    { type: "work", number: "555-5678" },
    { type: "mobile", number: "555-9012" }
  ]
}
```

---

### One-to-Many (Bounded): Embed or Hybrid

```javascript
// Product with reviews (bounded — say, up to 100)
// Option A: Embed (if reviews are small and always shown with product)
{
  _id: ObjectId("..."),
  name: "Widget Pro",
  price: 49.99,
  reviews: [
    { user: "alice", rating: 5, text: "Great!", date: ISODate("2026-01-15") },
    { user: "bob", rating: 4, text: "Good value", date: ISODate("2026-02-01") }
  ]
}

// Option B: Hybrid — embed recent, reference all
{
  _id: ObjectId("..."),
  name: "Widget Pro",
  price: 49.99,
  recent_reviews: [  // Last 5 reviews (embedded for fast reads)
    { user: "alice", rating: 5, text: "Great!", date: ISODate("2026-01-15") }
  ],
  total_reviews: 47,
  avg_rating: 4.3
}
// Full reviews in separate collection:
// reviews: { _id: ..., product_id: ObjectId("..."), user: "bob", rating: 4, ... }
```

---

### One-to-Many (Unbounded): Reference

```javascript
// Blog post with comments (could be thousands)
// posts collection
{
  _id: ObjectId("post1"),
  title: "MongoDB Schema Design",
  content: "...",
  author: "alice",
  comment_count: 1523
}

// comments collection — reference parent
{
  _id: ObjectId("..."),
  post_id: ObjectId("post1"),  // foreign key reference
  user: "bob",
  text: "Great article!",
  created_at: ISODate("2026-03-17")
}

// Query: get comments for a post
db.comments.find({ post_id: ObjectId("post1") }).sort({ created_at: -1 }).limit(20)
```

---

### Many-to-Many: Array of References

```javascript
// Students ←→ Courses (many-to-many)
// Option A: Array of references in one side
// students collection
{
  _id: ObjectId("student1"),
  name: "Alice",
  course_ids: [ObjectId("course1"), ObjectId("course2"), ObjectId("course3")]
}

// courses collection
{
  _id: ObjectId("course1"),
  title: "Database Systems",
  student_ids: [ObjectId("student1"), ObjectId("student2")]
  // ⚠️ Dual arrays = must update both on changes
}

// Option B: Junction collection (like relational M:N)
// enrollments collection
{
  student_id: ObjectId("student1"),
  course_id: ObjectId("course1"),
  enrolled_at: ISODate("2026-01-10"),
  grade: "A"
}
// Better for M:N with relationship metadata
```

---

## Advanced Schema Design Patterns

### 1. Bucket Pattern

**Problem:** Storing time-series data (IoT, metrics) — millions of tiny documents.

**Solution:** Group data into "buckets" (e.g., per hour/day).

```javascript
// ❌ BAD — one doc per reading (millions of docs)
{ sensor_id: "temp_01", value: 22.5, timestamp: ISODate("2026-03-17T10:00:01") }
{ sensor_id: "temp_01", value: 22.6, timestamp: ISODate("2026-03-17T10:00:02") }
// ... millions more

// ✅ GOOD — bucket per hour
{
  sensor_id: "temp_01",
  bucket_start: ISODate("2026-03-17T10:00:00"),
  bucket_end: ISODate("2026-03-17T10:59:59"),
  count: 3600,
  sum: 81000,
  avg: 22.5,
  min: 21.8,
  max: 23.2,
  readings: [
    { t: ISODate("2026-03-17T10:00:01"), v: 22.5 },
    { t: ISODate("2026-03-17T10:00:02"), v: 22.6 },
    // ... up to 3600 readings per hour
  ]
}
```

**Benefits:** 60x fewer documents, pre-aggregated stats, fewer indexes, better query performance.

> **Note:** MongoDB 5.0+ has native **Time Series collections** that handle this automatically.

---

### 2. Outlier Pattern

**Problem:** Most documents are uniform, but a few "outliers" break the pattern (e.g., a celebrity with millions of followers vs. normal users).

**Solution:** Embed normally for the majority, use overflow for outliers.

```javascript
// Normal user — followers embedded
{
  _id: "user_bob",
  name: "Bob",
  followers: ["alice", "charlie", "diana"],
  has_overflow: false
}

// Celebrity — flag + overflow collection
{
  _id: "user_celebrity",
  name: "Celebrity",
  followers: ["alice", "bob", ...],  // First 1000
  has_overflow: true
}

// Overflow collection
{
  user_id: "user_celebrity",
  page: 2,
  followers: ["user_1001", "user_1002", ...]  // Next batch
}
```

---

### 3. Computed Pattern

**Problem:** Expensive computations on read (e.g., total revenue, average rating).

**Solution:** Pre-compute and store results, update on writes.

```javascript
{
  _id: ObjectId("product1"),
  name: "Widget Pro",
  price: 49.99,
  // Computed fields — updated on each review insert
  review_count: 1523,
  rating_sum: 6854,
  avg_rating: 4.5,
  rating_distribution: {
    "5": 800,
    "4": 400,
    "3": 200,
    "2": 80,
    "1": 43
  }
}

// On new review, atomically update computed fields
db.products.updateOne(
  { _id: ObjectId("product1") },
  {
    $inc: {
      review_count: 1,
      rating_sum: 5,
      "rating_distribution.5": 1
    },
    $set: {
      avg_rating: 4.51  // recomputed
    }
  }
)
```

---

### 4. Subset Pattern

**Problem:** Large documents with data that's rarely needed (e.g., product with 1000 reviews — only show latest 10).

**Solution:** Keep a subset embedded, reference the full data.

```javascript
// products collection — hot data (frequently accessed)
{
  _id: ObjectId("product1"),
  name: "Widget Pro",
  price: 49.99,
  top_reviews: [  // Only 10 most helpful reviews
    { user: "alice", rating: 5, text: "Amazing!", helpful_votes: 120 },
    { user: "bob", rating: 5, text: "Best purchase", helpful_votes: 95 }
  ],
  total_reviews: 1523,
  avg_rating: 4.5
}

// reviews collection — cold data (loaded on demand)
{
  _id: ObjectId("..."),
  product_id: ObjectId("product1"),
  user: "charlie",
  rating: 3,
  text: "It's okay",
  helpful_votes: 5,
  created_at: ISODate("2026-03-10")
}
```

**Benefits:** Smaller document = fits in WiredTiger cache = faster reads.

---

### 5. Polymorphic Pattern

**Problem:** Different types of entities share common attributes but have type-specific fields.

**Solution:** Store all types in one collection with a discriminator field.

```javascript
// Single "vehicles" collection for all types
{ type: "car", brand: "Toyota", model: "Camry", doors: 4, trunk_size: 15 }
{ type: "truck", brand: "Ford", model: "F-150", payload_capacity: 3300, tow_capacity: 13200 }
{ type: "motorcycle", brand: "Honda", model: "CBR", engine_cc: 600 }

// Query all vehicles
db.vehicles.find({ brand: "Toyota" })

// Query specific type
db.vehicles.find({ type: "truck", tow_capacity: { $gt: 10000 } })
```

**Benefits:** Single collection, simple queries, common indexes. Used in content management (articles, videos, podcasts all in one collection).

---

### 6. Extended Reference Pattern

**Problem:** Frequently joining two collections (e.g., order → customer name).

**Solution:** Duplicate frequently-accessed reference fields.

```javascript
// Instead of just storing customer_id...
// ❌ Requires $lookup every time to show customer name
{
  _id: ObjectId("order1"),
  customer_id: ObjectId("cust1"),
  items: [...]
}

// ✅ Embed frequently-accessed customer fields
{
  _id: ObjectId("order1"),
  customer: {
    _id: ObjectId("cust1"),
    name: "Alice Johnson",    // Duplicated for fast reads
    email: "alice@example.com" // Duplicated
  },
  items: [...],
  total: 299.99
}
// Trade-off: faster reads, but must update denormalized data on customer name change
```

---

## Schema Validation

```javascript
// Create collection with validation
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price", "category"],
      properties: {
        name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 200,
          description: "Product name — required string"
        },
        price: {
          bsonType: "decimal",
          minimum: 0,
          description: "Must be a positive decimal"
        },
        category: {
          enum: ["electronics", "clothing", "food", "books"],
          description: "Must be one of the allowed categories"
        },
        tags: {
          bsonType: "array",
          items: { bsonType: "string" },
          maxItems: 10
        },
        reviews: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["user", "rating"],
            properties: {
              user: { bsonType: "string" },
              rating: { bsonType: "int", minimum: 1, maximum: 5 }
            }
          }
        }
      }
    }
  }
})

// Modify validation on existing collection
db.runCommand({
  collMod: "products",
  validator: { /* new schema */ },
  validationLevel: "moderate",  // Don't validate existing docs
  validationAction: "warn"      // Warn instead of reject
})
```

---

## Anti-Patterns to Avoid

### 1. Massive Arrays (Unbounded Growth)

```javascript
// ❌ BAD — array grows forever
{
  _id: "user_celeb",
  name: "Celebrity",
  followers: ["user1", "user2", ... "user_10000000"]  // 10M entries!
  // Document will exceed 16 MB!
}

// ✅ GOOD — reference in separate collection
// followers: { follower_id: "user1", following_id: "user_celeb" }
```

### 2. Unnecessary Normalization

```javascript
// ❌ BAD — over-normalized like SQL (too many lookups)
// users: { _id: 1, name_id: 10, addr_id: 20, phone_id: 30 }
// names: { _id: 10, first: "Alice", last: "Smith" }
// addresses: { _id: 20, city: "NYC" }
// phones: { _id: 30, number: "555-1234" }

// ✅ GOOD — embed what you read together
{ _id: 1, name: "Alice Smith", city: "NYC", phone: "555-1234" }
```

### 3. Using MongoDB as a Queue

```javascript
// ❌ BAD — find-and-modify as a job queue
// Causes write contention, lock issues at scale
db.jobs.findOneAndUpdate(
  { status: "pending" },
  { $set: { status: "processing", worker: "w1" } }
)

// ✅ GOOD — use dedicated queue systems (Redis, RabbitMQ, SQS)
// Or use MongoDB Change Streams for event-driven architectures
```

### 4. Case-Sensitive Mistakes

```javascript
// MongoDB is case-sensitive by default
db.users.find({ name: "alice" })   // Won't find "Alice"

// Fix: use collation or store lowercase version
db.users.find({ name: "alice" }).collation({ locale: "en", strength: 2 })
// Or add normalized field: name_lower: "alice"
```

---

## Interview Questions — Schema Design

### Q1: How do you decide between embedding and referencing?

**Framework (use the "3 questions" approach):**

1. **How often is data accessed together?** → Together = embed, independently = reference
2. **What's the cardinality?** → One-to-few = embed, one-to-many unbounded = reference
3. **How does data change?** → Changes together = embed, changes independently = reference

Also consider:
- 16 MB document limit
- Read/write ratio (reads favor embedding, writes favor referencing)
- Data duplication tolerance

---

### Q2: What is denormalization in MongoDB and when is it appropriate?

Denormalization = storing duplicate data to avoid joins.

**Appropriate when:**
- Read performance is more important than write performance
- Duplicated data rarely changes (e.g., product name in order)
- The alternative (joins/$lookup) is too expensive

**Inappropriate when:**
- Data changes frequently (update all copies)
- Data integrity is critical (risk of inconsistency)
- Storage is a constraint (duplication wastes space)

---

### Q3: How would you model a social media feed?

```javascript
// Fan-out on write (Twitter-style for users with few followers)
// When user posts → push to all followers' feeds
// feeds collection
{
  user_id: "follower_123",
  feed: [
    { post_id: "p1", author: "alice", text: "Hello!", ts: ISODate("...") },
    { post_id: "p2", author: "bob", text: "Hi!", ts: ISODate("...") }
  ]
}

// Fan-out on read (for celebrities with millions of followers)
// When user opens feed → query posts from followed users
db.posts.find({ author_id: { $in: followedUserIds } })
  .sort({ created_at: -1 })
  .limit(20)

// Hybrid: Fan-out on write for normal users, fan-out on read for celebrities
```
