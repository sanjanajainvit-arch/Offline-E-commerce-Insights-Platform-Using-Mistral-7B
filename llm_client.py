import requests
import logging

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL = "mistral"  # or "mistral:7b-instruct-v0.3" if you've pulled a specific tag

logger = logging.getLogger(__name__)

def get_sql_from_llm(question: str, table_info: str) -> str:
    """
    Calls Mistral 7B on Ollama to return a SQLite-compatible SQL statement.
    """
    prompt = f"""
You are a SQL expert for SQLite.

Schema:
{table_info}

Instructions:
- Return ONE valid SQLite SELECT ... ; statement, nothing else.
- Use only SQLite SQL: no DIV/FILTER, always guard division by zero.
- Use 'eligibility = 1' or 'eligibility = 0' for booleans.
- Never wrap SQL in markdown or add extra explanation.
-  For daily metrics: use WHERE date = 'YYYY-MM-DD'.
4. If the question refers to "each item", group by item_id.
5. Use ROUND(..., 2) to return 2 decimal places.
6. Return ONLY the final SQL. No explanation, markdown, or quotes.
When parsing vague month names like "in June", use the latest known year from the dataset or default to '2025-06'.
For example:
- "in June" → WHERE strftime('%Y-%m', date) = '2025-06'

Example:
Q: What is the conversion rate on 2025-06-01?
A:
SELECT ROUND(SUM(units_sold) * 1.0 / NULLIF(SUM(clicks), 0), 2) AS conversion_rate
FROM ad_sales
WHERE date = '2025-06-01';

User question: {question}
SQL Query:
"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 300
                }
            },
            timeout=300
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Failed to contact Ollama: {e}")

    response_text = response.text.strip()
    logger.debug(f"[DEBUG] Raw Ollama Response: {response_text}")

    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.status_code} {response_text}")

    if not response_text:
        raise Exception("❌ LLM returned an empty response.")

    try:
        json_data = response.json()
    except Exception as e:
        raise Exception(f"❌ Failed to parse JSON from LLM: {e}\nRaw response: {response_text}")

    sql = json_data.get("response")
    if not sql:
        raise Exception(f"❌ LLM returned no SQL in 'response': {json_data}")

    logger.info(f"[INFO] Generated SQL:\n{sql}")
    return sql.strip()
