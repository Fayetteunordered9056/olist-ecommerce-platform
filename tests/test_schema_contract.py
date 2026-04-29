from app.prompt_builder import build_schema_description
from app.schema import ALLOWED_TABLES, SCHEMA_TABLES


def test_allowed_tables_match_schema_tables():
    assert ALLOWED_TABLES == set(SCHEMA_TABLES.keys())


def test_prompt_mentions_all_allowed_tables():
    schema_text = build_schema_description()

    for table_name in ALLOWED_TABLES:
        assert f") {table_name}" in schema_text
