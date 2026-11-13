
"""
TRANSERA - Scheduler API
"""

from fastapi import APIRouter, Query

from app.services.scheduler.scheduler_service import SchedulerService


router = APIRouter(
    prefix="/scheduler",
    tags=["Execution Scheduler"]
)

scheduler_service = SchedulerService()


@router.post("/fcfs")
def fcfs():
    return scheduler_service.execute_scheduler("FCFS")


@router.post("/sjf")
def sjf():
    return scheduler_service.execute_scheduler("SJF")


@router.post("/priority")
def priority():
    return scheduler_service.execute_scheduler("PRIORITY")


@router.post("/round-robin")
def round_robin():
    return scheduler_service.execute_scheduler("ROUND_ROBIN")


@router.post("/run/{process_id}")
def start_running_process(
    process_id: str,
    algorithm: str = Query(default="FCFS")
):
    return scheduler_service.start_running_process(
        process_id,
        algorithm
    )


@router.post("/complete-burst/{process_id}")
def complete_cpu_burst(process_id: str):
    return scheduler_service.complete_cpu_burst(process_id)


@router.post("/complete-quantum/{process_id}")
def complete_quantum(
    process_id: str,
    duration: float = Query(gt=0, le=2)
):
    return scheduler_service.complete_quantum(
        process_id,
        duration
    )
