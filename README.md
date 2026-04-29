# Olist E-commerce Analytics Platform

> [!NOTE]
> **Consolidated Platform**
>
> This project is a unified platform created by merging three previous specialized repositories:
> 1. [**olist-etl-pipeline**](https://github.com/Brightpmk/olist-etl-pipeline) — Robust data ingestion and validation.
> 2. [**olist-ecommerce-data-analysis**](https://github.com/Brightpmk/Basic_data-analysis-project_00) — KPI modeling and structured analytics.
> 3. [**ecommerce-ai-analytics-assistant**](https://github.com/Brightpmk/ecommerce-ai-analytics-assistant) — LLM-powered natural language interface.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI-purple)
![ETL](https://img.shields.io/badge/Data%20Engineering-ETL-blueviolet)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-green)
![License](https://img.shields.io/badge/License-MIT-green)

An **end-to-end e-commerce analytics platform** built on the **Olist Brazilian E-commerce dataset**.

This project unifies three core capabilities into a single platform:

1. **ETL Pipeline** — Extract, transform, validate, and load raw CSV data into PostgreSQL
2. **Data Analysis** — Structured analytics with fact/dimension tables, SQL queries, notebooks, and dashboards
3. **AI Analytics Assistant** — Natural language to SQL powered by LLM, with safety guardrails and auto-visualization

---

## Architecture

```
                Raw CSV files
                     │
                     ▼
            ┌─────────────────┐
            │   ETL Pipeline  │  ← main_etl.py
            │   Extract       │
            │   Transform     │
            │   Validate      │
            │   Load          │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   PostgreSQL    │  ← Unified Database
            │   8 tables +    │
            │   1 fact table  │
            └───┬─────────┬───┘
                │         │
       ┌────────┘         └────────┐
       ▼                           ▼
┌──────────────┐          ┌──────────────────┐
│ Data Analysis│          │ AI Analytics     │
│ Scripts      │          │ Assistant        │
│ Notebooks    │          │ (Streamlit)      │
│ SQL Queries  │          │ NL → SQL → Chart │
│ Power BI     │          │ + Business       │
│ Dashboard    │          │   Insights       │
└──────────────┘          └──────────────────┘
```

---

## Key Features

### ETL Pipeline
- Config-driven CSV extraction with file validation
- Data deduplication, type cleaning, and datetime standardization
- Comprehensive data validation (null checks, FK checks, domain checks)
- Schema-based loading into PostgreSQL
- Pre-built fact table (`fact_order_item_sales`) for quick analytics
- Data quality report generation

### Data Analysis
- End-to-end reproducible data pipeline (processed → marts)
- Proper item-level vs order-level metric separation
- Star schema modeling (fact_sales, fact_orders, dim_customers, dim_products, dim_sellers, dim_date)
- RFM customer segmentation
- 12 pre-built SQL analysis queries
- Automated chart and summary table generation
- Power BI dashboard integration

### AI Analytics Assistant
- Natural language to SQL conversion via OpenAI LLM
- SQL safety guardrails (blocks DELETE, DROP, UPDATE, etc.)
- Schema-aware prompt building with business context
- Automatic chart generation (line/bar based on data patterns)
- LLM-powered business insight summaries
- Schema profiling and join suggestion engine

---

## Dataset

Source: **Olist Brazilian E-commerce Public Dataset**

| Table | Description |
|-------|-------------|
| customers | Customer profiles with location |
| orders | Order metadata and timestamps |
| order_items | Items within each order |
| order_payments | Payment details per order |
| order_reviews | Customer review scores |
| products | Product attributes |
| sellers | Seller profiles with location |
| product_category_translation | Portuguese → English category names |
| fact_order_item_sales | Pre-joined analytics fact table |

---

## Project Structure

```
olist-ecommerce-platform/
├── config/
│   └── config.yaml              # ETL pipeline configuration
├── db/
│   ├── schema.sql               # Unified PostgreSQL schema
│   └── init_db.py               # Database initialization
├── etl/                         # ETL Pipeline
│   ├── extract.py               # CSV extraction
│   ├── transform.py             # Data cleaning & fact table
│   ├── validate.py              # Data quality validation
│   ├── load.py                  # PostgreSQL loading
│   ├── report.py                # Quality report generation
│   └── logger.py                # Logging setup
├── app/                         # AI Analytics Assistant
│   ├── main.py                  # Streamlit application
│   ├── config.py                # Shared configuration
│   ├── db.py                    # Database connection
│   ├── llm.py                   # OpenAI integration
│   ├── prompt_builder.py        # SQL prompt construction
│   ├── schema.py                # Schema contract
│   ├── validator.py             # SQL safety validation
│   ├── charts.py                # Auto chart generation
│   ├── insights.py              # Business insight generation
│   ├── analytics.py             # DataFrame utilities
│   ├── utils.py                 # Helper functions
│   ├── schema_profiler.py       # Schema inference engine
│   └── join_suggester.py        # Join recommendation engine
├── analysis/                    # Data Analysis
│   ├── scripts/
│   │   ├── build_processed_data.py
│   │   ├── build_analytics_mart.py
│   │   └── run_analysis.py
│   └── notebooks/               # Jupyter notebooks
├── sql/
│   ├── analysis/                # 12 SQL analysis queries
│   └── sample_queries.sql       # Example queries
├── dashboard/                   # Power BI exports & notes
├── data/
│   └── raw/                     # Raw CSV files
├── outputs/                     # Generated charts & tables
├── tests/                       # All test suites
├── docs/                        # Documentation
├── main_etl.py                  # ETL entry point
├── requirements.txt
├── .env                         # Environment variables
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11 |
| Database | PostgreSQL |
| ETL | pandas, PyYAML, SQLAlchemy |
| Frontend | Streamlit |
| Visualization | Plotly, Matplotlib |
| LLM | OpenAI API |
| Data Processing | pandas, NumPy |
| Testing | pytest |
| Dashboard | Power BI |

---

## Installation

```bash
git clone https://github.com/Brightpmk/olist-ecommerce-platform.git
cd olist-ecommerce-platform
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

---

## Configuration

Create `.env` from the example:

```bash
copy .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=your_api_key
MODEL_NAME=gpt-4o-mini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_analytics_ecommerce
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## Usage

### 1. Run the ETL Pipeline

Load raw CSV data into PostgreSQL:

```bash
python main_etl.py
```

This will:
- Initialize the database schema
- Extract CSV files from `data/raw/`
- Clean and transform the data
- Validate data quality
- Load into PostgreSQL

### 2. Build Processed Dataset

Create the denormalized analysis dataset:

```bash
python analysis/scripts/build_processed_data.py
```

### 3. Build Analytics Mart

Generate fact/dimension tables for BI:

```bash
python analysis/scripts/build_analytics_mart.py
```

### 4. Run Analysis

Generate charts and summary tables:

```bash
python analysis/scripts/run_analysis.py
```

### 5. Launch AI Analytics Assistant

Start the Streamlit app:

```bash
python -m streamlit run app/main.py
```

---

## Testing

```bash
pytest
```

---

## Example Questions (AI Assistant)

- What is the monthly revenue trend?
- Which product categories generate the highest revenue?
- What are the most common payment types?
- Which states have the most customers?
- What is the average review score by delivery status?
- Which sellers generate the most revenue?

---

## License

MIT License
