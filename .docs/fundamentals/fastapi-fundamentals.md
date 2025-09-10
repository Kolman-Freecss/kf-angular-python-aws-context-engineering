# FastAPI Fundamentals

## Core Concepts

### Router Structure
Organize endpoints by domain:

```python
# api/users.py
from fastapi import APIRouter, Depends
from models.user import UserCreate, UserResponse
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_users(skip=skip, limit=limit)
```

### Pydantic Models
Strong typing with validation:

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Dependency Injection
```python
# core/dependencies.py
from fastapi import Depends
from services.user_service import UserService
from core.security import get_current_user

def get_user_service() -> UserService:
    return UserService()

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

## Architecture Patterns

### Project Structure
```
app/
├── api/               # API routers
│   ├── users.py
│   ├── products.py
│   └── auth.py
├── core/              # Core functionality
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── dependencies.py
├── models/            # Pydantic models
│   ├── user.py
│   └── product.py
├── schemas/           # Database schemas
│   ├── user.py
│   └── product.py
├── services/          # Business logic
│   ├── user_service.py
│   └── product_service.py
└── main.py           # Application entry point
```

### Database Integration
```python
# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Service Layer
```python
# services/user_service.py
from sqlalchemy.orm import Session
from models.user import UserCreate, UserUpdate
from schemas.user import User

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
    
    async def create_user(self, user: UserCreate) -> User:
        db_user = User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
```

## Security

### Authentication
```python
# core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### CORS Configuration
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing

### Unit Tests
```python
# tests/test_user_service.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.user_service import UserService
from models.user import UserCreate

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_user(db_session):
    service = UserService(db_session)
    user_data = UserCreate(
        name="John Doe",
        email="john@example.com",
        password="securepassword"
    )
    
    user = service.create_user(user_data)
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
```

### API Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["name"] == "John Doe"
```

## Best Practices

1. **Use Pydantic models** for request/response validation
2. **Implement proper error handling** with HTTPException
3. **Use dependency injection** for services and database
4. **Organize by domain** with separate routers
5. **Implement proper authentication** and authorization
6. **Use async/await** for I/O operations
7. **Write comprehensive tests** for all endpoints
8. **Use environment variables** for configuration
9. **Implement proper logging** and monitoring
10. **Use type hints** throughout the codebase
