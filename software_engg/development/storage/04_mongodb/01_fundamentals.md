# MongoDB Fundamentals

## What is MongoDB?

**MongoDB** is an **open-source, document-oriented NoSQL database** designed for scalability, flexibility, and high performance. Instead of storing data in rows and columns (like relational databases), MongoDB stores data as **JSON-like documents** (BSON format).

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Document Model** | Data stored as flexible JSON-like documents (BSON) |
| **Schema-less** | No fixed schema — documents in the same collection can have different fields |
| **Horizontal Scaling** | Built-in sharding for distributing data across machines |
| **Rich Query Language** | Ad-hoc queries, indexing, aggregation framework |
| **High Availability** | Replica sets with automatic failover |
| **ACID Transactions** | Multi-document ACID transactions (since 4.0) |

---

## How MongoDB Works Internally

```
Client Application
       │
       ▼
┌──────────────────┐
│   MongoDB Driver  │  ← Language-specific (PyMongo, Mongoose, etc.)
└────────┬─────────┘
         │  BSON over TCP (Wire Protocol)
         ▼
┌──────────────────┐
│     mongos        │  ← Query router (only in sharded clusters)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     mongod        │  ← Core database process
│  ┌──────────────┐ │
│  │  WiredTiger   │ │  ← Default storage engine
│  │  Storage Eng. │ │
│  └──────────────┘ │
│  ┌──────────────┐ │
│  │  In-Memory    │ │  ← Document cache + indexes
│  │  Cache        │ │
│  └──────────────┘ │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│   Disk (Data +    │  ← Data files + journal
│   Journal Files)  │
└──────────────────┘
```

### MongoDB vs Relational Databases — Terminology

| RDBMS | MongoDB |
|-------|---------|
| Database | Database |
| Table | Collection |
| Row | Document |
| Column | Field |
| Primary Key | `_id` field (auto-generated ObjectId) |
| JOIN | `$lookup` (aggregation) / embedding |
| Index | Index |
| Transaction | Transaction (multi-document since 4.0) |

---

## BSON — Binary JSON

MongoDB stores documents in **BSON** (Binary JSON), which extends JSON with additional data types and is optimized for:

- **Speed** — binary format, faster to parse than text JSON
- **Size** — length-prefixed, so no need to scan entire document
- **Rich types** — supports types JSON doesn't (Date, ObjectId, Decimal128, Binary, etc.)

```
JSON:                          BSON (conceptual):
{                              \x27\x00\x00\x00        (document size)
  "name": "Alice",            \x02 name \x00 \x06 Alice\x00
  "age": 30                   \x10 age \x00 \x1e\x00\x00\x00
}                              \x00                    (terminator)
```

### BSON Data Types

| Type | Description | Example |
|------|-------------|---------|
| `String` | UTF-8 string | `"hello"` |
| `Int32` / `Int64` | 32/64-bit integer | `42`, `NumberLong("9999999999")` |
| `Double` | 64-bit float | `3.14` |
| `Boolean` | true/false | `true` |
| `ObjectId` | 12-byte unique identifier | `ObjectId("507f1f77bcf86cd799439011")` |
| `Date` | Milliseconds since Unix epoch | `ISODate("2026-03-17T00:00:00Z")` |
| `Array` | Ordered list | `[1, 2, 3]` |
| `Embedded Document` | Nested document | `{ "street": "123 Main" }` |
| `Null` | Null value | `null` |
| `Binary Data` | Binary blob | Used for images, files |
| `Decimal128` | High-precision decimal | `NumberDecimal("9.99")` |
| `Regular Expression` | Regex pattern | `/^hello/i` |
| `Timestamp` | Internal timestamp (replication) | Oplog entries |

### ObjectId Structure (12 bytes)

```
 4 bytes     5 bytes        3 bytes
┌──────────┬──────────────┬──────────┐
│ timestamp │   random     │ counter  │
│ (seconds) │  (per-process)│(incrementing)│
└──────────┴──────────────┴──────────┘

Example: ObjectId("507f1f77bcf86cd799439011")
  - 507f1f77 → Unix timestamp (seconds since epoch)
  - bcf86cd799 → Random value (unique to machine+process)
  - 439011 → Incrementing counter
```

- **Roughly time-sortable** — first 4 bytes are timestamp
- **Unique across machines** — no coordination needed
- Use `ObjectId.getTimestamp()` to extract creation time

---

## Installation & Setup

```bash
# Docker (recommended for learning)
docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  mongo:latest

# Connect with mongosh
docker exec -it mongodb mongosh -u admin -p secret

# Or use MongoDB Atlas (free tier)
# https://www.mongodb.com/atlas → Create free cluster → Connect
```

### mongosh Basics

```javascript
// Show databases
show dbs

// Switch to / create database
use mydb

// Show collections
show collections

// Current database
db.getName()

// Server status
db.serverStatus()

// Help
db.help()
db.collection.help()
```

> **Note:** A database is not actually created until you insert data into it.

---

## CRUD Operations

