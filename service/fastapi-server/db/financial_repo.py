from .base_repo import BaseRepository

class FinancialRepository(BaseRepository):
    def get_financials(self, company_id, view_name):
        query = f"SELECT * FROM {view_name} WHERE company_id = %s"
        return self.execute_query(query, (company_id,), fetch_all=True)
