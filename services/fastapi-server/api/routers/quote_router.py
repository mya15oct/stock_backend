from fastapi import APIRouter, Query, HTTPException
from services.quote_service import QuoteService

router = APIRouter()

@router.get("/quote", tags=["Real-Time Data"])
async def get_quote(ticker: str = Query(..., example="IBM")):
    service = QuoteService()
    try:
        data = service.get_quote(ticker)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
