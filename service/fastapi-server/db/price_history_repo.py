from .base_repo import BaseRepository

class PriceHistoryRepository(BaseRepository):
    def get_price_history(self, stock_id, days=None, limit=None, start_date=None):
        query = """
            SELECT
                trading_date as date,
                open_price as open,
                high_price as high,
                low_price as low,
                close_price as close,
                volume,
                pct_change
            FROM market_data_oltp.stock_eod_prices
            WHERE stock_id = %s
        """
        params = [stock_id]
        
        if start_date:
            query += " AND trading_date >= %s"
            params.append(start_date)
        elif days:
            query += " AND trading_date >= CURRENT_DATE - INTERVAL '%s days'"
            params.append(days)
            
        query += " ORDER BY trading_date DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
            
        return self.execute_query(query, tuple(params), fetch_all=True)
