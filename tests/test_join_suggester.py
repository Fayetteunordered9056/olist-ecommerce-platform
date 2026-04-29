import pandas as pd

from app.join_suggester import suggest_joins_from_dataframes


def test_suggests_order_join_with_confidence_and_explanation():
    orders = pd.DataFrame({"order_id": ["o1", "o2", "o3"], "customer_id": ["c1", "c2", "c3"]})
    order_items = pd.DataFrame({"order_id": ["o1", "o1", "o2", "o3"], "order_item_id": [1, 2, 1, 1], "price": [10, 15, 20, 30]})

    suggestions = suggest_joins_from_dataframes({"orders": orders, "order_items": order_items})

    assert suggestions, "Expected at least one join suggestion"
    top = suggestions[0]
    assert top.left_column == "order_id"
    assert top.right_column == "order_id"
    assert top.confidence >= 0.55
    assert "key-overlap ratio" in top.explanation
    assert top.suggested_sql_on == "orders.order_id = order_items.order_id"


def test_does_not_suggest_join_for_low_overlap():
    left = pd.DataFrame({"customer_id": ["a", "b", "c"]})
    right = pd.DataFrame({"customer_id": ["x", "y", "z"]})

    suggestions = suggest_joins_from_dataframes({"customers_a": left, "customers_b": right})
    assert suggestions == []


def test_supports_multiple_join_suggestions_across_three_tables():
    orders = pd.DataFrame({"order_id": ["o1", "o2", "o3"], "customer_id": ["c1", "c2", "c3"]})
    order_items = pd.DataFrame({"order_id": ["o1", "o1", "o2", "o3"], "order_item_id": [1, 2, 1, 1]})
    order_payments = pd.DataFrame({"order_id": ["o1", "o2", "o3"], "payment_sequential": [1, 1, 1]})

    suggestions = suggest_joins_from_dataframes(
        {"orders": orders, "order_items": order_items, "order_payments": order_payments}
    )
    suggested_on_clauses = {s.suggested_sql_on for s in suggestions}

    assert "orders.order_id = order_items.order_id" in suggested_on_clauses
    assert "orders.order_id = order_payments.order_id" in suggested_on_clauses
