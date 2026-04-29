## Data Modeling Notes

### Fact Tables

- fact_sales → item-level (granularity: order item)
- fact_orders → order-level (recommended for KPI calculations)

### Best Practice

- Use `fact_orders` for:
  - revenue KPIs
  - AOV
  - review score
  - delivery metrics

- Use `fact_sales` for:
  - category analysis
  - product-level insights

---

### Warning

Do NOT sum `order_total_payment_value` in fact_sales
→ it is duplicated across item rows

Always use:
fact_orders[order_total_payment_value]