### Create (Insert)

```javascript
// Insert one document
db.users.insertOne({
  name: "Alice",
  age: 30,
  email: "alice@example.com",
  tags: ["developer", "admin"],
  address: {
    city: "NYC",
    zip: "10001"
  },
  createdAt: new Date()
})
// Returns: { acknowledged: true, insertedId: ObjectId("...") }

// Insert multiple documents
db.users.insertMany([
  { name: "Bob", age: 25, email: "bob@example.com" },
  { name: "Charlie", age: 35, email: "charlie@example.com" },
  { name: "Diana", age: 28, email: "diana@example.com" }
])
// Returns: { acknowledged: true, insertedIds: { '0': ..., '1': ..., '2': ... } }

// Insert with custom _id
db.users.insertOne({
  _id: "user_alice",
  name: "Alice"
})

// Ordered vs Unordered inserts
db.users.insertMany(docs, { ordered: false })
// ordered: true (default) → stops on first error
// ordered: false → continues inserting remaining docs on error
```

---

### Read (Query)

```javascript
// Find all documents
db.users.find()

// Find with filter
db.users.find({ age: 30 })

// Find one (returns first match)
db.users.findOne({ name: "Alice" })

// Projection — select specific fields
db.users.find({ age: { $gt: 25 } }, { name: 1, email: 1, _id: 0 })
//  1 = include, 0 = exclude
//  Cannot mix inclusion and exclusion (except _id)

// Pretty print
db.users.find().pretty()

// Count
db.users.countDocuments({ age: { $gt: 25 } })
db.users.estimatedDocumentCount()  // faster, uses metadata
```

#### Comparison Operators

```javascript
db.users.find({ age: { $eq: 30 } })    // Equal (same as { age: 30 })
db.users.find({ age: { $ne: 30 } })    // Not equal
db.users.find({ age: { $gt: 25 } })    // Greater than
db.users.find({ age: { $gte: 25 } })   // Greater than or equal
db.users.find({ age: { $lt: 30 } })    // Less than
db.users.find({ age: { $lte: 30 } })   // Less than or equal
db.users.find({ age: { $in: [25, 30, 35] } })   // In array
db.users.find({ age: { $nin: [25, 30] } })       // Not in array
```

#### Logical Operators

```javascript
// AND (implicit)
db.users.find({ age: { $gt: 25 }, name: "Alice" })

// AND (explicit — needed when multiple conditions on same field)
db.users.find({ $and: [{ age: { $gt: 20 } }, { age: { $lt: 35 } }] })

// OR
db.users.find({ $or: [{ age: 25 }, { name: "Alice" }] })

// NOT
db.users.find({ age: { $not: { $gt: 30 } } })

// NOR
db.users.find({ $nor: [{ age: 25 }, { name: "Bob" }] })
```

#### Element Operators

```javascript
// Field exists
db.users.find({ email: { $exists: true } })

// Field type check
db.users.find({ age: { $type: "int" } })
db.users.find({ age: { $type: ["int", "double"] } })
```

#### Array Operators

```javascript
// Exact array match (order matters)
db.users.find({ tags: ["developer", "admin"] })

// Contains element
db.users.find({ tags: "developer" })

// Contains all elements (any order)
db.users.find({ tags: { $all: ["developer", "admin"] } })

// Array size
db.users.find({ tags: { $size: 2 } })

// Match array element by condition
db.users.find({ scores: { $elemMatch: { $gt: 80, $lt: 90 } } })
// $elemMatch: at least ONE element must satisfy ALL conditions
// Without $elemMatch: different elements can satisfy different conditions
```

#### String / Regex

```javascript
// Regex match
db.users.find({ name: { $regex: /^ali/i } })
db.users.find({ name: { $regex: "^ali", $options: "i" } })

// Text search (requires text index)
db.articles.find({ $text: { $search: "mongodb tutorial" } })
```

#### Cursor Methods

```javascript
// Sort
db.users.find().sort({ age: 1 })    // 1 = ascending, -1 = descending
db.users.find().sort({ age: -1, name: 1 })  // Multi-field sort

// Limit & Skip (pagination)
db.users.find().limit(10)
db.users.find().skip(20).limit(10)   // Page 3 (0-indexed)

// Note: skip() is O(n) — inefficient for large offsets
// Better: use range-based pagination with _id or indexed field
db.users.find({ _id: { $gt: lastSeenId } }).limit(10)
```

---

### Update

```javascript
// Update one document
db.users.updateOne(
  { name: "Alice" },            // filter
  { $set: { age: 31, city: "SF" } }  // update
)

// Update multiple documents
db.users.updateMany(
  { age: { $lt: 30 } },
  { $set: { status: "young" } }
)

// Replace entire document (keep _id)
db.users.replaceOne(
  { name: "Alice" },
  { name: "Alice", age: 31, email: "alice@new.com" }
)

// Upsert — insert if not found
db.users.updateOne(
  { email: "new@example.com" },
  { $set: { name: "New User", age: 25 } },
  { upsert: true }
)
```

