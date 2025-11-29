from fastapi import APIRouter, Query, HTTPException
from services.profile_service import ProfileService

router = APIRouter()

@router.get("/profile", tags=["Company Info"])
async def get_profile(ticker: str = Query(..., example="IBM")):
    """Get company profile with industry, sector, and description"""
    service = ProfileService()
    try:
        data = service.get_profile(ticker)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
