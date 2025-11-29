import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PriceHistoryService:
    """Service for stock price history data"""

    def get_price_history(self, ticker: str, period: str = "3m"):
        """Get price history for a given ticker and period with OHLC data"""
        try:
            logger.info(f"Fetching price history for {ticker}, period: {period}")

            DB_CONFIG = {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "dbname": settings.DB_NAME,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD
            }

            # Convert period to days
            period_days_map = {
                "1d": 1,
                "5d": 5,
                "1m": 30,
                "3m": 90,
                "6m": 180,
                "ytd": 365,  # Simplified
                "1y": 365,
                "5y": 1825,
                "max": 3650  # 10 years
            }

            days = period_days_map.get(period, 90)

            conn = psycopg2.connect(**DB_CONFIG)
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get stock_id from ticker
                    cur.execute("""
                        SELECT stock_id
                        FROM market_data_oltp.stocks
                        WHERE stock_ticker = %s
                    """, (ticker.upper(),))

                    stock_result = cur.fetchone()
                    if not stock_result:
                        logger.warning(f"Stock ticker {ticker} not found in database")
                        return []

                    stock_id = stock_result['stock_id']

                    # Get OHLC data from stock_eod_prices
                    cur.execute("""
                        SELECT
                            trading_date as date,
                            open_price as open,
                            high_price as high,
                            low_price as low,
                            close_price as close,
                            volume
                        FROM market_data_oltp.stock_eod_prices
                        WHERE stock_id = %s
                            AND trading_date >= CURRENT_DATE - INTERVAL '%s days'
                        ORDER BY trading_date ASC
                    """, (stock_id, days))

                    rows = cur.fetchall()

                    # Transform to array of OHLC objects
                    price_history = []
                    for row in rows:
                        price_history.append({
                            "date": row['date'].isoformat() if row['date'] else None,
                            "open": float(row['open']) if row['open'] else 0,
                            "high": float(row['high']) if row['high'] else 0,
                            "low": float(row['low']) if row['low'] else 0,
                            "close": float(row['close']) if row['close'] else 0,
                            "volume": int(row['volume']) if row['volume'] else 0
                        })

                    logger.info(f"Retrieved {len(price_history)} price records for {ticker}")
                    return price_history

            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            raise
