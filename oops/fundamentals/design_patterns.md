```markdown
# Top 12 Design Patterns — MAANG Preparation

Design patterns are typical structural layouts to solve repeated software engineering problems.

## Creational Patterns
1. **Singleton**: Ensures a class has only one instance.
```python
class Database:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

2. **Factory Method**: Interface for creating objects, letting subclasses decide the type.
```python
class Creator(ABC):
    @abstractmethod
    def factory_method(self): pass

class BoatCreator(Creator):
    def factory_method(self): return Boat()
```

3. **Builder**: Constructs complex objects step by step.
```python
query = QueryBuilder().select("*").from_table("users").where("id=1").build()
```

## Structural Patterns
4. **Adapter**: Bridges incompatible interfaces.
```python
class Adapter(Target):
    def request(self):
        return self.adaptee.specific_request()
```

5. **Decorator**: Adds behavior to objects dynamically.
```python
def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache: cache[args] = func(*args)
        return cache[args]
    return wrapper
```

6. **Facade**: Simple interface to a complex subsystem.
```python
class CloudDeploymentFacade:
    def deploy(self):
        S3().upload()
        EC2().provision()
        Route53().update_dns()
```

7. **Composite**: Treats individual objects and compositions uniformly.
```python
class Directory(Component):
    def operation(self):
        for child in self.children: child.operation()
```

8. **Proxy**: Placeholder to control access.
```python
class CachedImageProxy:
    def display(self):
        if not self.real_image: self.real_image = RealImage(self.filename)
        self.real_image.display()
```

## Behavioral Patterns
9. **Strategy**: Interchangeable algorithms at runtime.
```python
class Order:
    def process(self, payment_strategy):
        payment_strategy.pay(self.amount)
```

10. **Observer**: One-to-many notification dependency.
```python
class Subject:
    def notify(self, data):
        for observer in self._observers: observer.update(data)
```

11. **State**: Changes behavior when internal state changes.
```python
class Document:
    def publish(self):
        self.state.publish(self) # State might be Draft, Review, or Published
```

```markdown
12. **Command**: Encapsulates a request as an object to support undo/redo.
```python
class Invoker:
    def run(self, command):
        command.execute()
        self.history.append(command)
    def undo(self):
        self.history.pop().undo()
```
```
```

---

## MAANG Cross-Examination Questions

**Q1. Singletons are often considered an "anti-pattern." Why?**
> **Answer**: They act as global variables, making unit testing difficult due to state bleeding and hidden coupling. Use Dependency Injection instead.

**Q2. Strategy vs State?**
> **Answer**: **Strategy** is about *how* a task is done (client chooses). **State** is about *what* an object is (object transitions itself).

**Q3. Decorator vs Proxy?**
> **Answer**: **Decorator** adds features; **Proxy** manages access/lifecycle.

**Q4. Factory Method vs Abstract Factory?**
> **Answer**: Factory Method creates *one* product; Abstract Factory creates *families* of related products.

**Q5. The "Lapsed Listener" problem?**
> **Answer**: Memory leaks where subjects hold strong references to dead observers. Solve with `weakref` in Python.

**Q6. Undo/Redo implementation?**
> **Answer**: **Command Pattern**. Store executed commands in a stack; pop and call `undo()` to revert.

