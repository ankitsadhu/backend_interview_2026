# Design Patterns — Complete MANG Interview Guide (Python)

> The **essential** design patterns every backend engineer must know, with Python-specific implementations, real-world analogies, violation → fix examples, and tiered interview questions (Basic → MANG).

---

## Table of Contents

1. [What Are Design Patterns?](#1-what-are-design-patterns)
2. [Creational Patterns](#2-creational-patterns) — Singleton, Factory Method, Abstract Factory, Builder, Prototype
3. [Structural Patterns](#3-structural-patterns) — Adapter, Decorator, Facade, Proxy, Composite, Flyweight
4. [Behavioral Patterns](#4-behavioral-patterns) — Strategy, Observer, State, Command, Chain of Responsibility, Template Method, Iterator
5. [OOP Interview Questions — Basic to MANG](#5-oop-interview-questions--basic-to-mang)
6. [Pattern Selection Cheat Sheet](#6-pattern-selection-cheat-sheet)
7. [Anti-Patterns to Avoid](#7-anti-patterns-to-avoid)

---

## 1. What Are Design Patterns?

Design patterns are **proven, reusable solutions** to common software design problems. They are NOT code — they are **templates** for solving recurring architectural challenges.

### Three Categories

| Category | Purpose | Examples |
|----------|---------|---------|
| **Creational** | Control **object creation** mechanisms | Singleton, Factory, Builder, Prototype |
| **Structural** | Compose classes/objects into **larger structures** | Adapter, Decorator, Facade, Proxy |
| **Behavioral** | Define **communication** between objects | Strategy, Observer, State, Command |

> **Interview Tip**: Interviewers don't want textbook definitions. They want you to say *"I used Strategy pattern in X situation because Y"* — always tie patterns to **real problems**.

---

## 2. Creational Patterns

### 2.1 Singleton — "Exactly One Instance"

> **Intent**: Ensure a class has only one instance and provide a global point of access.

#### When to Use
- Database connection pools
- Configuration managers
- Logger instances
- Thread pools

#### ❌ Naive Approach — Broken with Threads

```python
class NaiveSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Problem: In multithreaded code, two threads can both see _instance as None
# and create two separate instances (race condition)
```

#### ✅ Thread-Safe Singleton — Metaclass Approach

```python
import threading

class SingletonMeta(type):
    """Metaclass-based Singleton — handles subclassing correctly."""
    _instances: dict = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class DatabasePool(metaclass=SingletonMeta):
    def __init__(self, url: str, pool_size: int = 5):
        self.url = url
        self.pool_size = pool_size
        self._connections = []

    def get_connection(self):
        return f"Connection to {self.url}"

# Usage
db1 = DatabasePool("postgres://localhost", pool_size=10)
db2 = DatabasePool("mysql://localhost")  # Ignored — returns existing instance
print(db1 is db2)       # True
print(db1.url)           # postgres://localhost
```

#### ✅ Pythonic Singleton — Module-Level (Simplest)

```python
# config.py — The module IS the singleton
class _Config:
    def __init__(self):
        self.debug = False
        self.db_url = "postgres://localhost"

config = _Config()  # Single instance created at import time

# Usage elsewhere:
# from config import config
# config.debug = True
```

> **MANG Insight**: In real Python codebases, **module-level singletons** are most common (Django's `settings`, Flask's `app`). Metaclass singletons are for cases where you need lazy initialization or subclassing.

#### ✅ Singleton via `__init_subclass__` + Decorator

```python
import threading
from functools import wraps

def singleton(cls):
    """Decorator-based singleton — clean and simple."""
    instances = {}
    lock = threading.Lock()

    @wraps(cls)
    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class AppConfig:
    def __init__(self, env: str = "production"):
        self.env = env

c1 = AppConfig("dev")
c2 = AppConfig("staging")
print(c1 is c2)  # True — but note: c1 is NOT an instance of AppConfig anymore!
# isinstance(c1, AppConfig) → TypeError (AppConfig is now a function)
```

#### Real-World Analogy
A country has **one president** at a time. No matter how many citizens ask for "the president," they all get the same person.

---

### 2.2 Factory Method — "Let Subclasses Decide"

> **Intent**: Define an interface for creating objects, but let subclasses decide which class to instantiate.

#### ❌ Without Factory — Hardcoded `if/elif`

```python
class Notification:
    def send(self, message: str):
        ...

class EmailNotification(Notification):
    def send(self, message: str):
        print(f"📧 Email: {message}")

class SMSNotification(Notification):
    def send(self, message: str):
        print(f"📱 SMS: {message}")

class PushNotification(Notification):
    def send(self, message: str):
        print(f"🔔 Push: {message}")

# ❌ Adding a new type requires modifying this function (violates OCP)
def create_notification(channel: str) -> Notification:
    if channel == "email":
        return EmailNotification()
    elif channel == "sms":
        return SMSNotification()
    elif channel == "push":
        return PushNotification()
    raise ValueError(f"Unknown channel: {channel}")
```

#### ✅ Factory Method Pattern

```python
from abc import ABC, abstractmethod

class NotificationFactory(ABC):
    """Creator — declares the factory method."""

    @abstractmethod
    def create_notification(self) -> Notification:
        """Factory method — subclasses override this."""
        ...

    def notify(self, message: str):
        """Template method — uses the factory method."""
        notification = self.create_notification()
        notification.send(message)

class EmailFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return EmailNotification()

class SMSFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return SMSNotification()

# Adding Slack = new factory + new notification class, ZERO changes to existing code
class SlackNotification(Notification):
    def send(self, message: str):
        print(f"💬 Slack: {message}")

class SlackFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return SlackNotification()
```

#### ✅ Pythonic Factory — Registry Pattern

```python
class NotificationRegistry:
    """Auto-registration factory using __init_subclass__."""
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, channel: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if channel:
            NotificationRegistry._registry[channel] = cls

    @classmethod
    def create(cls, channel: str, **kwargs) -> "NotificationRegistry":
        if channel not in cls._registry:
            raise ValueError(f"Unknown channel: {channel}")
        return cls._registry[channel](**kwargs)

    def send(self, message: str):
        raise NotImplementedError

class Email(NotificationRegistry, channel="email"):
    def send(self, message: str):
        print(f"📧 {message}")

class SMS(NotificationRegistry, channel="sms"):
    def send(self, message: str):
        print(f"📱 {message}")

# Usage — no if/elif, auto-registered
notif = NotificationRegistry.create("email")
notif.send("Hello!")  # 📧 Hello!
```

#### Real-World Analogy
A **hiring manager** (factory) doesn't know the exact candidate they'll hire. They define the job requirements (interface), and the recruiting process (subclass) decides the actual hire.

---

### 2.3 Abstract Factory — "Families of Related Objects"

> **Intent**: Create families of related objects without specifying their concrete classes.

```python
from abc import ABC, abstractmethod

# --- Abstract Products ---
class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

class TextInput(ABC):
    @abstractmethod
    def render(self) -> str: ...

class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str: ...

# --- Concrete Products: Material Design ---
class MaterialButton(Button):
    def render(self) -> str: return "[ Material Button ]"

class MaterialTextInput(TextInput):
    def render(self) -> str: return "| Material Input |"

class MaterialCheckbox(Checkbox):
    def render(self) -> str: return "[✓] Material Checkbox"

# --- Concrete Products: iOS Design ---
class IOSButton(Button):
    def render(self) -> str: return "( iOS Button )"

class IOSTextInput(TextInput):
    def render(self) -> str: return "[ iOS Input ]"

class IOSCheckbox(Checkbox):
    def render(self) -> str: return "(●) iOS Checkbox"

# --- Abstract Factory ---
class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_text_input(self) -> TextInput: ...
    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

class MaterialFactory(UIFactory):
    def create_button(self) -> Button: return MaterialButton()
    def create_text_input(self) -> TextInput: return MaterialTextInput()
    def create_checkbox(self) -> Checkbox: return MaterialCheckbox()

class IOSFactory(UIFactory):
    def create_button(self) -> Button: return IOSButton()
    def create_text_input(self) -> TextInput: return IOSTextInput()
    def create_checkbox(self) -> Checkbox: return IOSCheckbox()

# --- Client Code — works with ANY factory ---
def render_form(factory: UIFactory):
    button = factory.create_button()
    text_input = factory.create_text_input()
    checkbox = factory.create_checkbox()
    print(button.render(), text_input.render(), checkbox.render())

render_form(MaterialFactory())  # All Material components
render_form(IOSFactory())        # All iOS components
```

> **Factory Method vs Abstract Factory**: Factory Method creates **one product**. Abstract Factory creates **families of related products** that must be used together.

---

### 2.4 Builder — "Complex Object Construction"

> **Intent**: Separate the construction of a complex object from its representation.

#### ❌ Telescoping Constructor Anti-Pattern

```python
# How many args is too many? This is unreadable.
query = DatabaseQuery("users", ["name", "email"], "age > 18",
                      "name ASC", 100, 0, True, False, "read_replica")
```

#### ✅ Builder Pattern

```python
from dataclasses import dataclass, field

@dataclass
class DatabaseQuery:
    table: str
    columns: list[str] = field(default_factory=lambda: ["*"])
    where: str = ""
    order_by: str = ""
    limit: int = 0
    offset: int = 0
    distinct: bool = False

    def to_sql(self) -> str:
        sql = f"SELECT {'DISTINCT ' if self.distinct else ''}"
        sql += ", ".join(self.columns)
        sql += f" FROM {self.table}"
        if self.where:
            sql += f" WHERE {self.where}"
        if self.order_by:
            sql += f" ORDER BY {self.order_by}"
        if self.limit:
            sql += f" LIMIT {self.limit}"
        if self.offset:
            sql += f" OFFSET {self.offset}"
        return sql

class QueryBuilder:
    """Fluent builder — method chaining for readable construction."""

    def __init__(self, table: str):
        self._query = DatabaseQuery(table=table)

    def select(self, *columns: str) -> "QueryBuilder":
        self._query.columns = list(columns)
        return self

    def where(self, condition: str) -> "QueryBuilder":
        self._query.where = condition
        return self

    def order_by(self, column: str) -> "QueryBuilder":
        self._query.order_by = column
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._query.limit = n
        return self

    def offset(self, n: int) -> "QueryBuilder":
        self._query.offset = n
        return self

    def distinct(self) -> "QueryBuilder":
        self._query.distinct = True
        return self

    def build(self) -> DatabaseQuery:
        return self._query

# Usage — reads like English
query = (
    QueryBuilder("users")
    .select("name", "email")
    .where("age > 18")
    .order_by("name ASC")
    .limit(100)
    .distinct()
    .build()
)
print(query.to_sql())
# SELECT DISTINCT name, email FROM users WHERE age > 18 ORDER BY name ASC LIMIT 100
```

#### Real-World Analogy
Ordering a **custom burger**: you choose the bun, patty, toppings, sauce step by step. The builder assembles them into the final product.

---

### 2.5 Prototype — "Clone Existing Objects"

> **Intent**: Create new objects by copying an existing object (prototype) instead of building from scratch.

```python
import copy
from dataclasses import dataclass, field

@dataclass
class ServerConfig:
    host: str
    port: int
    ssl: bool
    middleware: list[str] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)

    def clone(self) -> "ServerConfig":
        """Deep copy — nested mutables are independent."""
        return copy.deepcopy(self)

# Base template
production = ServerConfig(
    host="prod.example.com",
    port=443,
    ssl=True,
    middleware=["auth", "logging", "rate_limit"],
    headers={"X-Environment": "production"}
)

# Clone and customize — much faster than building from scratch
staging = production.clone()
staging.host = "staging.example.com"
staging.headers["X-Environment"] = "staging"

dev = production.clone()
dev.host = "localhost"
dev.port = 8000
dev.ssl = False
dev.middleware.remove("rate_limit")

# Originals are NOT affected
print(production.middleware)  # ['auth', 'logging', 'rate_limit']
print(dev.middleware)          # ['auth', 'logging']
```

> **Key**: Always use `copy.deepcopy()` for objects with mutable nested attributes. Shallow copy (`copy.copy()`) shares references to nested objects.

---

## 3. Structural Patterns

### 3.1 Adapter — "Make Incompatible Interfaces Work Together"

> **Intent**: Convert the interface of a class into another interface clients expect. Lets classes work together that couldn't otherwise because of incompatible interfaces.

```python
from abc import ABC, abstractmethod
import json
import xml.etree.ElementTree as ET

# --- Target Interface (what our system expects) ---
class DataParser(ABC):
    @abstractmethod
    def parse(self, raw_data: str) -> dict:
        """All parsers must return a dict."""
        ...

# --- Adaptee (third-party library with incompatible interface) ---
class LegacyXMLProcessor:
    """Old library that returns XML ElementTree, not dict."""
    def process_xml(self, xml_string: str) -> ET.Element:
        return ET.fromstring(xml_string)

# --- Adapter ---
class XMLParserAdapter(DataParser):
    """Wraps LegacyXMLProcessor to match DataParser interface."""
    def __init__(self):
        self._processor = LegacyXMLProcessor()

    def parse(self, raw_data: str) -> dict:
        root = self._processor.process_xml(raw_data)
        return self._element_to_dict(root)

    def _element_to_dict(self, element: ET.Element) -> dict:
        result = {}
        for child in element:
            result[child.tag] = child.text
        return result

class JSONParser(DataParser):
    def parse(self, raw_data: str) -> dict:
        return json.loads(raw_data)

# --- Client code — works with any DataParser ---
def process_data(parser: DataParser, data: str):
    result = parser.parse(data)
    print(f"Parsed: {result}")

# Both work through the same interface
process_data(JSONParser(), '{"name": "Alice"}')
process_data(XMLParserAdapter(), '<user><name>Alice</name></user>')
```

#### Real-World Analogy
A **power adapter** lets you plug a US device into a European outlet. The device and outlet don't change — the adapter bridges the gap.

---

### 3.2 Decorator — "Add Behavior Dynamically"

> **Intent**: Attach additional responsibilities to an object dynamically. An alternative to subclassing for extending functionality.

#### ❌ Subclassing Explosion

```python
# Want: logging + caching + retry + auth for an API client
# With inheritance: LoggingCachingRetryAuthAPIClient ???
# Every combination = another subclass. 4 features = 16 possible combinations!
```

#### ✅ Decorator Pattern — Object Composition

```python
from abc import ABC, abstractmethod
import time
import functools

class DataSource(ABC):
    @abstractmethod
    def read(self) -> str: ...

    @abstractmethod
    def write(self, data: str) -> None: ...

class FileDataSource(DataSource):
    def __init__(self, filename: str):
        self.filename = filename
        self._data = ""

    def read(self) -> str:
        return self._data

    def write(self, data: str) -> None:
        self._data = data

# --- Decorators (wrap DataSource, ARE DataSource) ---
class DataSourceDecorator(DataSource):
    """Base decorator — delegates everything to wrapped source."""
    def __init__(self, source: DataSource):
        self._source = source

    def read(self) -> str:
        return self._source.read()

    def write(self, data: str) -> None:
        self._source.write(data)

class EncryptionDecorator(DataSourceDecorator):
    def read(self) -> str:
        data = super().read()
        return self._decrypt(data)

    def write(self, data: str) -> None:
        super().write(self._encrypt(data))

    def _encrypt(self, data: str) -> str:
        return data[::-1]  # Simple reversing for demo

    def _decrypt(self, data: str) -> str:
        return data[::-1]

class CompressionDecorator(DataSourceDecorator):
    def read(self) -> str:
        data = super().read()
        return self._decompress(data)

    def write(self, data: str) -> None:
        super().write(self._compress(data))

    def _compress(self, data: str) -> str:
        return f"compressed({data})"

    def _decompress(self, data: str) -> str:
        return data.replace("compressed(", "").rstrip(")")

class LoggingDecorator(DataSourceDecorator):
    def read(self) -> str:
        print(f"[LOG] Reading data...")
        result = super().read()
        print(f"[LOG] Read {len(result)} chars")
        return result

    def write(self, data: str) -> None:
        print(f"[LOG] Writing {len(data)} chars...")
        super().write(data)

# --- Stack decorators like Lego blocks ---
source = FileDataSource("data.txt")
source = LoggingDecorator(source)         # Add logging
source = EncryptionDecorator(source)      # Add encryption
source = CompressionDecorator(source)     # Add compression

source.write("Hello, World!")
print(source.read())  # "Hello, World!" — each layer unwraps
```

#### ✅ Python-Native Decorators (Function-Based)

```python
import functools
import time
import logging

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = delay * (2 ** attempt)
                    logging.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
        return wrapper
    return decorator

def cache(ttl_seconds: int = 60):
    """Simple TTL cache decorator."""
    def decorator(func):
        _cache: dict = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in _cache:
                result, timestamp = _cache[key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            result = func(*args, **kwargs)
            _cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator

# Stack multiple decorators
@retry(max_attempts=3, delay=0.5)
@cache(ttl_seconds=300)
def fetch_user(user_id: int) -> dict:
    """Simulates an API call."""
    return {"id": user_id, "name": "Alice"}
```

> **Decorator Pattern (GoF) vs Python `@decorator`**: Both add behavior without modifying the original. GoF uses object wrapping (composition). Python uses function wrapping. They solve the same problem differently.

---

### 3.3 Facade — "Simplified Interface to Complex Subsystem"

> **Intent**: Provide a unified, simple interface to a set of interfaces in a subsystem.

```python
class VideoCodec:
    def extract_audio(self, file: str) -> str:
        return f"audio_from_{file}"

    def extract_video(self, file: str) -> str:
        return f"video_from_{file}"

class AudioMixer:
    def normalize(self, audio: str) -> str:
        return f"normalized_{audio}"

    def apply_effects(self, audio: str, effects: list[str]) -> str:
        return f"effected_{audio}"

class VideoRenderer:
    def render(self, video: str, audio: str, quality: str) -> str:
        return f"rendered_{video}+{audio}@{quality}"

class SubtitleEncoder:
    def encode(self, subtitles: str, video: str) -> str:
        return f"subtitled_{video}"

# --- Facade — hides all complexity behind one method ---
class VideoConverterFacade:
    """Simple API for complex video conversion pipeline."""

    def __init__(self):
        self._codec = VideoCodec()
        self._mixer = AudioMixer()
        self._renderer = VideoRenderer()
        self._subtitles = SubtitleEncoder()

    def convert(self, file: str, format: str = "mp4",
                quality: str = "1080p", subtitles: str = None) -> str:
        # Complex multi-step pipeline hidden behind one call
        audio = self._codec.extract_audio(file)
        video = self._codec.extract_video(file)
        audio = self._mixer.normalize(audio)
        result = self._renderer.render(video, audio, quality)
        if subtitles:
            result = self._subtitles.encode(subtitles, result)
        return result

# Client code — blissfully simple
converter = VideoConverterFacade()
result = converter.convert("movie.avi", format="mp4", quality="4k")
```

> **Facade vs Adapter**: Adapter makes an incompatible interface compatible. Facade simplifies a complex interface. Adapter wraps ONE object; Facade wraps a SUBSYSTEM.

---

### 3.4 Proxy — "Controlled Access to an Object"

> **Intent**: Provide a surrogate or placeholder for another object to control access.

```python
from abc import ABC, abstractmethod
import time

class DatabaseService(ABC):
    @abstractmethod
    def query(self, sql: str) -> list[dict]: ...

class RealDatabaseService(DatabaseService):
    """Expensive — connects to actual database."""
    def __init__(self, connection_url: str):
        self.url = connection_url
        print(f"🔌 Connecting to {connection_url}...")  # Expensive operation
        time.sleep(0.1)  # Simulate connection time

    def query(self, sql: str) -> list[dict]:
        print(f"📊 Executing: {sql}")
        return [{"id": 1, "name": "Alice"}]

# --- Lazy Proxy (Virtual Proxy) ---
class LazyDatabaseProxy(DatabaseService):
    """Delays creation of RealDatabaseService until first query."""
    def __init__(self, connection_url: str):
        self._url = connection_url
        self._real_service: RealDatabaseService | None = None

    def _initialize(self):
        if self._real_service is None:
            self._real_service = RealDatabaseService(self._url)

    def query(self, sql: str) -> list[dict]:
        self._initialize()  # Connect only when needed
        return self._real_service.query(sql)

# --- Protection Proxy (Access Control) ---
class AccessControlProxy(DatabaseService):
    """Adds permission checking before delegating."""
    def __init__(self, service: DatabaseService, user_role: str):
        self._service = service
        self._role = user_role

    def query(self, sql: str) -> list[dict]:
        if "DROP" in sql.upper() and self._role != "admin":
            raise PermissionError(f"Role '{self._role}' cannot execute DROP")
        return self._service.query(sql)

# --- Caching Proxy ---
class CachingProxy(DatabaseService):
    """Caches query results to avoid repeated expensive calls."""
    def __init__(self, service: DatabaseService, ttl: int = 60):
        self._service = service
        self._cache: dict[str, tuple[list, float]] = {}
        self._ttl = ttl

    def query(self, sql: str) -> list[dict]:
        if sql in self._cache:
            result, timestamp = self._cache[sql]
            if time.time() - timestamp < self._ttl:
                print(f"📦 Cache hit: {sql}")
                return result
        result = self._service.query(sql)
        self._cache[sql] = (result, time.time())
        return result

# Stack proxies!
db = LazyDatabaseProxy("postgres://prod")
db = CachingProxy(db, ttl=300)
db = AccessControlProxy(db, user_role="reader")
```

#### Four Types of Proxy

| Type | Purpose | Example |
|------|---------|---------|
| **Virtual (Lazy)** | Delay expensive initialization | DB connections, large files |
| **Protection** | Access control | Role-based permissions |
| **Caching** | Cache results | Query caching, API responses |
| **Logging** | Log operations | Audit trails, debugging |

---

### 3.5 Composite — "Tree Structures"

> **Intent**: Compose objects into tree structures. Let clients treat individual objects and compositions uniformly.

```python
from abc import ABC, abstractmethod

class FileSystemItem(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_size(self) -> int: ...

    @abstractmethod
    def display(self, indent: int = 0) -> str: ...

class File(FileSystemItem):
    """Leaf — has no children."""
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size

    def get_size(self) -> int:
        return self.size

    def display(self, indent: int = 0) -> str:
        return f"{'  ' * indent}📄 {self.name} ({self.size}B)"

class Directory(FileSystemItem):
    """Composite — contains children (files or subdirectories)."""
    def __init__(self, name: str):
        super().__init__(name)
        self._children: list[FileSystemItem] = []

    def add(self, item: FileSystemItem) -> "Directory":
        self._children.append(item)
        return self  # Fluent API

    def remove(self, item: FileSystemItem):
        self._children.remove(item)

    def get_size(self) -> int:
        return sum(child.get_size() for child in self._children)

    def display(self, indent: int = 0) -> str:
        lines = [f"{'  ' * indent}📁 {self.name}/ ({self.get_size()}B)"]
        for child in self._children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)

# Build a tree — client treats files and directories the same way
root = Directory("project")
src = Directory("src")
src.add(File("main.py", 1500))
src.add(File("utils.py", 800))
root.add(src)
root.add(File("README.md", 200))
root.add(File(".gitignore", 50))

print(root.display())
# 📁 project/ (2550B)
#   📁 src/ (2300B)
#     📄 main.py (1500B)
#     📄 utils.py (800B)
#   📄 README.md (200B)
#   📄 .gitignore (50B)
```

---

### 3.6 Flyweight — "Share Common State"

> **Intent**: Minimize memory usage by sharing common data across many similar objects.

```python
class CharacterStyle:
    """Flyweight — shared intrinsic state (font, size, color)."""
    _cache: dict[tuple, "CharacterStyle"] = {}

    def __new__(cls, font: str, size: int, color: str):
        key = (font, size, color)
        if key not in cls._cache:
            instance = super().__new__(cls)
            instance.font = font
            instance.size = size
            instance.color = color
            cls._cache[key] = instance
        return cls._cache[key]

    def render(self, char: str, position: tuple[int, int]) -> str:
        return f"'{char}' at {position} [{self.font} {self.size}px {self.color}]"

# 10,000 characters but only a few unique styles
style_body = CharacterStyle("Arial", 12, "black")
style_heading = CharacterStyle("Arial", 24, "blue")
style_body2 = CharacterStyle("Arial", 12, "black")

print(style_body is style_body2)  # True — same object, shared!

# Extrinsic state (character, position) is NOT stored in the flyweight
# It's passed in when needed
print(style_body.render("H", (0, 0)))
print(style_heading.render("T", (0, 0)))
```

> **When to use**: When you have millions of similar objects (game particles, document characters, tree nodes in a forest). The shared part (intrinsic) is the flyweight; the unique part (extrinsic) is passed in.

---

## 4. Behavioral Patterns

### 4.1 Strategy — "Swappable Algorithms"

> **Intent**: Define a family of algorithms, encapsulate each one, and make them interchangeable at runtime.

```python
from abc import ABC, abstractmethod
from typing import Protocol

# --- Strategy Interface ---
class PricingStrategy(Protocol):
    def calculate(self, base_price: float) -> float: ...

# --- Concrete Strategies ---
class RegularPricing:
    def calculate(self, base_price: float) -> float:
        return base_price

class PremiumPricing:
    """10% discount for premium members."""
    def calculate(self, base_price: float) -> float:
        return base_price * 0.90

class HolidaySalePricing:
    """25% off during sales."""
    def calculate(self, base_price: float) -> float:
        return base_price * 0.75

class BulkPricing:
    """Tiered discount based on quantity."""
    def __init__(self, quantity: int):
        self.quantity = quantity

    def calculate(self, base_price: float) -> float:
        if self.quantity > 100:
            return base_price * 0.60
        elif self.quantity > 50:
            return base_price * 0.75
        elif self.quantity > 10:
            return base_price * 0.90
        return base_price

# --- Context — uses a strategy ---
class ShoppingCart:
    def __init__(self, pricing: PricingStrategy):
        self._pricing = pricing
        self._items: list[tuple[str, float]] = []

    def add_item(self, name: str, price: float):
        self._items.append((name, price))

    def set_pricing(self, pricing: PricingStrategy):
        """Change strategy at runtime."""
        self._pricing = pricing

    def total(self) -> float:
        return sum(self._pricing.calculate(price) for _, price in self._items)

# Usage — swap strategies without changing ShoppingCart
cart = ShoppingCart(RegularPricing())
cart.add_item("Laptop", 1000)
cart.add_item("Mouse", 50)
print(cart.total())  # 1050.0

cart.set_pricing(HolidaySalePricing())
print(cart.total())  # 787.5
```

> **Strategy vs If/Elif**: If you have 3+ variants that can change independently, use Strategy. For 2 simple variants, `if/else` is fine.

---

### 4.2 Observer — "Event-Driven Communication"

> **Intent**: Define a one-to-many dependency so that when one object changes state, all dependents are notified automatically.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

class EventType(Enum):
    ORDER_PLACED = auto()
    ORDER_SHIPPED = auto()
    ORDER_DELIVERED = auto()
    PAYMENT_RECEIVED = auto()

@dataclass
class Event:
    type: EventType
    data: dict

# --- Observer Interface ---
class EventListener(ABC):
    @abstractmethod
    def handle(self, event: Event) -> None: ...

# --- Concrete Observers ---
class EmailNotifier(EventListener):
    def handle(self, event: Event) -> None:
        if event.type == EventType.ORDER_PLACED:
            print(f"📧 Email: Order #{event.data['order_id']} confirmed!")
        elif event.type == EventType.ORDER_SHIPPED:
            print(f"📧 Email: Order shipped! Tracking: {event.data.get('tracking')}")

class SMSNotifier(EventListener):
    def handle(self, event: Event) -> None:
        print(f"📱 SMS: {event.type.name} for order #{event.data.get('order_id')}")

class AnalyticsLogger(EventListener):
    def handle(self, event: Event) -> None:
        print(f"📊 Analytics: {event.type.name} | {event.data}")

class InventoryManager(EventListener):
    def handle(self, event: Event) -> None:
        if event.type == EventType.ORDER_PLACED:
            print(f"📦 Inventory: Reserving items for order #{event.data['order_id']}")

# --- Event Bus (Subject) ---
class EventBus:
    def __init__(self):
        self._listeners: dict[EventType, list[EventListener]] = {}

    def subscribe(self, event_type: EventType, listener: EventListener):
        self._listeners.setdefault(event_type, []).append(listener)

    def unsubscribe(self, event_type: EventType, listener: EventListener):
        self._listeners.get(event_type, []).remove(listener)

    def publish(self, event: Event):
        for listener in self._listeners.get(event.type, []):
            try:
                listener.handle(event)
            except Exception as e:
                print(f"⚠️ Listener {listener.__class__.__name__} failed: {e}")

# --- Wiring ---
bus = EventBus()
bus.subscribe(EventType.ORDER_PLACED, EmailNotifier())
bus.subscribe(EventType.ORDER_PLACED, SMSNotifier())
bus.subscribe(EventType.ORDER_PLACED, AnalyticsLogger())
bus.subscribe(EventType.ORDER_PLACED, InventoryManager())
bus.subscribe(EventType.ORDER_SHIPPED, EmailNotifier())

bus.publish(Event(EventType.ORDER_PLACED, {"order_id": "ORD-123", "total": 99.99}))
# All 4 listeners respond to ORDER_PLACED
```

> **Real-World**: Redis Pub/Sub, Kafka consumers, Django signals, React's `useEffect` — all Observer pattern variants.

---

### 4.3 State — "Object Changes Behavior When State Changes"

> **Intent**: Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

```python
from abc import ABC, abstractmethod

# --- State Interface ---
class OrderState(ABC):
    @abstractmethod
    def confirm(self, order: "Order") -> None: ...

    @abstractmethod
    def ship(self, order: "Order") -> None: ...

    @abstractmethod
    def deliver(self, order: "Order") -> None: ...

    @abstractmethod
    def cancel(self, order: "Order") -> None: ...

# --- Concrete States ---
class PendingState(OrderState):
    def confirm(self, order: "Order"):
        print("✅ Order confirmed!")
        order.set_state(ConfirmedState())

    def ship(self, order: "Order"):
        print("❌ Cannot ship — order not confirmed yet")

    def deliver(self, order: "Order"):
        print("❌ Cannot deliver — order not shipped yet")

    def cancel(self, order: "Order"):
        print("🚫 Order cancelled from pending")
        order.set_state(CancelledState())

class ConfirmedState(OrderState):
    def confirm(self, order: "Order"):
        print("⚠️ Order already confirmed")

    def ship(self, order: "Order"):
        print("📦 Order shipped!")
        order.set_state(ShippedState())

    def cancel(self, order: "Order"):
        print("🚫 Order cancelled — refund initiated")
        order.set_state(CancelledState())

    def deliver(self, order: "Order"):
        print("❌ Cannot deliver — not shipped yet")

class ShippedState(OrderState):
    def confirm(self, order: "Order"):
        print("⚠️ Already confirmed and shipped")

    def ship(self, order: "Order"):
        print("⚠️ Already shipped")

    def deliver(self, order: "Order"):
        print("🎉 Order delivered!")
        order.set_state(DeliveredState())

    def cancel(self, order: "Order"):
        print("❌ Cannot cancel — already shipped")

class DeliveredState(OrderState):
    def confirm(self, order: "Order"):
        print("⚠️ Order already delivered")

    def ship(self, order: "Order"):
        print("⚠️ Order already delivered")

    def deliver(self, order: "Order"):
        print("⚠️ Already delivered")

    def cancel(self, order: "Order"):
        print("❌ Cannot cancel — already delivered. Use returns.")

class CancelledState(OrderState):
    def confirm(self, order: "Order"):
        print("❌ Cannot confirm — order is cancelled")

    def ship(self, order: "Order"):
        print("❌ Cannot ship — order is cancelled")

    def deliver(self, order: "Order"):
        print("❌ Cannot deliver — order is cancelled")

    def cancel(self, order: "Order"):
        print("⚠️ Already cancelled")

# --- Context ---
class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self._state: OrderState = PendingState()

    def set_state(self, state: OrderState):
        self._state = state

    @property
    def state_name(self) -> str:
        return self._state.__class__.__name__

    def confirm(self): self._state.confirm(self)
    def ship(self): self._state.ship(self)
    def deliver(self): self._state.deliver(self)
    def cancel(self): self._state.cancel(self)

# Usage
order = Order("ORD-001")
order.confirm()   # ✅ Order confirmed!
order.ship()      # 📦 Order shipped!
order.cancel()    # ❌ Cannot cancel — already shipped
order.deliver()   # 🎉 Order delivered!
```

> **State vs Strategy**: Strategy lets the **client** choose the algorithm. State changes **internally** based on transitions. State objects know about each other; Strategies don't.

---

### 4.4 Command — "Encapsulate a Request as an Object"

> **Intent**: Turn a request into a stand-alone object containing all information about the request. Enables undo, redo, queueing, and logging.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

# --- Command Interface ---
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...

# --- Receiver ---
class TextEditor:
    def __init__(self):
        self.content: str = ""
        self.cursor: int = 0

    def insert(self, text: str, position: int):
        self.content = self.content[:position] + text + self.content[position:]
        self.cursor = position + len(text)

    def delete(self, position: int, length: int) -> str:
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        self.cursor = position
        return deleted

    def __str__(self):
        return f"'{self.content}' (cursor at {self.cursor})"

# --- Concrete Commands ---
class InsertCommand(Command):
    def __init__(self, editor: TextEditor, text: str, position: int):
        self.editor = editor
        self.text = text
        self.position = position

    def execute(self):
        self.editor.insert(self.text, self.position)

    def undo(self):
        self.editor.delete(self.position, len(self.text))

class DeleteCommand(Command):
    def __init__(self, editor: TextEditor, position: int, length: int):
        self.editor = editor
        self.position = position
        self.length = length
        self._deleted_text: str = ""

    def execute(self):
        self._deleted_text = self.editor.delete(self.position, self.length)

    def undo(self):
        self.editor.insert(self._deleted_text, self.position)

# --- Invoker (manages history) ---
class CommandHistory:
    def __init__(self):
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute(self, command: Command):
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()  # New action invalidates redo

    def undo(self):
        if not self._undo_stack:
            print("Nothing to undo")
            return
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self):
        if not self._redo_stack:
            print("Nothing to redo")
            return
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)

# Usage
editor = TextEditor()
history = CommandHistory()

history.execute(InsertCommand(editor, "Hello", 0))
print(editor)  # 'Hello' (cursor at 5)

history.execute(InsertCommand(editor, " World", 5))
print(editor)  # 'Hello World' (cursor at 11)

history.undo()
print(editor)  # 'Hello' (cursor at 5)

history.redo()
print(editor)  # 'Hello World' (cursor at 11)
```

---

### 4.5 Chain of Responsibility — "Pass Request Along a Chain"

> **Intent**: Pass a request along a chain of handlers. Each handler decides to process the request or pass it to the next handler.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class Request:
    path: str
    method: str
    headers: dict[str, str]
    body: dict | None = None
    user_role: str = "anonymous"

# --- Handler Interface ---
class Middleware(ABC):
    def __init__(self):
        self._next: Middleware | None = None

    def set_next(self, handler: "Middleware") -> "Middleware":
        self._next = handler
        return handler  # Enable chaining

    def handle(self, request: Request) -> dict:
        if self._next:
            return self._next.handle(request)
        return {"status": 200, "body": "OK"}

# --- Concrete Handlers ---
class AuthenticationMiddleware(Middleware):
    def handle(self, request: Request) -> dict:
        token = request.headers.get("Authorization")
        if not token:
            return {"status": 401, "body": "Missing auth token"}
        if token != "Bearer valid-token":
            return {"status": 403, "body": "Invalid token"}
        print(f"✅ Auth passed: {request.path}")
        return super().handle(request)

class RateLimitMiddleware(Middleware):
    def __init__(self, max_requests: int = 100):
        super().__init__()
        self._counts: dict[str, int] = {}
        self._max = max_requests

    def handle(self, request: Request) -> dict:
        ip = request.headers.get("X-Forwarded-For", "unknown")
        self._counts[ip] = self._counts.get(ip, 0) + 1
        if self._counts[ip] > self._max:
            return {"status": 429, "body": "Rate limit exceeded"}
        print(f"✅ Rate limit OK ({self._counts[ip]}/{self._max})")
        return super().handle(request)

class ValidationMiddleware(Middleware):
    def handle(self, request: Request) -> dict:
        if request.method == "POST" and not request.body:
            return {"status": 400, "body": "POST requires a body"}
        print(f"✅ Validation passed")
        return super().handle(request)

class LoggingMiddleware(Middleware):
    def handle(self, request: Request) -> dict:
        print(f"📋 {request.method} {request.path}")
        response = super().handle(request)
        print(f"📋 Response: {response['status']}")
        return response

# --- Build the chain ---
logging = LoggingMiddleware()
auth = AuthenticationMiddleware()
rate_limit = RateLimitMiddleware(max_requests=10)
validation = ValidationMiddleware()

logging.set_next(auth).set_next(rate_limit).set_next(validation)

# Process request through the chain
request = Request(
    path="/api/users",
    method="GET",
    headers={"Authorization": "Bearer valid-token", "X-Forwarded-For": "1.2.3.4"}
)
response = logging.handle(request)
```

---

### 4.6 Template Method — "Define the Skeleton, Let Subclasses Fill In Steps"

> **Intent**: Define the skeleton of an algorithm in a base class, letting subclasses override specific steps without changing the algorithm's structure.

```python
from abc import ABC, abstractmethod

class DataExporter(ABC):
    """Template method — defines the export pipeline."""

    def export(self, data: list[dict]) -> str:
        """The template method — skeleton algorithm. DON'T override this."""
        self._validate(data)
        formatted = self._format(data)
        header = self._add_header()
        footer = self._add_footer()
        result = header + formatted + footer
        self._post_process(result)
        return result

    def _validate(self, data: list[dict]):
        """Hook — optional override."""
        if not data:
            raise ValueError("No data to export")

    @abstractmethod
    def _format(self, data: list[dict]) -> str:
        """Required — each exporter formats differently."""
        ...

    def _add_header(self) -> str:
        """Hook — default empty header."""
        return ""

    def _add_footer(self) -> str:
        """Hook — default empty footer."""
        return ""

    def _post_process(self, result: str):
        """Hook — optional post-processing."""
        pass

class CSVExporter(DataExporter):
    def _format(self, data: list[dict]) -> str:
        if not data:
            return ""
        headers = ",".join(data[0].keys())
        rows = [",".join(str(v) for v in row.values()) for row in data]
        return headers + "\n" + "\n".join(rows)

    def _add_header(self) -> str:
        return "# CSV Export\n"

class JSONExporter(DataExporter):
    def _format(self, data: list[dict]) -> str:
        import json
        return json.dumps(data, indent=2)

class HTMLExporter(DataExporter):
    def _format(self, data: list[dict]) -> str:
        if not data:
            return "<table></table>"
        headers = "".join(f"<th>{k}</th>" for k in data[0].keys())
        rows = "".join(
            "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
            for row in data
        )
        return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"

    def _add_header(self) -> str:
        return "<!DOCTYPE html><html><body>"

    def _add_footer(self) -> str:
        return "</body></html>"

# Usage
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
print(CSVExporter().export(data))
print(JSONExporter().export(data))
```

> **Template Method vs Strategy**: Template Method uses **inheritance** (subclass overrides steps). Strategy uses **composition** (inject algorithm object). Prefer Strategy when algorithms are completely different; use Template when sharing skeleton logic.

---

### 4.7 Iterator — "Sequential Access Without Exposing Internals"

> **Intent**: Provide a way to access elements of a collection sequentially without exposing its underlying representation.

```python
class BinaryTreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

class BinaryTree:
    """Custom iterable — supports multiple traversal strategies."""
    def __init__(self, root: BinaryTreeNode):
        self.root = root

    def __iter__(self):
        """Default: in-order traversal."""
        return self.inorder()

    def inorder(self):
        """Generator-based iterator — Pythonic and memory efficient."""
        def _traverse(node):
            if node:
                yield from _traverse(node.left)
                yield node.value
                yield from _traverse(node.right)
        return _traverse(self.root)

    def preorder(self):
        def _traverse(node):
            if node:
                yield node.value
                yield from _traverse(node.left)
                yield from _traverse(node.right)
        return _traverse(self.root)

    def level_order(self):
        """BFS traversal — uses a queue."""
        from collections import deque
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node:
                yield node.value
                queue.append(node.left)
                queue.append(node.right)

# Build tree:    4
#              /   \
#             2     6
#            / \   / \
#           1   3 5   7
tree = BinaryTree(
    BinaryTreeNode(4,
        BinaryTreeNode(2, BinaryTreeNode(1), BinaryTreeNode(3)),
        BinaryTreeNode(6, BinaryTreeNode(5), BinaryTreeNode(7))
    )
)

print(list(tree))                # [1, 2, 3, 4, 5, 6, 7] — in-order
print(list(tree.preorder()))     # [4, 2, 1, 3, 6, 5, 7]
print(list(tree.level_order()))  # [4, 2, 6, 1, 3, 5, 7]
```

> **Python's Iterator Protocol**: Any object with `__iter__` (returns iterator) and `__next__` (returns next value, raises `StopIteration`) is an iterator. Generators implement this automatically.

---

## 5. OOP Interview Questions — Basic to MANG

### 🟢 Level 1: Fundamentals (Startup / Phone Screen)

**Q1. What are the four pillars of OOP? Explain each in one sentence.**
> - **Encapsulation** — Bundling data and methods together, restricting direct access to internal state.
> - **Abstraction** — Hiding complex implementation details, exposing only what's necessary through interfaces.
> - **Inheritance** — Creating new classes from existing ones, inheriting attributes and behavior.
> - **Polymorphism** — Same interface, different behavior depending on the actual object type at runtime.

**Q2. What is the difference between an Abstract Class and an Interface?**
> | Aspect | Abstract Class (`ABC`) | Interface (`Protocol`) |
> |--------|----------------------|----------------------|
> | Typing | Nominal (must inherit) | Structural (just match methods) |
> | Concrete methods | ✅ Can have | ❌ Only signatures |
> | State | ✅ Can have attributes | ❌ No state |
> | Multiple inheritance | Can cause diamond problem | No issues |
> | When to use | Shared behavior + contract | Pure contract, loose coupling |
>
> In Python, `ABC` = abstract class, `Protocol` = interface. Use `Protocol` when you only need method signatures.

**Q3. What is Encapsulation? How does Python implement it?**
> Encapsulation bundles data (attributes) with the methods that operate on it, controlling access. Python uses **conventions**, not enforcement:
> - `public` — no prefix, accessible everywhere
> - `_protected` — single underscore, "internal use" convention
> - `__private` — double underscore, **name-mangled** to `_ClassName__attr` to prevent accidental collisions in inheritance
>
> Use `@property` for controlled access with validation.

**Q4. What is Polymorphism? Name three types in Python.**
> Polymorphism = "many forms." The same method call behaves differently based on the object.
> 1. **Duck typing** — `if it quacks like a duck...` No type checking, just call the method.
> 2. **Method overriding** — Subclass redefines a parent method. `Circle.area()` vs `Rectangle.area()`.
> 3. **Operator overloading** — `__add__`, `__eq__`, `__lt__` let objects respond to `+`, `==`, `<`.
>
> Python does NOT support method overloading (same name, different arg count). Use `@singledispatch` or default args instead.

**Q5. What is the difference between Composition and Inheritance?**
> | Aspect | Inheritance | Composition |
> |--------|------------|-------------|
> | Relationship | "is-a" | "has-a" |
> | Coupling | Tight — child depends on parent internals | Loose — depends on interface only |
> | Flexibility | Fixed at class definition | Swappable at runtime |
> | Testing | Harder — need to mock parent | Easier — inject mock dependencies |
> | Example | `class Dog(Animal)` | `class Dog: def __init__(self, voice: Voice)` |
>
> **Rule**: Favor composition over inheritance. Use inheritance only for genuine "is-a" with shared implementation.

**Q6. What design pattern would you use to avoid a giant `if/elif` chain?**
> **Strategy Pattern**. Extract each branch into its own class implementing a common interface. The context object delegates to whichever strategy is injected. Adding a new case = adding a new class, zero changes to existing code (follows OCP).

**Q7. What is a Factory Pattern? When would you use it?**
> Factory encapsulates object creation logic. Instead of `if type == "email": return Email()`, you register creators and let the factory decide. Use it when:
> - Object creation is complex (many dependencies, configuration)
> - You want to decouple client code from concrete classes
> - You need to support new types without modifying existing code

**Q8. Name three design patterns and where you'd use them in a web application.**
> 1. **Strategy** — Payment processing (Stripe, PayPal, Bank Transfer — each a strategy)
> 2. **Observer** — Event-driven notifications (order placed → email, SMS, analytics, inventory)
> 3. **Decorator** — Middleware stack (logging → auth → rate-limiting → validation)
> 4. **Builder** — Complex query construction (SQL query builder with method chaining)
> 5. **Singleton** — Database connection pool (one shared pool across the app)

---

### 🟡 Level 2: Intermediate (Mid-Level / Onsite Round 1)

**Q9. What is the difference between Strategy and State patterns?**
> | Aspect | Strategy | State |
> |--------|----------|-------|
> | Who decides | **Client** selects the algorithm | **Object itself** transitions internally |
> | Awareness | Strategies don't know about each other | States know about valid transitions |
> | Purpose | Swap algorithms at will | Model state machines with valid transitions |
> | Example | Pricing algorithm (regular, premium, bulk) | Order lifecycle (pending → confirmed → shipped) |

**Q10. How does the Decorator pattern differ from Python's `@decorator`?**
> - **GoF Decorator**: Object-level composition. A `LoggingDataSource` wraps a `DataSource`, adding logging. Both share the same interface. Stack multiple wrappers.
> - **Python `@decorator`**: Function-level wrapping. A function wraps another function, adding behavior. Uses closures and `functools.wraps`.
> - Both achieve the same goal (add behavior without modifying original), but through different mechanisms (composition vs closure).

**Q11. Explain the Observer pattern. How would you prevent memory leaks in it?**
> Observer defines a pub/sub relationship. The Subject (EventBus) maintains a list of Listeners and notifies them on state changes.
> **Memory leak risk**: If observers hold strong references, they prevent garbage collection even after they're logically removed.
> **Fix**: Use `weakref.WeakSet` or `weakref.ref` for the listener list:
> ```python
> import weakref
>
> class EventBus:
>     def __init__(self):
>         self._listeners: dict[str, weakref.WeakSet] = {}
>
>     def subscribe(self, event: str, listener):
>         self._listeners.setdefault(event, weakref.WeakSet()).add(listener)
>         # Listener is automatically removed when garbage collected
> ```

**Q12. When would you use the Builder pattern over a constructor?**
> Use Builder when:
> - Constructor has 5+ parameters (telescoping constructor anti-pattern)
> - Some params are optional with complex defaults
> - Object needs to be constructed step-by-step (e.g., SQL query, HTTP request)
> - You want validation at build-time, not after creation
> - Same construction process should create different representations

**Q13. What is the Chain of Responsibility pattern? Where is it used in real frameworks?**
> Uses a chain of handler objects. Each handler either processes the request or passes it to the next. Real-world examples:
> - **Django/Express middleware** — request passes through auth → logging → CORS → rate-limit → handler
> - **Exception handling** — `try/except` blocks form a chain up the call stack
> - **DOM event bubbling** — events propagate from child to parent elements
> - **Logging frameworks** — log message flows through handlers (file → console → remote)

**Q14. What is the difference between Adapter, Facade, and Proxy?**
> | Pattern | Purpose | Wraps | Changes Interface? |
> |---------|---------|-------|--------------------|
> | **Adapter** | Make incompatible interface compatible | One object | ✅ Yes — translates interface |
> | **Facade** | Simplify complex subsystem | Multiple objects | ✅ Yes — provides simpler API |
> | **Proxy** | Control access to an object | One object | ❌ No — same interface |
>
> - **Adapter**: "I can't use this library, its API doesn't match mine"
> - **Facade**: "This subsystem has 20 classes, I want one simple method"
> - **Proxy**: "I want to add caching/auth/lazy-loading without changing the interface"

**Q15. How is the Composite pattern used in real systems?**
> Composite creates tree structures where nodes and leaves share the same interface:
> - **File systems** — files and directories have `get_size()`, `display()`
> - **UI frameworks** — `Component` can be a `Button` (leaf) or `Panel` (container with children)
> - **Organization hierarchy** — individual employees and departments both implement `get_salary()`
> - **DOM tree** — `Element` can contain other `Element`s, all support `render()`
> - **Menu systems** — `MenuItem` can be a single item or a submenu with children

**Q16. What is the Template Method pattern? How does it relate to the Hollywood Principle?**
> Template Method defines the **skeleton** of an algorithm in a base class, letting subclasses fill in specific steps without changing the structure.
> **Hollywood Principle**: "Don't call us, we'll call you." The base class calls the subclass's hook methods, not the other way around. This is **Inversion of Control**.
> ```python
> class DataPipeline(ABC):  # Base — defines the skeleton
>     def run(self, data):         # Template method — DON'T override
>         data = self.extract(data)
>         data = self.transform(data)
>         self.load(data)
>
>     @abstractmethod
>     def extract(self, data): ...  # Subclass fills in
>     @abstractmethod
>     def transform(self, data): ...
>     @abstractmethod
>     def load(self, data): ...
> ```

**Q17. What is the Flyweight pattern? When is it critical?**
> Flyweight **shares common state** (intrinsic) across many objects to save memory. Each object only stores unique state (extrinsic).
> **Critical when**:
> - Creating millions of objects (game particles, characters in a text editor, tree instances in a forest renderer)
> - Python example: `str` interning — Python caches small strings. `"hello" is "hello"` → `True`
> - `int` caching — Python caches integers -5 to 256. `a = 256; b = 256; a is b` → `True`
>
> In Python, implement with `__new__` + class-level cache dict, or use `functools.lru_cache` on factory functions.

---

### 🔴 Level 3: Advanced (MANG / Staff-Level)

**Q18. Design a plugin system using OOP and design patterns. Which patterns would you combine?**
> A plugin system combines **multiple patterns**:
> - **Strategy** — each plugin implements a common `Plugin` protocol
> - **Factory + Registry** — `__init_subclass__` auto-registers plugins, factory creates them by name
> - **Observer** — plugins subscribe to events and react
> - **Chain of Responsibility** — plugins can form a processing pipeline
> - **Template Method** — base plugin defines lifecycle hooks (`setup()`, `execute()`, `teardown()`)
> ```python
> from typing import Protocol, Any
>
> class Plugin(Protocol):
>     name: str
>     def setup(self) -> None: ...
>     def execute(self, data: dict) -> dict: ...
>     def teardown(self) -> None: ...
>
> class PluginRegistry:
>     _plugins: dict[str, type] = {}
>
>     def __init_subclass__(cls, plugin_name: str = None, **kwargs):
>         super().__init_subclass__(**kwargs)
>         if plugin_name:
>             PluginRegistry._plugins[plugin_name] = cls
>
>     @classmethod
>     def get(cls, name: str) -> "PluginRegistry":
>         return cls._plugins[name]()
>
> class PluginEngine:
>     """Orchestrator — runs plugins as a pipeline."""
>     def __init__(self):
>         self._pipeline: list[Plugin] = []
>
>     def add(self, plugin: Plugin) -> "PluginEngine":
>         plugin.setup()
>         self._pipeline.append(plugin)
>         return self
>
>     def run(self, data: dict) -> dict:
>         for plugin in self._pipeline:
>             data = plugin.execute(data)
>         return data
>
>     def shutdown(self):
>         for plugin in reversed(self._pipeline):
>             plugin.teardown()
> ```

**Q19. How do design patterns apply to microservices architecture?**
> | Pattern | Microservices Application |
> |---------|--------------------------|
> | **Facade** | API Gateway — single entry point to multiple services |
> | **Adapter** | Anti-corruption layer between services with different schemas |
> | **Observer** | Event-driven architecture (Kafka, RabbitMQ) — services publish/subscribe |
> | **Strategy** | Service mesh routing (canary, blue-green, weighted) |
> | **Proxy** | Service proxy / sidecar (Envoy, Istio) — adds auth, logging, circuit breaking |
> | **Chain of Responsibility** | Request pipeline (auth → rate-limit → validation → handler) |
> | **Factory** | Service instantiation based on environment (dev, staging, prod) |
> | **State** | Saga pattern — distributed transaction state machine |
> | **Command** | CQRS — separate read/write models with command objects |

**Q20. Explain CQRS (Command Query Responsibility Segregation). Which OOP patterns does it use?**
> CQRS separates **read** and **write** operations into different models.
> - **Command pattern** — write operations are encapsulated as command objects (`CreateUserCommand`, `UpdateOrderCommand`)
> - **Strategy** — different query strategies for read optimization (cache, search index, materialized view)
> - **Observer** — write model publishes events, read model subscribes and updates projections
> - **Repository** — separate repositories for reads and writes
> ```python
> # Command side
> class CreateUserCommand:
>     def __init__(self, name: str, email: str):
>         self.name = name
>         self.email = email
>
> class CommandHandler(ABC):
>     @abstractmethod
>     def handle(self, command) -> None: ...
>
> class CreateUserHandler(CommandHandler):
>     def __init__(self, repo, event_bus):
>         self._repo = repo
>         self._bus = event_bus
>
>     def handle(self, cmd: CreateUserCommand):
>         user = User(cmd.name, cmd.email)
>         self._repo.save(user)
>         self._bus.publish(UserCreatedEvent(user.id))
>
> # Query side — completely separate model optimized for reads
> class UserQueryService:
>     def __init__(self, read_store):
>         self._store = read_store
>
>     def get_user_summary(self, user_id: str) -> dict:
>         return self._store.get(user_id)  # Pre-computed, denormalized
> ```

**Q21. How would you make the Observer pattern thread-safe and handle slow subscribers?**
> **Thread safety**:
> - Use `threading.Lock` to protect the subscriber list
> - Copy the subscriber list before iterating (snapshot) to avoid modification during iteration
>
> **Slow subscribers**:
> - **Async dispatch** — use `concurrent.futures.ThreadPoolExecutor` to notify in parallel
> - **Event queue** — each subscriber has its own queue; publisher just enqueues
> - **Timeout** — skip subscribers that don't respond within a timeout
> - **Circuit breaker** — disable failing subscribers after N failures
> ```python
> import threading
> from concurrent.futures import ThreadPoolExecutor, as_completed
>
> class AsyncEventBus:
>     def __init__(self, max_workers: int = 4, timeout: float = 5.0):
>         self._lock = threading.Lock()
>         self._listeners: dict[str, list] = {}
>         self._executor = ThreadPoolExecutor(max_workers=max_workers)
>         self._timeout = timeout
>
>     def publish(self, event_type: str, data: dict):
>         with self._lock:
>             listeners = list(self._listeners.get(event_type, []))  # Snapshot
>
>         futures = {
>             self._executor.submit(listener.handle, data): listener
>             for listener in listeners
>         }
>         for future in as_completed(futures, timeout=self._timeout):
>             try:
>                 future.result()
>             except Exception as e:
>                 listener = futures[future]
>                 print(f"⚠️ {listener.__class__.__name__} failed: {e}")
> ```

**Q22. Design a retry mechanism using the Decorator pattern. Support configurable backoff strategies.**
> ```python
> import time
> import functools
> import random
> from abc import ABC, abstractmethod
>
> class BackoffStrategy(ABC):
>     @abstractmethod
>     def wait_time(self, attempt: int) -> float: ...
>
> class ExponentialBackoff(BackoffStrategy):
>     def __init__(self, base: float = 1.0, max_wait: float = 60.0):
>         self.base = base
>         self.max_wait = max_wait
>
>     def wait_time(self, attempt: int) -> float:
>         wait = min(self.base * (2 ** attempt), self.max_wait)
>         return wait + random.uniform(0, wait * 0.1)  # Jitter
>
> class LinearBackoff(BackoffStrategy):
>     def __init__(self, delay: float = 1.0):
>         self.delay = delay
>
>     def wait_time(self, attempt: int) -> float:
>         return self.delay * (attempt + 1)
>
> def retry(max_attempts: int = 3,
>           backoff: BackoffStrategy = None,
>           retryable_exceptions: tuple = (Exception,)):
>     """Decorator with pluggable backoff strategy."""
>     if backoff is None:
>         backoff = ExponentialBackoff()
>
>     def decorator(func):
>         @functools.wraps(func)
>         def wrapper(*args, **kwargs):
>             for attempt in range(max_attempts):
>                 try:
>                     return func(*args, **kwargs)
>                 except retryable_exceptions as e:
>                     if attempt == max_attempts - 1:
>                         raise
>                     wait = backoff.wait_time(attempt)
>                     print(f"Retry {attempt+1}/{max_attempts} in {wait:.1f}s: {e}")
>                     time.sleep(wait)
>         return wrapper
>     return decorator
>
> @retry(max_attempts=3, backoff=ExponentialBackoff(base=0.5))
> def call_api(url: str) -> dict:
>     ...  # May raise ConnectionError
> ```
> This combines **Decorator** (function wrapping) + **Strategy** (pluggable backoff) + **OCP** (new backoff = new class, no modification).

**Q23. How do you test code that uses design patterns? What are the testing advantages?**
> Design patterns make code **highly testable** by design:
>
> | Pattern | Testing Advantage |
> |---------|-------------------|
> | **Strategy** | Inject mock strategy → test context in isolation |
> | **Observer** | Subscribe a test spy → verify events were published |
> | **Factory** | Register test doubles → control what gets created |
> | **Proxy** | Wrap real service with recording proxy for assertions |
> | **Command** | Execute + undo in tests → verify state before/after |
> | **State** | Test each state class independently with mock context |
> | **DIP** | Inject `InMemoryRepository` instead of real DB |
>
> ```python
> # Example: Testing Strategy pattern
> class MockPricing:
>     def calculate(self, base_price: float) -> float:
>         return base_price  # No discount — predictable
>
> def test_shopping_cart_total():
>     cart = ShoppingCart(MockPricing())
>     cart.add_item("Widget", 10.0)
>     cart.add_item("Gadget", 20.0)
>     assert cart.total() == 30.0  # Exact, no floating point surprises
>
> # Example: Testing Observer with spy
> class SpyListener:
>     def __init__(self):
>         self.events_received = []
>
>     def handle(self, event):
>         self.events_received.append(event)
>
> def test_event_bus_publishes():
>     bus = EventBus()
>     spy = SpyListener()
>     bus.subscribe("order.placed", spy)
>     bus.publish(Event("order.placed", {"id": 123}))
>     assert len(spy.events_received) == 1
>     assert spy.events_received[0].data["id"] == 123
> ```

**Q24. What is the Null Object pattern? When does it prevent bugs?**
> Instead of returning `None` and forcing callers to null-check everywhere, return a **Null Object** that implements the interface but does nothing:
> ```python
> class Logger(Protocol):
>     def log(self, message: str) -> None: ...
>
> class ConsoleLogger:
>     def log(self, message: str) -> None:
>         print(f"[LOG] {message}")
>
> class NullLogger:
>     """Does nothing — no null checks needed."""
>     def log(self, message: str) -> None:
>         pass  # Silently ignore
>
> class UserService:
>     def __init__(self, logger: Logger = None):
>         self._logger = logger or NullLogger()  # Never None!
>
>     def create_user(self, name: str):
>         self._logger.log(f"Creating user: {name}")  # Always safe
>         # No need for: if self._logger: self._logger.log(...)
> ```
> **Prevents**: `AttributeError: 'NoneType' has no attribute 'log'` and eliminates scattered `if x is not None:` checks.

**Q25. Compare these approaches to the Singleton pattern in Python. What are the trade-offs?**
> | Approach | Thread-Safe? | Subclass-Safe? | `isinstance` works? | Complexity |
> |----------|-------------|---------------|---------------------|------------|
> | Module-level instance | ✅ (import lock) | N/A | ✅ | Simplest |
> | `__new__` override | ❌ (race condition) | ❌ (shared `_instance`) | ✅ | Simple |
> | Decorator (`@singleton`) | ✅ (with lock) | N/A | ❌ (returns function) | Medium |
> | Metaclass (`SingletonMeta`) | ✅ (with lock) | ✅ (per-class dict) | ✅ | Complex |
> | `__init_subclass__` | ✅ (with lock) | ✅ | ✅ | Medium |
>
> **Recommendation**: Use module-level for 90% of cases. Use metaclass when you need lazy init + subclassing + `isinstance`.

**Q26. Design an event-sourced system using OOP patterns. How do Command, Observer, and State interact?**
> Event sourcing stores **all state changes as events** instead of just the current state:
> - **Command** — represents intent (`PlaceOrderCommand`). Commands are validated and may be rejected.
> - **Event** — represents something that **happened** (`OrderPlacedEvent`). Events are facts, never rejected.
> - **State** — rebuilt by replaying events. Each event applies a state transition.
> - **Observer** — downstream projections subscribe to events and build read models.
> ```python
> @dataclass(frozen=True)
> class DomainEvent:
>     aggregate_id: str
>     timestamp: float
>
> @dataclass(frozen=True)
> class OrderPlaced(DomainEvent):
>     items: tuple[str, ...]
>     total: float
>
> @dataclass(frozen=True)
> class OrderShipped(DomainEvent):
>     tracking_number: str
>
> class OrderAggregate:
>     """Rebuilds state from event history."""
>     def __init__(self, order_id: str):
>         self.order_id = order_id
>         self.status = "new"
>         self.items: list[str] = []
>         self._pending_events: list[DomainEvent] = []
>
>     def place(self, items: list[str], total: float):
>         if self.status != "new":
>             raise ValueError("Order already placed")
>         event = OrderPlaced(self.order_id, time.time(), tuple(items), total)
>         self._apply(event)
>         self._pending_events.append(event)
>
>     def _apply(self, event: DomainEvent):
>         """Apply event to update internal state."""
>         if isinstance(event, OrderPlaced):
>             self.status = "placed"
>             self.items = list(event.items)
>         elif isinstance(event, OrderShipped):
>             self.status = "shipped"
>
>     @classmethod
>     def from_events(cls, order_id: str, events: list[DomainEvent]):
>         """Rebuild state by replaying events."""
>         aggregate = cls(order_id)
>         for event in events:
>             aggregate._apply(event)
>         return aggregate
> ```

**Q27. When should you deliberately NOT use design patterns?**
> Patterns are **solutions to specific problems**, not goals in themselves. Avoid when:
> - **The problem is simple** — A 50-line script doesn't need a Strategy hierarchy. `if/elif` is fine.
> - **Only 2-3 variants exist** — Don't create a factory for 2 classes that never change.
> - **Premature abstraction** — Don't add patterns "just in case." Wait until the pain is real (Rule of Three).
> - **Team unfamiliarity** — A pattern nobody understands increases maintenance cost.
> - **Performance-critical paths** — Virtual dispatch and object creation have overhead. Hot loops may need direct calls.
>
> **Signs of over-engineering**:
> - More interfaces than concrete classes
> - Factory that creates exactly one type
> - Observer with exactly one subscriber
> - Strategy that never gets swapped
> - Singleton protecting a stateless utility class

---
