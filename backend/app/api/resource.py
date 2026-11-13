"""
---------------------------------------------------------
Resource API
---------------------------------------------------------
Purpose:
Provides APIs for Resource Center.
---------------------------------------------------------
"""

from fastapi import APIRouter

from app.services.resource.resource_service import ResourceService

router = APIRouter(
    prefix="/resources",
    tags=["Resource Center"]
)

resource_service = ResourceService()

@router.post("/allocate")
def allocate_resources():

    return resource_service.manage_resources()
# =====================================================
# RESOURCE HISTORY
# =====================================================

@router.get("/history")
def resource_history():

    return resource_service.get_resource_history()

from fastapi import HTTPException

@router.post("/release/{process_id}")
def release_resources(process_id: str):

    result = resource_service.complete_and_release(process_id)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result