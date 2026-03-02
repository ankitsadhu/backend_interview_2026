# SOLID Principles — Complete MANG Interview Guide

> Five design principles that make software **understandable, flexible, and maintainable**. Each principle below includes the theory, Python code (violation → fix), real-world analogies, and cross-questions interviewers actually ask.

---

## S — Single Responsibility Principle (SRP)

> *"A class should have one, and only one, reason to change."* — Robert C. Martin

A "reason to change" = one **actor** or **business concern**. If Product Manager changes break your class AND DevOps changes also break it, the class has two responsibilities.

### ❌ Violation

```python
class Employee:
    def __init__(self, name: str, salary: float):
        self.name = name
        self.salary = salary

    def calculate_pay(self) -> float:
        """Business logic — owned by Finance team"""
        return self.salary * 1.2  # With bonus

    def save_to_db(self):
        """Persistence — owned by Engineering/DBA team"""
        db.execute(f"INSERT INTO employees VALUES ('{self.name}', {self.salary})")

    def generate_report(self) -> str:
        """Reporting — owned by HR team"""
        return f"Employee Report: {self.name} earns {self.salary}"
```

Three teams, three reasons to change → violates SRP.

### ✅ Fix — Separate by Actor

```python
class Employee:
    """Pure data / domain model"""
    def __init__(self, name: str, salary: float):
        self.name = name
        self.salary = salary

class PayCalculator:
    """Finance team's concern"""
    def calculate(self, emp: Employee) -> float:
        return emp.salary * 1.2

class EmployeeRepository:
    """Engineering team's concern"""
    def save(self, emp: Employee):
        db.execute("INSERT INTO employees (name, salary) VALUES (?, ?)",
                   (emp.name, emp.salary))

class ReportGenerator:
    """HR team's concern"""
    def generate(self, emp: Employee) -> str:
        return f"Employee Report: {emp.name} earns {emp.salary}"
```

### Real-World Analogy
A **chef** shouldn't also be the **waiter** and the **cashier**. Each role changes for different reasons (menu changes vs service protocol vs payment systems).

### When SRP Goes Too Far
Splitting a 10-line class into 5 single-method classes creates **fragmentation**. Use the **Facade pattern** to group cohesive micro-classes behind a clean API:

```python
class EmployeeFacade:
    """Unified API — clients don't know about the internal split"""
    def __init__(self):
        self._repo = EmployeeRepository()
        self._pay = PayCalculator()
        self._report = ReportGenerator()

    def hire_and_report(self, name: str, salary: float) -> str:
        emp = Employee(name, salary)
        self._repo.save(emp)
        return self._report.generate(emp)
```

---

## O — Open/Closed Principle (OCP)

> *"Software entities should be open for extension, but closed for modification."*

You should be able to **add new behavior** without **changing existing code**.

### ❌ Violation — The `if/elif` Explosion

```python
class DiscountCalculator:
    def calculate(self, customer_type: str, amount: float) -> float:
        if customer_type == "regular":
            return amount * 0.95
        elif customer_type == "premium":
            return amount * 0.85
        elif customer_type == "vip":
            return amount * 0.75
        # Every new type = modify this class = risk breaking existing logic
```

### ✅ Fix — Strategy Pattern (Extension Without Modification)

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, amount: float) -> float: ...

class RegularDiscount(DiscountStrategy):
    def apply(self, amount: float) -> float:
        return amount * 0.95

class PremiumDiscount(DiscountStrategy):
    def apply(self, amount: float) -> float:
        return amount * 0.85

class VIPDiscount(DiscountStrategy):
    def apply(self, amount: float) -> float:
        return amount * 0.75

# Adding a new type = add a NEW class, touch NOTHING existing
class EmployeeDiscount(DiscountStrategy):
    def apply(self, amount: float) -> float:
        return amount * 0.70

class DiscountCalculator:
    """Closed for modification — never changes"""
    def calculate(self, strategy: DiscountStrategy, amount: float) -> float:
        return strategy.apply(amount)
```

### Other Extension Mechanisms in Python

```python
# 1. Decorators — extend function behavior without modifying it
import functools, time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.3f}s")
        return result
    return wrapper

# 2. __init_subclass__ — auto-register new plugins without modifying base
class Handler:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, handles: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if handles:
            Handler._registry[handles] = cls

class JsonHandler(Handler, handles="application/json"):
    def parse(self, data): ...

class XmlHandler(Handler, handles="application/xml"):
    def parse(self, data): ...

