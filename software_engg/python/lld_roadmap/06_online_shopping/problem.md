# 🛒 Online Shopping System (Amazon) — Problem Statement

## Category: E-Commerce / Inventory Systems
**Difficulty**: Hard | **Time**: 45 min | **Week**: 6

---

## Problem Statement

Design an object-oriented online shopping system that supports:

1. **Product catalog**: Categories, search, filter, sort
2. **Shopping cart**: Add/remove items, update quantities
3. **Order lifecycle**: Placed → Confirmed → Shipped → Delivered → Returned
4. **Inventory management**: Track stock, prevent overselling
5. **Payment**: Multiple payment methods with payment gateway abstraction
6. **Pricing**: Coupons, discounts, tax calculation
7. **Notifications**: Order confirmation, shipping updates

---

## Requirements Gathering (Practice Questions)

1. Single seller or marketplace (multiple sellers)?
2. Do sellers manage their own inventory?
3. What payment methods do we support?
4. Do we need wish lists?
5. Is there a review/rating system for products?
6. Do we need a recommendation engine?
7. How do returns/refunds work?
8. Do we need real-time inventory (prevent overselling)?

---

## Core Entities

| Entity | Responsibility |
|--------|---------------|
| `Product` | Item with name, price, description, category |
| `Category` | Hierarchical product categorization |
| `Inventory` | Tracks stock per product (warehouse-level) |
| `Cart` | User's shopping cart with items |
| `CartItem` | Product + quantity in cart |
| `Order` | Placed order with items, shipping, payment |
| `OrderStatus` | State machine for order lifecycle |
| `Payment` | Handles payment processing |
| `User` | Buyer with profile, address book, order history |
| `Seller` | Product lister (marketplace model) |
| `Coupon` | Discount codes with rules |
| `ShippingService` | Handles shipping logistics |

---

## Key Design Decisions

### 1. Order State Machine
```python
class OrderStatus(Enum):
    PENDING = "pending"           # Cart → Order, awaiting payment
    CONFIRMED = "confirmed"       # Payment successful
    PROCESSING = "processing"     # Seller preparing
    SHIPPED = "shipped"           # In transit
    DELIVERED = "delivered"       # Received by buyer
    CANCELLED = "cancelled"       # Cancelled before shipping
    RETURN_REQUESTED = "return_requested"
    RETURNED = "returned"
    REFUNDED = "refunded"
```

### 2. Cart Operations
```python
class Cart:
    def __init__(self, user: User):
        self.user = user
        self.items: Dict[str, CartItem] = {}  # product_id → CartItem
    
    def add_item(self, product: Product, quantity: int):
        if product.id in self.items:
            self.items[product.id].quantity += quantity
        else:
            self.items[product.id] = CartItem(product, quantity)
    
    def remove_item(self, product_id: str):
        self.items.pop(product_id, None)
    
    def get_total(self) -> float:
        return sum(item.product.price * item.quantity 
                   for item in self.items.values())
    
    def checkout(self, payment_strategy: PaymentStrategy, 
                 shipping_address: Address) -> Order:
        # 1. Validate inventory for all items
        # 2. Reserve inventory
        # 3. Create order
        # 4. Process payment
        # 5. Clear cart
        # 6. Notify user
        pass
```

### 3. Inventory with Concurrency
```python
class Inventory:
    def __init__(self):
        self._stock: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def reserve(self, product_id: str, quantity: int) -> bool:
        with self._lock:
            available = self._stock.get(product_id, 0)
            if available >= quantity:
                self._stock[product_id] -= quantity
                return True
            return False
    
    def release(self, product_id: str, quantity: int):
        """Called on order cancellation"""
        with self._lock:
            self._stock[product_id] = self._stock.get(product_id, 0) + quantity
```

### 4. Payment Strategy
```python
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> PaymentResult:
        pass

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str, cvv: str, expiry: str):
        ...

class UPIPayment(PaymentStrategy):
    def __init__(self, upi_id: str):
        ...

class WalletPayment(PaymentStrategy):
    def __init__(self, wallet_id: str, balance: float):
        ...

class CODPayment(PaymentStrategy):
    """Cash on Delivery — always succeeds"""
    def process_payment(self, amount: float) -> PaymentResult:
        return PaymentResult(success=True, method="COD")
```

### 5. Discount / Coupon Strategy
```python
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, cart: Cart) -> float:
        """Returns discount amount"""
        pass

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float, max_discount: float):
        self.percentage = percentage
        self.max_discount = max_discount
    
    def apply(self, cart: Cart) -> float:
        discount = cart.get_total() * self.percentage / 100
        return min(discount, self.max_discount)

class FlatDiscount(DiscountStrategy):
    def __init__(self, amount: float, min_order: float):
        self.amount = amount
        self.min_order = min_order
    
    def apply(self, cart: Cart) -> float:
        if cart.get_total() >= self.min_order:
            return self.amount
        return 0

class BuyXGetYDiscount(DiscountStrategy):
    """Buy 2, Get 1 free"""
    pass
```

### 6. Search with Filters (Strategy/Builder)
```python
class ProductFilter(ABC):
    @abstractmethod
    def matches(self, product: Product) -> bool:
        pass

class CategoryFilter(ProductFilter):
    def __init__(self, category: str):
        self.category = category

class PriceRangeFilter(ProductFilter):
    def __init__(self, min_price: float, max_price: float):
        ...

class SearchService:
    def search(self, keyword: str, filters: List[ProductFilter], 
               sort_by: str = "relevance") -> List[Product]:
        results = self._text_search(keyword)
        for f in filters:
            results = [p for p in results if f.matches(p)]
        return self._sort(results, sort_by)
```

---

## Variations This Unlocks

| Variation | What Changes |
|-----------|-------------|
| **Vending Machine** | Tiny product catalog, coin-based payment, no shipping |
| **Auction System** | Cart replaced by bidding, price is dynamic |
| **Coupon Engine** | Discount strategies extracted as standalone system |
| **Subscription Box** | Recurring orders with fixed schedule |

---

## Interview Checklist

- [ ] Clarified requirements (single/marketplace, payment methods)
- [ ] Designed Product catalog with Category hierarchy
- [ ] Implemented Cart with add/remove/update
- [ ] Implemented Order state machine
- [ ] Implemented Inventory with thread-safe reserve/release
- [ ] Implemented Payment with Strategy pattern
- [ ] Implemented Discount/Coupon system
- [ ] Discussed search and filtering
- [ ] Discussed notification on order events (Observer)
