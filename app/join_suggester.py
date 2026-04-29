from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
import re
from typing import Any

import pandas as pd

from app.schema_profiler import TableProfile, profile_dataframe

SEMANTIC_KEYS = {
    "order_id",
    "customer_id",
    "product_id",
    "seller_id",
    "payment_id",
    "category_id",
}


@dataclass
class JoinSuggestion:
    left_table: str
    right_table: str
    left_column: str
    right_column: str
    join_type: str
    confidence: float
    explanation: str
    overlap_ratio: float
    name_similarity: float
    semantic_score: float
    left_unique: bool
    right_unique: bool
    suggested_sql_on: str


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "", text.strip().lower())


def _tokenize(text: str) -> set[str]:
    cleaned = _normalize(text)
    return {t for t in cleaned.split("_") if t}


def _name_similarity(col_a: str, col_b: str) -> float:
    a = _normalize(col_a)
    b = _normalize(col_b)
    if a == b:
        return 1.0

    tokens_a = _tokenize(col_a)
    tokens_b = _tokenize(col_b)
    if not tokens_a or not tokens_b:
        return 0.0

    jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
    return round(jaccard, 3)


def _is_candidate_key_column(profile: TableProfile, col: str) -> bool:
    if col in profile.id_columns:
        return True
    return _normalize(col).endswith("_id") or _normalize(col) == "id"


def _relationship_type(left_unique: bool, right_unique: bool) -> str:
    if left_unique and not right_unique:
        return "one_to_many"
    if right_unique and not left_unique:
        return "many_to_one"
    if left_unique and right_unique:
        return "one_to_one"
    return "many_to_many"


def _candidate_columns(profile: TableProfile) -> list[str]:
    candidates: list[str] = []
    for col_profile in profile.columns:
        if _is_candidate_key_column(profile, col_profile.name):
            candidates.append(col_profile.name)
    return candidates


def _confidence_score(
    name_similarity: float,
    overlap_ratio: float,
    left_unique: bool,
    right_unique: bool,
    semantic_score: float,
) -> float:
    uniqueness_score = 1.0 if (left_unique or right_unique) else 0.4
    raw = (
        0.35 * name_similarity
        + 0.35 * overlap_ratio
        + 0.2 * uniqueness_score
        + 0.1 * semantic_score
    )
    return round(min(0.99, raw), 2)


def suggest_joins_from_profiles(
    table_profiles: list[TableProfile],
    dataframes: dict[str, pd.DataFrame],
    min_confidence: float = 0.55,
) -> list[JoinSuggestion]:
    suggestions: list[JoinSuggestion] = []
    profiles_by_table = {t.table_name: t for t in table_profiles}

    for left_table, right_table in combinations(profiles_by_table.keys(), 2):
        left_profile = profiles_by_table[left_table]
        right_profile = profiles_by_table[right_table]
        left_df = dataframes[left_table]
        right_df = dataframes[right_table]

        for left_col in _candidate_columns(left_profile):
            for right_col in _candidate_columns(right_profile):
                name_similarity = _name_similarity(left_col, right_col)
                if name_similarity < 0.5:
                    continue

                left_non_null = left_df[left_col].dropna().astype(str)
                right_non_null = right_df[right_col].dropna().astype(str)
                if left_non_null.empty or right_non_null.empty:
                    continue

                left_keys = set(left_non_null.unique())
                right_keys = set(right_non_null.unique())
                overlap = left_keys & right_keys
                overlap_ratio = len(overlap) / max(min(len(left_keys), len(right_keys)), 1)
                if overlap_ratio < 0.2:
                    continue

                left_unique = len(left_non_null.unique()) == len(left_non_null)
                right_unique = len(right_non_null.unique()) == len(right_non_null)
                semantic_score = 1.0 if _normalize(left_col) in SEMANTIC_KEYS else 0.5
                confidence = _confidence_score(
                    name_similarity=name_similarity,
                    overlap_ratio=overlap_ratio,
                    left_unique=left_unique,
                    right_unique=right_unique,
                    semantic_score=semantic_score,
                )
                if confidence < min_confidence:
                    continue

                join_type = _relationship_type(left_unique, right_unique)
                suggestions.append(
                    JoinSuggestion(
                        left_table=left_table,
                        right_table=right_table,
                        left_column=left_col,
                        right_column=right_col,
                        join_type=join_type,
                        confidence=confidence,
                        explanation=(
                            f"Column-name similarity={name_similarity:.2f}, "
                            f"key-overlap ratio={overlap_ratio:.2f}, "
                            f"cardinality suggests {join_type}."
                        ),
                        overlap_ratio=round(overlap_ratio, 3),
                        name_similarity=name_similarity,
                        semantic_score=semantic_score,
                        left_unique=left_unique,
                        right_unique=right_unique,
                        suggested_sql_on=(
                            f"{left_table}.{left_col} = {right_table}.{right_col}"
                        ),
                    )
                )

    deduped: dict[tuple[str, str, str, str], JoinSuggestion] = {}
    for suggestion in suggestions:
        key = (
            suggestion.left_table,
            suggestion.right_table,
            suggestion.left_column,
            suggestion.right_column,
        )
        if key not in deduped or suggestion.confidence > deduped[key].confidence:
            deduped[key] = suggestion

    return sorted(deduped.values(), key=lambda s: s.confidence, reverse=True)


def suggest_joins_from_dataframes(
    dataframes: dict[str, pd.DataFrame],
    min_confidence: float = 0.55,
) -> list[JoinSuggestion]:
    table_profiles = [
        profile_dataframe(df, table_name=table_name)
        for table_name, df in dataframes.items()
    ]
    return suggest_joins_from_profiles(
        table_profiles=table_profiles,
        dataframes=dataframes,
        min_confidence=min_confidence,
    )


def suggestions_to_dict(suggestions: list[JoinSuggestion]) -> list[dict[str, Any]]:
    return [asdict(suggestion) for suggestion in suggestions]