# Handler._registry is populated automatically. Base class never modified.
```

---

## L — Liskov Substitution Principle (LSP)

> *"Subtypes must be usable in place of their base types without altering correctness."*

If client code works with `Base`, it must work identically with **any** subclass of `Base` — no surprise exceptions, no violated assumptions.

### ❌ Classic Violation — Rectangle / Square

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float):
        self._width = value

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float):
        self._height = value

    def area(self) -> float:
        return self._width * self._height

class Square(Rectangle):
    def __init__(self, side: float):
        super().__init__(side, side)

    @Rectangle.width.setter
    def width(self, value: float):
        self._width = value
        self._height = value  # ← Surprise side-effect!

    @Rectangle.height.setter
    def height(self, value: float):
        self._width = value
        self._height = value

# Client code that breaks:
def test_rectangle(rect: Rectangle):
    rect.width = 5
    rect.height = 10
    assert rect.area() == 50  # ✅ for Rectangle, ❌ for Square (area = 100)
```

### ✅ Fix — Separate Hierarchies

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: float):
        self.side = side
    def area(self) -> float:
        return self.side ** 2
```

### LSP Rules (Behavioral Contracts)

| Rule | Meaning |
|------|---------|
| **Preconditions** | Subclass must accept **same or weaker** preconditions (can't require MORE) |
| **Postconditions** | Subclass must guarantee **same or stronger** postconditions (can't promise LESS) |
| **Invariants** | Subclass must preserve all parent invariants |
| **No new exceptions** | Subclass shouldn't raise exceptions the parent didn't declare |
| **History constraint** | Subclass shouldn't allow state transitions the parent disallows |

### ❌ Another Common Violation — Raising Unexpected Errors

```python
class Bird:
    def fly(self) -> str:
        return "Flying"

class Ostrich(Bird):
    def fly(self) -> str:
        raise NotImplementedError("Ostriches can't fly!")  # ← LSP violation

# Fix: Restructure the hierarchy
class Bird(ABC):
    @abstractmethod
    def move(self) -> str: ...

class FlyingBird(Bird):
    def move(self) -> str: return "Flying"

class FlightlessBird(Bird):
    def move(self) -> str: return "Running"
```

---

## I — Interface Segregation Principle (ISP)

> *"Clients should not be forced to depend on interfaces they do not use."*

### ❌ Violation — The Fat Interface

```python
from abc import ABC, abstractmethod

class Machine(ABC):
    @abstractmethod
    def print_doc(self, doc: str): ...

    @abstractmethod
    def scan_doc(self) -> str: ...

    @abstractmethod
    def fax_doc(self, doc: str, number: str): ...

    @abstractmethod
    def staple(self): ...

class SimplePrinter(Machine):
    def print_doc(self, doc: str):
        print(doc)

    def scan_doc(self) -> str:
        raise NotImplementedError  # Forced to implement! ← Smells like LSP violation too

    def fax_doc(self, doc: str, number: str):
        raise NotImplementedError

    def staple(self):
        raise NotImplementedError
```

### ✅ Fix — Segregated Interfaces

```python
class Printer(ABC):
    @abstractmethod
    def print_doc(self, doc: str): ...

class Scanner(ABC):
    @abstractmethod
    def scan_doc(self) -> str: ...

class Fax(ABC):
    @abstractmethod
    def fax_doc(self, doc: str, number: str): ...

# Simple printer — only implements what it can do
class SimplePrinter(Printer):
    def print_doc(self, doc: str):
        print(doc)

# Multi-function device — implements multiple interfaces
class MultiFunctionDevice(Printer, Scanner, Fax):
    def print_doc(self, doc: str): print(doc)
    def scan_doc(self) -> str: return "scanned content"
    def fax_doc(self, doc: str, number: str): print(f"Faxing to {number}")
```

### ISP in Python — The `Protocol` Approach

Python's duck typing + `Protocol` makes ISP natural:

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

class Writable(Protocol):
    def write(self, data: str) -> None: ...

class Closable(Protocol):
    def close(self) -> None: ...

# Functions declare EXACTLY what they need — nothing more
def process_input(source: Readable) -> str:
    return source.read()  # Only needs read() — doesn't care about write/close

def save_output(dest: Writable, data: str) -> None:
    dest.write(data)  # Only needs write()

# Any object with the right methods works — no inheritance required
class FileHandler:
    def read(self) -> str: return "data"
    def write(self, data: str) -> None: print(data)
    def close(self) -> None: print("closed")

process_input(FileHandler())  # ✅ Structural match
save_output(FileHandler(), "hello")  # ✅
```

---

## D — Dependency Inversion Principle (DIP)

