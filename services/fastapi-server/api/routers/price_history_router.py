from fastapi import APIRouter, Query, HTTPException
from services.price_history_service import PriceHistoryService

router = APIRouter()

@router.get("/price-history", tags=["Real-Time Data"])
async def get_price_history(
    ticker: str = Query(..., description="Stock ticker symbol", example="IBM"),
    period: str = Query("3m", description="Time period", example="3m")
):
    """Get price history data"""
    service = PriceHistoryService()
    try:
        data = service.get_price_history(ticker, period)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
