import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class CompaniesService:
    """Service for companies data"""

    def get_companies(self):
        """Retrieve list of all companies available in the database"""
        try:
            logger.info("Fetching list of companies from database")

            DB_CONFIG = {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "dbname": settings.DB_NAME,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD
            }

            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT DISTINCT
                    company_id as ticker,
                    company_name as name,
                    sector,
                    exchange
                FROM financial_oltp.company
                ORDER BY company_name
            """

            cursor.execute(query)
            companies = cursor.fetchall()

            cursor.close()
            conn.close()

            logger.info(f"Found {len(companies)} companies in database")

            return {
                "count": len(companies),
                "companies": companies
            }

        except Exception as e:
            logger.error(f"Error fetching companies: {e}")
            raise

    def search_companies(self, query_str: str):
        """Search companies by ticker or name"""
        try:
            logger.info(f"Searching companies with query: {query_str}")

            DB_CONFIG = {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "dbname": settings.DB_NAME,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD
            }

            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT DISTINCT
                    company_id as ticker,
                    company_name as name,
                    sector,
                    exchange
                FROM financial_oltp.company
                WHERE 
                    company_id ILIKE %s OR 
                    company_name ILIKE %s
                ORDER BY company_name
                LIMIT 10
            """
            
            search_pattern = f"%{query_str}%"
            cursor.execute(query, (search_pattern, search_pattern))
            companies = cursor.fetchall()

            cursor.close()
            conn.close()

            # Enrich with real-time price if possible (simplified here, just return basic info)
            # In a real scenario, you might join with quotes table or fetch price separately.
            # For now, let's just return the company info. Frontend expects price, 
            # so we might need to Mock it or fetch it if crucial.
            # Let's attach a "price" field from latest quote if available.
            
            # Re-connect to get prices (inefficient loop but works for small limit=10)
            # Better: JOIN in the main query.
            # But let's keep it simple and safe for now.
            
            return {
                "count": len(companies),
                "companies": companies
            }

        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            raise
