# Schema Profiling Layer

This project now includes a schema understanding layer in `app/schema_profiler.py`.

## What it infers
- column names and inferred types (`numeric`, `datetime`, `categorical`, `unknown`)
- ID/key-like columns
- target-like columns
- datetime columns
- numeric and categorical columns
- likely inter-table relationships (for multi-table inputs)

## Design notes
- Built as a standalone abstraction (`profile_dataframe`, `profile_dataframes`) so downstream analytics and LLM modules can consume structured metadata.
- Handles messy e-commerce data by attempting tolerant numeric parsing (e.g., `$1,250.00`) and datetime detection on object columns.
- Relationship inference is heuristic: it checks shared id-like column names and key overlap ratio.

## Structured output
- Returns dataclass-backed metadata (`SchemaProfile`) with `.to_dict()` for easy serialization.

## Reusing ingestion mapping
- Use `scripts/profile_csv_schema.py` to profile local raw CSVs.
- The script reuses `scripts/load_csvs.py` `FILE_TABLE_MAPPING` so table naming stays consistent.
