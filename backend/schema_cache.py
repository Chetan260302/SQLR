from sqlalchemy import inspect
from collections import defaultdict


def get_schema_for_db(cache_key: str, engine):
    inspector = inspect(engine)

    schema_info = {
        "tables": {},
        "foreign_keys": []
    }

    # 1️⃣ Detect schemas safely
    try:
        schemas = inspector.get_schema_names()
    except Exception:
        # SQLite / MySQL fallback
        schemas = [None]

    for schema in schemas:
        # Skip system schemas where applicable
        if schema and schema.lower() in ("sys", "information_schema"):
            continue

        try:
            tables = inspector.get_table_names(schema=schema)
        except Exception:
            continue

        for table in tables:
            full_table_name = f"{schema}.{table}" if schema else table

            # 2️⃣ Columns
            try:
                columns = inspector.get_columns(table, schema=schema)
                schema_info["tables"][full_table_name] = [
                    col["name"] for col in columns
                ]
            except Exception:
                continue

            # 3️⃣ Foreign Keys
            try:
                fks = inspector.get_foreign_keys(table, schema=schema)
                for fk in fks:
                    if not fk.get("referred_table"):
                        continue

                    source_cols = fk.get("constrained_columns", [])
                    target_cols = fk.get("referred_columns", [])

                    target_schema = fk.get("referred_schema")
                    target_table = fk.get("referred_table")

                    for src_col, tgt_col in zip(source_cols, target_cols):
                        schema_info["foreign_keys"].append({
                            "source_table": full_table_name,
                            "source_column": src_col,
                            "target_table": (
                                f"{target_schema}.{target_table}"
                                if target_schema else target_table
                            ),
                            "target_column": tgt_col
                        })
            except Exception:
                continue

    return schema_info
