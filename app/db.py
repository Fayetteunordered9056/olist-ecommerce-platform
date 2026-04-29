from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import Config

_engine: Engine | None = None

DEFAULT_MAX_ROWS = 1000
DEFAULT_STATEMENT_TIMEOUT_MS = 5000


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(Config.DATABASE_URL, pool_pre_ping=True)
    return _engine


def enforce_limit(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> str:
    sql_clean = sql.strip().rstrip(";")
    sql_lower = sql_clean.lower()

    if " limit " in f" {sql_lower} ":
        return sql_clean + ";"

    return f"{sql_clean} LIMIT {max_rows};"


def run_select_query(
    sql: str,
    max_rows: int = DEFAULT_MAX_ROWS,
    statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS,
) -> pd.DataFrame:
    safe_sql = enforce_limit(sql, max_rows=max_rows)

    logging.info("Executing SQL with max_rows=%s", max_rows)
    logging.info("Final SQL: %s", safe_sql)

    with get_engine().connect() as connection:
        connection.execute(text(f"SET statement_timeout TO {statement_timeout_ms}"))
        df = pd.read_sql(text(safe_sql), connection)

    logging.info("Query returned %s rows", len(df))
    return df


def test_connection() -> bool:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logging.exception("Database connection failed.")
        return False
