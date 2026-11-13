
from fastapi import APIRouter, HTTPException

from app.services.transaction_service import TransactionService


router = APIRouter(
    prefix="/transactions",
    tags=["Transaction Center"]
)


@router.post("/execute")
def execute_transactions():
    try:
        service = TransactionService()
        return service.execute_transactions()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@router.get("/history")
def get_transaction_history():
    try:
        service = TransactionService()
        return service.get_history()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
