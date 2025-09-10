# FastAPI router template
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/{{endpoint-name}}", tags=["{{endpoint-name}}"])

# TODO: Define Pydantic models
class {{ModelName}}Base(BaseModel):
    # TODO: Add base fields
    pass

class {{ModelName}}Create({{ModelName}}Base):
    # TODO: Add creation-specific fields
    pass

class {{ModelName}}Response({{ModelName}}Base):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class {{ModelName}}Update(BaseModel):
    # TODO: Add optional update fields
    pass

# TODO: Implement dependencies
# async def get_current_user() -> User:
#     pass

# TODO: Implement service injection
# def get_{{service_name}}_service() -> {{ServiceName}}Service:
#     return {{ServiceName}}Service()

# Endpoints
@router.get("/", response_model=List[{{ModelName}}Response])
async def get_{{endpoint_name}}(
    skip: int = 0,
    limit: int = 100,
    # TODO: Add authentication dependency
    # current_user: User = Depends(get_current_user)
):
    """Get {{endpoint-name}} list"""
    # TODO: Implement business logic
    return []

@router.post("/", response_model={{ModelName}}Response)
async def create_{{endpoint_name}}({{endpoint_name}}: {{ModelName}}Create):
    """Create new {{endpoint-name}}"""
    # TODO: Implement creation logic
    pass

@router.get("/{id}", response_model={{ModelName}}Response)
async def get_{{endpoint_name}}_by_id(id: int):
    """Get {{endpoint-name}} by ID"""
    # TODO: Implement retrieval logic
    pass

@router.put("/{id}", response_model={{ModelName}}Response)
async def update_{{endpoint_name}}(
    id: int,
    {{endpoint_name}}_update: {{ModelName}}Update,
    # TODO: Add authentication dependency
    # current_user: User = Depends(get_current_user)
):
    """Update {{endpoint-name}}"""
    # TODO: Implement update logic
    pass

@router.delete("/{id}")
async def delete_{{endpoint_name}}(id: int):
    """Delete {{endpoint-name}}"""
    # TODO: Implement deletion logic
    pass