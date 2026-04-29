WITH order_level AS (
    SELECT
        order_id,
        customer_unique_id,
        MAX(is_delivered) AS is_delivered,
        SUM(revenue) AS order_revenue
    FROM olist
    GROUP BY order_id, customer_unique_id
)

SELECT
    customer_unique_id,
    COUNT(order_id) AS total_orders,
    SUM(order_revenue) AS total_revenue,
    AVG(order_revenue) AS avg_order_value
FROM order_level
WHERE is_delivered = 1
GROUP BY customer_unique_id;