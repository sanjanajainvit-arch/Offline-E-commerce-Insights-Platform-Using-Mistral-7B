import sqlite3
import pandas as pd
import os

def csv_to_sqlite():
    db_path = "database.db"
    conn = None  # Initialize conn to None

    try:
        # Check for files
        ad_sales_path = "data/ad_sales.csv"
        total_sales_path = "data/total_sales.csv"
        eligibility_path = "data/eligibility.csv"

        print("[OK] Found data/ad_sales.csv" if os.path.exists(ad_sales_path) else "[ERROR] Missing data/ad_sales.csv")
        print("[OK] Found data/total_sales.csv" if os.path.exists(total_sales_path) else "[ERROR] Missing data/total_sales.csv")
        print("[OK] Found data/eligibility.csv" if os.path.exists(eligibility_path) else "[ERROR] Missing data/eligibility.csv")


        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Define files and table names
        csv_files = [
            (ad_sales_path, "ad_sales"),
            (total_sales_path, "total_sales"),
            (eligibility_path, "eligibility")
        ]

        for file_path, table_name in csv_files:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"[✓] Inserted data into table: {table_name}")
            else:
                print(f"[SKIPPED] File not found: {file_path}")

    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")

    finally:
        if conn:
            conn.close()
            print("[✓] Database connection closed.")

if __name__ == "__main__":
    csv_to_sqlite()


def run_sql_query(query: str):
    db_path = "database.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # ✅ This enables dict-style access

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]  # ✅ Return list of dicts
    finally:
        conn.close()