"""
---------------------------------------------------------
Scheduler API
---------------------------------------------------------
Purpose:
Provides CPU Scheduling APIs.
---------------------------------------------------------
"""

from fastapi import APIRouter

from app.services.scheduler.scheduler_service import SchedulerService

router = APIRouter(
    prefix="/scheduler",
    tags=["Execution Scheduler"]
)

scheduler_service = SchedulerService()


# =====================================================
# FCFS
# =====================================================

@router.post("/fcfs")
def fcfs():

    return scheduler_service.execute_scheduler("FCFS")

# =====================================================
# START RUNNING PROCESS
# =====================================================

@router.post("/run/{process_id}")
def start_running_process(process_id: str):

    return scheduler_service.start_running_process(process_id)


# =====================================================
# COMPLETE CPU BURST
# =====================================================

@router.post("/complete-burst/{process_id}")
def complete_cpu_burst(process_id: str):

    return scheduler_service.complete_cpu_burst(process_id)


# =====================================================
# SJF
# =====================================================



@router.post("/sjf")
def sjf():

    return scheduler_service.execute_scheduler("SJF")


# =====================================================
# PRIORITY
# =====================================================

@router.post("/priority")
def priority():

    return scheduler_service.execute_scheduler("PRIORITY")


# =====================================================
# ROUND ROBIN
# =====================================================

@router.post("/round-robin")
def round_robin():

    return scheduler_service.execute_scheduler("ROUND_ROBIN")