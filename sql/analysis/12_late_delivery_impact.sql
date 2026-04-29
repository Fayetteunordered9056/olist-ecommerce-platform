WITH order_level AS (
    SELECT
        order_id,
        MAX(is_delivered) AS is_delivered,
        MAX(is_late_delivery) AS is_late_delivery,
        MAX(review_score) AS review_score,
        MAX(delivery_delay_days) AS delivery_delay_days,
        SUM(revenue) AS order_revenue
    FROM olist
    GROUP BY order_id
)

SELECT
    CASE
        WHEN is_late_delivery = 1 THEN 'Late'
        WHEN delivery_delay_days IS NOT NULL THEN 'On Time / Early'
        ELSE 'Unknown'
    END AS delivery_bucket,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(AVG(order_revenue), 2) AS avg_order_value
FROM order_level
WHERE is_delivered = 1
GROUP BY delivery_bucket
ORDER BY total_orders DESC;