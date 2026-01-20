def sql_matches_question(llm, question: str, sql: str) -> bool:
    prompt = f"""
User question:
{question}

Generated SQL:
{sql}

Does this SQL correctly answer the user's question?
Reply with only YES or NO.
"""
    response = llm.invoke(prompt).content.strip().lower()
    return response.startswith("yes")