> *"High-level modules should not depend on low-level modules. Both should depend on abstractions."*

### ❌ Violation — Direct Dependency

```python
class MySQLDatabase:
    def query(self, sql: str) -> list:
        # Direct MySQL connection
        return mysql_connection.execute(sql)

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # ← Hardcoded dependency!

    def get_user(self, user_id: int):
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Problems:
# 1. Can't switch to PostgreSQL without modifying UserService
# 2. Can't test without a real MySQL database
# 3. UserService knows about MySQL implementation details
```

### ✅ Fix — Depend on Abstractions

```python
from abc import ABC, abstractmethod

# Abstraction — owned by the high-level module
class Database(ABC):
    @abstractmethod
    def query(self, sql: str) -> list: ...

# Low-level modules implement the abstraction
class MySQLDatabase(Database):
    def query(self, sql: str) -> list:
        return mysql_connection.execute(sql)

class PostgreSQLDatabase(Database):
    def query(self, sql: str) -> list:
        return pg_connection.execute(sql)

class InMemoryDatabase(Database):
    """Perfect for testing — no external dependencies"""
    def __init__(self):
        self._store: dict = {}

    def query(self, sql: str) -> list:
        return list(self._store.values())

# High-level module depends on abstraction, NOT concrete class
class UserService:
    def __init__(self, db: Database):  # ← Injected as abstraction
        self.db = db

    def get_user(self, user_id: int) -> list:
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Production
service = UserService(PostgreSQLDatabase())

# Testing
service = UserService(InMemoryDatabase())
```

### DI Patterns in Python Frameworks

```python
# 1. FastAPI — Depends()
from fastapi import Depends, FastAPI

app = FastAPI()

def get_db() -> Database:
    db = PostgreSQLDatabase()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Database = Depends(get_db)):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# 2. Pytest — Fixtures (natural DI)
import pytest

@pytest.fixture
def db():
    return InMemoryDatabase()

@pytest.fixture
def user_service(db):
    return UserService(db)  # Automatically injected

def test_get_user(user_service):
    result = user_service.get_user(1)
    assert result == []

# 3. Manual DI Container
class Container:
    """Simple DI container for wiring dependencies"""
    _bindings: dict[type, type] = {}

    @classmethod
    def bind(cls, abstract: type, concrete: type):
        cls._bindings[abstract] = concrete

    @classmethod
    def resolve(cls, abstract: type):
        concrete = cls._bindings.get(abstract, abstract)
        return concrete()

Container.bind(Database, PostgreSQLDatabase)
db = Container.resolve(Database)  # Returns PostgreSQLDatabase()
```

---

## How SOLID Principles Interact

```
SRP ──────→ Each class has one job
  │
  ├── OCP ──→ New behaviors via new classes, not modifying existing ones
  │    │
  │    └── Strategy, Decorator, Plugin patterns
  │
  ├── LSP ──→ Subclasses are safe drop-in replacements
  │    │
  │    └── Guards against "clever" inheritance that breaks contracts
  │
  ├── ISP ──→ Small, focused interfaces (Protocol in Python)
  │    │
  │    └── Enables SRP — clients depend only on what they use
  │
  └── DIP ──→ Depend on abstractions, inject dependencies
       │
       └── Enables OCP (swap implementations) + testability
```

> **Key Insight**: SOLID principles are **mutually reinforcing**. Violating one often means violating others. ISP violations often cause LSP violations (forced `NotImplementedError`). DIP enables OCP (swap strategies without modifying context).

---

## Interview Questions — Tiered by Difficulty

### 🟢 Level 1: Fundamentals (Startup / Phone Screen)

**Q1. Explain each SOLID principle in one sentence.**
> **S** — A class should have only one reason to change (one actor/concern).
> **O** — Add behavior by extending (new classes), not modifying existing code.
> **L** — Subclasses must be substitutable for their base classes without breaking correctness.
> **I** — Don't force clients to depend on methods they don't use.
> **D** — Depend on abstractions, not concrete implementations.

**Q2. Give a real-world example of SRP violation.**
> A `User` model that handles authentication, authorization, database persistence, email sending, and report generation. Each of these changes for different reasons (security policy, DB schema, email provider, business rules).

**Q3. What is the relationship between OCP and the Strategy pattern?**
> Strategy is a **primary mechanism** for achieving OCP. By wrapping algorithms in an interface, you add new behaviors (new strategy classes) without touching the context class that uses them.

