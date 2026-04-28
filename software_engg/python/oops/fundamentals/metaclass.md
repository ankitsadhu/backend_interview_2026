A metaclass is **the class of a class**.

Just as an object is an instance of a class, a **class is an instance of a metaclass**.

```python
x = 42
type(x)        # <class 'int'>    → int is x's class

type(int)      # <class 'type'>   → type is int's metaclass
type(str)      # <class 'type'>
type(list)     # <class 'type'>
```

`type` is the default metaclass for every class in Python.

---

### What does a metaclass control?

When Python sees:
```python
class Foo:
    pass
```

It's actually calling:
```python
Foo = type('Foo', (object,), {})
#          name    bases      namespace dict
```

A metaclass lets you **intercept and customize this class creation**.

---

### Simple example

```python
class UpperMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Force all method names to uppercase
        upper_ns = {k.upper(): v for k, v in namespace.items()}
        return super().__new__(mcs, name, bases, upper_ns)

class MyClass(metaclass=UpperMeta):
    def hello(self):
        return "hi"

obj = MyClass()
obj.HELLO()   # works
obj.hello()   # AttributeError
```

---

### The hierarchy

```
type        ← metaclass (class of classes)
  └── int   ← class
        └── 42  ← object
```

Everything in Python is an object — including classes. Metaclasses are just the next level up.

---

### When do you actually use this?

Rarely in application code. Common real-world uses:
- **ORMs** — Django/SQLAlchemy use metaclasses to turn class attributes into DB columns
- **API validation** — auto-registering subclasses
- **Abstract base classes** — `ABCMeta` enforces `@abstractmethod`

In modern Python, most metaclass use cases are replaced by `__init_subclass__` or class decorators, which are simpler.


## `__init_subclass__`

Whenever a class is **subclassed**, Python automatically calls `__init_subclass__` on the parent.

```python
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print(f"{cls.__name__} just subclassed Base")

class Foo(Base):   # prints: "Foo just subclassed Base"
    pass

class Bar(Base):   # prints: "Bar just subclassed Base"
    pass
```

`cls` here is the **child class** being created, not the parent.

---

### Practical example — auto-registry

A common metaclass pattern was maintaining a registry of all subclasses:

```python
# Old way — needed a metaclass
class PluginMeta(type):
    registry = {}
    def __new__(mcs, name, bases, ns):
        cls = super().__new__(mcs, name, bases, ns)
        mcs.registry[name] = cls
        return cls

# New way — __init_subclass__
class Plugin:
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin._registry[cls.__name__] = cls

class PDFPlugin(Plugin): pass
class CSVPlugin(Plugin): pass

print(Plugin._registry)
# {'PDFPlugin': <class 'PDFPlugin'>, 'CSVPlugin': <class 'CSVPlugin'>}
```

Same result, no metaclass needed.

---

### You can also pass keyword arguments

```python
class Animal:
    def __init_subclass__(cls, sound, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.sound = sound

class Dog(Animal, sound="woof"): pass
class Cat(Animal, sound="meow"): pass

Dog.sound  # "woof"
Cat.sound  # "meow"
```

---

### Summary

| | Metaclass | `__init_subclass__` |
|---|---|---|
| Complexity | High | Low |
| Hook point | Class creation | Subclassing |
| Use case | Deep class machinery | Most common patterns |

If you just need to **react when someone subclasses you**, `__init_subclass__` is almost always the right tool.