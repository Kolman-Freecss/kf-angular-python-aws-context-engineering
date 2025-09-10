# Patrón de Arquitectura FastAPI

## Estructura de Carpetas

```
app/
├── api/               # Routers por dominio
│   ├── users.py
│   ├── products.py
│   └── auth.py
├── core/              # Configuración core
│   ├── config.py
│   ├── database.py
│   └── security.py
├── models/            # Modelos Pydantic
│   ├── user.py
│   └── product.py
├── schemas/           # Esquemas de base de datos
│   ├── user.py
│   └── product.py
└── services/          # Lógica de negocio
    ├── user_service.py
    └── product_service.py
```

## Patrones de Routers

### Router por Dominio
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

### Inyección de Dependencias
```python
# core/dependencies.py
from services.user_service import UserService

def get_user_service() -> UserService:
    return UserService()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return user_service.get_current_user(token)
```

## Modelos Pydantic

### Modelos Base y Respuesta
```python
# models/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
```
