import pandas as pd
import plotly.express as px


def find_best_chart_columns(df: pd.DataFrame) -> tuple[str | None, str | None, str | None]:
    datetime_cols = []
    numeric_cols = []
    object_cols = []

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        elif pd.api.types.is_object_dtype(df[col]):
            object_cols.append(col)

    if datetime_cols and numeric_cols:
        return "line", datetime_cols[0], numeric_cols[0]

    if object_cols and numeric_cols and len(df) <= 30:
        return "bar", object_cols[0], numeric_cols[0]

    return None, None, None


def build_chart(df: pd.DataFrame):
    if df.empty or len(df.columns) < 2:
        return None

    chart_type, x_col, y_col = find_best_chart_columns(df)

    if chart_type is None or x_col is None or y_col is None:
        return None

    chart_df = df.copy()

    if chart_type == "line":
        chart_df = chart_df.sort_values(by=x_col)
        return px.line(chart_df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")

    if chart_type == "bar":
        return px.bar(chart_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")

    return None
