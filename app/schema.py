from __future__ import annotations

SCHEMA_TABLES: dict[str, list[str]] = {
    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
    "order_payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],
    "order_reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ],
    "products": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
    "sellers": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
    "product_category_translation": [
        "product_category_name",
        "product_category_name_english",
    ],
    "fact_order_item_sales": [
        "order_id",
        "order_item_id",
        "seller_id",
        "product_id",
        "product_category_name_english",
        "order_purchase_timestamp",
        "price",
        "freight_value",
        "revenue",
    ],
}

SCHEMA_RELATIONSHIPS: list[str] = [
    "orders.customer_id = customers.customer_id",
    "order_items.order_id = orders.order_id",
    "order_payments.order_id = orders.order_id",
    "order_reviews.order_id = orders.order_id",
    "order_items.product_id = products.product_id",
    "order_items.seller_id = sellers.seller_id",
    (
        "products.product_category_name = "
        "product_category_translation.product_category_name"
    ),
]

ALLOWED_TABLES = set(SCHEMA_TABLES.keys())
