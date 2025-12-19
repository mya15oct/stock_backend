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
        
        # 1. Update Transaction Type Check Constraint
        logger.info("Updating transaction_type check constraint...")
        # Check if we need to drop the old constraint name. 
        # Postgres usually names it {table}_{column}_check.
        # We can try to drop explicitly or catch error.
        try:
           cur.execute("ALTER TABLE portfolio_oltp.portfolio_transactions DROP CONSTRAINT IF EXISTS portfolio_transactions_transaction_type_check")
        except Exception as e:
           logger.warning(f"Could not drop constraint (might be named differently): {e}")

        # Re-add with new types
        cur.execute("""
            ALTER TABLE portfolio_oltp.portfolio_transactions 
            ADD CONSTRAINT portfolio_transactions_transaction_type_check 
            CHECK (transaction_type IN ('BUY', 'SELL', 'ADJUSTMENT'))
        """)

        # 2. Add 'amount' column
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'portfolio_oltp' 
            AND table_name = 'portfolio_transactions' 
            AND column_name = 'amount';
        """)
        exists = cur.fetchone()

        if not exists:
            logger.info("Adding 'amount' column...")
            cur.execute("ALTER TABLE portfolio_oltp.portfolio_transactions ADD COLUMN amount NUMERIC(18, 6)")
            
            # 3. Backfill data
            logger.info("Backfilling amount data...")
            cur.execute("""
                UPDATE portfolio_oltp.portfolio_transactions 
                SET amount = quantity * price 
                WHERE amount IS NULL
            """)
            
            # Optional: Enforce NOT NULL after backfill?
            # Let's keep it nullable slightly for safety in case of partial failures, 
            # but ideally it should be NOT NULL. 
            # For now, let's just make sure it's populated.
        else:
            logger.info("'amount' column already exists.")

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
