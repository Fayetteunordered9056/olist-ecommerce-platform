# KPI Definitions (Order-Level, Delivered Only)

## Core Principle
All KPIs are calculated at the **order level** and use **delivered orders only** unless stated otherwise.

---

## 1. Total Orders
Number of unique orders:
COUNT(DISTINCT order_id)

Condition:
is_delivered = 1

---

## 2. Total Revenue
Sum of revenue from delivered orders:
SUM(order_revenue)

---

## 3. Average Order Value (AOV)
Average revenue per order:
AVG(order_revenue)

---

## 4. Average Review Score
Average review score at order level:
AVG(review_score)

---

## 5. Late Delivery Rate
Percentage of orders delivered late:
AVG(is_late_delivery)

---

## 6. Month-over-Month Growth
Revenue growth:
(current_month - previous_month) / previous_month

---

## Important Notes

- All metrics use **order-level aggregation**
- Item-level data is only used for category/product analysis
- Revenue excludes non-delivered orders
- Some records may contain delivery-status inconsistencies (flagged in dataset)