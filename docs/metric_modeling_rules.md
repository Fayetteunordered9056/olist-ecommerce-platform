# Metric Modeling Rules

## Core Rule

Always confirm the analytical grain before calculating a metric.

---

## 1. Order-Level Metrics

Use `fact_orders` or an order-level aggregation for:

- total orders
- total delivered revenue
- average order value
- average review score
- late delivery rate
- customer repeat rate
- RFM analysis

Reason:
These are business metrics that should treat each order as one observation.

---

## 2. Item-Level Metrics

Use `fact_sales` or item-level rows for:

- category revenue
- seller-product analysis
- item-level revenue mix
- product category ranking

Reason:
These analyses naturally depend on order-item granularity.

---

## 3. Revenue Rule

For main business KPIs, use:
- delivered orders only

For operational analysis, a separate all-status revenue view may be created if needed.

---

## 4. Review Rule

Review score must be evaluated at the order level.

Do not average review score directly from item-level rows, because multi-item orders would be overweighted.

---

## 5. Delivery Rule

Late delivery is evaluated as an order-level outcome.

Do not calculate late delivery rate from raw item rows unless the analysis explicitly intends item-row weighting.

---

## 6. Payment Rule

`order_total_payment_value` is repeated across item rows.

Safe usage:
- order-level analysis
- reconciliation checks

Unsafe usage:
- direct summation in item-level fact tables