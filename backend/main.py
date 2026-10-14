"""
---------------------------------------------------------
Transera Backend
---------------------------------------------------------
Main FastAPI Application
---------------------------------------------------------
"""

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.api.operation import router as operation_router
from app.api.simulation import router as simulation_router
from app.api.scheduler import router as scheduler_router
from app.api.resource import router as resource_router
from app.api.deadlock import router as deadlock_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="Transera API",
    description="Business Execution & System Operations Console",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(operation_router)
app.include_router(simulation_router)
app.include_router(scheduler_router)
app.include_router(resource_router)
app.include_router(deadlock_router)



@app.get("/")
def home():

    return {
        "application": "Transera",
        "version": "1.0",
        "status": "Running Successfully"
    }