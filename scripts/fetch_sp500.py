"""
Script to fetch S&P 500 (^GSPC) data from Yahoo Finance and populate the database.
This allows the frontend to query S&P 500 price history via the standard API.
"""

import yfinance as yf
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "Web_quan_li_danh_muc")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")

TICKER = "^GSPC"
NAME = "S&P 500"

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            options="-c search_path=market_data_oltp"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def fetch_sp500_data():
    print(f"Fetching data for {TICKER} from Yahoo Finance...")
    try:
        # Fetch data for max period to fill history
        # You can adjust period="1y" or "5y" if you don't want everything
        ticker = yf.Ticker(TICKER)
        hist = ticker.history(period="5y") 
        
        if hist.empty:
            print("No data found.")
            return None
            
        print(f"Fetched {len(hist)} records.")
        return hist
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def upsert_stock(conn):
    """Ensure S&P 500 exists in stocks table"""
    try:
        with conn.cursor() as cur:
            # Check if exists
            cur.execute("SELECT stock_id FROM stocks WHERE stock_ticker = %s", (TICKER,))
            res = cur.fetchone()
            
            if res:
                stock_id = res[0]
                print(f"Stock {TICKER} exists with ID {stock_id}.")
                return stock_id
            
            # Insert if not exists (company_id is NULL for indices)
            print(f"Inserting new stock: {TICKER}")
            cur.execute(
                """
                INSERT INTO stocks (stock_ticker, stock_name, company_id, exchange)
                VALUES (%s, %s, NULL, 'INDEX')
                RETURNING stock_id
                """,
                (TICKER, NAME)
            )
            stock_id = cur.fetchone()[0]
            conn.commit()
            print(f"Created stock ID {stock_id}.")
            return stock_id
            
    except Exception as e:
        print(f"Error upserting stock: {e}")
        conn.rollback()
        return None

def upsert_prices(conn, stock_id, df):
    """Upsert price history into stock_eod_prices"""
    print("Upserting price history...")
    try:
        data_tuples = []
        for index, row in df.iterrows():
            # index is Timestamp
            date_val = index.date()
            open_val = float(row['Open'])
            high_val = float(row['High'])
            low_val = float(row['Low'])
            close_val = float(row['Close'])
            volume_val = int(row['Volume'])
            
            # Simple pct_change calculation could be done here, 
            # but for simplicity we rely on what we have. 
            # We can calculate it relative to previous close if strictly needed.
            pct_change = 0.0 
            
            data_tuples.append((
                stock_id, 
                date_val, 
                open_val, 
                high_val, 
                low_val, 
                close_val, 
                volume_val, 
                pct_change
            ))
            
        query = """
            INSERT INTO stock_eod_prices 
            (stock_id, trading_date, open_price, high_price, low_price, close_price, volume, pct_change)
            VALUES %s
            ON CONFLICT (stock_id, trading_date) 
            DO UPDATE SET 
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                volume = EXCLUDED.volume;
        """
        
        with conn.cursor() as cur:
            execute_values(cur, query, data_tuples)
            
        conn.commit()
        print(f"Successfully upserted {len(data_tuples)} records.")
        
    except Exception as e:
        print(f"Error upserting prices: {e}")
        conn.rollback()

def main():
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        stock_id = upsert_stock(conn)
        if not stock_id:
            return
            
        df = fetch_sp500_data()
        if df is not None:
            upsert_prices(conn, stock_id, df)
            
    finally:
        conn.close()
        print("Done.")

if __name__ == "__main__":
    main()
