import sys
import os
import logging

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.base_repo import BaseRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    repo = BaseRepository()
    conn = repo.get_connection()
    try:
        cur = conn.cursor()
        
        # 1. Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'portfolio_oltp' 
            AND table_name = 'portfolios' 
            AND column_name = 'is_read_only';
        """)
        exists = cur.fetchone()
        
        if not exists:
            logger.info("Adding is_read_only column...")
            cur.execute("""
                ALTER TABLE portfolio_oltp.portfolios 
                ADD COLUMN is_read_only BOOLEAN DEFAULT FALSE;
            """)
        else:
            logger.info("is_read_only column already exists.")

        # 2. Rename Default Portfolio -> Demo Portfolio and set read_only
        logger.info("Updating Default Portfolio...")
        cur.execute("""
            UPDATE portfolio_oltp.portfolios
            SET name = 'Demo Portfolio', is_read_only = TRUE
            WHERE name = 'Default Portfolio';
        """)
        
        # Also ensure that if it was already renamed, we set it to read only
        cur.execute("""
            UPDATE portfolio_oltp.portfolios
            SET is_read_only = TRUE
            WHERE name = 'Demo Portfolio';
        """)
        
        conn.commit()
        logger.info("Migration completed successfully.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
