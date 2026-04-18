import pandas as pd
from sqlalchemy import create_engine
from src.config import DB_URL, DATA_PROCESSED

# Load order_summary view from PostgreSQL, then apply cleaning rules.

def build_order_summary(save_csv=True):
    
    print("Connecting to PostgreSQL...")
    engine = create_engine(DB_URL)
    
    print("Loading order_summary view...")
    df = pd.read_sql("SELECT * FROM order_summary", engine)
    
    print(f"Initial rows: {len(df)}")
    
    # ----- Cleaning rules 
    
    # Remove duplicates
    df = df.drop_duplicates(subset='order_id')
    
    # Convert date columns to datetime (they should already be, but ensure)
    date_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Remove orders with invalid date sequences (approval after delivery)
    invalid_mask = (
        (df['order_approved_at'].notna()) & 
        (df['order_delivered_customer_date'].notna()) & 
        (df['order_approved_at'] > df['order_delivered_customer_date'])
    ) | (
        (df['order_approved_at'].notna()) & 
        (df['order_delivered_carrier_date'].notna()) & 
        (df['order_approved_at'] > df['order_delivered_carrier_date'])
    )
    df = df[~invalid_mask]
    
    # Items but no payment -> drop (only one order in your case)
    df = df[~((df['total_items'] > 0) & (df['total_payment'] == 0))]
    
    # Fix order_status: if delivery date exists, mark as delivered
    mask = (df['order_status'] != 'delivered') & (df['order_delivered_customer_date'].notna())
    df.loc[mask, 'order_status'] = 'delivered'
    
    # Drop delivered orders missing delivery date
    df = df[~((df['order_status'] == 'delivered') & (df['order_delivered_customer_date'].isna()))]
    
    # Drop rows without approval
    df = df[df['order_approved_at'].notna()]
    
    # Keep only delivered orders
    df = df[df['order_status'] == 'delivered']
    
    # Final drop of any remaining nulls
    df = df.dropna()
    
    print(f"Rows after cleaning: {len(df)}")
    
    # Optionally save to CSV
    if save_csv:
        output_path = DATA_PROCESSED / "order_summary_clean.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved cleaned data to {output_path}")
    
    return df

if __name__ == "__main__":
    # Quick test
    df = build_order_summary()
    print(f"Final shape: {df.shape}")
    print(df[['order_id', 'total_payment', 'delivery_time_days']].head())