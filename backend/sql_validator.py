import sqlparse
FORBIDDEN = ("insert","update","delete","drop","alter","truncate","create","grant","revoke")
SENSITIVE_COLUMNS = {"email","phone","ssn"}

def is_safe_sql(sql: str) -> bool:
    lower = sql.lower()
    for kw in FORBIDDEN:
        if kw in lower:
            return False
    # simple heuristic: must start with select
    parsed = sqlparse.parse(sql)
    if not parsed:
        return False
    first = parsed[0].tokens[0].value.lower()
    return first.startswith("select")

def ensure_limit(sql: str, limit: int = 200) -> str:
    if "limit" in sql.lower():
        return sql
    return sql.rstrip(";") + f" LIMIT {limit};"
