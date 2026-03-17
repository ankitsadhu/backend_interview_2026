# 🏗️ Low-Level Design (LLD) Roadmap — MANG Level

> **Philosophy**: Solve **one canonical problem per category deeply**, and you'll be able to solve any variation thrown at you. Each "First Pick" below is the **minimum viable problem** that teaches the core patterns for its category.

---

## 📋 How To Use This Roadmap

1. **Master the fundamentals** first (SOLID, Design Patterns, OOP)
2. **Solve each "First Pick" problem** end-to-end with production-quality code
3. **Review the "Unlocked Variations"** — you should be able to sketch these after solving the first pick
4. **Time yourself** — MANG expects a working LLD in 45 minutes

---

## 🧠 Pre-requisites Checklist

| Topic | Status | Notes |
|-------|--------|-------|
| SOLID Principles | ⬜ | See `oops/fundamentals/` |
| Design Patterns (Strategy, Observer, Factory, State, Command, Decorator) | ⬜ | Must-know 6 patterns |
| UML Class Diagrams | ⬜ | Be able to draw on whiteboard |
| Concurrency basics (locks, thread safety) | ⬜ | See `02_concurrency/` |

---

## 🗺️ Problem Categories & First Picks

### Category 1: Booking / Reservation Systems
> Core Skill: **Slot management, conflict resolution, state machines, concurrency**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **Hotel Booking System** (First Pick) | Medium | P0 |
| | Movie Ticket Booking (BookMyShow) | Medium | P1 |
| | Meeting Room Scheduler | Medium | P1 |
| | Restaurant Reservation System | Medium | P2 |
| | Flight Booking System | Hard | P2 |
| | Doctor Appointment System | Medium | P2 |

**Why Hotel Booking is the First Pick:**
- Covers room inventory management (slot management)
- Check-in/check-out state machine
- Concurrent booking conflict handling
- Price calculation strategies (seasonal, dynamic)
- Search & filter with multiple criteria
- Once solved → Movie tickets = rooms as seats, Meeting rooms = rooms with time slots

**Key Patterns**: State Pattern, Strategy Pattern, Observer Pattern

---

### Category 2: Ride-Sharing / Matching Systems
> Core Skill: **Real-time matching, location-based logic, pricing strategies, state machines**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **Cab Booking System (Uber/Ola)** (First Pick) | Hard | P0 |
| | Food Delivery System (Swiggy/Zomato) | Hard | P1 |
| | Logistics/Package Delivery System | Medium | P2 |

**Why Cab Booking is the First Pick:**
- Driver-rider matching algorithm (proximity + availability)
- Ride state machine (Requested → Matched → InProgress → Completed → Rated)
- Surge pricing (Strategy pattern)
- Real-time location tracking
- Rating system
- Once solved → Food delivery = cab + restaurant + menu, Package delivery = cab without passengers

**Key Patterns**: Strategy Pattern, Observer Pattern, State Pattern, Command Pattern

---

### Category 3: Game Design
> Core Skill: **Turn-based logic, rule engines, board representation, extensibility**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **Chess** (First Pick) | Hard | P0 |
| | Tic-Tac-Toe | Easy | Warm-up |
| | Snakes & Ladders | Medium | P1 |
| | Card Game (Blackjack/UNO) | Medium | P1 |
| | Ludo | Medium | P2 |
| | Minesweeper | Medium | P2 |

**Why Chess is the First Pick:**
- Complex piece hierarchy (inheritance + polymorphism at its best)
- Move validation engine (each piece has unique rules)
- Board representation & coordinate system
- Turn management & game state
- Check/Checkmate detection (rule composability)
- Once solved → Tic-tac-toe is trivial, Snakes & Ladders = simpler board + dice, Card games = hand management instead of board

**Key Patterns**: Strategy Pattern, Command Pattern (undo moves), Factory Pattern, Template Method

---

