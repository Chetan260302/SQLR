import re
from collections import defaultdict


def extract_keywords(text: str):
    """
    Very lightweight keyword extractor
    """
    text = text.lower()
    words = re.findall(r"[a-zA-Z_]+", text)
    stopwords = {
        "the", "is", "are", "how", "many", "what",
        "list", "show", "give", "get", "find",
        "all", "with", "and", "of", "to", "for"
    }
    return {w for w in words if w not in stopwords and len(w) > 2}


def trim_schema_for_prompt(full_schema: dict, user_question: str, max_tables: int = 15):
    """
    Returns a trimmed schema dict safe to send to LLM
    """

    keywords = extract_keywords(user_question)

    tables = full_schema["tables"]
    foreign_keys = full_schema["foreign_keys"]

    matched_tables = set()

    # 1️⃣ Keyword → table / column matching
    for table, columns in tables.items():
        table_lc = table.lower()

        if any(k in table_lc for k in keywords):
            matched_tables.add(table)
            continue

        for col in columns:
            if any(k in col.lower() for k in keywords):
                matched_tables.add(table)
                break

    # 2️⃣ FK expansion
    expanded_tables = set(matched_tables)

    for fk in foreign_keys:
        if fk["source_table"] in matched_tables:
            expanded_tables.add(fk["target_table"])
        if fk["target_table"] in matched_tables:
            expanded_tables.add(fk["source_table"])

    # 3️⃣ Hard cap (token safety)
    final_tables = list(expanded_tables)[:max_tables]

    trimmed_schema = {
        "tables": {t: tables[t] for t in final_tables},
        "foreign_keys": [
            fk for fk in foreign_keys
            if fk["source_table"] in final_tables
            and fk["target_table"] in final_tables
        ]
    }

    return trimmed_schema
