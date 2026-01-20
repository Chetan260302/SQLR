from llm_utils import rows_to_markdown_table

MAX_DISPLAY_ROWS = 10
def format_static_response(
    *,
    db_name: str,
    dialect: str,
    sql: str,
    tables: list[str],
    columns: list[str],
    rows: list[tuple],
    total_rows: int
) -> str:


    out = []

    out.append("### Database Used")
    out.append(f"- **Name**: {db_name}")
    out.append(f"- **Dialect**: {dialect}\n")

    out.append("### Tables Involved")
    for t in tables:
        out.append(f"- `{t}`")
    out.append("")

    out.append("### Columns Selected")
    for c in columns:
        out.append(f"- `{c}`")
    out.append("")

    out.append("### SQL Query")
    out.append("```sql")
    out.append(sql)
    out.append("```")
    out.append("")
    out.append("### Query Result")

    if not rows:
        out.append("_No rows returned_")
        out.append("")
        out.append("### Insights")
        return "\n".join(out)

    # rows already limited by main.py
    out.append(rows_to_markdown_table(columns, rows))
    
    if total_rows > len(rows):
        out.append("")
        out.append(
            f"_Showing **first {len(rows)} of {total_rows} rows**. "
            "Refine your question to see more specific results._"
        )

    out.append("")
    out.append("### Insights")

    return "\n".join(out)
