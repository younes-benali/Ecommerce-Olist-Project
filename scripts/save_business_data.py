# scripts/save_business_data.py
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import create_engine
from src.config import DB_URL, DATA_PROCESSED

def main():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # 1. Sales summary
    print("Loading sales summary...")
    df_sales = pd.read_sql("SELECT * FROM sales_summary ORDER BY month", engine)
    df_sales.to_csv(DATA_PROCESSED / "sales_summary.csv", index=False)
    print(f"  -> Saved {len(df_sales)} rows to {DATA_PROCESSED / 'sales_summary.csv'}")
    
    # 2. Top 10 cities
    print("Loading top cities...")
    df_cities = pd.read_sql("""
        SELECT customer_city, COUNT(*) as count
        FROM customer_summary
        GROUP BY customer_city
        ORDER BY count DESC
        LIMIT 10
    """, engine)
    df_cities.to_csv(DATA_PROCESSED / "top_cities.csv", index=False)
    print(f"  -> Saved {len(df_cities)} rows to {DATA_PROCESSED / 'top_cities.csv'}")
    
    # 3. RFM raw data
    print("Loading RFM data...")
    df_rfm_raw = pd.read_sql("""
        SELECT 
            c.customer_unique_id,
            MAX(o.order_purchase_timestamp) as last_order_date,
            COUNT(o.order_id) as frequency,
            SUM(p.payment_value) as monetary
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN payments p ON o.order_id = p.order_id
        GROUP BY c.customer_unique_id
    """, engine)
    df_rfm_raw.to_csv(DATA_PROCESSED / "rfm_raw.csv", index=False)
    print(f"  -> Saved {len(df_rfm_raw)} rows to {DATA_PROCESSED / 'rfm_raw.csv'}")
    
    print("\n All business CSV files saved to data/processed/")

if __name__ == "__main__":
    main()