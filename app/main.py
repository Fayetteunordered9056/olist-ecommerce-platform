import logging

import streamlit as st

from app.analytics import coerce_datetime_columns, dataframe_summary, format_dataframe
from app.charts import build_chart
from app.db import run_select_query, test_connection
from app.insights import generate_basic_insight, generate_insight
from app.llm import generate_sql
from app.utils import setup_logging
from app.validator import validate_sql, validate_user_question

setup_logging()

EXAMPLE_QUESTIONS = [
    "What is the monthly revenue trend?",
    "Which product categories generate the highest revenue?",
    "What are the most common payment types?",
    "Which states have the most customers?",
    "What is the average freight cost per order by month?",
    "What is the average review score by delivery status?",
    "Which sellers generate the most revenue?",
    "What is the total revenue from fact_order_item_sales?",
]


def initialize_session_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []


def add_to_history(question: str) -> None:
    if question in st.session_state.history:
        st.session_state.history.remove(question)

    st.session_state.history.insert(0, question)
    st.session_state.history = st.session_state.history[:5]


def main() -> None:
    st.set_page_config(
        page_title="Olist E-commerce Analytics Platform",
        layout="wide",
    )

    initialize_session_state()

    st.title("Olist E-commerce Analytics Platform")
    st.markdown(
        """
        Ask business questions in natural language.  
        The app converts your question into SQL, validates it for safety, queries PostgreSQL,
        and returns results, charts, and concise business insights.
        
        *Powered by ETL Pipeline + Data Analysis + AI Analytics Assistant*
        """
    )

    with st.sidebar:
        st.header("About this project")
        st.write(
            "An end-to-end e-commerce analytics platform combining "
            "ETL ingestion, data analysis, and AI-powered self-service BI."
        )

        st.subheader("Database Status")
        if test_connection():
            st.success("Connected to PostgreSQL")
        else:
            st.error("Database connection failed")

        st.subheader("Recent Questions")
        if st.session_state.history:
            for item in st.session_state.history:
                st.write(f"- {item}")
        else:
            st.caption("No recent questions yet.")

    with st.expander("Example business questions"):
        for q in EXAMPLE_QUESTIONS:
            st.markdown(f"- {q}")

    user_question = st.text_input("Enter your business question")

    if st.button("Run Analysis"):
        if not user_question.strip():
            st.warning("Please enter a question first.")
            return

        question_ok, question_message = validate_user_question(user_question)
        if not question_ok:
            st.error(question_message)
            logging.warning("Blocked unsafe question: %s", user_question)
            return

        logging.info("User question: %s", user_question)

        try:
            with st.spinner("Generating SQL..."):
                sql = generate_sql(user_question)
        except Exception:
            logging.exception("SQL generation failed.")
            st.error("Failed to generate SQL from your question.")
            return

        st.subheader("Generated SQL")
        st.code(sql, language="sql")
        logging.info("Generated SQL: %s", sql)

        is_valid, validation_message = validate_sql(sql)
        if not is_valid:
            st.error(f"SQL validation failed: {validation_message}")
            logging.warning("Validation failed: %s", validation_message)
            return

        st.success("SQL validation passed.")

        try:
            with st.spinner("Running query..."):
                df = run_select_query(sql)
        except Exception:
            logging.exception("Database query failed.")
            st.error("Database query failed while processing your request.")
            return

        df = coerce_datetime_columns(df)
        df = format_dataframe(df)
        summary = dataframe_summary(df)

        add_to_history(user_question)

        st.subheader("Results")
        st.dataframe(df, use_container_width=True)
        st.caption(
            f"Rows: {summary['row_count']} | Columns: {summary['column_count']}"
        )

        chart = build_chart(df)
        if chart is not None:
            st.subheader("Chart")
            st.plotly_chart(chart, use_container_width=True)

        try:
            with st.spinner("Generating business insight..."):
                insight = generate_insight(user_question, df)
        except Exception:
            logging.exception("Insight stage failed unexpectedly.")
            insight = generate_basic_insight(df)

        st.subheader("Business Insight")
        st.write(insight)

        logging.info("Returned rows: %s", len(df))
        logging.info("Analysis completed successfully.")


if __name__ == "__main__":
    main()
