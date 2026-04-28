# Python Object-Oriented Programming — Complete MANG Interview Guide

> From fundamentals to advanced internals. Each section includes **theory**, **Python-specific behavior**, **code**, and **gotchas** that interviewers love to test.

---

## 1. Classes & Objects — The Foundation

### What Happens When You Write `class Foo`?

Python classes are **objects themselves** — instances of `type` (the metaclass). When the interpreter hits a `class` statement, it:

1. Creates a new namespace (dict)
2. Executes the class body inside that namespace
3. Calls `type(name, bases, namespace)` to create the class object

```python
# These two are IDENTICAL:
class Dog:
    sound = "woof"

Dog = type('Dog', (), {'sound': 'woof'})
```

### Instance Creation: `__new__` vs `__init__`

| Aspect | `__new__` | `__init__` |
|--------|-----------|------------|
| Purpose | **Creates** the instance | **Initializes** the instance |
| First arg | `cls` (the class) | `self` (the instance) |
| Returns | Must return the instance | Returns `None` |
| When to override | Immutable types, Singletons, caching | Almost always |

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value):
        self.value = value  # WARNING: __init__ runs EVERY time, even on cached instance

a = Singleton(1)
b = Singleton(2)
print(a is b)       # True — same object
print(a.value)      # 2 — __init__ overwrote it!
```

> **Gotcha**: `__init__` runs every time even when `__new__` returns a cached instance. Guard with a flag.

---

## 2. The Four Pillars of OOP

### 2.1 Encapsulation & Data Hiding

Python has **no true private** access — it uses **conventions** and **name mangling**.

| Prefix | Convention | Behavior |
|--------|-----------|----------|
| `name` | Public | Accessible everywhere |
| `_name` | Protected | "Internal use" convention only — still accessible |
| `__name` | Private | **Name mangled** to `_ClassName__name` |

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner            # Public
        self._account_type = "savings" # Protected (convention)
        self.__balance = balance       # Private (name mangled)

    @property
    def balance(self) -> float:
        """Read-only access with validation hook"""
        return self.__balance

    @balance.setter
    def balance(self, amount: float):
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self.__balance = amount

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.__balance += amount

acc = BankAccount("Alice", 1000)
# acc.__balance         → AttributeError
# acc._BankAccount__balance → 1000 (name mangling bypass — DON'T do this)
```

**Interview Follow-up**: *"If Python doesn't have real private, why use `__` at all?"*
> To prevent **accidental name collisions in inheritance**. If `BankAccount` has `__balance` and a subclass also defines `__balance`, they won't clash because they mangle to different names.

#### Properties vs Getters/Setters

```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius

    @property
    def fahrenheit(self) -> float:
        """Computed property — no stored duplicate data"""
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float):
        self._celsius = (value - 32) * 5/9

t = Temperature(100)
print(t.fahrenheit)     # 212.0
t.fahrenheit = 32
print(t._celsius)       # 0.0
```

### 2.2 Abstraction

Hiding complex implementation details, exposing only the **what**, not the **how**.

```python
from abc import ABC, abstractmethod
from typing import Protocol

# --- Approach 1: ABC (Nominal typing — explicit inheritance) ---
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool: ...

    @abstractmethod
    def refund(self, transaction_id: str) -> bool: ...

    def validate_amount(self, amount: float) -> bool:
        """Concrete method — shared logic for free"""
        return amount > 0

class StripeGateway(PaymentGateway):
    def charge(self, amount: float) -> bool:
        return self.validate_amount(amount) and self._call_stripe_api(amount)

    def refund(self, transaction_id: str) -> bool:
        return self._call_stripe_refund(transaction_id)

# --- Approach 2: Protocol (Structural typing — duck typing formalized) ---
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(shape: Drawable) -> None:
    shape.draw()  # Circle works WITHOUT inheriting Drawable

render(Circle())  # ✅ Works — structural compatibility
```

> **MANG Insight**: `Protocol` (PEP 544) is Python's answer to Go's interfaces. No inheritance needed — just matching method signatures. Prefer `Protocol` for loose coupling, `ABC` when you need shared concrete methods.

### 2.3 Inheritance & MRO (Method Resolution Order)

Python uses **C3 Linearization** for method lookup in multiple inheritance.

