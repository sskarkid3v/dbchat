import os
import requests
from db import fetch_schema
from dotenv import load_dotenv
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")
IGNORE_TABLES = set(filter(None, os.getenv("IGNORE_TABLES","").split(",")))

def build_schema_prompt(max_tables: int = 20, max_cols_per_table: int = 20) -> str:
    schema_rows = fetch_schema()
    tables = {}
    for r in schema_rows:
        key = f"{r['table_schema']}.{r['table_name']}"
        if key in IGNORE_TABLES:
            continue
        tables.setdefault(key, []).append(r)

    table_items = list(tables.items())[:max_tables]
    lines = []
    for tbl, cols in table_items:
        col_parts = []
        for c in cols[:max_cols_per_table]:
            col_parts.append(f"{c['column_name']} ({c['data_type']})")
        lines.append(f"TABLE {tbl} -> " + ", ".join(col_parts))
    return "\n".join(lines)

def nl_to_sql(user_message: str) -> str:
    schema_prompt = build_schema_prompt()

    # llama3 needs to be told to return ONLY SQL
    system_prompt = f"""
You are an assistant that writes PostgreSQL queries.

TASK:
Given a user request, output ONE VALID PostgreSQL SELECT statement.

HARD RULES:
1. Output ONLY the SQL. No explanation. No markdown. No backticks.
2. Use ONLY tables/columns from the schema below.
3. Do NOT generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, REVOKE.
4. If the user does not specify a limit, add LIMIT 200.
5. Prefer explicit JOINs.
6. If a column looks like an id, join on it.

SCHEMA:
{schema_prompt}
"""

    prompt = system_prompt + f"\nUser request: {user_message}\nSQL:"

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    resp = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    sql = data.get("response","").strip()

    # clean up if llama3 still adds formatting
    for tag in ("```sql", "```", "SQL:", "Sql:", "sql:"):
        sql = sql.replace(tag, "")
    return sql.strip()
