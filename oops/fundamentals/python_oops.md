```markdown
# Python Object-Oriented Programming (OOP) — MAANG Preparation

## 1. The Four Pillars of OOP

### 1.1 Encapsulation & Data Hiding
Encapsulation bundles data and methods, restricting direct access to prevent accidental modification.
```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self._status = "active"       # Protected: Internal use convention
        self.__balance = balance      # Private: Triggers Name Mangling (_BankAccount__balance)

    @property
    def balance(self):
        """Getter with logic"""
        return self.__balance

    @balance.setter
    def balance(self, amount):
        """Setter with validation"""
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self.__balance = amount
```

### 1.2 Abstraction
Hiding complex implementation details and showing only necessary features using Abstract Base Classes (ABC).
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Square(Shape):
    def __init__(self, side): self.side = side
    def area(self): return self.side ** 2
```

### 1.3 Inheritance & Method Resolution Order (MRO)
Python uses **C3 Linearization** to determine the search order in multiple inheritance.
```python
class Base:
    def action(self): print("Base")

class A(Base):
    def action(self): print("A"); super().action()

class B(Base):
    def action(self): print("B"); super().action()

class Child(A, B):
    def action(self): print("Child"); super().action()

# MRO: Child -> A -> B -> Base -> object
```

### 1.4 Polymorphism
The ability of different types to be treated as the same type through a common interface (Duck Typing).
```python
def calculate_area(shapes: list[Shape]):
    for shape in shapes:
        print(shape.area()) # Same call, different behavior based on object type
```

---

## 2. Advanced Pythonic Concepts

### Class vs Static Methods
- **`@classmethod`**: Receives the class (`cls`) as the first argument. Used for factory methods.
- **`@staticmethod`**: No implicit first argument. Used for utility functions related to the class.

### Memory Optimization: `__slots__`
By default, Python uses `__dict__` for attributes. `__slots__` reserves space for a fixed set of attributes, significantly reducing memory footprint for millions of instances.
```python
class Point:
    __slots__ = ('x', 'y') # No __dict__ created
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

---

## 3. MAANG Interview Deep-Dives

**Q: Composition vs. Inheritance?**
> **Answer**: Inheritance is "is-a" (tight coupling); Composition is "has-a" (loose coupling). **Prefer Composition** to build complex logic by combining simple objects, making the system more flexible and easier to test.

**Q: How to implement a Thread-Safe Singleton?**
```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance
```

**Q: Explain SOLID in Python.**
- **S**: One class, one responsibility.
- **O**: Open for extension (inheritance/plugins), closed for modification.
- **L**: Subclasses must be usable in place of their parent class without errors.
- **I**: Use small, specific interfaces (Duck Typing makes this natural in Python).
- **D**: Depend on abstractions (ABCs), not concrete implementations.
```
