# Repository Audit and v2 Roadmap

## Current architecture

### Tech stack
- **Frontend/UI:** Streamlit (`app/main.py`)
- **Core language/runtime:** Python 3.11+
- **Database layer:** PostgreSQL via SQLAlchemy + pandas (`app/db.py`)
- **LLM integration:** OpenAI Chat Completions (`app/llm.py`, `app/insights.py`)
- **Visualization:** Plotly Express (`app/charts.py`)
- **Testing:** pytest (currently validator-focused) (`tests/test_validator.py`)

### End-to-end data flow
1. User enters natural-language business question in Streamlit UI.
2. Question is screened by `validate_user_question` for dangerous intent.
3. Prompt builder injects schema + constraints and sends to LLM SQL generator.
4. Returned SQL is displayed and validated by `validate_sql` guardrails.
5. Safe query is run against PostgreSQL with row limit and statement timeout.
6. Result DataFrame is post-processed (datetime coercion, float formatting).
7. Chart heuristics attempt line/bar chart generation.
8. Insight generator produces natural-language summary (LLM if available, fallback otherwise).
9. UI renders SQL, table, chart, and insight.

### Module responsibilities
- `app/main.py`: UI orchestration + user interaction workflow.
- `app/prompt_builder.py`: schema prompt and SQL-generation instructions.
- `app/llm.py`: SQL generation call to OpenAI.
- `app/validator.py`: question and SQL safety validation.
- `app/db.py`: DB engine management + controlled SELECT execution.
- `app/analytics.py`: result formatting and lightweight profiling.
- `app/charts.py`: chart inference and rendering object creation.
- `app/insights.py`: business insight generation logic.
- `scripts/*`: operational checks/manual pipeline helpers.

## Existing features

### Implemented and working
- Natural-language-to-SQL generation for e-commerce analytics questions.
- Application-level SQL safety checks:
  - write/DDL keyword blocking,
  - no multiple statements,
  - SELECT/WITH only,
  - restricted table usage,
  - blocked system table access.
- Read query runtime controls:
  - default row limit (`LIMIT 1000` if omitted),
  - statement timeout.
- Streamlit UX with:
  - example questions,
  - recent-question history,
  - DB connection status,
  - generated SQL + query result display.
- Auto charting for common result shapes.
- Insight generation with LLM fallback behavior.
- Baseline unit tests for SQL validator behavior.

## Gaps / issues

### Correctness and schema consistency
1. **Schema/table mismatch between prompt and validator:**
   - prompt references `order_payments` and `product_category_translation`,
   - validator allowlist contains `payments` (not `order_payments`) and excludes `product_category_translation`.
   This will reject valid LLM SQL for supported schema joins.
2. **Prompt/schema coupling is hard-coded** in one large string; no single source of truth with actual DB schema.
3. **`requirements.txt` formatting issue** (`tabulatefrom app.validator...`) indicates accidental corruption and installation risk.

### Safety and reliability
4. SQL validator uses regex heuristics only; lacks SQL parser-backed validation, making edge cases fragile.
5. SQL execution safety is app-layer only; no DB-level read-only role enforcement documented in app/runtime.
6. No retry/backoff/structured handling around LLM transient failures besides broad exception handling.

### Product behavior limitations
7. Chart selection is simplistic (first datetime + first numeric, etc.) and can pick misleading axes.
8. Insight generation uses only first 10 rows markdown preview without aggregate awareness or uncertainty handling.
9. No caching of repeated questions/SQL results; repetitive requests re-hit LLM and DB.

### Maintainability and test depth
10. Tests are narrow (validator only); no coverage for prompt quality, db limit enforcement, charts, insights fallback, or main workflow integration.
11. Scripts are mostly manual checks; no CI workflow or automated quality gate is present in repo.
12. Observability is minimal: log file output exists, but no request IDs, timing metrics, or structured logs.

## Recommended next milestones (priority order)

### 1) Schema-contract alignment hardening (highest value)
- Create a single canonical schema metadata module (tables, columns, relationships).
- Reuse it in prompt builder and validator allowlist.
- Fix known table naming mismatches (`order_payments`, `product_category_translation`).
- Add tests that assert prompt-exposed tables are validator-allowed.

### 2) Reliability + safety hardening of execution path
- Enforce DB read-only credentials/role in deployment docs and startup checks.
- Improve SQL validator with stricter patterns (comments, nested edge cases) and explicit deny/allow rules.
- Add execution telemetry: latency for LLM call, validation, query runtime, rows returned.

### 3) Test coverage expansion (production-minded)
- Add targeted unit tests for:
  - `db.enforce_limit`,
  - chart selection heuristics,
  - insight fallback behavior,
  - prompt generation invariants.
- Add one lightweight integration test using mocked LLM and temporary DB fixtures.

### 4) User experience and result quality improvements
- Add “explain SQL” panel and confidence hints (without exposing unsafe internals).
- Improve chart inference by detecting explicit metric/dimension/date columns.
- Add result-state messaging (empty results suggestions, disambiguation prompts).

### 5) Incremental performance and cost controls
- Add cache layer for repeated question->SQL and SQL->result (TTL-based).
- Add guardrails for max columns and large text payloads before rendering insights.
- Optional model fallback strategy (primary + cheaper backup) with deterministic settings.

## Risks / assumptions
- Assumes PostgreSQL schema in `sql/create_tables.sql` is source-of-truth for current environment.
- Assumes Streamlit remains the preferred UI framework (no frontend migration).
- Assumes OpenAI API usage remains acceptable for both SQL generation and insights.
- Some gaps (read-only DB roles, production deploy constraints) depend on infra outside this repo.
- Priority order is tuned for preserving architecture and minimizing refactor risk.
