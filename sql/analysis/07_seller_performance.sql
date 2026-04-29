WITH seller_performance AS (
    SELECT
        seller_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(revenue) AS total_revenue,
        AVG(revenue) AS avg_item_revenue
    FROM olist
    WHERE is_delivered = 1
    GROUP BY seller_id
)

SELECT
    seller_id,
    total_orders,
    total_revenue,
    avg_item_revenue
FROM seller_performance
ORDER BY total_revenue DESC;