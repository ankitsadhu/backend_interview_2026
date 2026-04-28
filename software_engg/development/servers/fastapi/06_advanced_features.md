# Advanced Features

## Middleware

Middleware runs **before** every request and **after** every response.

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid

app = FastAPI()

# Method 1: @app.middleware decorator
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response

# Method 2: Class-based middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"→ {request.method} {request.url.path}")
        response = await call_next(request)
        print(f"← {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)
```

### Middleware Execution Order

```
Request comes in:
  Middleware 1 (first added) → enters first
    Middleware 2 → enters second
      Middleware 3 → enters third
        Route handler (endpoint)
      Middleware 3 → exits third
    Middleware 2 → exits second
  Middleware 1 → exits first
Response goes out

Note: Like an onion — first added = outermost layer
```

---

## Background Tasks

Run tasks **after** the response is sent (doesn't block the response).

```python
from fastapi import BackgroundTasks

def send_email(email: str, subject: str, body: str):
    """This runs AFTER the response is sent"""
    # Connect to SMTP, send email...
    print(f"Sending email to {email}: {subject}")

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")

@app.post("/users", status_code=201)
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
):
    # Create user in DB...
    new_user = await user_repo.create(user)
    
    # Queue background tasks (run after response)
    background_tasks.add_task(send_email, user.email, "Welcome!", "Thanks for signing up")
    background_tasks.add_task(write_log, f"User created: {user.email}")
    
    return new_user  # Response sent immediately, tasks run in background
```

> **When to use Background Tasks vs Celery:**
> - **BackgroundTasks:** Simple, quick tasks (sending one email, writing a log)
> - **Celery/RQ:** Heavy tasks, retries, scheduling, separate worker process

---

## WebSockets

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Room {room_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"User left room {room_id}")
```

---

## Server-Sent Events (SSE)

```python
from fastapi.responses import StreamingResponse
import asyncio
import json

async def event_generator():
    counter = 0
    while True:
        counter += 1
        data = json.dumps({"count": counter, "timestamp": str(datetime.now())})
        yield f"data: {data}\n\n"     # SSE format
        await asyncio.sleep(1)

@app.get("/events")
async def stream_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

---

## File Uploads & Downloads

```python
from fastapi import UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
import aiofiles

# Upload
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate
    if file.size > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=413, detail="File too large")
    
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Unsupported file type")
    
    # Save to disk
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return {"filename": file.filename, "size": len(content)}

# Multiple files
@app.post("/upload-multiple")
async def upload_multiple(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        results.append({"filename": file.filename, "size": len(content)})
    return results

# Download
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"uploads/{filename}"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
```

---

## Lifespan Events (Startup/Shutdown)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — runs before accepting requests
    print("Starting up...")
    app.state.db_pool = await create_db_pool()
    app.state.redis = await aioredis.from_url("redis://localhost")
    
    yield  # ← App runs here (handles requests)
    
    # SHUTDOWN — runs when app is stopping
    print("Shutting down...")
    await app.state.db_pool.close()
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)
```

---

## Custom Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "detail": exc.detail,
            "path": str(request.url),
        },
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "detail": "Resource not found"},
    )

# Usage
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await repo.get(item_id)
    if not item:
        raise AppException(
            status_code=404,
            detail=f"Item {item_id} not found",
            error_code="ITEM_NOT_FOUND",
        )
    return item
```

---

## Streaming Responses

```python
from fastapi.responses import StreamingResponse
import csv
import io

# Stream large CSV file
@app.get("/export/users")
async def export_users(db: AsyncSession = Depends(get_db)):
    async def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "name", "email"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)
        
        # Stream rows in batches
        offset = 0
        batch_size = 1000
        while True:
            result = await db.execute(
                select(User).offset(offset).limit(batch_size)
            )
            users = result.scalars().all()
            if not users:
                break
            
            for user in users:
                writer.writerow([user.id, user.name, user.email])
            
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            offset += batch_size
    
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )
```

---

## Interview Questions — Advanced

### Q1: BackgroundTasks vs Celery?

| Feature | BackgroundTasks | Celery |
|---------|----------------|--------|
| Runs in | Same process (after response) | Separate worker process |
| Use case | Quick tasks (log, email) | Heavy/long tasks (reports, ML) |
| Retries | ❌ | ✅ Built-in |
| Scheduling | ❌ | ✅ Celery Beat |
| Monitoring | ❌ | ✅ Flower dashboard |

### Q2: How do WebSockets work in FastAPI?

FastAPI supports WebSockets natively via Starlette. You define a `@app.websocket("/path")` endpoint that accepts a `WebSocket` object. The connection is bi-directional and persistent — both client and server can send messages at any time. You manage connections manually (accept, receive, send, close).

### Q3: What are lifespan events used for?

Lifespan events run code at app startup (before accepting requests) and shutdown (after all requests are done). Common uses: initialize DB connection pools, connect to Redis/cache, load ML models into memory, and clean up resources on shutdown.
