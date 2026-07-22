"""
database.py
Handles all data-source connectivity:
  - CSV / Excel uploads (loaded into an in-memory SQLite engine so the same
    SQL execution path works for files and real databases)
  - SQLite file uploads
  - MySQL / PostgreSQL live connections via SQLAlchemy

Also provides automatic schema introspection (tables, columns, dtypes,
primary keys, foreign keys) so the AI engine can ground its SQL generation
in the real structure of the data.
"""

import io
import sqlite3
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine


# ---------------------------------------------------------------------------
# Engine builders
# ---------------------------------------------------------------------------
def engine_from_dataframe(df: pd.DataFrame, table_name: str = "data") -> Engine:
    """Load a DataFrame into an in-memory SQLite DB so we can run real SQL on it."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    # Persist the underlying sqlite3 connection so the in-memory DB survives
    # across calls within this Streamlit session.
    df.to_sql(table_name, engine, index=False, if_exists="replace")
    return engine


def engine_from_sqlite_upload(uploaded_file) -> Engine:
    """Write an uploaded .db file to disk and connect via SQLAlchemy."""
    tmp_path = f"/tmp/{uploaded_file.name}"
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return create_engine(f"sqlite:///{tmp_path}")


def engine_from_credentials(db_type: str, host: str, port: str, database: str,
                             username: str, password: str) -> Engine:
    """Build a MySQL or PostgreSQL SQLAlchemy engine from credentials."""
    if db_type == "MySQL":
        uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "PostgreSQL":
        uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    else:
        raise ValueError("Unsupported database type.")
    return create_engine(uri, pool_pre_ping=True)


def test_connection(engine: Engine) -> tuple:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Connection successful."
    except Exception as e:
        return False, f"Connection failed: {e}"


# ---------------------------------------------------------------------------
# Schema introspection
# ---------------------------------------------------------------------------
def get_schema(engine: Engine) -> dict:
    """
    Returns a dict describing every table:
    {
      table_name: {
        "columns": [{"name":..., "type":..., "nullable":...}],
        "primary_keys": [...],
        "foreign_keys": [{"column":..., "ref_table":..., "ref_column":...}]
      }
    }
    """
    insp = inspect(engine)
    schema = {}
    for table_name in insp.get_table_names():
        columns = []
        for col in insp.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
            })
        pk = insp.get_pk_constraint(table_name).get("constrained_columns", [])
        fks = []
        for fk in insp.get_foreign_keys(table_name):
            for local_col, remote_col in zip(fk.get("constrained_columns", []),
                                               fk.get("referred_columns", [])):
                fks.append({
                    "column": local_col,
                    "ref_table": fk.get("referred_table"),
                    "ref_column": remote_col,
                })
        schema[table_name] = {
            "columns": columns,
            "primary_keys": pk,
            "foreign_keys": fks,
        }
    return schema


def schema_to_prompt_string(schema: dict) -> str:
    """Render the schema as compact text for grounding the AI's SQL generation."""
    lines = []
    for table, meta in schema.items():
        col_desc = ", ".join(f"{c['name']} ({c['type']})" for c in meta["columns"])
        lines.append(f"Table `{table}`: {col_desc}")
        if meta["primary_keys"]:
            lines.append(f"  Primary key: {', '.join(meta['primary_keys'])}")
        for fk in meta["foreign_keys"]:
            lines.append(f"  Foreign key: {fk['column']} -> {fk['ref_table']}.{fk['ref_column']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Query execution (parameterized where applicable, read-only by default)
# ---------------------------------------------------------------------------
DANGEROUS_KEYWORDS = ["DROP ", "DELETE ", "TRUNCATE ", "ALTER ", "UPDATE ", "INSERT ",
                       "GRANT ", "REVOKE ", "CREATE USER", "ATTACH "]


def is_safe_query(sql: str, allow_writes: bool = False) -> tuple:
    """Basic guardrail against destructive statements unless explicitly allowed."""
    upper_sql = sql.upper()
    if not allow_writes:
        for kw in DANGEROUS_KEYWORDS:
            if kw in upper_sql:
                return False, f"Blocked potentially destructive keyword: '{kw.strip()}'. " \
                               f"Enable 'allow writes' in Settings if this is intentional."
    if ";" in sql.strip().rstrip(";"):
        # multiple statements - reject to reduce injection / accidental multi-exec risk
        return False, "Multiple SQL statements in one query are not allowed."
    return True, "OK"


def execute_sql(engine: Engine, sql: str, allow_writes: bool = False) -> pd.DataFrame:
    ok, msg = is_safe_query(sql, allow_writes)
    if not ok:
        raise PermissionError(msg)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        if result.returns_rows:
            rows = result.fetchall()
            cols = result.keys()
            return pd.DataFrame(rows, columns=cols)
        else:
            conn.commit()
            return pd.DataFrame({"status": [f"OK - {result.rowcount} row(s) affected"]})


def load_table_preview(engine: Engine, table_name: str, limit: int = 100) -> pd.DataFrame:
    return execute_sql(engine, f"SELECT * FROM {table_name} LIMIT {limit}")