### Category 4: E-Commerce / Inventory Systems
> Core Skill: **Cart management, payment integration, inventory tracking, order lifecycle**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **Online Shopping System (Amazon)** (First Pick) | Hard | P0 |
| | Vending Machine | Medium | P1 |
| | Auction System (eBay) | Hard | P2 |
| | Coupon/Discount Engine | Medium | P2 |

**Why Online Shopping is the First Pick:**
- Product catalog with categories & search
- Shopping cart (add/remove/update quantities)
- Order state machine (Placed → Confirmed → Shipped → Delivered → Returned)
- Payment processing (Strategy pattern for multiple gateways)
- Inventory management with concurrency
- Once solved → Vending machine = tiny cart + inventory, Auction = cart with bidding, Coupons = pricing strategy

**Key Patterns**: Strategy Pattern, Observer Pattern, State Pattern, Factory Pattern

---

### Category 5: Social / Content Platforms
> Core Skill: **User relationships, feeds, notifications, content moderation**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **Social Media Platform (Twitter/Instagram)** (First Pick) | Hard | P0 |
| | Notification System | Medium | P1 |
| | Chat Application | Hard | P1 |
| | Stack Overflow (Q&A Platform) | Medium | P2 |

**Why Social Media is the First Pick:**
- User profile & relationship management (follow/unfollow/block)
- Post creation with different media types (text, image, video — Factory pattern)
- Feed generation (timeline algorithm)
- Like/Comment/Share interactions
- Notification fan-out on interactions
- Once solved → Notification system is a subsystem, Chat = direct messages + real-time, Q&A = posts with voting

**Key Patterns**: Observer Pattern, Factory Pattern, Strategy Pattern, Decorator Pattern

---

### Category 6: Storage / Infrastructure Systems  
> Core Skill: **Data structures for storage, caching strategies, file organization, concurrency**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **In-Memory Key-Value Store (Redis)** (First Pick) | Hard | P0 |
| | In-Memory File System | Hard | P1 |
| | Rate Limiter | Medium | P1 |
| | Cache with Eviction (LRU/LFU) | Medium | P1 |
| | Logger Framework | Medium | P2 |

**Why Key-Value Store is the First Pick:**
- Core data structure design (HashMap + LinkedList for LRU)
- TTL / expiry management (background threads)
- Multiple data type support (String, List, Set, HashMap)
- Thread-safe operations
- Persistence strategies (snapshotting, AOF)
- Once solved → File system = KV with tree structure, Rate limiter = KV with counters, Cache = subset of KV store, Logger = KV with append strategy

**Key Patterns**: Strategy Pattern, Singleton Pattern, Observer Pattern, Decorator Pattern

---

### Category 7: Task / Workflow Management
> Core Skill: **Scheduling, priority queues, state machines, dependency management**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **Task Scheduler (Cron)** (First Pick) | Hard | P0 |
| | Elevator System | Medium | P1 |
| | Traffic Signal Controller | Medium | P2 |
| | Workflow Engine | Hard | P2 |

**Why Task Scheduler is the First Pick:**
- Priority-based execution (heap/priority queue)
- Recurring vs one-time tasks
- Dependency resolution (DAG)
- Thread pool management
- Retry & failure handling
- Once solved → Elevator = scheduler with floor priorities, Traffic signal = time-based scheduler, Workflow engine = scheduler + DAG

**Key Patterns**: Strategy Pattern, Observer Pattern, Command Pattern, State Pattern

---

### Category 8: Access Control / Multi-tenancy
> Core Skill: **Permission hierarchies, authentication, authorization, plugin architecture**

| | Problem | Difficulty | Priority |
|---|---------|-----------|----------|
| 🥇 | **Parking Lot System** (First Pick) | Medium | P0 |
| | Library Management System | Medium | P0 |
| | ATM Machine | Medium | P1 |
| | Splitwise (Expense Sharing) | Medium | P1 |

