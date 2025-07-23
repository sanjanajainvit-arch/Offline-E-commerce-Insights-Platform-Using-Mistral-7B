text
# Offline-E-commerce-Insights-Platform-Using-Mistral-7B

**Last updated:** July 23, 2025

## Overview

The E-commerce AI Agent is an end-to-end intelligent data assistant and dashboard built with FastAPI and Streamlit. It lets you **ask natural language questions** about your Amazon-style ad sales, total sales, and product eligibility data. The system:
- ***Translates questions into valid SQLite queries via an LLM backend (Mistral on Ollama)***
- ***Executes those queries on CSV-backed SQLite tables***
- ***Displays answers, generated SQL, and visualizations in a modern UI***

---

## Features

- **Natural Language Query**: Type any question about your sales or ads data.
- **Automatic SQL Generation**: Your questions are converted to safe, interpretable SQLite queries by the LLM.
- **SQL Output**: See the exact SQL run for transparency.
- **Interactive Visualization**: Instantly visualize answers—metrics, charts, breakdowns.
- **Product Eligibility Reasoning**: Understand which items are eligible for ads and why.
- **REST API and Streamlit Dashboard**: Both programmatic and UI access to answers.
- **File-based Storage**: All data is loaded from local CSVs into SQLite seamlessly.

---

## File Structure

.
├── main.py # FastAPI backend (API server)
├── ui.py # Streamlit interface (dashboard)
├── ad_sales.csv # Ad sales data (in /data/)
├── total_sales.csv # Total sales data (in /data/)
├── eligibility.csv # Product eligibility data (in /data/)
├── query_engine.py # Ties LLM, SQL generator, database, and formatter
├── sql_generator.py # Adapts NL question → LLM → cleans/validates SQL
├── llm_client.py # Talks to Ollama/Mistral to get SQL
├── utils.py # CSV→SQLite loader, SQL execution utils
├── requirement.txt # Python dependencies
└── ...


---

## Installation

1. **Clone the Repository**

2. **Install Dependencies**
pip install -r requirement.txt

text

3. **Prepare Data**
- Place `ad_sales.csv`, `total_sales.csv`, `eligibility.csv` in a `data/` folder at the project root.

4. **(Optional) Start Ollama with Mistral model**
- [See: https://ollama.com/](https://ollama.com/)
- Required for LLM-powered SQL generation.

5. **Load Data into SQLite**
python utils.py

text

---

## Running

**Backend API**
uvicorn main:app --reload

API docs: http://localhost:8000/docs
text

**Streamlit Dashboard**
streamlit run ui.py

text

---

## API Usage

### POST `/query`
Submit a question and get an answer, SQL, and results.

#### Request:
{
"question": "What is my total sales?"
}



#### Response:
{
"question": "...",
"answer": "...",
"results": [...],
"sql": "SELECT ...;",
"status": "success"
}



*The response always includes the generated SQL query and visualisations like shown below*

![Question: What is the conversion rate per item on 2025-06-01? ](assets/bar_chart.jpg)

![Question: What is my total sales each day in June](assets/time_series.jpg)

![Question: What is my total sales?](assets/total_sales.jpg)

---

## How is the SQL Displayed?

- **Backend**: `query_engine.py`’s `handle_question()` function includes the generated SQL string in every response under the `"sql"` key.
- **Streamlit UI**: The UI will always show the "📄 View Generated SQL" expander, so users see the SQL for each answer.

---

## Data Sources

- **ad_sales.csv**: Per-item, per-day ad impressions, spend, clicks, units sold, and ad-attributed sales.
- **total_sales.csv**: Per-item, per-day total sales and orders, whether ad-driven or not.
- **eligibility.csv**: Per-item, per-day eligibility for advertising, with reasons for rejection.

---

## Security Notes

- The LLM-generated SQL is validated and sanitized before execution (see `validate_sql()` in `query_engine.py`).
- SQL queries and parameters are never written by the user directly.
- **NEVER expose this app with public write access without securing it.**

---

## Requirements

- See `requirement.txt`
  - fastapi
  - uvicorn
  - pydantic
  - pandas
  - requests
  - (streamlit, altair, plotly, if using dashboard)

---

## Customizing

- Tune which model Ollama runs in `llm_client.py` (`MODEL = "mistral"`)
- Add more sample questions/answers in `sql_generator.py`'s prompt as needed
- Replace data sources by adding to your local `data/` directory

---

## Troubleshooting

- **LLM errors**: Ensure Ollama is running and the API endpoint matches.
- **Data not loading**: Ensure CSVs are in `data/` and re-run `python utils.py`.
- **SQL errors**: The system checks for malformed or unsafe SQL and will report problems in the UI/API responses.

---

