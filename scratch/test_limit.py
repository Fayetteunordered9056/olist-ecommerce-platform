import re

def enforce_limit_new(sql: str, max_rows: int = 1000) -> str:
    sql_clean = sql.strip().rstrip(";")
    if re.search(r"\bLIMIT\b", sql_clean, re.IGNORECASE):
        return sql_clean + ";"
    return f"{sql_clean} LIMIT {max_rows};"

test_sql = """SELECT product_category_name_english, SUM(revenue) AS total_revenue
FROM fact_order_item_sales
GROUP BY product_category_name_english
ORDER BY total_revenue DESC
LIMIT 1"""

print(f"Original SQL ends with: {test_sql[-10:]!r}")
result = enforce_limit_new(test_sql)
print(f"Result: {result!r}")
