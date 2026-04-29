from __future__ import annotations

import pandas as pd
from typing import Callable


def _to_iso_datetime(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    return dt.dt.strftime("%Y-%m-%d %H:%M:%S")


def _deduplicate(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset).copy()


def _convert_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _convert_datetime(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = _to_iso_datetime(df[col])
    return df


def build_fact_order_item_sales(cleaned: dict[str, pd.DataFrame]) -> pd.DataFrame:
    oi = cleaned["order_items"][
        ["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"]
    ]

    o = cleaned["orders"][["order_id", "order_purchase_timestamp"]]
    p = cleaned["products"][["product_id", "product_category_name"]]
    ct = cleaned["category_translation"][["product_category_name", "product_category_name_english"]]

    fact = (
        oi.merge(o, on="order_id", how="left")
        .merge(p, on="product_id", how="left")
        .merge(ct, on="product_category_name", how="left")
    )

    fact["revenue"] = fact["price"] + fact["freight_value"]

    return fact[
        [
            "order_id",
            "order_item_id",
            "seller_id",
            "product_id",
            "product_category_name_english",
            "order_purchase_timestamp",
            "price",
            "freight_value",
            "revenue",
        ]
    ]


def transform(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}

    customers = _deduplicate(dfs["customers"], ["customer_id"])
    out["customers"] = customers

    orders = _deduplicate(dfs["orders"], ["order_id"])
    orders = _convert_datetime(
        orders,
        [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    out["orders"] = orders

    products = _deduplicate(dfs["products"], ["product_id"])
    out["products"] = products

    sellers = _deduplicate(dfs["sellers"], ["seller_id"])
    out["sellers"] = sellers

    order_items = _deduplicate(dfs["order_items"], ["order_id", "order_item_id"])
    order_items = _convert_numeric(order_items, ["price", "freight_value"])
    order_items = _convert_datetime(order_items, ["shipping_limit_date"])
    out["order_items"] = order_items

    order_payments = _deduplicate(dfs["order_payments"], ["order_id", "payment_sequential"])
    order_payments = _convert_numeric(order_payments, ["payment_value"])
    out["order_payments"] = order_payments

    order_reviews = _deduplicate(dfs["order_reviews"], ["review_id", "order_id"])
    order_reviews = _convert_datetime(
        order_reviews,
        ["review_creation_date", "review_answer_timestamp"],
    )
    out["order_reviews"] = order_reviews

    category_translation = _deduplicate(
        dfs["category_translation"],
        ["product_category_name"],
    )
    out["category_translation"] = category_translation

    out["fact_order_item_sales"] = build_fact_order_item_sales(out)

    return out
