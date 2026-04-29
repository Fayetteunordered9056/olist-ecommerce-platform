from openai import OpenAI
from app.config import Config
from app.prompt_builder import build_sql_generation_prompt
from app.utils import strip_markdown_fences


def generate_sql(user_question: str) -> str:
    if not Config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing. Please add it to your .env file.")

    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    prompt = build_sql_generation_prompt(user_question)

    response = client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a precise PostgreSQL analytics SQL generator.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content or ""
    sql = strip_markdown_fences(content)
    return sql.strip()
