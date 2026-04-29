from app.schema import SCHEMA_RELATIONSHIPS, SCHEMA_TABLES


def build_schema_description() -> str:
    table_sections: list[str] = []

    for index, (table_name, columns) in enumerate(SCHEMA_TABLES.items(), start=1):
        column_lines = "\n".join(f"- {col}" for col in columns)
        table_sections.append(f"{index}) {table_name}\n{column_lines}")

    relationships = "\n".join(f"- {join_condition}" for join_condition in SCHEMA_RELATIONSHIPS)

    return f"""
You are generating PostgreSQL SQL for an e-commerce analytics application.

Available tables and columns:

{chr(10).join(table_sections)}

Relationships:
{relationships}

Business guidance:
- Revenue should usually be calculated from order_items.price unless the question is explicitly about payments.
- Freight cost should come from order_items.freight_value.
- Monthly trends should usually use orders.order_purchase_timestamp.
- Category names should prefer product_category_name_english when available.
- Order counts should usually count DISTINCT orders.order_id when joins may duplicate rows.
- For customer distribution, use customers.customer_state or customers.customer_city.
- For payment analysis, use order_payments.payment_type, payment_installments, and payment_value.
- For review analysis, use order_reviews.review_score.
- For seller analysis, use sellers table joined via order_items.seller_id.
- The fact_order_item_sales table provides pre-joined revenue data for quick analytics.

SQL generation rules:
- Generate exactly one SQL query.
- Use PostgreSQL syntax.
- Only generate SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, or REVOKE.
- Do not generate multiple statements.
- Use readable aliases.
- Add ORDER BY when useful.
- Add LIMIT 100 for non-aggregated detailed row outputs.
- Return only raw SQL. No markdown. No explanation. No code fences.
""".strip()


def build_sql_generation_prompt(user_question: str) -> str:
    return f"""
{build_schema_description()}

User business question:
{user_question}

Return only the SQL query.
""".strip()
