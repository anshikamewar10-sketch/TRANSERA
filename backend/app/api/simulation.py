"""
---------------------------------------------------------
Simulation API
---------------------------------------------------------
Purpose:
Starts Operating System Simulation.
---------------------------------------------------------
"""

from fastapi import APIRouter

from app.models.process_model import SimulationRequest
from app.services.simulation_service import SimulationService

router = APIRouter(
    prefix="/simulation",
    tags=["Simulation Engine"]
)

simulation_service = SimulationService()


# ---------------------------------------------------------
# START SIMULATION
# ---------------------------------------------------------

@router.post("/start")
def start_simulation(request: SimulationRequest):

    return simulation_service.start_simulation(
        request.simulate_all,
        request.number_of_operations
    )