-- Monthly revenue trend
SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
    SUM(oi.price) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY 1
ORDER BY 1;

-- Top categories by revenue
SELECT
    pct.product_category_name_english AS category,
    SUM(oi.price) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN product_category_translation pct
    ON p.product_category_name = pct.product_category_name
GROUP BY 1
ORDER BY revenue DESC
LIMIT 10;

-- Customers by state
SELECT
    customer_state,
    COUNT(*) AS customer_count
FROM customers
GROUP BY 1
ORDER BY customer_count DESC;