```python
class Base:
    def greet(self):
        print("Base")

class A(Base):
    def greet(self):
        print("A")
        super().greet()

class B(Base):
    def greet(self):
        print("B")
        super().greet()

class C(A, B):
    def greet(self):
        print("C")
        super().greet()

C().greet()
# Output: C → A → B → Base
# MRO:   C → A → B → Base → object

print(C.__mro__)
# (<class 'C'>, <class 'A'>, <class 'B'>, <class 'Base'>, <class 'object'>)
```

#### The Diamond Problem — Solved by C3

```
      Base
      /  \
     A    B
      \  /
       C
```

Without C3, `Base.greet()` would be called **twice**. C3 ensures each class appears **exactly once** in the MRO.

#### `super()` Is NOT "Call Parent"

`super()` follows the **MRO**, not the direct parent. In class `A`, `super().greet()` calls `B.greet()`, NOT `Base.greet()`.

```python
# super() with arguments (rarely needed, but tested in interviews)
super(A, self).greet()  # Start MRO search AFTER class A
```

#### Mixins — The Pythonic Way to Compose

```python
class JsonSerializerMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class LoggingMixin:
    def log(self, message: str):
        print(f"[{self.__class__.__name__}] {message}")

class User(JsonSerializerMixin, LoggingMixin):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

u = User("Alice", "alice@example.com")
print(u.to_json())  # {"name": "Alice", "email": "alice@example.com"}
u.log("Created")     # [User] Created
```

### 2.4 Polymorphism

Python achieves polymorphism in **three** ways:

```python
# 1. Duck Typing (runtime) — "If it quacks like a duck..."
class Duck:
    def speak(self): return "Quack"

class Dog:
    def speak(self): return "Woof"

def make_speak(animal):
    print(animal.speak())  # No type check — just call it

# 2. Operator Overloading (dunder methods)
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

print(Vector(1, 2) + Vector(3, 4))  # Vector(4, 6)

# 3. Method Overriding (inheritance)
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Circle(Shape):
    def __init__(self, radius): self.radius = radius
    def area(self): return 3.14159 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h

# Uniform interface
shapes: list[Shape] = [Circle(5), Rectangle(3, 4)]
for s in shapes:
    print(s.area())  # Polymorphic dispatch
```

> **Note**: Python does **NOT** support method overloading natively. Use `@singledispatch` or default arguments instead.

---

## 3. Advanced Python OOP Internals

### 3.1 `__slots__` — Memory Optimization

```python
import sys

class WithDict:
    def __init__(self, x, y):
        self.x, self.y = x, y

class WithSlots:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x, self.y = x, y

a = WithDict(1, 2)
b = WithSlots(1, 2)
print(sys.getsizeof(a.__dict__))  # ~104 bytes for the dict alone
# b.__dict__  → AttributeError — no dict exists!
```

| Feature | `__dict__` (default) | `__slots__` |
|---------|---------------------|-------------|
| Memory | ~104 bytes + per attr | Fixed, much less |
| Dynamic attrs | ✅ Can add any | ❌ Only declared |
| Inheritance | Inherited | Must redeclare in subclass |
| Use case | General purpose | Millions of instances |

> **Gotcha**: If any class in the MRO does NOT use `__slots__`, a `__dict__` is still created.

### 3.2 Class, Static, and Instance Methods

```python
class Pizza:
    base_price = 10

    def __init__(self, toppings: list[str]):
        self.toppings = toppings

    def price(self):
        """Instance method — accesses self"""
        return self.base_price + len(self.toppings) * 2

    @classmethod
    def margherita(cls):
        """Factory method — accesses cls, NOT specific instance"""
        return cls(["mozzarella", "tomato"])

    @staticmethod
    def validate_topping(topping: str) -> bool:
        """Utility — no access to cls or self"""
        return topping.lower() not in ["pineapple"]
```

| Type | First arg | Can access instance? | Can access class? | Use case |
|------|-----------|---------------------|-------------------|----------|
| Instance | `self` | ✅ | ✅ (via `self.__class__`) | Most methods |
| Class | `cls` | ❌ | ✅ | Factory methods, alternate constructors |
| Static | None | ❌ | ❌ | Pure utility functions |

### 3.3 Descriptors — The Machinery Behind `@property`

Descriptors are the **protocol** behind `property`, `classmethod`, `staticmethod`, and `__slots__`.

```python
class Validated:
    """A descriptor that enforces type and range validation."""
    def __init__(self, min_val=None, max_val=None):
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name} must be >= {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name} must be <= {self.max_val}")
        setattr(obj, self.storage_name, value)

class Product:
    price = Validated(min_val=0)
    quantity = Validated(min_val=0, max_val=10000)

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price        # Triggers Validated.__set__
        self.quantity = quantity

p = Product("Widget", 9.99, 100)
# p.price = -1  → ValueError: price must be >= 0
```

