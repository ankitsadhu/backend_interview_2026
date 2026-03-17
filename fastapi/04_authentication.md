# Authentication & Security

## OAuth2 with JWT

```
Auth Flow (Bearer Token):
  
  Client                         Server
    │                               │
    │  POST /auth/login             │
    │  {username, password}  ──────→│
    │                               │  Verify credentials
    │                               │  Generate JWT
    │  ←──── {access_token}  ──────│  
    │                               │
    │  GET /users/me                │
    │  Authorization: Bearer <JWT> →│
    │                               │  Decode & verify JWT
    │  ←──── {user data}     ──────│
    │                               │
```

### JWT Implementation

```python
# auth/jwt.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "your-secret-key"      # Use env variable in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    sub: str                         # Subject (user ID or email)
    exp: datetime
    scopes: list[str] = []

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)
    except JWTError:
        return None
```

### Auth Routes

```python
# auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "scopes": user.scopes},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

### Auth Dependency

```python
# auth/dependencies.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = await get_user_by_id(db, int(token_data.sub))
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user

# Protected endpoint
@app.get("/users/me")
async def read_me(user: User = Depends(get_current_active_user)):
    return user
```

---

## Refresh Tokens

```python
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_refresh_token(user_id: str) -> str:
    return create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401)
    
    return {
        "access_token": create_access_token(data={"sub": str(user.id)}),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str, db=Depends(get_db)):
    token_data = decode_access_token(refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user = await get_user_by_id(db, int(token_data.sub))
    if not user:
        raise HTTPException(status_code=401)
    
    return {
        "access_token": create_access_token(data={"sub": str(user.id)}),
        "token_type": "bearer",
    }
```

---

## API Key Authentication

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(
    api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
):
    key = await db.execute(select(APIKey).where(APIKey.key == api_key, APIKey.is_active == True))
    if not key.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/external/data", dependencies=[Depends(verify_api_key)])
async def external_data():
    return {"data": "sensitive"}
```

---

## Role-Based Access Control (RBAC)

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.role}' not authorized",
            )
        return user

# Usage
allow_admin = RoleChecker([Role.ADMIN])
allow_admin_or_manager = RoleChecker([Role.ADMIN, Role.MANAGER])

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, user: User = Depends(allow_admin)):
    return {"deleted": user_id}

@app.get("/reports")
async def get_reports(user: User = Depends(allow_admin_or_manager)):
    return {"reports": []}
```

---

## CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
    max_age=600,  # Preflight cache (seconds)
)
```

---

## Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    return {"data": "limited"}

# Or custom rate limiting with Redis
import aioredis

async def rate_limit(
    request: Request,
    redis: Redis = Depends(get_redis),
):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60)  # 60-second window
    
    if current > 100:  # 100 requests per minute
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": "60"},
        )
```

---

## Interview Questions — Security

### Q1: How do you secure a FastAPI application?

1. **Authentication:** JWT tokens (OAuth2 Bearer)
2. **Authorization:** RBAC or permission-based dependency
3. **CORS:** Restrict allowed origins
4. **Rate limiting:** Prevent abuse
5. **Input validation:** Pydantic models (auto)
6. **HTTPS:** TLS termination at reverse proxy
7. **Secrets:** Environment variables, never in code
8. **Headers:** Security headers via middleware (CSP, HSTS)

### Q2: How does OAuth2PasswordBearer work?

It extracts the token from the `Authorization: Bearer <token>` header. The `tokenUrl` parameter tells Swagger UI where to send login requests. It does NOT validate the token — that's your dependency's job.

### Q3: Access token vs refresh token?

| Feature | Access Token | Refresh Token |
|---------|-------------|---------------|
| Lifetime | Short (15-30 min) | Long (7-30 days) |
| Sent with | Every API request | Only to /refresh endpoint |
| Storage | Memory (client) | HttpOnly cookie (secure) |
| If stolen | Limited damage (short-lived) | Higher risk (longer-lived) |
