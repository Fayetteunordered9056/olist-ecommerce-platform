from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text


def init_db(database_url: str, schema_path: str = "db/schema.sql") -> None:
    """Initialize the PostgreSQL database from the schema SQL file."""
    schema_sql = Path(schema_path).read_text(encoding="utf-8")

    engine = create_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text(schema_sql))
        conn.commit()
