WITH category_revenue AS (
    SELECT
        product_category_name_english,
        SUM(revenue) AS total_revenue
    FROM olist
    WHERE is_delivered = 1
    GROUP BY product_category_name_english
),

ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS rn,
        COUNT(*) OVER () AS total_categories
    FROM category_revenue
)

SELECT *
FROM ranked
WHERE rn <= CEIL(0.2 * total_categories);