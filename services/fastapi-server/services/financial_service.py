from db.financial_repo import FinancialRepository
from core.redis_client import RedisClient
from collections import defaultdict
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FinancialService:
    def __init__(self):
        self.repo = FinancialRepository()
        self.redis = RedisClient()

    def get_financials(self, company: str, statement_type: str, period_type: str):
        # Check cache
        cache_key = f"bctc:{company}:{statement_type}:{period_type}"
        cached = self.redis.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}")
            return cached

        # Map statement type to view name
        view_mapping = {
            "IS": "financial_oltp.vw_income_statement_recent",
            "BS": "financial_oltp.vw_balance_sheet_recent",
            "CF": "financial_oltp.vw_cashflow_statement_recent"
        }
        view_name = view_mapping.get(statement_type)
        if not view_name:
            raise ValueError("Invalid statement type")

        # In a real app, we'd look up company_id from ticker first
        # For now assuming company is passed as ID or we need a lookup
        # This part needs adjustment based on actual DB schema
        # Assuming company ticker is passed and we need to look up ID
        # But for now let's reuse the logic from original server.py which passed company ticker directly to query?
        # Wait, original server.py query was: "SELECT * FROM {view_name} WHERE company_id = %s"
        # And it passed 'company' (ticker) to it. This implies company_id column might actually hold ticker string?
        # Or there was a mismatch in original code. 
        # Let's assume company_id is the ticker for now based on original code.
        
        rows = self.repo.get_financials(company, view_name)
        if not rows:
            return None
            
        result = self._transform_data(rows, company, statement_type, period_type)
        
        # Cache result
        self.redis.set(cache_key, result)
        
        return result

    def _transform_data(self, rows: List[Dict[str, Any]], company: str, statement_type: str, period_type: str) -> Dict[str, Any]:
        # Reuse transformation logic from original server.py
        data_dict = defaultdict(dict)
        periods_set = set()
        
        for row in rows:
            item_name = row['item_name']
            item_value = float(row['item_value']) if row['item_value'] is not None else 0
            fiscal_year = row['fiscal_year']
            fiscal_quarter = row['fiscal_quarter']
            
            if period_type == "annual":
                period_key = str(fiscal_year)
            else:
                period_key = f"{fiscal_year}-{fiscal_quarter}"
            
            data_dict[item_name][period_key] = item_value
            periods_set.add(period_key)
        
        if period_type == "annual":
            periods_sorted = sorted(list(periods_set), key=lambda x: int(x), reverse=True)
        else:
            def sort_key(period_str):
                year_str, quarter_str = period_str.split('-')
                year = int(year_str)
                quarter_num = int(quarter_str[1])
                return (year, quarter_num)
            periods_sorted = sorted(list(periods_set), key=sort_key, reverse=True)
        
        return {
            "company": company,
            "type": statement_type,
            "period": period_type,
            "periods": periods_sorted[:10],
            "data": dict(data_dict)
        }
