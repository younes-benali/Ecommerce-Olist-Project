import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
from src.config import DB_URL, DATA_PROCESSED

# Load cleaned orders and enrich with customer & product features,
# then engineer time features, encode categories, and create target.
def build_feature_set(save_csv=True):
    
    print("Loading cleaned orders...")
    df_orders = pd.read_csv(DATA_PROCESSED / "order_summary_clean.csv", parse_dates=[
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ])
    
    print("Connecting to PostgreSQL for customer and product views...")
    engine = create_engine(DB_URL)
    
    # Load customer_summary view (contains customer_state)
    df_customers = pd.read_sql("SELECT customer_id, customer_state FROM customer_summary", engine)
    
    # Load product_summary view (contains product aggregates)
    df_products = pd.read_sql("SELECT * FROM product_summary", engine)
    
    # Load order_items to map products to orders
    df_order_items = pd.read_sql("SELECT order_id, product_id FROM order_items", engine)
    
    # ----- Merge product info with order_items -----
    order_product = df_order_items.merge(df_products, on='product_id', how='left')
    
    # Aggregate product features per order
    order_agg = order_product.groupby('order_id').agg({
        'avg_price': 'mean',
        'avg_freight': 'mean',
        'avg_review_score': 'mean',
        'product_weight_g': 'mean',
        'product_category_name': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
    }).reset_index()
    
    order_agg.columns = [
        'order_id', 'avg_product_price', 'avg_product_freight',
        'avg_product_review', 'avg_product_weight', 'main_category'
    ]
    
    # Count unique products per order
    product_count = df_order_items.groupby('order_id')['product_id'].nunique().reset_index()
    product_count.columns = ['order_id', 'total_products_in_order']
    
    order_agg = order_agg.merge(product_count, on='order_id', how='left')
    
    # ----- Build main dataframe -----
    df = df_orders.merge(
        df_customers[['customer_id', 'customer_state']],
        on='customer_id',
        how='left'
    )
    
    df = df.merge(order_agg, on='order_id', how='left')
    
    # ----- Drop rows with missing main_category (Unknown handled later) -----
    df = df.dropna(subset=['main_category'])
    
    # ----- Feature engineering: time features -----
    df['purchase_month'] = df['order_purchase_timestamp'].dt.month
    df['purchase_day'] = df['order_purchase_timestamp'].dt.day
    df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
    df['is_weekend'] = df['order_purchase_timestamp'].dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)
    df['purchase_quarter'] = df['order_purchase_timestamp'].dt.quarter
    
    # ----- Drop original timestamp and unnecessary columns -----
    drop_cols = [
        'delivery_time_days',
        'order_delivered_customer_date',
        'avg_review_score',
        'order_id',
        'customer_id',
        'order_status',
        'order_estimated_delivery_date',
        'order_approved_at',
        'order_delivered_carrier_date',
        'total_payment',
        'avg_payment',
        'total_reviews',
        'total_product_value',
        'order_purchase_timestamp'
    ]
    # Keep only columns that exist
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols)
    
    # ----- Encode categoricals -----
    # One-hot for customer_state
    df = pd.get_dummies(df, columns=['customer_state'], prefix='state', dtype=int, drop_first=True)
    
    # Label encoding for main_category
    le = LabelEncoder()
    df['main_category'] = le.fit_transform(df['main_category'])
    
    # ----- Create target variable -----
    df['is_late'] = (df['delivery_delay_days'] > 0).astype(int)
    df = df.drop(columns=['delivery_delay_days'])
    
    # ----- Remove Unknown category rows (already handled) -----
    # Also drop any rows with nulls in remaining columns
    df = df.dropna()
    
    print(f"Final feature set shape: {df.shape}")
    print(f"Target distribution:\n{df['is_late'].value_counts()}")
    
    if save_csv:
        output_path = DATA_PROCESSED / "feature_engineered_data.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved feature set to {output_path}")
    
    return df

if __name__ == "__main__":
    df = build_feature_set()
    print("\nSample of final features:")
    print(df.head())