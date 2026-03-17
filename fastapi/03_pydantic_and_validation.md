# Pydantic & Validation

## Pydantic v2 Basics

Pydantic models define **data shapes** with automatic validation, serialization, and documentation.

```python
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Alice"])
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    tags: list[str] = Field(default_factory=list, max_length=10)
    bio: Optional[str] = Field(None, max_length=500)

# Validation happens automatically
user = UserCreate(name="Alice", email="alice@example.com", age=30)
print(user.model_dump())        # {"name": "Alice", "email": "alice@example.com", ...}
print(user.model_dump_json())   # JSON string
print(user.model_json_schema()) # JSON Schema (for OpenAPI docs)

# Invalid data raises ValidationError
try:
    bad = UserCreate(name="", email="bad", age=-1)
except ValidationError as e:
    print(e.errors())
    # [{"type": "string_too_short", "loc": ("name",), ...}]
```

---

## Field Types

| Type | Example | Notes |
|------|---------|-------|
| `str` | `name: str` | Basic string |
| `int`, `float` | `age: int` | Numeric |
| `bool` | `active: bool` | Boolean |
| `datetime` | `created: datetime` | ISO 8601 parsed |
| `EmailStr` | `email: EmailStr` | Requires `pydantic[email]` |
| `HttpUrl` | `url: HttpUrl` | Validated URL |
| `UUID` | `id: UUID` | UUID v4 etc. |
| `Path` | `file: Path` | File path |
| `list[T]` | `tags: list[str]` | Typed list |
| `dict[K, V]` | `meta: dict[str, Any]` | Typed dict |
| `Optional[T]` | `bio: Optional[str]` | Nullable |
| `Literal["a","b"]` | `role: Literal["admin","user"]` | Fixed values |
| `Annotated[T, ...]` | `Annotated[int, Field(ge=0)]` | Metadata enriched |

---

## Custom Validators

### Field Validators

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip().title()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        allowed_domains = ["company.com", "partner.com"]
        domain = v.split("@")[-1]
        if domain not in allowed_domains:
            raise ValueError(f"Email domain must be one of: {allowed_domains}")
        return v.lower()
```

### Model Validators (Cross-Field)

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    
    @model_validator(mode="after")
    def at_least_one_field(self):
        if not any([self.name, self.email, self.password]):
            raise ValueError("At least one field must be provided")
        return self
```

---

## Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")

class Company(BaseModel):
    name: str
    address: Address       # Nested model

class UserProfile(BaseModel):
    user: UserCreate       # Nested
    company: Optional[Company] = None
    addresses: list[Address] = []    # List of nested models

# Request body is deeply nested JSON — all validated recursively:
# {
#   "user": {"name": "Alice", "email": "alice@example.com", "age": 30},
#   "company": {"name": "ACME", "address": {"street": "123 Main", ...}},
#   "addresses": [{"street": "456 Oak", ...}]
# }
```

---

## Discriminated Unions

Handle **polymorphic types** based on a discriminator field.

```python
from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated

class CreditCardPayment(BaseModel):
    type: Literal["credit_card"] = "credit_card"
    card_number: str
    cvv: str

class BankTransferPayment(BaseModel):
    type: Literal["bank_transfer"] = "bank_transfer"
    account_number: str
    routing_number: str

class WalletPayment(BaseModel):
    type: Literal["wallet"] = "wallet"
    wallet_id: str

# Discriminated union — Pydantic picks the right model based on "type"
Payment = Annotated[
    Union[CreditCardPayment, BankTransferPayment, WalletPayment],
    Field(discriminator="type"),
]

class Order(BaseModel):
    total: float
    payment: Payment

# {"total": 99.99, "payment": {"type": "credit_card", "card_number": "...", "cvv": "..."}}
# → Pydantic auto-selects CreditCardPayment
```

---

## Request/Response Model Pattern

```python
# Separate models for Create, Update, Response, DB
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str          # Only on create

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None   # All optional for partial update

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    model_config = {"from_attributes": True}  # ORM mode

class UserInDB(UserBase):
    id: int
    hashed_password: str   # Never exposed in API

# Endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    ...

@app.patch("/users/{id}", response_model=UserResponse)
async def update_user(id: int, user: UserUpdate):
    ...
```

---

## Pydantic Settings

```python
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Loaded from environment variables (case-insensitive)
    app_name: str = "My App"
    debug: bool = False
    database_url: str = Field(..., alias="DATABASE_URL")
    redis_url: str = "redis://localhost:6379"
    secret_key: str
    allowed_origins: list[str] = ["http://localhost:3000"]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",   # DB__HOST → db.host
    }

@lru_cache
def get_settings():
    return Settings()

# .env file:
# DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/mydb
# SECRET_KEY=mysecretkey123
# DEBUG=true
# ALLOWED_ORIGINS=["http://localhost:3000","https://myapp.com"]
```

---

## Serialization (model_dump)

```python
class User(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: str
    created_at: datetime

user = User(id=1, name="Alice", email="a@b.com",
            hashed_password="xxx", created_at=datetime.now())

# Full dump
user.model_dump()

# Exclude fields
user.model_dump(exclude={"hashed_password"})

# Include only specific fields
user.model_dump(include={"id", "name"})

# Exclude unset fields (useful for PATCH updates)
update = UserUpdate(name="Bob")
update.model_dump(exclude_unset=True)  # {"name": "Bob"} (no email, no password)

# JSON serialization
user.model_dump_json()
user.model_dump(mode="json")  # Python dict with JSON-safe types
```

---

## Interview Questions — Pydantic

### Q1: What is the difference between Pydantic v1 and v2?

| Feature | v1 | v2 |
|---------|-----|-----|
| Core engine | Pure Python | Rust (pydantic-core) → **5-50x faster** |
| Config | `class Config` | `model_config = {}` dict |
| Validators | `@validator` | `@field_validator`, `@model_validator` |
| ORM mode | `orm_mode = True` | `from_attributes = True` |
| Dump | `.dict()`, `.json()` | `.model_dump()`, `.model_dump_json()` |
| Schema | `.schema()` | `.model_json_schema()` |

### Q2: How do you do partial updates (PATCH)?

Make all fields `Optional` in an update model, then use `model_dump(exclude_unset=True)` to get only the fields the client actually sent:

```python
update_data = user_update.model_dump(exclude_unset=True)
for key, value in update_data.items():
    setattr(db_user, key, value)
```

### Q3: What is `from_attributes = True`?

Enables Pydantic to read data from ORM objects (SQLAlchemy models) by accessing **attributes** instead of only dict keys. Without it, `UserResponse.model_validate(sqlalchemy_user)` would fail.
