import logging
from sql_generator import generate_sql_from_question
from typing import Dict, Any, List
from utils import run_sql_query

logger = logging.getLogger(__name__)

def handle_question(question: str) -> Dict[str, Any]:
    try:
        # Step 1: Generate SQL from LLM
        raw_sql = generate_sql_from_question(question)
        logger.info(f"Generated SQL:\n{raw_sql}")

        # Step 2: Validate SQL (basic safety check)
        if not validate_sql(raw_sql):
            raise ValueError("Invalid or unsafe SQL returned by LLM")

        # Step 3: Run SQL on SQLite
        rows = run_sql_query(raw_sql)

        # Step 4: Format answer
        columns = list(rows[0].keys()) if rows else []
        answer = format_answer(rows, columns)

        # ✅ Step 5: Return SQL in response
        return {
            "question": question,
            "answer": answer,
            "results": rows,
            "sql": raw_sql,  # ✅ include SQL for display in UI
            "status": "success"
        }

    except Exception as e:
        logger.error(f"❌ Error while handling question: {e}")
        return {
            "question": question,
            "answer": f"❌ Failed to process: {e}",
            "results": [],
            "sql": raw_sql if 'raw_sql' in locals() else None,  # show raw_sql even on error
            "status": "error"
        }

def validate_sql(sql_query: str) -> bool:
    if not sql_query or not isinstance(sql_query, str):
        return False
    sql_upper = sql_query.upper().strip()
    if not sql_upper.startswith('SELECT'):
        return False
    if not sql_query.strip().endswith(';'):
        return False
    for keyword in ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']:
        if keyword in sql_upper:
            return False
    return True

def format_answer(rows: List[Dict[str, Any]], columns: List[str]) -> str:
    if not rows:
        return "No results found."

    # Format short results nicely
    if len(rows) <= 10:
        return "\n".join(
            ", ".join(f"{col}: {row[col]}" for col in columns)
            for row in rows
        )

    # Format long results with preview
    preview = "\n".join(
        ", ".join(f"{col}: {row[col]}" for col in columns)
        for row in rows[:5]
    )
    return f"Found {len(rows)} results. First few entries:\n{preview}"
