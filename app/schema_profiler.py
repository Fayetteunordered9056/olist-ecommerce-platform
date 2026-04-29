from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

import pandas as pd

TARGET_NAME_HINTS = (
    "target",
    "label",
    "class",
    "churn",
    "conversion",
    "is_",
    "has_",
    "status",
    "revenue",
    "sales",
    "price",
    "amount",
    "value",
    "profit",
)


@dataclass
class ColumnProfile:
    name: str
    inferred_type: str
    null_ratio: float
    unique_ratio: float
    non_null_count: int
    sample_values: list[str]
    is_id_like: bool
    is_target_like: bool
    is_datetime_like: bool
    is_numeric_like: bool
    is_categorical_like: bool


@dataclass
class TableProfile:
    table_name: str
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    id_columns: list[str]
    datetime_columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    target_like_columns: list[str]


@dataclass
class RelationshipProfile:
    left_table: str
    left_column: str
    right_table: str
    right_column: str
    relationship_type: str
    confidence: float
    reason: str


@dataclass
class SchemaProfile:
    tables: list[TableProfile]
    relationships: list[RelationshipProfile]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clean_numeric_candidate(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"[\$,]", "", regex=True)
        .str.replace(r"\s+", "", regex=True)
    )


def _infer_series_type(series: pd.Series) -> tuple[str, bool, bool, bool]:
    non_null = series.dropna()
    if non_null.empty:
        return "unknown", False, False, False

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime", True, False, False

    if pd.api.types.is_numeric_dtype(series):
        return "numeric", False, True, False

    as_text = non_null.astype(str).str.strip()
    datetime_like_mask = as_text.str.contains(r"\d", regex=True) & as_text.str.contains(
        r"[-/:T ]", regex=True
    )
    if datetime_like_mask.mean() >= 0.5:
        datetime_parsed = pd.to_datetime(non_null, errors="coerce", utc=False)
        datetime_ratio = datetime_parsed.notna().mean()
        if datetime_ratio >= 0.8:
            return "datetime", True, False, False

    cleaned = _clean_numeric_candidate(non_null)
    numeric_parsed = pd.to_numeric(cleaned, errors="coerce")
    numeric_ratio = numeric_parsed.notna().mean()
    if numeric_ratio >= 0.85:
        return "numeric", False, True, False

    return "categorical", False, False, True


def _is_id_like(
    col_name: str,
    non_null_count: int,
    unique_count: int,
    total_rows: int,
    inferred_type: str,
) -> bool:
    name = col_name.lower().strip()
    if name == "id" or name.endswith("_id") or name.endswith("key"):
        return True

    if total_rows == 0 or non_null_count == 0:
        return False

    unique_ratio = unique_count / max(non_null_count, 1)
    low_null = (1 - (non_null_count / max(total_rows, 1))) <= 0.05
    return inferred_type in {"numeric", "categorical"} and unique_ratio >= 0.95 and low_null


def _is_target_like(col_name: str, inferred_type: str, unique_count: int) -> bool:
    name = col_name.lower().strip()

    if any(hint in name for hint in TARGET_NAME_HINTS):
        return True

    if inferred_type == "categorical" and 2 <= unique_count <= 10:
        return True

    return False


