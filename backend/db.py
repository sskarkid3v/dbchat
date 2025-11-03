import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST","localhost"),
        port=os.getenv("DB_PORT","5432"),
        user=os.getenv("DB_USER","pocuser"),
        password=os.getenv("DB_PASS","pocpass"),
        dbname=os.getenv("DB_NAME","pocdb"),
    )

def run_query(sql: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                cols = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
            else:
                cols = []
                rows = []
        return cols, rows
    finally:
        conn.close()

def fetch_schema():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_schema, table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name, ordinal_position;
            """)
            rows = cur.fetchall()
    finally:
        conn.close()

    result = []
    for r in rows:
        result.append({
            "table_schema": r[0],
            "table_name": r[1],
            "column_name": r[2],
            "data_type": r[3],
        })
    return result
