"""
Build a processed (denormalized) dataset from PostgreSQL and save as CSV.

This script reads normalized tables from PostgreSQL (loaded by the ETL pipeline),
joins them into a single denormalized item-level dataset with feature engineering,
and saves the output to data/processed/clean_olist_data.csv.
"""

import os
import sys

import pandas as pd
from sqlalchemy import create_engine

# Add project root to sys.path so we can import app.config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.config import Config


PROCESSED_DIR = "data/processed"


def load_data_from_postgres() -> dict[str, pd.DataFrame]:
    """Read all normalized tables from PostgreSQL."""
    engine = create_engine(Config.DATABASE_URL)

    return {
        "orders": pd.read_sql("SELECT * FROM orders", engine),
        "items": pd.read_sql("SELECT * FROM order_items", engine),
        "payments": pd.read_sql("SELECT * FROM order_payments", engine),
        "reviews": pd.read_sql("SELECT * FROM order_reviews", engine),
        "customers": pd.read_sql("SELECT * FROM customers", engine),
        "products": pd.read_sql("SELECT * FROM products", engine),
        "categories": pd.read_sql("SELECT * FROM product_category_translation", engine),
        "sellers": pd.read_sql("SELECT * FROM sellers", engine),
    }


def build_payment_agg(payments: pd.DataFrame) -> pd.DataFrame:
    return (
        payments.groupby("order_id", as_index=False)
        .agg(
            order_total_payment_value=("payment_value", "sum"),
            payment_installments_max=("payment_installments", "max"),
            payment_type_nunique=("payment_type", "nunique"),
        )
    )


def build_review_agg(reviews: pd.DataFrame) -> pd.DataFrame:
    return (
        reviews.groupby("order_id", as_index=False)
        .agg(
            review_score=("review_score", "mean"),
            has_review_comment=("review_comment_message", lambda x: int(x.notna().any())),
            review_count=("review_id", "nunique"),
        )
    )


def build_processed_dataset(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = data["orders"].copy()
    items = data["items"].copy()
    payments = data["payments"].copy()
    reviews = data["reviews"].copy()
    customers = data["customers"].copy()
    products = data["products"].copy()
    categories = data["categories"].copy()
    sellers = data["sellers"].copy()

    # Ensure datetime columns
    datetime_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in datetime_cols:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    items["price"] = pd.to_numeric(items["price"], errors="coerce")
    items["freight_value"] = pd.to_numeric(items["freight_value"], errors="coerce")

    payment_agg = build_payment_agg(payments)
    review_agg = build_review_agg(reviews)

    products_enriched = products.merge(categories, on="product_category_name", how="left")

    df = (
        items.merge(orders, on="order_id", how="left")
        .merge(customers, on="customer_id", how="left")
        .merge(products_enriched, on="product_id", how="left")
        .merge(sellers, on="seller_id", how="left", suffixes=("", "_seller"))
        .merge(payment_agg, on="order_id", how="left")
        .merge(review_agg, on="order_id", how="left")
    )

    df["is_delivered"] = (df["order_status"] == "delivered").astype(int)
    df["is_canceled"] = (df["order_status"] == "canceled").astype(int)

    df["item_revenue"] = df["price"].fillna(0)
    df["shipping_revenue"] = df["freight_value"].fillna(0)
    df["revenue"] = df["item_revenue"] + df["shipping_revenue"]

    purchase_ts = df["order_purchase_timestamp"]
    delivered_ts = df["order_delivered_customer_date"]
    est_delivery_ts = df["order_estimated_delivery_date"]

    df["order_date"] = purchase_ts.dt.date
    df["order_month"] = purchase_ts.dt.to_period("M").astype(str)
    df["order_year"] = purchase_ts.dt.year
    df["order_quarter"] = purchase_ts.dt.to_period("Q").astype(str)
    df["order_weekday"] = purchase_ts.dt.day_name()
    df["purchase_hour"] = purchase_ts.dt.hour

    df["delivery_days"] = (delivered_ts - purchase_ts).dt.days
    df["estimated_delivery_days"] = (est_delivery_ts - purchase_ts).dt.days
    df["delivery_delay_days"] = (delivered_ts - est_delivery_ts).dt.days

    df["is_late_delivery"] = (
        (df["delivery_delay_days"] > 0) & df["delivery_delay_days"].notna()
    ).astype(int)

    df["delivery_status"] = pd.Series("unknown", index=df.index)
    df.loc[
        df["delivery_delay_days"].notna() & (df["delivery_delay_days"] <= 0),
        "delivery_status",
    ] = "on_time_or_early"
    df.loc[
        df["delivery_delay_days"].notna() & (df["delivery_delay_days"] > 0),
        "delivery_status",
    ] = "late"
    df.loc[df["order_status"] != "delivered", "delivery_status"] = "not_delivered"

    df["product_category_name_english"] = df["product_category_name_english"].fillna("unknown")

    df["missing_review_score_flag"] = df["review_score"].isna().astype(int)
    df["missing_product_category_flag"] = df["product_category_name_english"].eq("unknown").astype(int)
    df["missing_delivery_info_flag"] = df["delivery_days"].isna().astype(int)
    df["order_status_delivery_conflict_flag"] = (
        df["order_status"].ne("delivered") & df["order_delivered_customer_date"].notna()
    ).astype(int)

    keep_cols = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "customer_id",
        "customer_unique_id",
        "customer_city",
        "customer_state",
        "seller_city",
        "seller_state",
        "order_status",
        "is_delivered",
        "is_canceled",
        "order_purchase_timestamp",
        "order_date",
        "order_month",
        "order_year",
        "order_quarter",
        "order_weekday",
        "purchase_hour",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "delivery_days",
        "estimated_delivery_days",
        "delivery_delay_days",
        "is_late_delivery",
        "delivery_status",
        "price",
        "freight_value",
        "item_revenue",
        "shipping_revenue",
        "revenue",
        "payment_installments_max",
        "payment_type_nunique",
        "order_total_payment_value",
        "review_score",
        "review_count",
        "has_review_comment",
        "missing_review_score_flag",
        "product_category_name",
        "product_category_name_english",
        "missing_product_category_flag",
        "missing_delivery_info_flag",
        "order_status_delivery_conflict_flag",
    ]

    return df[keep_cols].copy()


def save_outputs(df: pd.DataFrame) -> None:
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    csv_path = os.path.join(PROCESSED_DIR, "clean_olist_data.csv")
    df.to_csv(csv_path, index=False)

    print(f"Saved processed CSV to: {csv_path}")
    print(f"Dataset shape: {df.shape}")


def main() -> None:
    print("Loading data from PostgreSQL...")
    data = load_data_from_postgres()
    print("Building processed dataset...")
    df = build_processed_dataset(data)
    save_outputs(df)


if __name__ == "__main__":
    main()