**Q4. What is Dependency Injection? How does it relate to DIP?**
> DI is a **technique** to achieve DIP. Instead of a class creating its dependencies internally (`self.db = MySQL()`), they're passed in from outside (`def __init__(self, db: Database)`). This inverts the dependency direction — high-level modules no longer depend on low-level ones.

---

### 🟡 Level 2: Intermediate (Mid-Level / Onsite Round 1)

**Q5. You implemented `Rectangle` and `Square(Rectangle)`. Setting width on a Square also sets height. What principle did you violate and why?**
> **LSP**. Client code expects that setting `rect.width = 5` doesn't change `rect.height`. `Square` silently breaks this postcondition. `assert rect.area() == new_width * old_height` fails. A Square is mathematically a Rectangle, but **behaviorally in mutable code**, it is not a safe substitute.

**Q6. Isn't SRP just "small classes"? How do you avoid creating hundreds of tiny classes?**
> SRP defines "responsibility" as an **axis of change** (one actor), not "one method." Things that change together for the same reason should stay together. Extreme fragmentation is mitigated with the **Facade pattern** — group related micro-classes behind a unified API. The key metric is **cohesion**, not class size.

**Q7. Does Python's duck typing make ISP irrelevant?**
> No — it changes how ISP manifests. Without explicit interfaces, a function expecting `read()`, `write()`, and `close()` forces callers to implement all three even if they only need `read()`. ISP in Python means: (1) Functions should accept the **minimum protocol** they need. (2) Use `typing.Protocol` to formalize these minimal contracts. (3) Design function signatures around what they actually use.

**Q8. How do you test code that follows DIP vs code that doesn't?**
> **Without DIP**: `UserService` creates `MySQLDatabase()` internally → tests need a real MySQL server or ugly monkey-patching.
> **With DIP**: `UserService(db: Database)` → inject `InMemoryDatabase()` or a mock in tests. No external dependencies, fast, deterministic.
> ```python
> # Easy to test with DIP
> def test_user_service():
>     mock_db = InMemoryDatabase()
>     service = UserService(mock_db)
>     assert service.get_user(1) == []
> ```

**Q9. Can you violate OCP while following SRP?**
> Yes. A class can have a single responsibility (SRP ✅) but require modification every time a new variant is needed (OCP ❌). Example: a `TaxCalculator` with one responsibility (calculating tax) but using `if/elif` for each country. Adding a new country modifies the class.

**Q10. What's the difference between DIP and IoC (Inversion of Control)?**
> **DIP** is a principle (depend on abstractions). **IoC** is a broader design pattern where the framework calls your code (Hollywood Principle: "Don't call us, we'll call you"). **DI** is a specific technique to achieve both. DI ⊂ IoC ⊂ DIP conceptually, but DI is the most common way to implement DIP.

---

### 🔴 Level 3: Advanced (MANG / Staff-Level)

**Q11. In a large Python application, how do you enforce DIP without a DI framework?**
> 1. **Constructor injection** — pass dependencies through `__init__` with type hints to `ABC`/`Protocol`.
> 2. **Factory functions** — centralize object creation in a `create_app()` or `Container` that wires everything.
> 3. **Pytest fixtures** — natural DI for testing; fixtures inject dependencies transitively.
> 4. **FastAPI `Depends()`** — framework-level DI with cleanup support via generators.
> 5. **Module-level composition root** — a single entry point (`main.py`) where all dependencies are wired.
>
> Avoid service locators (global registries) — they hide dependencies.

**Q12. How does LSP interact with Python's `raise NotImplementedError` pattern?**
> Raising `NotImplementedError` in a subclass is almost always an **LSP violation**. If client code calls `bird.fly()` on a `Bird` reference and `Ostrich` raises `NotImplementedError`, the program crashes unexpectedly. Solutions:
> - Restructure the hierarchy (`FlyingBird` vs `FlightlessBird`)
> - Use ISP — don't put `fly()` on `Bird` if not all birds fly
> - Use composition — `FlyBehavior` injected into animals that can fly

**Q13. How do SOLID principles apply to microservices architecture?**
> - **SRP** → Each microservice owns one bounded context (User Service, Payment Service)
> - **OCP** → New features as new services, not modifying existing ones; event-driven extensions
> - **LSP** → API versioning — v2 must be backward-compatible with v1 contracts
> - **ISP** → API Gateway exposes only what each client needs (BFF pattern)
> - **DIP** → Services communicate via message contracts/events (abstractions), not direct HTTP calls to specific implementations

