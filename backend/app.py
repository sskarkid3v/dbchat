from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm import nl_to_sql
from db import run_query
from sql_validator import is_safe_sql, ensure_limit, SENSITIVE_COLUMNS
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    sql = nl_to_sql(req.message)
    if not is_safe_sql(sql):
        raise HTTPException(400, detail=f"Unsafe SQL generated: {sql}")
    sql = ensure_limit(sql)
    try:
        cols, rows = run_query(sql)
    except Exception as e:
        raise HTTPException(500, detail=f"DB error: {e}")
    # PII mask
    safe_rows = []
    for r in rows:
        new_row = []
        for c, v in zip(cols, r):
            if c.lower() in SENSITIVE_COLUMNS and v is not None:
                new_row.append("****")
            else:
                new_row.append(v)
        safe_rows.append(new_row)
    narrative = f"Returned {len(safe_rows)} rows."
    return {"sql": sql, "columns": cols, "rows": safe_rows, "narrative": narrative}
