from pydantic import BaseModel


class SimulationRequest(BaseModel):
    simulate_all: bool
    number_of_operations: int = 0