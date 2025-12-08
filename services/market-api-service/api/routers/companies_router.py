from fastapi import APIRouter, HTTPException
from services.companies_service import CompaniesService

router = APIRouter()

@router.get("/api/companies", tags=["Company Info"])
async def get_companies():
    """📋 Get all available companies"""
    service = CompaniesService()
    try:
        result = service.get_companies()
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/search", tags=["Company Info"])
async def search_companies(q: str):
    """🔍 Search companies by ticker or name"""
    service = CompaniesService()
    try:
        result = service.search_companies(q)
        return {"success": True, "data": result['companies']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/search", tags=["Company Info"])
async def search_companies(q: str):
    """🔍 Search companies by ticker or name"""
    service = CompaniesService()
    try:
        result = service.search_companies(q)
        # Flatten structure to match what frontend expects (list of stocks)
        # The service returns {count, companies}, but legacy API might expect just list or nested.
        # Let's check apiBase.ts or Header.tsx expectation.
        # Header.tsx expects Stock[] directly or wrapped.
        # Let's return the list directly in 'data' or 'results' wrapper via common response format.
        return {"success": True, "data": result['companies']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
