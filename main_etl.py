import yaml

from app.config import Config
from db.init_db import init_db
from etl.extract import extract_all
from etl.load import load_to_postgres
from etl.logger import setup_logger
from etl.transform import transform
from etl.validate import validate
from etl.report import build_quality_report, save_quality_report


def _log_table_counts(logger, title: str, dfs: dict) -> None:
    logger.info(title)
    for table_name, df in dfs.items():
        logger.info("  - %s: %s rows", table_name, len(df))


def main():
    logger = setup_logger()

    with open("config/config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    raw_dir = cfg["paths"]["raw_dir"]
    tables = cfg["tables"]
    quality_report_path = cfg["paths"]["quality_report_path"]

    database_url = str(Config.DATABASE_URL)

    logger.info("Starting ETL pipeline")

    logger.info("Initializing database schema")
    init_db(database_url=database_url, schema_path="db/schema.sql")

    logger.info("Extracting data")
    dfs = extract_all(raw_dir=raw_dir, tables=tables)
    _log_table_counts(logger, "Extracted tables", dfs)

    logger.info("Transforming data")
    cleaned = transform(dfs)
    _log_table_counts(logger, "Transformed tables", cleaned)

    logger.info("Validating data")
    validate(cleaned)
    logger.info("Validation passed")

    logger.info("Building data quality report")
    report = build_quality_report(dfs, cleaned)
    save_quality_report(report, quality_report_path)
    logger.info("Saved data quality report to %s", quality_report_path)

    logger.info("Loading data into PostgreSQL")
    load_to_postgres(database_url=database_url, cleaned=cleaned)

    logger.info("ETL pipeline completed successfully")


if __name__ == "__main__":
    main()
