# FastAPI router example with Pydantic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

# Modelos Pydantic
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

# Dependencias
async def get_current_user() -> UserResponse:
    # Implementar lógica de autenticación
    pass

# Endpoints
@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get users list"""
    # Implementar lógica de negocio
    return []

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create new user"""
    # Implementar lógica de creación
    pass

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    # Implementar lógica de búsqueda
    pass

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user"""
    # Implementar lógica de actualización
    pass
