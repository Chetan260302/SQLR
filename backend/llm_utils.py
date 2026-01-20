from sqlalchemy import text
from sqlalchemy.orm import Session
from prompts import SQL_PROMPT,ANSWER_PROMPT,SQL_REPAIR_PROMPT
import re

def clean_sql(sql: str) -> str:
    # remove markdown fences
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    sql = sql.strip()

    # must start with SELECT or WITH
    lowered = sql.lower()
    if lowered.startswith("select") or lowered.startswith("with"):
        return sql

    raise ValueError("No valid SQL statement found")

def generate_sql(llm,schema:str,question:str,dialect:str)->str:
    raw = llm.invoke(
        SQL_PROMPT.format(schema=schema, question=question,dialect=dialect)
    )
    if hasattr(raw,"content"):
        raw=raw.content
    raw=raw.strip()
    sql=clean_sql(raw)
    
    return sql

def execute_sql(engine,sql:str):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        columns = columns = [
            col.split(".")[-1] if "." in col else col
            for col in result.keys()
        ]
        return list(columns), rows

def generate_answer(llm,question,columns,rows):
    resp= llm.invoke(
        ANSWER_PROMPT.format(
            question=question,
            columns=list(columns),
            rows=rows
        )
    )

    return resp.content.strip()

def repair_sql(llm,sql,error,schema,dialect,question):
    prompt=SQL_REPAIR_PROMPT.format(
        sql=sql,
        error=error,
        schema=schema,
        dialect=dialect,
        question=question
    )
    response=llm.invoke(prompt)
    return response.content.strip()

def prune_schema(llm, full_schema: str, question: str) -> str:
    """
    Uses LLM to select only relevant tables & columns.
    Returns a SMALL schema string.
    """

    prompt = f"""
    You are a database schema selection agent.

Your task:
- Select ONLY tables, columns, AND relationships needed to answer the question
- Preserve foreign key relationships (FK)
- Do NOT invent tables or columns
- Do NOT generate SQL
- Do NOT explain

Output format (STRICT):
example
Table: table_name
- column1
- column2
FK: table_name.column → table_name.column    

Schema:
{full_schema}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return response.content.strip()

def generate_answer_stream(llm, question, columns, rows):
    if not rows:
        yield "No results were found."
        return

    prompt = f"""
You are a data analyst.

Question:
{question}

Result Columns:
{columns}

Result Rows:
{rows}

OUTPUT RULES:
- Respond ONLY with bullet points
- Each bullet must fit in ONE line
- Do NOT repeat table values verbatim
- No SQL
- No explanations of SQL
- just Summarise the result briefly
- If rows are empty, say exactly:
  - No results were found.
"""


    for chunk in llm.stream(prompt):
        yield chunk.content


def rows_to_markdown_table(columns, rows):
    if not rows:
        return ""

    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"

    body = []
    for row in rows:
        body.append("| " + " | ".join(str(v) for v in row) + " |")

    return "\n".join([header, sep] + body)


def generate_chat_title_llm(llm, question: str) -> str:
    prompt = f"""
    Generate a very short chat title (max 6 words).
    No punctuation.
    No quotes.
    No markdown.

    Question:
    {question}
    """
    try:
        title = llm.invoke(prompt).strip()
        return title[:60]
    except Exception:
        return ""


