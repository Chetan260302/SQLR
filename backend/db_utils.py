from sqlalchemy import inspect

def get_database_schema(engine)->str:
    inspector=inspect(engine)
    lines = []

    for table in inspector.get_table_names():
        lines.append(f"Table: {table}")
        for col in inspector.get_columns(table):
            lines.append(f" - {col['name']} ({col['type']})")

        # Foreign keys
        fks = inspector.get_foreign_keys(table)
        for fk in fks:
            src_cols = ", ".join(fk["constrained_columns"])
            tgt_table = fk["referred_table"]
            tgt_cols = ", ".join(fk["referred_columns"])
            lines.append(
                f"   FK: {table}.{src_cols} → {tgt_table}.{tgt_cols}"
            )

        lines.append("")  # spacing

    return "\n".join(lines)