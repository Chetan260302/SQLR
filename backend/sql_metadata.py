import sqlglot
from sqlglot import exp


def extract_sql_metadata(sql: str, dialect: str):
    """
    Returns:
    {
      "tables": ["Sales.Customer", "Sales.SalesOrderHeader"],
      "columns": ["Sales.Customer.CustomerID", "Sales.SalesOrderHeader.TotalDue"]
    }
    """

    dialect_map = {
        "mssql": "tsql",
        "postgresql": "postgres",
        "mysql": "mysql",
        "sqlite": "sqlite",
    }

    read_dialect = dialect_map.get(dialect, None)

    parsed = sqlglot.parse_one(sql, read=read_dialect)

    tables = {}
    alias_map = {}

    # ---- 1. Extract tables + aliases ----
    for table in parsed.find_all(exp.Table):
        schema = table.db
        name = table.name
        alias = table.alias

        full_name = f"{schema}.{name}" if schema else name

        tables[full_name] = True

        if alias:
            alias_map[alias] = full_name
        else:
            alias_map[name] = full_name

    # ---- 2. Extract columns ----
    columns = set()

    for col in parsed.find_all(exp.Column):
        col_name = col.name
        table_alias = col.table

        if table_alias and table_alias in alias_map:
            full_table = alias_map[table_alias]
            columns.add(f"{full_table}.{col_name}")
        else:
            # fallback (rare but safe)
            columns.add(col_name)

    return {
        "tables": sorted(tables.keys()),
        "columns": sorted(columns),
    }
