import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self):
        self.db_config = {
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "dbname": settings.DB_NAME,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "sslmode": settings.DB_SSL_MODE
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch_one:
                    result = cur.fetchone()
                    conn.commit()
                    return result
                if fetch_all:
                    result = cur.fetchall()
                    conn.commit()
                    return result
                conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        return self.execute_query(query, params, fetch_one=True)

    def fetch_all(self, query, params=None):
        return self.execute_query(query, params, fetch_all=True)
