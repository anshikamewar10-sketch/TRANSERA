
"""
---------------------------------------------------------
Deadlock API
---------------------------------------------------------
Purpose:
Banker's Safety Check, Deadlock Detection
and Deadlock Recovery.
---------------------------------------------------------
"""

from fastapi import APIRouter

from app.services.deadlock.deadlock_service import DeadlockService
from app.services.deadlock.recovery_service import DeadlockRecoveryService


router = APIRouter(
    prefix="/deadlock",
    tags=["Deadlock Resolver"]
)

deadlock_service = DeadlockService()
recovery_service = DeadlockRecoveryService()


# =====================================================
# BANKER'S SAFETY CHECK
# =====================================================

@router.get("/check")
def check_deadlock():

    return deadlock_service.check_deadlock()


# =====================================================
# ACTUAL DEADLOCK DETECTION
# =====================================================

# =====================================================
# DETECT DEADLOCK + SIMULATED COMPLETION
# =====================================================

@router.post("/detect")
def detect_deadlock():

    return deadlock_service.detect_deadlock()

# =====================================================
# DEADLOCK RECOVERY
# =====================================================

@router.post("/recover")
def recover_deadlock():

    return recovery_service.recover_deadlock()

# =====================================================
# RESUME RECOVERY VICTIM
# =====================================================

@router.post("/resume/{process_id}")
def resume_process(process_id: str):

    return recovery_service.resume_process(process_id)
