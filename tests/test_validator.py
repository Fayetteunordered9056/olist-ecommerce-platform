from app.validator import validate_sql

def test_select_passes():
    ok, _ = validate_sql("SELECT * FROM orders LIMIT 5")
    assert ok is True

def test_with_select_passes():
    ok, _ = validate_sql("WITH x AS (SELECT * FROM orders) SELECT * FROM x")
    assert ok is True

def test_delete_rejected():
    ok, _ = validate_sql("DELETE FROM orders")
    assert ok is False

def test_drop_rejected():
    ok, _ = validate_sql("DROP TABLE orders")
    assert ok is False

def test_multiple_statements_rejected():
    ok, _ = validate_sql("SELECT * FROM orders; DROP TABLE orders;")
    assert ok is False

def test_empty_sql_rejected():
    ok, _ = validate_sql("")
    assert ok is False


def test_order_payments_table_allowed():
    ok, _ = validate_sql("SELECT payment_type, SUM(payment_value) FROM order_payments GROUP BY payment_type")
    assert ok is True


def test_product_category_translation_table_allowed():
    ok, _ = validate_sql(
        """
        SELECT pct.product_category_name_english, COUNT(*) AS product_count
        FROM products p
        JOIN product_category_translation pct
          ON p.product_category_name = pct.product_category_name
        GROUP BY pct.product_category_name_english
        """
    )
    assert ok is True


def test_sellers_table_allowed():
    ok, _ = validate_sql("SELECT seller_id, seller_state FROM sellers LIMIT 10")
    assert ok is True


def test_order_reviews_table_allowed():
    ok, _ = validate_sql("SELECT order_id, review_score FROM order_reviews LIMIT 10")
    assert ok is True


def test_fact_order_item_sales_table_allowed():
    ok, _ = validate_sql(
        "SELECT product_category_name_english, SUM(revenue) FROM fact_order_item_sales GROUP BY product_category_name_english"
    )
    assert ok is True
