import logging

import pandas as pd
from openai import OpenAI

from app.config import Config


def generate_basic_insight(df: pd.DataFrame) -> str:
    if df.empty:
        return "No results were returned for this question."

    if len(df.columns) >= 2:
        first_col = df.columns[0]
        second_col = df.columns[1]

        if pd.api.types.is_numeric_dtype(df[second_col]):
            first_row = df.iloc[0]
            return (
                f"The result contains {len(df)} rows. "
                f"The first row shows '{first_row[first_col]}' "
                f"with {second_col} = {first_row[second_col]}."
            )

    return f"The query returned {len(df)} rows across {len(df.columns)} columns."


def generate_insight(user_question: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "No results were returned for this question."

    if not Config.OPENAI_API_KEY:
        return generate_basic_insight(df)

    try:
        preview = df.head(10).to_markdown(index=False)
        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        prompt = f"""
You are a business analytics assistant.

User question:
{user_question}

Query result preview:
{preview}

Write a concise business insight in 2-4 sentences.
Focus on the business meaning of the result.
Do not mention SQL.
Do not mention "preview" or "table".
""".strip()

        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You summarize analytics results clearly and concisely.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content or ""
        content = content.strip()

        if not content:
            return generate_basic_insight(df)

        return content

    except Exception:
        logging.exception("Insight generation failed. Falling back to basic insight.")
        return generate_basic_insight(df)
