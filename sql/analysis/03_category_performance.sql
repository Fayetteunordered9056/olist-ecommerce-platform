WITH delivered_items AS (
    SELECT *
    FROM olist
    WHERE is_delivered = 1
)

SELECT
    product_category_name_english,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    AVG(revenue) AS avg_item_revenue
FROM delivered_items
GROUP BY product_category_name_english
ORDER BY total_revenue DESC;