### 3.4 Metaclasses — Classes of Classes

```python
class SingletonMeta(type):
    """Metaclass that makes any class a Singleton."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, url: str):
        self.url = url

db1 = Database("postgres://localhost")
db2 = Database("mysql://localhost")
print(db1 is db2)  # True
print(db1.url)     # postgres://localhost (first init wins)
```

### 3.5 Dataclasses & `__post_init__`

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)  # Immutable — generates __hash__ automatically
class Money:
    amount: float
    currency: str = "USD"

    def __post_init__(self):
        # Runs after __init__ for validation
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

@dataclass
class Order:
    items: list[str] = field(default_factory=list)  # Mutable default done right
    total: float = field(init=False)  # Computed, not in __init__

    def __post_init__(self):
        self.total = len(self.items) * 9.99
```

| Feature | Regular Class | `@dataclass` | `@dataclass(frozen=True)` |
|---------|--------------|-------------|--------------------------|
| `__init__` | Manual | Auto-generated | Auto-generated |
| `__repr__` | Manual | Auto-generated | Auto-generated |
| `__eq__` | By identity | By value | By value |
| `__hash__` | By identity | Unhashable | Auto-generated |
| Mutability | Mutable | Mutable | Immutable |

### 3.6 Context Managers & `__enter__`/`__exit__`

```python
class DatabaseConnection:
    def __init__(self, url: str):
        self.url = url
        self.connection = None

    def __enter__(self):
        print(f"Connecting to {self.url}")
        self.connection = {"connected": True}  # Simulate
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.connection = None
        return False  # Don't suppress exceptions

with DatabaseConnection("postgres://localhost") as db:
    print(db.connection)  # {'connected': True}
# "Closing connection" — guaranteed cleanup even on exceptions
```

---

## 4. Composition vs Inheritance

This is the **single most asked OOP design question** at MANG interviews.

```python
# ❌ Inheritance nightmare — "Gorilla Banana Problem"
class Animal:
    def eat(self): ...
    def sleep(self): ...
    def move(self): ...

class FlyingAnimal(Animal):
    def fly(self): ...

class SwimmingAnimal(Animal):
    def swim(self): ...

# Duck can fly AND swim — multiple inheritance mess
class Duck(FlyingAnimal, SwimmingAnimal): ...

# ✅ Composition — inject behaviors
class FlyBehavior(Protocol):
    def fly(self) -> str: ...

class SwimBehavior(Protocol):
    def swim(self) -> str: ...

class Wings:
    def fly(self) -> str: return "Flying with wings"

class Fins:
    def swim(self) -> str: return "Swimming with fins"

class Duck:
    def __init__(self, fly_behavior: FlyBehavior, swim_behavior: SwimBehavior):
        self._fly = fly_behavior
        self._swim = swim_behavior

    def perform_fly(self): return self._fly.fly()
    def perform_swim(self): return self._swim.swim()

