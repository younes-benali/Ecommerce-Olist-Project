import pandas as pd
from src.config import OLIST_DB


def load_customers():
    return pd.read_csv(OLIST_DB / "olist_customers_dataset.csv")

def load_orders():
    return pd.read_csv(OLIST_DB / "olist_orders_dataset.csv")

def load_order_items():
    return pd.read_csv(OLIST_DB / "olist_order_items_dataset.csv")

def load_products():
    return pd.read_csv(OLIST_DB / "olist_products_dataset.csv")

def load_payments():
    return pd.read_csv(OLIST_DB / "olist_order_payments_dataset.csv")

def load_reviews():
    return pd.read_csv(OLIST_DB / "olist_order_reviews_dataset.csv")

def load_sellers():
    return pd.read_csv(OLIST_DB / "olist_sellers_dataset.csv")

def load_category_translation():
    return pd.read_csv(OLIST_DB / "product_category_name_translation.csv")

if __name__ == "__main__":
    print("Testing data loader...")
    df = load_orders()
    print(f"Orders loaded: {df.shape}")
    print("Success!")