WITH order_level AS (
    SELECT
        order_id,
        order_month,
        MAX(is_delivered) AS is_delivered,
        SUM(revenue) AS order_revenue,
        MAX(review_score) AS review_score,
        MAX(is_late_delivery) AS is_late_delivery
    FROM olist
    GROUP BY order_id, order_month
)

SELECT
    order_month,
    COUNT(order_id) AS total_orders,
    SUM(order_revenue) AS total_revenue,
    AVG(order_revenue) AS avg_order_value,
    AVG(review_score) AS avg_review_score,
    AVG(is_late_delivery) AS late_delivery_rate
FROM order_level
WHERE is_delivered = 1
GROUP BY order_month
ORDER BY order_month;