**Q14. When should you deliberately violate SOLID?**
> SOLID are **guidelines, not laws**. Legitimate violations:
> - **SRP**: Premature splitting creates unnecessary complexity. A 50-line script doesn't need 10 classes.
> - **OCP**: If there are only 2-3 variants that rarely change, `if/elif` is simpler than a full strategy hierarchy.
> - **LSP**: Performance-critical code may need specialized subclasses that trade substitutability for speed.
> - **ISP**: Over-granular interfaces (1 method each) create explosion of types — group cohesive methods.
> - **DIP**: Simple utility classes (e.g., `json.dumps()`) don't need abstraction layers.
>
> **Apply SOLID at boundaries** (public APIs, module interfaces). Internal implementation can be pragmatic.

**Q15. In a real codebase, how do you identify SRP violations?**
> 1. **"And" test** — if you describe the class with "and", it likely has multiple responsibilities: "This class manages users AND sends emails AND generates reports."
> 2. **Change frequency** — use `git log --stat` to find files that change for unrelated reasons.
> 3. **Import analysis** — if a class imports from 5+ unrelated modules (HTTP, DB, email, cache, queue), it's doing too much.
> 4. **Test pain** — if testing one method requires mocking 10 unrelated dependencies, the class has too many concerns.

**Q16. Design a plugin system that follows all five SOLID principles.**
> ```python
> from abc import ABC, abstractmethod
> from typing import Protocol
>
> # ISP — minimal interface for plugins
> class Plugin(Protocol):
>     name: str
>     def execute(self, data: dict) -> dict: ...
>
> # OCP — new plugins without modifying engine
> # DIP — engine depends on Plugin abstraction
> class PluginEngine:
>     def __init__(self):
>         self._plugins: list[Plugin] = []  # SRP — only orchestrates plugins
>
>     def register(self, plugin: Plugin) -> None:
>         self._plugins.append(plugin)
>
>     def run_pipeline(self, data: dict) -> dict:
>         for plugin in self._plugins:
>             data = plugin.execute(data)  # LSP — any Plugin works here
>         return data
>
> # Adding plugins = adding new classes, ZERO changes to PluginEngine
> class ValidationPlugin:
>     name = "validator"
>     def execute(self, data: dict) -> dict:
>         if "email" not in data:
>             raise ValueError("Email required")
>         return data
>
> class EnrichmentPlugin:
>     name = "enricher"
>     def execute(self, data: dict) -> dict:
>         data["enriched"] = True
>         return data
>
> engine = PluginEngine()
> engine.register(ValidationPlugin())
> engine.register(EnrichmentPlugin())
> result = engine.run_pipeline({"email": "a@b.com"})
> ```

**Q17. How does OCP apply to database migrations?**
> Migrations should be **append-only** (open for extension). Each migration is a new file that extends the schema. You never modify a migration that has already been applied (closed for modification).
> ```
> migrations/
>   001_create_users.py    # Never modified after applying
>   002_add_email_field.py  # New migration = extension
>   003_add_index.py
> ```
> Modifying old migrations breaks existing deployments — the exact problem OCP prevents.

**Q18. How do you apply DIP to third-party libraries?**
> Wrap third-party libraries behind your own abstractions (Anti-Corruption Layer):
> ```python
> # Your abstraction
> class EmailSender(ABC):
>     @abstractmethod
>     def send(self, to: str, subject: str, body: str): ...
>
> # Thin adapter wrapping the third-party library
> class SendGridEmailSender(EmailSender):
>     def __init__(self, api_key: str):
>         self._client = sendgrid.SendGridAPIClient(api_key)
>
>     def send(self, to: str, subject: str, body: str):
>         self._client.send(Mail(to, subject, body))
>
> # Your code NEVER imports sendgrid directly
> # Switching to AWS SES = new class, zero changes to business logic
> ```

---

## Quick Reference — SOLID Violations & Smells

| Principle | Violation Smell | Fix Pattern |
|-----------|----------------|-------------|
| **SRP** | Class described with "and"; changes for multiple reasons | Extract classes, use Facade |
| **OCP** | Adding a feature requires modifying existing `if/elif` | Strategy, Decorator, Plugin, `__init_subclass__` |
| **LSP** | Subclass raises `NotImplementedError` or has surprise side-effects | Restructure hierarchy, use composition |
| **ISP** | Classes implement methods they don't need; `pass` or `raise` stubs | Split into smaller Protocols/ABCs |
| **DIP** | `import concrete_thing` inside high-level module; hard to test | Constructor injection, ABC/Protocol abstractions |

---

*See also: [python_oops.md](./python_oops.md) for OOP fundamentals and internals, and [design_patterns.md](./design_patterns.md) for the 12 essential patterns.*