**Why Parking Lot is the First Pick:**
- Vehicle type hierarchy (inheritance)
- Spot allocation strategies (nearest, type-based)
- Multi-floor/zone management
- Payment calculation (hourly, daily rates — Strategy)
- Entry/exit gate management
- Capacity tracking
- Once solved → Library = parking lot with books instead of cars + due dates, ATM = payment + state machine, Splitwise = payment splitting strategies

**Key Patterns**: Strategy Pattern, Factory Pattern, Singleton Pattern, Observer Pattern

---

## 🎯 Recommended Solving Order (8-Week Plan)

| Week | Problem | Category | Est. Time |
|------|---------|----------|-----------|
| 1 | Parking Lot | Access Control | 3-4 hrs |
| 2 | Chess | Game Design | 5-6 hrs |
| 3 | Hotel Booking | Booking Systems | 4-5 hrs |
| 4 | Key-Value Store | Storage/Infra | 5-6 hrs |
| 5 | Cab Booking (Uber) | Ride-Sharing | 5-6 hrs |
| 6 | Online Shopping (Amazon) | E-Commerce | 5-6 hrs |
| 7 | Task Scheduler | Task Management | 4-5 hrs |
| 8 | Social Media (Twitter) | Social Platforms | 5-6 hrs |

> **After Week 4**, you should be able to handle most MANG LLD rounds. Weeks 5-8 give you breadth for harder rounds.

---

## 🧩 Pattern Mastery Matrix

> This shows which patterns each first-pick problem teaches. Solve all 8 and you've used every important pattern multiple times.

| Pattern | Parking Lot | Chess | Hotel | KV Store | Uber | Amazon | Scheduler | Twitter |
|---------|:-----------:|:-----:|:-----:|:--------:|:----:|:------:|:---------:|:-------:|
| Strategy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Observer | ✅ | | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Factory | ✅ | ✅ | | | | ✅ | | ✅ |
| State | | | ✅ | | ✅ | ✅ | | |
| Command | | ✅ | | | | | ✅ | |
| Singleton | ✅ | | | ✅ | | | | |
| Decorator | | | | ✅ | | | | ✅ |
| Template | | ✅ | | | | | | |

---

## 📁 Folder Structure

```
lld_roadmap/
├── 00_roadmap.md              ← You are here
├── 01_parking_lot/
│   ├── problem.md             ← Problem statement + requirements
│   ├── design.md              ← Class diagram + API design
│   ├── solution.py            ← Clean implementation
│   └── variations.md          ← How to adapt for Library, ATM, etc.
├── 02_chess/
├── 03_hotel_booking/
├── 04_kv_store/
├── 05_cab_booking/
├── 06_online_shopping/
├── 07_task_scheduler/
├── 08_social_media/
└── patterns/
    ├── strategy.md
    ├── observer.md
    ├── factory.md
    ├── state.md
    ├── command.md
    └── decorator.md
```

---

## ✅ Completion Tracker

| # | Problem | Problem Statement | Design | Implementation | Variations | Done? |
|---|---------|:-:|:-:|:-:|:-:|:-:|
| 1 | Parking Lot | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 2 | Chess | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 3 | Hotel Booking | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 4 | Key-Value Store | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 5 | Cab Booking | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 6 | Online Shopping | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 7 | Task Scheduler | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 8 | Social Media | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

---

## 🎤 MANG Interview Tips

1. **Start by clarifying requirements** — Ask 3-5 clarifying questions before designing
2. **Identify core entities first** — Nouns in requirements = classes
3. **Draw class diagrams** — Show relationships before writing code
4. **Apply SOLID aggressively** — Interviewers watch for this
5. **Handle concurrency** — Always mention thread safety for shared resources
6. **Think about extensibility** — "What if we add a new vehicle type / payment method / game piece?"
7. **Use enums for finite states** — Don't use strings for status tracking
8. **45-minute target** — Spend 10 min on requirements, 10 on design, 25 on code
