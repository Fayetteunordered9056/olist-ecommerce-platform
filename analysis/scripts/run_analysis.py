"""
Run analysis and generate charts + summary tables from processed data.
"""

import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

DATA_PATH = "data/processed/clean_olist_data.csv"
FIGURE_DIR = "outputs/figures"
TABLE_DIR = "outputs/summary_tables"


def ensure_dirs() -> None:
    os.makedirs(FIGURE_DIR, exist_ok=True)
    os.makedirs(TABLE_DIR, exist_ok=True)


def build_order_level_dataset(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    base["order_purchase_timestamp"] = pd.to_datetime(base["order_purchase_timestamp"])
    return (
        base.sort_values(["order_id", "order_item_id"])
        .groupby("order_id", as_index=False)
        .agg(
            order_month=("order_month", "first"),
            order_weekday=("order_weekday", "first"),
            customer_unique_id=("customer_unique_id", "first"),
            order_status=("order_status", "first"),
            is_delivered=("is_delivered", "max"),
            order_revenue=("revenue", "sum"),
            review_score=("review_score", "first"),
            is_late_delivery=("is_late_delivery", "max"),
            delivery_status=("delivery_status", "first"),
            delivery_delay_days=("delivery_delay_days", "first"),
        )
    )


def save_monthly_kpi(order_level: pd.DataFrame) -> None:
    delivered = order_level[order_level["is_delivered"] == 1].copy()
    monthly = (
        delivered.groupby("order_month", as_index=False)
        .agg(total_orders=("order_id", "nunique"), total_revenue=("order_revenue", "sum"),
             avg_order_value=("order_revenue", "mean"), avg_review_score=("review_score", "mean"),
             late_delivery_rate=("is_late_delivery", "mean"))
        .sort_values("order_month")
    )
    monthly["mom_revenue_growth_pct"] = monthly["total_revenue"].pct_change() * 100
    monthly.to_csv(f"{TABLE_DIR}/monthly_kpi.csv", index=False)
    plt.figure(figsize=(10, 5))
    plt.plot(monthly["order_month"], monthly["total_revenue"])
    plt.xticks(rotation=45); plt.title("Monthly Delivered Revenue Trend")
    plt.xlabel("Order Month"); plt.ylabel("Delivered Revenue"); plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/monthly_revenue_trend.png"); plt.close()


def save_top_categories(df: pd.DataFrame) -> None:
    delivered = df[df["is_delivered"] == 1].copy()
    cat = (delivered.groupby("product_category_name_english", as_index=False)
           .agg(total_revenue=("revenue", "sum"), total_orders=("order_id", "nunique"),
                avg_item_revenue=("revenue", "mean"))
           .sort_values("total_revenue", ascending=False).head(10))
    cat.to_csv(f"{TABLE_DIR}/top_categories_revenue.csv", index=False)
    plt.figure(figsize=(10, 6))
    plt.barh(cat["product_category_name_english"], cat["total_revenue"])
    plt.gca().invert_yaxis(); plt.title("Top 10 Product Categories by Delivered Revenue")
    plt.xlabel("Delivered Revenue"); plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/top_categories_revenue.png"); plt.close()


def save_delivery_review_analysis(order_level: pd.DataFrame) -> None:
    delivered = order_level[order_level["is_delivered"] == 1].copy()
    delivery = (delivered.groupby("delivery_status", as_index=False)
                .agg(total_orders=("order_id", "nunique"), avg_review_score=("review_score", "mean"),
                     avg_delivery_delay_days=("delivery_delay_days", "mean"),
                     avg_order_value=("order_revenue", "mean"))
                .sort_values("total_orders", ascending=False))
    delivery.to_csv(f"{TABLE_DIR}/delivery_review_analysis.csv", index=False)
    plt.figure(figsize=(8, 5))
    plt.bar(delivery["delivery_status"], delivery["avg_review_score"])
    plt.title("Average Review Score by Delivery Status")
    plt.xlabel("Delivery Status"); plt.ylabel("Average Review Score"); plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/review_by_delivery_status.png"); plt.close()


def save_weekday_weekend(order_level: pd.DataFrame) -> None:
    delivered = order_level[order_level["is_delivered"] == 1].copy()
    delivered["day_type"] = delivered["order_weekday"].apply(
        lambda x: "Weekend" if x in ["Saturday", "Sunday"] else "Weekday")
    summary = (delivered.groupby("day_type", as_index=False)
               .agg(total_orders=("order_id", "nunique"), total_revenue=("order_revenue", "sum"),
                    avg_order_value=("order_revenue", "mean"), avg_review_score=("review_score", "mean")))
    summary.to_csv(f"{TABLE_DIR}/weekday_vs_weekend.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.bar(summary["day_type"], summary["total_revenue"])
    plt.title("Weekday vs Weekend Delivered Revenue")
    plt.xlabel("Day Type"); plt.ylabel("Delivered Revenue"); plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/weekday_vs_weekend.png"); plt.close()


def save_customer_repeat_proxy(order_level: pd.DataFrame) -> None:
    delivered = order_level[order_level["is_delivered"] == 1].copy()
    cust = (delivered.groupby("customer_unique_id", as_index=False)
            .agg(total_orders=("order_id", "nunique"), total_revenue=("order_revenue", "sum")))
    cust["customer_type"] = cust["total_orders"].apply(lambda x: "Repeat" if x > 1 else "One-time")
    summary = (cust.groupby("customer_type", as_index=False)
               .agg(total_customers=("customer_unique_id", "count"),
                    avg_customer_revenue=("total_revenue", "mean")))
    summary.to_csv(f"{TABLE_DIR}/customer_repeat_proxy.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.bar(summary["customer_type"], summary["total_customers"])
    plt.title("Customer Repeat Proxy (Delivered Orders)")
    plt.xlabel("Customer Type"); plt.ylabel("Total Customers"); plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/customer_repeat_proxy.png"); plt.close()


def main() -> None:
    ensure_dirs()
    df = pd.read_csv(DATA_PATH)
    order_level = build_order_level_dataset(df)
    save_monthly_kpi(order_level)
    save_top_categories(df)
    save_delivery_review_analysis(order_level)
    save_weekday_weekend(order_level)
    save_customer_repeat_proxy(order_level)
    print("Analysis outputs generated successfully.")


if __name__ == "__main__":
    main()
