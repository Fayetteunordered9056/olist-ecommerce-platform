SELECT
    SUM(revenue) AS total_revenue
FROM olist
WHERE is_delivered = 1;