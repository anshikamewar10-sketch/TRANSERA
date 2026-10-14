"""
---------------------------------------------------------
Deadlock API
---------------------------------------------------------
Purpose:
Provides APIs for Deadlock Detection.
---------------------------------------------------------
"""

from fastapi import APIRouter

from app.services.deadlock.deadlock_service import DeadlockService

router = APIRouter(
    prefix="/deadlock",
    tags=["Deadlock Resolver"]
)

deadlock_service = DeadlockService()


# =====================================================
# CHECK DEADLOCK
# =====================================================

@router.get("/check")
def check_deadlock():

    return deadlock_service.check_deadlock()