duck = Duck(Wings(), Fins())
# Easy to test: Duck(MockFly(), MockSwim())
# Easy to extend: Duck(JetPack(), Surfboard())
```

> **Rule of Thumb**: Use inheritance for **"is-a"** with shared implementation. Use composition for **"has-a"** and when behaviors vary independently.

---

## 5. Interview Questions — Tiered by Difficulty

### 🟢 Level 1: Fundamentals (Startup / Phone Screen)

**Q1. What is the difference between a class and an object?**
> A **class** is a blueprint/template. An **object** is a concrete instance created from that blueprint. A class defines attributes and methods; an object holds actual values in memory.

**Q2. Explain `self` in Python. Is it a keyword?**
> `self` is **not a keyword** — it's a convention. It's the first parameter of instance methods and refers to the current instance. You can name it anything (but never should).
> ```python
> class Foo:
>     def bar(this):  # Works but violates PEP 8
>         print(this)
> ```

**Q3. What is the difference between `__init__` and `__new__`?**
> `__new__` **creates** the instance (allocates memory), `__init__` **initializes** it (sets attributes). `__new__` is a static method that returns the instance; `__init__` returns `None`. Override `__new__` for immutable types or singletons.

**Q4. What are class variables vs instance variables?**
> ```python
> class Dog:
>     species = "Canine"  # Class variable — shared by ALL instances
>     def __init__(self, name):
>         self.name = name  # Instance variable — unique per instance
>
> d1 = Dog("Rex")
> d2 = Dog("Max")
> Dog.species = "K9"       # Changes for ALL instances
> d1.species = "Wolf"      # Creates a NEW instance variable on d1, shadows class var
> print(d2.species)        # "K9" — still reads class variable
> ```

**Q5. What is the difference between `==` and `is`?**
> `==` calls `__eq__` and compares **values**. `is` compares **identity** (memory address). Two different objects can be `==` but not `is`.

**Q6. What is `@property` and why use it?**
> `@property` creates a managed attribute with getter/setter/deleter methods. It lets you add validation, computation, or logging without changing the calling code. It follows the **Uniform Access Principle**.

---

### 🟡 Level 2: Intermediate (Mid-Level / Onsite Round 1)

**Q7. Explain Python's MRO and the Diamond Problem.**
> Python uses **C3 Linearization** to compute a deterministic method lookup order. In the diamond pattern (`D(B, C)` where both `B` and `C` inherit `A`), C3 ensures `A` appears **only once** at the end of the MRO. `super()` follows the MRO chain, not the direct parent.

**Q8. What is name mangling? When is it useful?**
> Attributes prefixed with `__` (double underscore) are mangled to `_ClassName__attribute`. This prevents **accidental override** in subclasses, not security. It's useful when building frameworks where subclass attribute collisions would cause bugs.

**Q9. What happens if you define `__eq__` but not `__hash__`?**
> Python sets `__hash__` to `None`, making the object **unhashable**. You can't use it in sets or as dict keys. This is intentional — if two objects are equal, they must have the same hash, and Python can't guarantee that.
> ```python
> class Point:
>     def __init__(self, x, y): self.x, self.y = x, y
>     def __eq__(self, other): return self.x == other.x and self.y == other.y
>
> {Point(1, 2)}  # TypeError: unhashable type: 'Point'
>
>     def __hash__(self): return hash((self.x, self.y))  # Fix
> ```

**Q10. `@classmethod` vs `@staticmethod` — when to use which?**
> `@classmethod` receives the class as first arg → use for **factory methods** and **alternate constructors**. `@staticmethod` receives nothing → use for **utility functions** that don't need class or instance state but logically belong to the class namespace.

**Q11. What is a Descriptor? How does `@property` work internally?**
> A descriptor is any object implementing `__get__`, `__set__`, or `__delete__`. `@property` is syntactic sugar for a descriptor. When you access `obj.x`, Python checks if `type(obj).x` is a **data descriptor** (has `__set__`), then `obj.__dict__['x']`, then **non-data descriptor** (only `__get__`).

**Q12. Explain `__slots__` — benefits and limitations.**
> `__slots__` replaces per-instance `__dict__` with a fixed-size struct, saving ~40-50% memory. Limitations: can't add arbitrary attributes, must redeclare in subclasses, breaks if any base class lacks `__slots__`, incompatible with `__dict__`-based serialization.

**Q13. How do you make an immutable class in Python?**
> Use `@dataclass(frozen=True)`, which generates `__setattr__` and `__delattr__` that raise `FrozenInstanceError`. Alternatively, use `__slots__` + override `__setattr__`. For truly immutable value objects, subclass `tuple` or use `NamedTuple`.

---

### 🔴 Level 3: Advanced (MANG / Staff-Level)

**Q14. What are metaclasses? When would you use one?**
> A metaclass is the class of a class (default is `type`). It controls class **creation**, not instance creation. Use cases: ORM field registration (Django's `Model`), API endpoint registration, automatic method decoration, schema validation. Regular code rarely needs metaclasses — prefer class decorators or `__init_subclass__`.
> ```python
> class RegistryMeta(type):
>     registry = {}
>     def __new__(mcs, name, bases, namespace):
>         cls = super().__new__(mcs, name, bases, namespace)
>         if bases:  # Don't register the base class itself
>             mcs.registry[name] = cls
>         return cls
>
> class Plugin(metaclass=RegistryMeta):
>     pass
>
> class AudioPlugin(Plugin):
>     pass
>
> print(RegistryMeta.registry)  # {'AudioPlugin': <class 'AudioPlugin'>}
> ```

**Q15. Explain `__init_subclass__` and when to prefer it over metaclasses.**
> Introduced in Python 3.6, `__init_subclass__` is a hook called on the **parent** when a child class is created. It covers 90% of metaclass use cases (validation, registration) with far less complexity.
> ```python
> class Serializable:
>     _registry = {}
>
>     def __init_subclass__(cls, type_id: str = None, **kwargs):
>         super().__init_subclass__(**kwargs)
>         if type_id:
>             Serializable._registry[type_id] = cls
>
> class UserEvent(Serializable, type_id="user_event"):
>     pass
>
> print(Serializable._registry)  # {'user_event': <class 'UserEvent'>}
> ```

**Q16. Explain the Descriptor Protocol lookup order.**
> When accessing `obj.attr`, Python's lookup order is:
> 1. **Data descriptor** on `type(obj)` (has `__set__` or `__delete__`)
> 2. Instance `__dict__`
> 3. **Non-data descriptor** on `type(obj)` (only `__get__`)
> 4. `__getattr__` (if defined)
>
> This is why `@property` (a data descriptor) wins over instance dict.

**Q17. How does `super()` work internally? What is the zero-argument form?**
> `super()` (zero-arg, Python 3) uses compiler magic — `__class__` cell variable and the first arg of the enclosing method. `super(CurrentClass, self)` is the explicit form. `super()` returns a **proxy object** that delegates method calls following the MRO of `type(self)`, starting AFTER the class where `super()` is called.

**Q18. Design a thread-safe Singleton that also handles subclassing correctly.**
> ```python
> import threading
>
> class SingletonMeta(type):
>     _instances = {}
>     _lock = threading.Lock()
>
>     def __call__(cls, *args, **kwargs):
>         with cls._lock:
>             if cls not in cls._instances:
>                 instance = super().__call__(*args, **kwargs)
>                 cls._instances[cls] = instance
>         return cls._instances[cls]
>
> class Database(metaclass=SingletonMeta):
>     def __init__(self, url: str):
>         self.url = url
>
> class Cache(metaclass=SingletonMeta):  # Independent singleton
>     def __init__(self, max_size: int):
>         self.max_size = max_size
> ```
> **Why metaclass?** Using `__new__` on the class itself breaks when subclassing — all subclasses share the parent's `_instance`. The metaclass approach gives each class its own entry in the `_instances` dict.

**Q19. Explain the GIL's impact on OOP design in concurrent Python.**
> The GIL (Global Interpreter Lock) means only one thread executes Python bytecode at a time. Impact on OOP:
> - **Single operations** like `self.x = value` are atomic (single bytecode), but compound operations like `self.count += 1` are NOT (read-modify-write).
> - Thread-safe patterns: use `threading.Lock` for mutable shared state, `queue.Queue` for producer-consumer, or `dataclasses(frozen=True)` for immutable objects.
> - For CPU-bound work, use `multiprocessing` (each process has its own GIL) or C extensions that release the GIL.

**Q20. What is `__class_getitem__` and how does it enable generic types?**
> ```python
> class MyList:
>     def __class_getitem__(cls, item):
>         # Called when you write MyList[int]
>         return cls  # Simplified — real generics use typing._GenericAlias
>
> # This is how list[int], dict[str, Any], etc work
> # typing.Generic uses __class_getitem__ under the hood
> ```

**Q21. How would you implement the `__getattr__` / `__getattribute__` chain for a proxy object?**
> ```python
> class Proxy:
>     """Lazy-loading proxy that delegates all attribute access."""
>     def __init__(self, factory):
>         # Use object.__setattr__ to avoid infinite recursion
>         object.__setattr__(self, '_factory', factory)
>         object.__setattr__(self, '_obj', None)
>
>     def _load(self):
>         if object.__getattribute__(self, '_obj') is None:
>             factory = object.__getattribute__(self, '_factory')
>             object.__setattr__(self, '_obj', factory())
>
>     def __getattr__(self, name):
>         self._load()
>         return getattr(self._obj, name)
>
>     def __setattr__(self, name, value):
>         self._load()
>         setattr(self._obj, name, value)
> ```
> **Key distinction**: `__getattribute__` is called on **every** attribute access. `__getattr__` is called only when normal lookup **fails**. Override `__getattribute__` with extreme caution — infinite recursion is easy.

**Q22. Compare `ABC`, `Protocol`, and Duck Typing — when do you use each?**
> | Approach | Typing | Coupling | Error Timing | Use When |
> |----------|--------|----------|-------------|----------|
> | Duck Typing | None | Loosest | Runtime | Quick scripts, internal code |
> | `Protocol` | Structural | Loose | Mypy (static) | Public APIs, type-checked codebases |
> | `ABC` | Nominal | Tight | Instantiation | When you need shared concrete methods or want to enforce a contract at class creation |

**Q23. How does Python garbage collection work with circular references in OOP?**
> Python uses **reference counting** as primary GC. When an object's refcount hits 0, it's deallocated immediately. But circular references (e.g., parent ↔ child) never reach 0. Python's **cyclic GC** (generational collector) periodically scans for unreachable cycles. OOP implications:
> - `__del__` finalizers on objects in cycles may cause **resurrection** — the GC can't safely call them.
> - Use `weakref.ref` or `weakref.WeakValueDictionary` for caches and observer patterns to avoid cycles.
> - `with` statements (context managers) are preferred over `__del__` for cleanup.

**Q24. Design a class that prevents subclassing (like `final` in Java).**
> ```python
> # Approach 1: __init_subclass__
> class Final:
>     def __init_subclass__(cls, **kwargs):
>         raise TypeError(f"Cannot subclass {cls.__bases__[0].__name__}")
>
> # class Child(Final):  →  TypeError: Cannot subclass Final
>
> # Approach 2: Metaclass (more robust)
> class FinalMeta(type):
>     def __new__(mcs, name, bases, namespace):
>         for base in bases:
>             if isinstance(base, FinalMeta) and base is not Final:
>                 raise TypeError(f"Cannot subclass final class {base.__name__}")
>         return super().__new__(mcs, name, bases, namespace)
>
> # Approach 3: typing.final decorator (static check only, with mypy)
> from typing import final
>
> @final
> class Config:
>     pass
> ```

**Q25. Explain Cooperative Multiple Inheritance and how to design for it.**
> ```python
> class Base:
>     def __init__(self, **kwargs):
>         # Base eats remaining kwargs — stops the chain
>         super().__init__()
>
> class A(Base):
>     def __init__(self, x, **kwargs):
>         self.x = x
>         super().__init__(**kwargs)  # Forward unknown kwargs
>
> class B(Base):
>     def __init__(self, y, **kwargs):
>         self.y = y
>         super().__init__(**kwargs)
>
> class C(A, B):
>     def __init__(self, x, y, z, **kwargs):
>         self.z = z
>         super().__init__(x=x, y=y, **kwargs)
>
> c = C(x=1, y=2, z=3)
> print(c.x, c.y, c.z)  # 1 2 3
> ```
> **Rules for cooperative MI**: (1) Always use `**kwargs` and forward them. (2) Always call `super().__init__()`. (3) Use keyword-only arguments. (4) Have a base class that terminates the chain.

---

## 6. Common OOP Design Traps (Cross-Questions)

| Trap | Example | Fix |
|------|---------|-----|
| Mutable default args | `def __init__(self, items=[])` | Use `items=None`; `self.items = items or []` |
| God class | 2000-line `UserManager` that does everything | Split by SRP (see `solid_principles.md`) |
| Inheritance for code reuse | `Stack(list)` — exposes `insert`, `sort`, etc. | Composition: wrap a `list` internally |
| `isinstance` checks everywhere | `if isinstance(x, Dog): ...` | Polymorphism — define methods on the interface |
| Circular imports | `models.py` ↔ `services.py` | Use `TYPE_CHECKING` guard or restructure |
| Forgetting `super().__init__()` | Breaks cooperative MI chain | Always call it, even if parent is `object` |

---

## 7. Quick Reference — Key Dunder Methods

| Method | Trigger | Example |
|--------|---------|---------|
| `__init__` | `MyClass()` | Initialize attributes |
| `__new__` | Before `__init__` | Singleton, immutable types |
| `__repr__` | `repr(obj)` | Unambiguous, for developers |
| `__str__` | `str(obj)`, `print()` | Readable, for users |
| `__eq__` / `__hash__` | `==`, `set()`, `dict` | Value equality |
| `__lt__` / `__le__` / etc. | `<`, `<=` | Use `@functools.total_ordering` |
| `__add__` / `__radd__` | `+` | `radd` when left operand doesn't support it |
| `__len__` / `__getitem__` | `len()`, `obj[key]` | Make objects iterable/indexable |
| `__contains__` | `in` operator | Custom membership test |
| `__call__` | `obj()` | Make instances callable |
| `__enter__` / `__exit__` | `with` statement | Resource management |
| `__get__` / `__set__` | Descriptor protocol | `@property` internals |
| `__class_getitem__` | `MyClass[int]` | Generic types |
| `__init_subclass__` | `class Child(Parent):` | Hook on subclass creation |

---

*See also: [design_patterns.md](./design_patterns.md) for the 12 essential patterns, and [solid_principles.md](./solid_principles.md) for SOLID with Python examples.*
