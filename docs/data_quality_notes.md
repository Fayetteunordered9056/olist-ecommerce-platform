# Data Quality Notes

This project uses the Olist e-commerce public dataset and applies a cleaned analytical layer for portfolio analysis.

## 1. Dataset Grain

The processed dataset `clean_olist_data.csv` is stored at the **order-item level**.

That means:
- 1 row = 1 item in an order
- An order with multiple items appears in multiple rows

Because of this, business KPIs such as:
- average review score
- late delivery rate
- average order value

must be calculated at the **order level**, not directly from raw item rows.

---

## 2. Revenue Definition

Two revenue concepts exist in the dataset:

- `revenue` = item price + freight at the item-row level
- `order_revenue` = sum of item-row revenue aggregated to the order level

For dashboard KPIs, this project uses:

- **Delivered revenue only**
- Revenue from non-delivered orders is excluded from primary business KPIs

This avoids overstating realized sales.

---

## 3. Payment Value Warning

`order_total_payment_value` is an order-level attribute merged back into the item-level table.

As a result:
- the same value is repeated across all items of the same order

So:
- use it carefully in item-level tables
- do not sum it directly in `fact_sales`
- prefer `fact_orders` when using payment totals

---

## 4. Delivery Data Caveat

A small number of rows contain inconsistent delivery information, such as:

- non-delivered order status
- but a non-null customer delivery timestamp

These rows are flagged with:

`order_status_delivery_conflict_flag`

This is treated as a source-data inconsistency, not silently removed.

---

## 5. Review Data Interpretation

Review metrics are handled at the order level after aggregation.

Important distinction:
- missing review comments are common and expected
- missing review score should be interpreted separately

This project does not treat all missing review-related fields as data quality problems.

---

## 6. Date Dimension Design

`dim_date` is intentionally modeled at:
- 1 row per date

Time-of-day fields such as `purchase_hour` remain outside the date dimension to preserve a clean star schema.

---

## 7. KPI Modeling Rule

Default rule used across marts, SQL, and dashboard logic:

- KPI layer = order-level
- Product/category analysis = item-level
- Primary revenue KPI = delivered orders only