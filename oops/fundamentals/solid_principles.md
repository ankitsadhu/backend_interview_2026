# SOLID Principles — MAANG Preparation

SOLID is an acronym for five design principles intended to make software designs more understandable, flexible, and maintainable.

1. **S - Single Responsibility Principle (SRP)**
   - *Definition*: A class should have one, and only one, reason to change.
   - *Example*: An `Employee` class should only hold employee data. Saving the employee to a database should be handled by a separate `EmployeeRepository` class.

2. **O - Open/Closed Principle (OCP)**
   - *Definition*: Software entities should be open for extension, but closed for modification.
   - *Example*: Instead of modifying a `DiscountCalculator` with a massive `if/else` block whenever a new discount type is added, define an interface `DiscountStrategy` and create new classes for new discounts.

3. **L - Liskov Substitution Principle (LSP)**
   - *Definition*: Subtypes must be substitutable for their base types without altering the correctness of the program.
   - *Example*: If `Ostrich` inherits from `Bird`, but `Bird` has a `fly()` method that `Ostrich` necessarily fails on (raises NotImplementedError), you have violated LSP. The abstraction is wrong.

4. **I - Interface Segregation Principle (ISP)**
   - *Definition*: Clients should not be forced to depend on interfaces they do not use.
   - *Example*: Instead of a massive `IMachine` interface with `print()`, `scan()`, and `fax()`, break it up into `IPrinter`, `IScanner`, and `IFax`. A dumb printer only needs to implement `IPrinter`.

5. **D - Dependency Inversion Principle (DIP)**
   - *Definition*: High-level modules should not depend on low-level modules. Both should depend on abstractions.
   - *Example*: A `PaymentProcessor` shouldn't directly instantiate a `StripeAPI` class. It should take an `IPaymentGateway` interface via its constructor (Dependency Injection).

---

## MAANG Cross-Examination Questions

**Q1. You implemented a `Rectangle` class and then a `Square` class that inherits from it. To ensure a square keeps equal sides, you overrode `set_width()` to also set the height. What principle did you violate and why?**
> **Answer**: The **Liskov Substitution Principle (LSP)**. If the client code expects a `Rectangle`, it assumes that changing the width will *not* change the height (`assert area == new_width * old_height`). Because `Square` silently changes the height, passing a `Square` where a `Rectangle` is expected will break client code logic. A Square is mathematically a Rectangle, but behaviorally in code, it is not a direct substitute if mutability is involved.

**Q2. How does the Open/Closed Principle (OCP) relate to the Strategy Pattern?**
> **Answer**: The Strategy Pattern is a primary mechanism for achieving OCP. By wrapping an algorithm or logic block inside an interface (Strategy), you can add entirely new behaviors (Open for extension) without ever touching the core context class that uses those strategies (Closed for modification). 

**Q3. If applying the Single Responsibility Principle results in dozens of tiny, single-method classes, isn't the system harder to understand?**
> **Answer**: This is a classic trade-off question. Yes, extreme fragmentation leads to "spaghetti architecture" where the cognitive load shifts from "understanding a massive class" to "understanding how 50 tiny classes interact." The key is cohesion: things that change together for the same business reason should stay together. A "responsibility" is an axis of change, not necessarily a single method. We mitigate fragmentation by using the **Facade pattern** to group these cohesive tiny classes under a clean, unified API for clients.

**Q4. Explain practical ways to achieve Dependency Inversion Configuration in a large Python application.**
> **Answer**: In Python, we often achieve this via **Dependency Injection (DI)**. Instead of hardcoding `db = PostgresDb()` inside an overriding service class, we pass the db connection through `def __init__(self, db: DatabaseABC):`. In large frameworks, we use DI containers (like `dependency-injector` package) or built-in context dependency handling (like Pytest fixtures or FastAPI `Depends`) to wire dependencies at runtime based on configuration, rather than instantiation at the call site.

**Q5. Does Python's "Duck Typing" make Interface Segregation Principle (ISP) irrelevant?**
> **Answer**: It changes how ISP manifests, but it doesn't make it irrelevant. Python doesn't force explicit `implements` keywords, but if a function expects a duck-typed object to have `read()`, `write()`, and `close()` methods, but the user passes an object that only supports `read()`, it will crash at runtime. ISP in Python means designing functions and classes to explicitly check for, or expect, the *minimum required protocol* (using `typing.Protocol` is a great modern way to enforce ISP structurally in Python).
