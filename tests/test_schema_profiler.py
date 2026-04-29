import pandas as pd

from app.schema_profiler import profile_dataframe, profile_dataframes


def test_profile_dataframe_infers_core_column_types_and_roles():
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "customer_id": ["c1", "c2", "c3"],
            "order_purchase_timestamp": [
                "2018-01-01 10:00:00",
                "2018-01-02 11:00:00",
                "2018-01-03 12:00:00",
            ],
            "price": [100.0, 50.5, 20.0],
            "order_status": ["delivered", "shipped", "delivered"],
        }
    )

    profile = profile_dataframe(df, table_name="orders")

    assert profile.table_name == "orders"
    assert "order_id" in profile.id_columns
    assert "customer_id" in profile.id_columns
    assert "order_purchase_timestamp" in profile.datetime_columns
    assert "price" in profile.numeric_columns
    assert "order_status" in profile.target_like_columns


def test_profile_dataframe_handles_messy_numeric_strings():
    df = pd.DataFrame(
        {
            "payment_value": ["$100.50", "1,250.00", "90", None],
            "payment_type": ["credit_card", "boleto", "debit_card", "voucher"],
        }
    )

    profile = profile_dataframe(df, table_name="order_payments")
    by_name = {c.name: c for c in profile.columns}

    assert by_name["payment_value"].inferred_type == "numeric"
    assert by_name["payment_type"].inferred_type == "categorical"


def test_profile_dataframes_infers_relationships_for_shared_id_like_columns():
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "customer_id": ["c1", "c2", "c3"],
            "order_status": ["delivered", "shipped", "delivered"],
        }
    )
    order_items = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2", "o3"],
            "order_item_id": [1, 2, 1, 1],
            "price": [10, 15, 20, 30],
        }
    )
    order_payments = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "payment_sequential": [1, 1, 1],
            "payment_value": [25, 20, 30],
        }
    )

    schema_profile = profile_dataframes(
        {
            "orders": orders,
            "order_items": order_items,
            "order_payments": order_payments,
        }
    )

    rel_pairs = {
        (r.left_table, r.right_table, r.left_column, r.right_column)
        for r in schema_profile.relationships
    }

    assert ("order_items", "orders", "order_id", "order_id") in rel_pairs
    assert ("orders", "order_payments", "order_id", "order_id") in rel_pairs
