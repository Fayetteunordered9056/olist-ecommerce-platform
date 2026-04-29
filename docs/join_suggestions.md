# Multi-dataset Join Suggestions

This project now supports automatic join recommendations for multiple uploaded/loaded datasets.

## Module
- `app/join_suggester.py`

## API
- `suggest_joins_from_dataframes(dataframes, min_confidence=0.55)`
- `suggest_joins_from_profiles(table_profiles, dataframes, min_confidence=0.55)`

Each suggestion includes:
- left/right table + column
- inferred relationship type (`one_to_one`, `one_to_many`, `many_to_one`, `many_to_many`)
- confidence score
- explanation string
- SQL `ON` clause recommendation

## Heuristics used
- column-name similarity
- id/key-likeness from schema profiling
- uniqueness/cardinality on each side
- key overlap ratio between datasets
- e-commerce semantics bonus for common keys (`order_id`, `customer_id`, etc.)

## Usage with existing ingestion mapping
Run:

```bash
python scripts/suggest_joins_csv.py
```

This reuses `FILE_TABLE_MAPPING` in `scripts/load_csvs.py` and prints JSON suggestions.
