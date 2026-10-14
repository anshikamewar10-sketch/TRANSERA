"""
---------------------------------------------------------
Operation API
---------------------------------------------------------
Purpose:
Provides API endpoints for Business Operations.
---------------------------------------------------------
"""

from fastapi import APIRouter
from app.models.operation_model import (
    OperationCreate,
    OperationStatusUpdate
)
from app.services.operation_service import OperationService

router = APIRouter(
    prefix="/operations",
    tags=["Operation Hub"]
)

operation_service = OperationService()


# --------------------------------------------------
# CREATE OPERATION
# --------------------------------------------------

@router.post("/create")
def create_operation(operation: OperationCreate):
    return operation_service.create_operation(operation)


# --------------------------------------------------
# VIEW ALL OPERATIONS
# --------------------------------------------------

@router.get("/all")
def get_all_operations():
    return operation_service.get_all_operations()


# --------------------------------------------------
# SEARCH OPERATION
# --------------------------------------------------

@router.get("/search/{keyword}")
def search_operation(keyword: str):
    return operation_service.search_operation(keyword)


# --------------------------------------------------
# UPDATE STATUS
# --------------------------------------------------

@router.put("/update-status/{operation_id}")
def update_status(
    operation_id: str,
    status: OperationStatusUpdate
):
    return operation_service.update_status(
        operation_id,
        status.business_status
    )
    # =====================================================
# GET OPERATION DETAILS
# =====================================================

@router.get("/details/{operation_id}")
def get_operation_details(operation_id: str):

    return operation_service.get_operation_details(
        operation_id
    )