WITH order_level AS (
    SELECT
        order_id,
        order_weekday,
        MAX(is_delivered) AS is_delivered,
        SUM(revenue) AS order_revenue,
        MAX(review_score) AS review_score
    FROM olist
    GROUP BY order_id, order_weekday
)

SELECT
    CASE
        WHEN order_weekday IN ('Saturday', 'Sunday') THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(order_id) AS total_orders,
    SUM(order_revenue) AS total_revenue,
    AVG(order_revenue) AS avg_order_value,
    AVG(review_score) AS avg_review_score
FROM order_level
WHERE is_delivered = 1
GROUP BY day_type;