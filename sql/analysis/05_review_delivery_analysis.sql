WITH order_level AS (
    SELECT
        order_id,
        MAX(is_delivered) AS is_delivered,
        MAX(delivery_status) AS delivery_status,
        MAX(review_score) AS review_score,
        MAX(delivery_delay_days) AS delivery_delay_days,
        SUM(revenue) AS order_revenue
    FROM olist
    GROUP BY order_id
)

SELECT
    delivery_status,
    COUNT(order_id) AS total_orders,
    AVG(review_score) AS avg_review_score,
    AVG(delivery_delay_days) AS avg_delay_days,
    AVG(order_revenue) AS avg_order_value
FROM order_level
WHERE is_delivered = 1
GROUP BY delivery_status
ORDER BY total_orders DESC;