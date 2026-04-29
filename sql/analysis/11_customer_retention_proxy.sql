WITH order_level AS (
    SELECT
        order_id,
        customer_unique_id,
        MAX(is_delivered) AS is_delivered
    FROM olist
    GROUP BY order_id, customer_unique_id
),

customer_orders AS (
    SELECT
        customer_unique_id,
        COUNT(order_id) AS total_orders
    FROM order_level
    WHERE is_delivered = 1
    GROUP BY customer_unique_id
)

SELECT
    CASE
        WHEN total_orders = 1 THEN 'One-time Customers'
        ELSE 'Repeat Customers'
    END AS customer_type,
    COUNT(*) AS total_customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct
FROM customer_orders
GROUP BY customer_type
ORDER BY total_customers DESC;