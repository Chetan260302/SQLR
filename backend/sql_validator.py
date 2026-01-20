import re

FORBIDDEN = {
    "insert", "update", "delete", "drop",
    "alter", "truncate", "pragma", "attach",
    "detach", "grant", "revoke"
}

def validate_sql(sql: str) -> None:
    sql_l = sql.lower().strip()

    # 1️⃣ Allow SELECT and WITH only
    if not sql_l.startswith(("select", "with")):
        raise ValueError("Only read-only queries are allowed")

    # 2️⃣ Block destructive operations
    for kw in FORBIDDEN:
        if re.search(rf"\b{kw}\b", sql_l):
            raise ValueError(f"Forbidden operation: {kw}")