def profile_dataframe(df: pd.DataFrame, table_name: str = "dataset") -> TableProfile:
    row_count = len(df)
    column_profiles: list[ColumnProfile] = []

    id_columns: list[str] = []
    datetime_columns: list[str] = []
    numeric_columns: list[str] = []
    categorical_columns: list[str] = []
    target_like_columns: list[str] = []

    for col in df.columns:
        series = df[col]
        non_null = series.dropna()
        unique_count = non_null.nunique(dropna=True)
        non_null_count = non_null.shape[0]
        null_ratio = (row_count - non_null_count) / max(row_count, 1)
        unique_ratio = unique_count / max(non_null_count, 1)

        inferred_type, is_datetime_like, is_numeric_like, is_categorical_like = _infer_series_type(series)
        is_id_like = _is_id_like(
            col_name=col,
            non_null_count=non_null_count,
            unique_count=unique_count,
            total_rows=row_count,
            inferred_type=inferred_type,
        )
        is_target_like = _is_target_like(
            col_name=col,
            inferred_type=inferred_type,
            unique_count=unique_count,
        )

        sample_values = [str(v) for v in non_null.head(3).tolist()]
        column_profiles.append(
            ColumnProfile(
                name=col,
                inferred_type=inferred_type,
                null_ratio=round(null_ratio, 4),
                unique_ratio=round(unique_ratio, 4),
                non_null_count=non_null_count,
                sample_values=sample_values,
                is_id_like=is_id_like,
                is_target_like=is_target_like,
                is_datetime_like=is_datetime_like,
                is_numeric_like=is_numeric_like,
                is_categorical_like=is_categorical_like,
            )
        )

        if is_id_like:
            id_columns.append(col)
        if is_datetime_like:
            datetime_columns.append(col)
        if is_numeric_like:
            numeric_columns.append(col)
        if is_categorical_like:
            categorical_columns.append(col)
        if is_target_like:
            target_like_columns.append(col)

    return TableProfile(
        table_name=table_name,
        row_count=row_count,
        column_count=len(df.columns),
        columns=column_profiles,
        id_columns=id_columns,
        datetime_columns=datetime_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        target_like_columns=target_like_columns,
    )


def _normalize_key_name(col_name: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "", col_name.lower().strip())


def infer_relationships(table_profiles: list[TableProfile], raw_frames: dict[str, pd.DataFrame]) -> list[RelationshipProfile]:
    relationships: list[RelationshipProfile] = []

    for left in table_profiles:
        for right in table_profiles:
            if left.table_name == right.table_name:
                continue

            left_df = raw_frames[left.table_name]
            right_df = raw_frames[right.table_name]

            for left_col in left.id_columns:
                for right_col in right.id_columns:
                    if _normalize_key_name(left_col) != _normalize_key_name(right_col):
                        continue

                    left_non_null = left_df[left_col].dropna()
                    right_non_null = right_df[right_col].dropna()
                    if left_non_null.empty or right_non_null.empty:
                        continue

                    overlap = set(left_non_null.astype(str)).intersection(
                        set(right_non_null.astype(str))
                    )
                    overlap_ratio = len(overlap) / max(min(left_non_null.nunique(), right_non_null.nunique()), 1)
                    if overlap_ratio < 0.3:
                        continue

                    left_unique = left_non_null.nunique() == len(left_non_null)
                    right_unique = right_non_null.nunique() == len(right_non_null)

                    if left_unique and not right_unique:
                        rel_type = "one_to_many"
                    elif right_unique and not left_unique:
                        rel_type = "many_to_one"
                    elif left_unique and right_unique:
                        rel_type = "one_to_one"
                    else:
                        rel_type = "many_to_many"

                    confidence = round(min(0.99, 0.5 + overlap_ratio / 2), 2)
                    relationships.append(
                        RelationshipProfile(
                            left_table=left.table_name,
                            left_column=left_col,
                            right_table=right.table_name,
                            right_column=right_col,
                            relationship_type=rel_type,
                            confidence=confidence,
                            reason=(
                                "Matched id-like column names and substantial key overlap "
                                f"(ratio={overlap_ratio:.2f})."
                            ),
                        )
                    )

    deduped: dict[tuple[str, str, str, str], RelationshipProfile] = {}
    for rel in relationships:
        key = (rel.left_table, rel.left_column, rel.right_table, rel.right_column)
        if key not in deduped or rel.confidence > deduped[key].confidence:
            deduped[key] = rel

    return list(deduped.values())


def profile_dataframes(dataframes: dict[str, pd.DataFrame]) -> SchemaProfile:
    table_profiles = [
        profile_dataframe(df, table_name=table_name)
        for table_name, df in dataframes.items()
    ]
    relationships = infer_relationships(table_profiles, raw_frames=dataframes)
    return SchemaProfile(tables=table_profiles, relationships=relationships)
