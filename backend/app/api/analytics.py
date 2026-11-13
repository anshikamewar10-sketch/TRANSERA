
from fastapi import APIRouter, HTTPException

from app.services.analytics_service import AnalyticsService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics & Insights"]
)


@router.get("/dashboard")
def get_analytics_dashboard():
    try:
        service = AnalyticsService()
        return service.get_dashboard()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
