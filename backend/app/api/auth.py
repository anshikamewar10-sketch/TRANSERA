"""
---------------------------------------------------------
Authentication API
---------------------------------------------------------
Purpose:
Provides Login API.
---------------------------------------------------------
"""

from fastapi import APIRouter

from app.models.auth_model import LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

auth_service = AuthService()


@router.post("/login")
def login(request: LoginRequest):

    return auth_service.login(request)