#### Update Operators

```javascript
// $set — set field values
{ $set: { name: "Alice", age: 31 } }

// $unset — remove fields
{ $unset: { temporaryField: "" } }

// $inc — increment numeric fields
{ $inc: { age: 1, score: -5 } }

// $mul — multiply
{ $mul: { price: 1.1 } }    // increase by 10%

// $min / $max — update only if new value is less/greater
{ $min: { lowScore: 50 } }  // sets lowScore to 50 only if current > 50
{ $max: { highScore: 99 } }

// $rename — rename a field
{ $rename: { "old_name": "new_name" } }

// $currentDate — set to current date
{ $currentDate: { lastModified: true } }
{ $currentDate: { lastModified: { $type: "timestamp" } } }

// Array update operators
{ $push: { tags: "newTag" } }          // Append to array
{ $push: { tags: { $each: ["a", "b"] } } }  // Append multiple
{ $push: { scores: { $each: [90], $sort: -1, $slice: 5 } } }  // Push, sort, keep top 5
{ $addToSet: { tags: "uniqueTag" } }   // Add only if not present
{ $pull: { tags: "removeThis" } }      // Remove matching elements
{ $pop: { tags: 1 } }                  // Remove last element (-1 for first)
{ $pullAll: { tags: ["a", "b"] } }     // Remove all matching values

// Positional operator $
db.users.updateOne(
  { "scores.subject": "math" },
  { $set: { "scores.$.grade": "A" } }   // Update matching array element
)

// Positional all [$[]]
db.users.updateOne(
  { _id: 1 },
  { $inc: { "scores.$[].value": 10 } }  // Increment ALL array elements
)

// Filtered positional [$[identifier]]
db.users.updateOne(
  { _id: 1 },
  { $set: { "scores.$[elem].passed": true } },
  { arrayFilters: [{ "elem.value": { $gte: 60 } }] }
)
```

---

### Delete

```javascript
// Delete one
db.users.deleteOne({ name: "Alice" })

// Delete many
db.users.deleteMany({ status: "inactive" })

// Delete all documents (keep collection)
db.users.deleteMany({})

// Drop collection (delete collection + indexes)
db.users.drop()

// Drop database
db.dropDatabase()

// findOneAndDelete — returns deleted document
db.users.findOneAndDelete(
  { status: "inactive" },
  { sort: { createdAt: 1 } }  // delete oldest first
)
```

---

### Bulk Operations

```javascript
// Ordered bulk (stops on error)
db.users.bulkWrite([
  { insertOne: { document: { name: "Eve", age: 22 } } },
  { updateOne: { filter: { name: "Bob" }, update: { $set: { age: 26 } } } },
  { deleteOne: { filter: { name: "Charlie" } } },
  { replaceOne: { filter: { name: "Diana" }, replacement: { name: "Diana", age: 29 } } }
])

// Unordered bulk (continues on error, better performance)
db.users.bulkWrite(operations, { ordered: false })
```

---

## Common Interview Questions — Beginner

### Q1: What is the maximum document size in MongoDB?

**16 MB** per BSON document. This is a hard limit.

For larger data, use **GridFS** — it splits files into 255 KB chunks stored across two collections (`fs.files` + `fs.chunks`).

```javascript
// GridFS is typically used via drivers
const bucket = new GridFSBucket(db);
const uploadStream = bucket.openUploadStream("large_file.pdf");
fs.createReadStream("./large_file.pdf").pipe(uploadStream);
```

---

### Q2: What is the `_id` field?

- **Required** in every document — acts as the primary key
- **Automatically generated** as an `ObjectId` if not provided
- **Immutable** — cannot be changed after insert
- **Automatically indexed** — unique index on `_id`
- Can be **any BSON type** except arrays

---

### Q3: MongoDB is "schema-less" — does that mean there's no schema at all?

MongoDB is **schema-flexible**, not truly schema-less:

- Documents in a collection **can** have different structures
- In practice, applications enforce **implicit schemas** through code
- MongoDB supports **schema validation** rules (since 3.6):

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email"],
      properties: {
        name: { bsonType: "string", description: "must be a string" },
        email: { bsonType: "string", pattern: "^.+@.+$" },
        age: { bsonType: "int", minimum: 0, maximum: 150 }
      }
    }
  },
  validationLevel: "strict",    // "strict" | "moderate" (skip existing invalid docs)
  validationAction: "error"     // "error" | "warn" (log but allow)
})
```

---

### Q4: When should you use MongoDB over a relational database?

| Use MongoDB When | Use RDBMS When |
|-----------------|----------------|
| Schema evolves frequently | Schema is stable and well-defined |
| Hierarchical / nested data | Highly relational data with many JOINs |
| High write throughput needed | Complex transactions across many tables |
| Horizontal scaling required | ACID compliance is critical |
| Rapid prototyping | Strong consistency is mandatory |
| Working with JSON/BSON natively | Complex reporting / BI queries |
| Event logging / IoT data | Financial / banking applications |
