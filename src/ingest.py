# src/ingest.py
# Job: read the raw Olist CSVs into pandas DataFrames.
# This file does NOT clean anything - it only loads, so if loading
# breaks, you know the problem is here, not mixed in with cleaning logic.

import pandas as pd
from config import RAW_DATA_DIR

def load_raw_data():
    """
    Reads every Olist CSV from data/raw and returns them as a dictionary
    of DataFrames, e.g. tables["customers"] gives you that table.
    A dictionary is used (instead of separate variables) so we can loop
    over all tables easily later, and so adding a table is a one-line change.
    """
    files = {
        "customers": "olist_customers_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "payments": "olist_order_payments_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }
    # Note: geolocation.csv is skipped for now - it's large and not
    # needed for the core KPIs. We can add it later if needed.

    tables = {}
    for name, filename in files.items():
        path = RAW_DATA_DIR / filename
        tables[name] = pd.read_csv(path)
        print(f"Loaded {name}: {tables[name].shape[0]} rows, {tables[name].shape[1]} columns")

    return tables


if __name__ == "__main__":
    # This block only runs when you execute this file directly
    # (python ingest.py), not when another file imports load_raw_data().
    # Useful for quickly testing this file on its own.
    tables = load_raw_data()
    print("\nAll tables loaded successfully.")