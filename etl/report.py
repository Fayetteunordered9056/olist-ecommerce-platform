from __future__ import annotations

import json
from pathlib import Path
import pandas as pd


def build_quality_report(raw: dict[str, pd.DataFrame], cleaned: dict[str, pd.DataFrame]) -> dict:
    report: dict = {
        "raw_row_counts": {},
        "cleaned_row_counts": {},
        "rows_removed_by_cleaning": {},
        "null_counts": {},
    }

    for table_name, df in raw.items():
        report["raw_row_counts"][table_name] = len(df)

    for table_name, df in cleaned.items():
        report["cleaned_row_counts"][table_name] = len(df)
        report["null_counts"][table_name] = df.isna().sum().to_dict()

        if table_name in raw:
            report["rows_removed_by_cleaning"][table_name] = len(raw[table_name]) - len(df)

    return report


def save_quality_report(report: dict, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
