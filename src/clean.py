# src/clean.py
# Job: take the raw tables from ingest.py and fix missing values,
# wrong data types, duplicates, and inconsistent text.
# One function per table keeps each cleaning job small and testable.

import pandas as pd


def clean_customers(df):
    df = df.drop_duplicates()
    # .str.lower().str.strip() standardizes text so "Sao Paulo" and
    # "sao paulo " are treated as the same city.
    df["customer_city"] = df["customer_city"].str.lower().str.strip()
    df["customer_state"] = df["customer_state"].str.upper().str.strip()
    return df


def clean_orders(df):
    df = df.drop_duplicates()

    # These columns are dates stored as text - convert them to real
    # datetime type so SQL Server / Power BI can do date math on them.
    # errors="coerce" turns any unreadable date into NaT (missing)
    # instead of crashing the whole script on one bad row.
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # order_status has known values like "delivered", "shipped",
    # "canceled". Standardize casing just in case.
    df["order_status"] = df["order_status"].str.lower().str.strip()

    return df


def clean_order_items(df):
    df = df.drop_duplicates()
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
    # price and freight_value should be numbers, not text - astype(float)
    # forces the type; if a row has garbage text, this would raise an
    # error so we notice it rather than silently miscalculating later.
    df["price"] = df["price"].astype(float)
    df["freight_value"] = df["freight_value"].astype(float)
    return df


def clean_payments(df):
    df = df.drop_duplicates()
    df["payment_type"] = df["payment_type"].str.lower().str.strip()
    df["payment_value"] = df["payment_value"].astype(float)
    return df


def clean_reviews(df):
    df = df.drop_duplicates()
    date_cols = ["review_creation_date", "review_answer_timestamp"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    # review_comment_title / _message are often empty - that's expected
    # (many customers don't leave a comment), so we fill with an empty
    # string rather than dropping the whole row over a missing comment.
    df["review_comment_title"] = df["review_comment_title"].fillna("")
    df["review_comment_message"] = df["review_comment_message"].fillna("")
    return df


def clean_products(df):
    df = df.drop_duplicates()
    # A few products are missing a category - label them instead of
    # dropping the row, since we still want their price/sales data.
    df["product_category_name"] = df["product_category_name"].fillna("unknown")
    # Numeric columns: fill missing with the median (robust to outliers)
    # rather than dropping rows over a missing weight/dimension.
    numeric_cols = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
    return df


def clean_sellers(df):
    df = df.drop_duplicates()
    df["seller_city"] = df["seller_city"].str.lower().str.strip()
    df["seller_state"] = df["seller_state"].str.upper().str.strip()
    return df


def clean_category_translation(df):
    df = df.drop_duplicates()
    return df


def clean_all(tables: dict) -> dict:
    """
    Takes the dictionary of raw tables from ingest.py and returns a
    dictionary of cleaned tables, using the matching function above
    for each one.
    """
    cleaners = {
        "customers": clean_customers,
        "orders": clean_orders,
        "order_items": clean_order_items,
        "payments": clean_payments,
        "reviews": clean_reviews,
        "products": clean_products,
        "sellers": clean_sellers,
        "category_translation": clean_category_translation,
    }

    cleaned = {}
    for name, df in tables.items():
        before = df.shape[0]
        cleaned[name] = cleaners[name](df)
        after = cleaned[name].shape[0]
        print(f"Cleaned {name}: {before} -> {after} rows")

    return cleaned


if __name__ == "__main__":
    from ingest import load_raw_data
    tables = load_raw_data()
    cleaned = clean_all(tables)
    print("\nAll tables cleaned successfully.")