# FastAPI Fundamentals

## What is FastAPI?

**FastAPI** is a modern, high-performance Python web framework built on **Starlette** (ASGI) and **Pydantic** (validation).

```
┌──────────────────────────────────────────────────────┐
│                     FastAPI                           │
│                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Starlette   │  │  Pydantic    │  │  OpenAPI   │ │
│  │  (ASGI,      │  │  (Validation,│  │  (Auto     │ │
│  │   routing,   │  │   models,    │  │   docs,    │ │
│  │   middleware) │  │   settings)  │  │   Swagger) │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              Uvicorn (ASGI Server)             │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### WSGI vs ASGI

| Aspect | WSGI (Flask, Django) | ASGI (FastAPI, Starlette) |
|--------|---------------------|--------------------------|
| I/O model | Synchronous | Asynchronous (async/await) |
| Protocol | HTTP only | HTTP + WebSocket + HTTP/2 |
| Concurrency | Thread-based | Event loop + coroutines |
| Server | Gunicorn, uWSGI | Uvicorn, Hypercorn, Daphne |
| Performance | Good | Excellent (on par with Node.js, Go) |

---

## Minimal Application

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="A sample FastAPI application",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# Run: uvicorn main:app --reload
# Docs: http://localhost:8000/docs (Swagger)
# Alt docs: http://localhost:8000/redoc
```

---

## Path Parameters

```python
from fastapi import FastAPI, Path

app = FastAPI()

# Basic path parameter
@app.get("/users/{user_id}")
async def get_user(user_id: int):     # Auto-validates as int
    return {"user_id": user_id}

# Path with validation
@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(
        ...,                           # Required
        title="Item ID",
        description="The ID of the item",
        ge=1,                          # >= 1
        le=1000,                       # <= 1000
    )
):
    return {"item_id": item_id}

# Multiple path parameters
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}

# Enum path parameters
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model": model_name.value}
```

---

## Query Parameters

```python
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

# Basic query parameters
@app.get("/items")
async def list_items(
    skip: int = 0,                     # Default: 0
    limit: int = 10,                   # Default: 10
    search: Optional[str] = None,      # Optional
):
    # GET /items?skip=0&limit=10&search=phone
    return {"skip": skip, "limit": limit, "search": search}

# Query with validation
@app.get("/products")
async def list_products(
    q: str = Query(
        default=None,
        min_length=3,                  # Min 3 characters
        max_length=50,                 # Max 50 characters
        regex="^[a-zA-Z0-9 ]+$",      # Regex validation
        title="Search query",
        description="Search term for filtering",
    ),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    return {"q": q, "page": page, "size": size}

# List query parameters
@app.get("/filter")
async def filter_items(
    tags: list[str] = Query(default=[]),
    # GET /filter?tags=python&tags=fastapi
):
    return {"tags": tags}
```

---

## Request Body (Pydantic Models)

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

app = FastAPI()

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    bio: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    bio: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}  # For ORM mode

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    # user is auto-validated Pydantic model
    # Invalid data → 422 Unprocessable Entity (auto-generated)
    return {
        "id": 1,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "bio": user.bio,
        "created_at": datetime.now(),
    }
```

### Multiple Body Parameters

```python
from fastapi import Body

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str

@app.put("/items/{item_id}")
async def update_item(
    item_id: int,                      # Path parameter
    item: Item,                        # Body (JSON key: "item")
    user: User,                        # Body (JSON key: "user")
    importance: int = Body(...),       # Body (singular value)
):
    # Expected JSON body:
    # {
    #   "item": {"name": "Phone", "price": 999},
    #   "user": {"username": "alice"},
    #   "importance": 5
    # }
    return {"item_id": item_id, "item": item, "user": user}
```

---

## Response Model & Status Codes

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class ItemOut(BaseModel):
    name: str
    price: float
    # Note: 'internal_code' is NOT in response → filtered out!

class ItemIn(BaseModel):
    name: str
    price: float
    internal_code: str  # Sensitive field

@app.post(
    "/items",
    response_model=ItemOut,             # Filters response to only these fields
    status_code=201,                     # Created
    summary="Create an item",
    description="Create a new item in the inventory",
    response_description="The created item",
    tags=["items"],                      # Group in docs
)
async def create_item(item: ItemIn):
    return item  # internal_code is filtered out by response_model!

# Multiple response types
from fastapi import status

@app.get(
    "/items/{item_id}",
    responses={
        200: {"description": "Item found"},
        404: {"description": "Item not found"},
    },
)
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
            headers={"X-Error": "Item not found"},
        )
    return items_db[item_id]
```

---

## Route Organization with APIRouter

```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def list_users():
    return [{"id": 1, "name": "Alice"}]

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}

@router.post("/", status_code=201)
async def create_user(user: UserCreate):
    return {"id": 1, **user.model_dump()}
```

```python
# main.py
from fastapi import FastAPI
from routers import users, items, auth

app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
```

---

## Headers, Cookies, and Form Data

```python
from fastapi import FastAPI, Header, Cookie, Form, File, UploadFile

app = FastAPI()

# Headers
@app.get("/headers")
async def read_headers(
    user_agent: str = Header(None),
    x_custom: Optional[str] = Header(None, alias="x-custom-header"),
):
    return {"user_agent": user_agent, "custom": x_custom}

# Cookies
@app.get("/cookies")
async def read_cookies(
    session_id: Optional[str] = Cookie(None),
):
    return {"session_id": session_id}

# Form data
@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    return {"username": username}

# File upload
@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }
```

---

## Async vs Sync Endpoints

```python
# Async endpoint — runs on the event loop (non-blocking)
@app.get("/async")
async def async_endpoint():
    data = await some_async_operation()  # Non-blocking I/O
    return data

# Sync endpoint — runs in a thread pool automatically!
@app.get("/sync")
def sync_endpoint():
    data = some_blocking_operation()     # FastAPI runs this in a thread pool
    return data

# ⚠️ DON'T DO THIS — blocks the event loop:
@app.get("/bad")
async def bad_endpoint():
    data = some_blocking_operation()     # Blocks event loop! No 'await'!
    return data
```

| Function type | FastAPI behavior | Use when |
|--------------|-----------------|----------|
| `async def` | Runs on event loop (main thread) | Using `await` with async libraries |
| `def` (sync) | Runs in thread pool (won't block loop) | Using blocking libraries (requests, sqlalchemy sync) |

---

## Interview Questions — Fundamentals

### Q1: What makes FastAPI fast?

1. **ASGI** — async I/O (non-blocking, event-loop based)
2. **Starlette** — high-performance ASGI framework underneath
3. **Pydantic** — Rust-based validation (pydantic-core in v2)
4. **Auto-generated docs** — no runtime overhead for documentation
5. **Type hints** — compile-time-like checks, no reflection needed

### Q2: What's the difference between `async def` and `def` endpoints?

- `async def` → runs on the event loop. Must use `await` for I/O. Blocking calls freeze the loop!
- `def` (sync) → FastAPI automatically runs it in a **thread pool** so it doesn't block the event loop.

**Rule:** Use `async def` with async libraries. Use `def` with blocking libraries.

### Q3: How does FastAPI auto-generate API docs?

FastAPI generates an **OpenAPI schema** from your type hints, Pydantic models, and decorator metadata. Swagger UI (`/docs`) and ReDoc (`/redoc`) render this schema as interactive documentation — all automatic, no manual specification needed.
