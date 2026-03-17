# 🧩 Design Patterns Quick Reference for LLD Interviews

> These 8 patterns cover **95% of MANG LLD interview needs**. Master them.

---

## 1. Strategy Pattern ⭐ (Most Used)
**When**: Multiple algorithms/behaviors for the same operation

```python
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

class CreditCard(PaymentStrategy):
    def pay(self, amount): ...

class UPI(PaymentStrategy):
    def pay(self, amount): ...

# Usage: inject at runtime
order.process_payment(CreditCard())
order.process_payment(UPI())
```

**Used In**: Pricing, Payment, Matching, Eviction, Feed ranking, Sorting

---

## 2. Observer Pattern ⭐
**When**: One event should notify multiple interested parties

```python
class EventEmitter:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def on(self, event: str, callback: Callable):
        self._listeners.setdefault(event, []).append(callback)
    
    def emit(self, event: str, data: Any):
        for cb in self._listeners.get(event, []):
            cb(data)

# Usage
emitter.on("order_placed", send_email)
emitter.on("order_placed", update_inventory)
emitter.on("order_placed", notify_seller)
emitter.emit("order_placed", order)
```

**Used In**: Notifications, Display boards, Event-driven systems

---

## 3. Factory Pattern
**When**: Creating objects without specifying exact class

```python
class VehicleFactory:
    @staticmethod
    def create(vehicle_type: str) -> Vehicle:
        if vehicle_type == "car":
            return Car()
        elif vehicle_type == "truck":
            return Truck()
        raise ValueError(f"Unknown: {vehicle_type}")
```

**Used In**: Vehicle/Piece creation, Post types, Payment methods

---

## 4. State Pattern
**When**: Object behavior changes based on internal state (state machines)

```python
class OrderState(ABC):
    @abstractmethod
    def next(self, order: 'Order'): pass
    @abstractmethod
    def cancel(self, order: 'Order'): pass

class PendingState(OrderState):
    def next(self, order):
        order.state = ConfirmedState()
    def cancel(self, order):
        order.state = CancelledState()

class ConfirmedState(OrderState):
    def next(self, order):
        order.state = ShippedState()
    def cancel(self, order):
        order.state = CancelledState()

class ShippedState(OrderState):
    def next(self, order):
        order.state = DeliveredState()
    def cancel(self, order):
        raise Exception("Cannot cancel shipped order")
```

**Used In**: Order lifecycle, Ride status, Booking status, Game state

---

## 5. Command Pattern
**When**: Encapsulate actions as objects (undo/redo, task queues)

```python
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    @abstractmethod
    def undo(self): pass

class MoveCommand(Command):
    def __init__(self, piece, from_pos, to_pos):
        self.piece = piece
        self.from_pos = from_pos
        self.to_pos = to_pos
    
    def execute(self):
        self.piece.move(self.to_pos)
    
    def undo(self):
        self.piece.move(self.from_pos)
```

**Used In**: Chess moves, Task scheduling, Transaction logs

---

## 6. Singleton Pattern
**When**: Exactly one instance needed (use sparingly)

```python
class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Used In**: DB connection pool, Configuration, Logger

---

## 7. Decorator Pattern
**When**: Add behavior to objects dynamically (wrapping)

```python
class BasePricing:
    def calculate(self, ride) -> float:
        return ride.distance * 10  # ₹10/km

class SurgeDecorator:
    def __init__(self, base: BasePricing, multiplier: float):
        self.base = base
        self.multiplier = multiplier
    
    def calculate(self, ride) -> float:
        return self.base.calculate(ride) * self.multiplier

# Usage
price = SurgeDecorator(BasePricing(), 1.5).calculate(ride)
```

**Used In**: Pricing modifiers, Logging wrappers, Caching layers

---

## 8. Template Method
**When**: Define algorithm skeleton, let subclasses fill in steps

```python
class Game(ABC):
    def play(self):           # Template method
        self.initialize()
        while not self.is_over():
            self.make_move()
        self.declare_winner()
    
    @abstractmethod
    def initialize(self): pass
    @abstractmethod
    def make_move(self): pass
    @abstractmethod
    def is_over(self) -> bool: pass
    @abstractmethod
    def declare_winner(self): pass
```

**Used In**: Game loops, Data processing pipelines, Validation flows

---

## 🎯 Pattern Selection Cheat Sheet

| When you need... | Use |
|-----------------|-----|
| Multiple algorithms for same task | **Strategy** |
| Notify multiple listeners on events | **Observer** |
| Create objects without hardcoding class | **Factory** |
| Behavior changes with internal state | **State** |
| Encapsulate actions for undo/queue | **Command** |
| One global instance | **Singleton** |
| Add features without modifying class | **Decorator** |
| Define algorithm skeleton | **Template Method** |
