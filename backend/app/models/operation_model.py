from pydantic import BaseModel
from typing import Optional


class OperationCreate(BaseModel):
    user_id: str
    product_id: str
    operation_type: str
    description: Optional[str] = None
    department: str
    operation_quantity: int
    operation_mode: str
    priority: str


class OperationStatusUpdate(BaseModel):
    business_status: str


class OperationSearch(BaseModel):
    keyword: str