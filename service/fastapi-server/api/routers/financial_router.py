from fastapi import APIRouter, Depends, HTTPException, Query
from services.financial_service import FinancialService
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict

router = APIRouter()

class StatementType(str, Enum):
    IS = "IS"
    BS = "BS"
    CF = "CF"

class PeriodType(str, Enum):
    annual = "annual"
    quarterly = "quarterly"

class FinancialDataResponse(BaseModel):
    company: str
    type: str
    period: str
    periods: List[str]
    data: Dict[str, Dict[str, float]]

@router.get("/api/financials", response_model=FinancialDataResponse, tags=["Financial Data"])
async def get_financials(
    company: str = Query(..., min_length=1),
    type: StatementType = Query(...),
    period: PeriodType = Query(...)
):
    service = FinancialService()
    try:
        result = service.get_financials(company, type.value, period.value)
        if not result:
            raise HTTPException(status_code=404, detail=f"No financial data found for {company}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
