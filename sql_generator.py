import logging
import re
from llm_client import get_sql_from_llm

logger = logging.getLogger(__name__)

table_info = """
You are an expert at writing SQLite queries. Your ONLY job is to convert a user's question into a valid SQLite query for the schema provided.

CRITICAL RULES:
1. YOU MUST USE SQLITE SYNTAX ONLY. Do NOT use PostgreSQL syntax like ::FLOAT. For division with decimals, use CAST(column AS REAL).
2. For any metric involving ads (RoAS, CPC, ad_spend, ad_sales, clicks), you MUST get the data from the ad_sales table.
3. For any metric involving total sales, you MUST get the data from the total_sales table.
4. NEVER try to access ad_spend or clicks from the total_sales table. They are ONLY in ad_sales.
5. For CPC, always filter WHERE clicks > 0 to prevent division by zero.
6. Output ONLY the raw SQL query. Nothing else.

Rules:
- Only return the SQL query
- End the query with a semicolon
- Use exact column and table names
- Do not include any markdown (e.g., triple backticks)
- For boolean fields like 'eligibility', use: eligibility = 1 or eligibility = 0
- SQLite does not support YEAR() or MONTH(); use:
    - strftime('%Y-%m', date) = 'YYYY-MM'
- Use table aliases (e.g., ad_sales.item_id) in SELECT, JOIN, and GROUP BY clauses to avoid ambiguity
- Do not include trailing quotes or > characters
- Ensure the SQL query is syntactically complete and ends properly with a semicolon
- Avoid cutting off subqueries or JOINs — return the full SQL query
- “When the user includes a date (e.g. ‘June 1, 2025’), always generate a WHERE clause filtering the ‘date’ column by that exact day in YYYY-MM-DD format.”
- Use ad_sales for RoAS, CPC, etc.
- Use total_sales for overall revenue.
- Use NULLIF(..., 0) to avoid division by zero.
- For daily filters, use: WHERE date = 'YYYY-MM-DD'
- If user says "each item", use GROUP BY item_id.
- Return only raw SQL.
- For CPC (Cost Per Click), compute: SUM(ad_spend) / NULLIF(SUM(clicks), 0)
- Always use WHERE clicks > 0 when computing CPC
- Return only raw SQLite SQL, no markdown, no commentary.
If the question refers to "each item", group by item_id.
5. Use ROUND(..., 2) to return 2 decimal places.

You are working with a SQLite database containing 3 tables:

1. ad_sales
- date
- item_id
- ad_sales
- impressions
- ad_spend
- clicks
- units_sold

2. total_sales
- date
- item_id
- total_sales
- total_units_ordered

3. eligibility
- eligibility_datetime_utc
- item_id
- eligibility
- message

Example Questions and Answers:
Q: What is the total ad spend?
A: SELECT SUM(ad_spend) FROM ad_sales;

Q: Show RoAS (Return on Ad Spend).
A: SELECT ROUND(SUM(ad_sales) / NULLIF(SUM(ad_spend), 0), 2) AS roas FROM ad_sales;

Q: What is my total sales?
A: SELECT SUM(total_sales) FROM total_sales;

Q: How many items are eligible?
A: SELECT COUNT(*) FROM eligibility WHERE eligibility = 1;

Q: What is the average number of units sold per item?
A: SELECT item_id, ROUND(AVG(units_sold), 2) AS avg_units FROM ad_sales GROUP BY item_id;
"""

def generate_sql_from_question(question: str) -> str:
    raw_sql = get_sql_from_llm(question, table_info)
    return clean_sql_response(raw_sql)

def clean_sql_response(raw_sql: str) -> str:
    raw_sql = raw_sql.replace("```", "").strip()
    match = re.search(r"(SELECT\s.+?;)", raw_sql, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    if raw_sql.upper().startswith("SELECT"):
        return raw_sql if raw_sql.endswith(";") else raw_sql + ";"
    return None
