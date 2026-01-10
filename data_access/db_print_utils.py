def pretty_describe_row(row: tuple) -> str:
    name, dtype, nullable, key, default, extra = row

    parts = [f"{name}: {dtype}"]

    parts.append("NOT NULL" if nullable == "NO" else "NULLABLE")

    if key == "PRI":
        parts.append("PRIMARY KEY")

    if default is not None:
        parts.append(f"DEFAULT {default}")

    if extra is not None:
        parts.append(f"EXTRA {extra}")

    return " | ".join(parts)

def pretty_describe_table(rows: list[tuple]) -> list[str]:
    return [pretty_describe_row(row) for row in rows]

def pretty_foreign_key(fk_row: tuple, table_columns: list[str]) -> str:
    name, table, _, column_indexes = fk_row
    cols = [table_columns[i] for i in column_indexes]
    return f"{name}: {table}({', '.join(cols)})"