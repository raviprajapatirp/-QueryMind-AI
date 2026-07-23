"""
sql_generator.py
All natural-language <-> SQL functionality:
  - English -> SQL (schema-grounded)
  - SQL -> English explanation
  - SQL optimization suggestions
  - SQL error correction
  - SQL formatting
  - Follow-up-aware conversational context

The generated SQL always targets the dialect of the currently connected
engine (SQLite for uploaded files, MySQL/PostgreSQL for live DB connections)
so keywords like LIMIT vs TOP or date functions come out correct.
"""

import re
import sqlparse
from ai_engine import chat_completion


def _dialect_name(engine) -> str:
    try:
        return engine.dialect.name  # 'sqlite', 'mysql', 'postgresql'
    except Exception:
        return "sqlite"


def _extract_sql(text: str) -> str:
    """Pull the SQL code block out of a model response, or return raw text."""
    match = re.search(r"```sql\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def natural_language_to_sql(question: str, schema_prompt: str, engine, chat_history=None) -> str:
    dialect = _dialect_name(engine)
    history_snippet = ""
    if chat_history:
        recent = chat_history[-6:]
        history_snippet = "\n".join(f"{m['role']}: {m['content']}" for m in recent)

    system = (
        f"You are an expert SQL generator targeting {dialect} SQL dialect. "
        "You are given a database schema and a user question in plain English. "
        "Respond with ONLY a single valid SQL query inside a ```sql code block, "
        "no explanation. Use only tables/columns that exist in the schema. "
        "Prefer explicit column lists over SELECT *. Add a LIMIT to exploratory "
        "queries unless the user asks for all rows or an aggregate."
    )
    user_prompt = (
        f"Schema:\n{schema_prompt}\n\n"
        f"Recent conversation (for follow-up context):\n{history_snippet}\n\n"
        f"Question: {question}"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]
    raw = chat_completion(messages, temperature=0.1)
    return _extract_sql(raw)


def explain_sql(sql: str) -> str:
    system = (
        "You are a SQL teacher. Explain what the given SQL query does in plain "
        "English, step by step, for a non-technical business user. Be concise."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": sql},
    ]
    return chat_completion(messages, temperature=0.2)


def optimize_sql(sql: str, dialect: str = "sqlite") -> str:
    system = (
        f"You are a {dialect} performance expert. Review the SQL query and "
        "suggest concrete optimizations (indexing, avoiding SELECT *, join "
        "order, avoiding subqueries where a JOIN works, etc). Then provide the "
        "optimized query in a ```sql code block."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": sql},
    ]
    return chat_completion(messages, temperature=0.2)


def fix_sql_error(sql: str, error_message: str, schema_prompt: str) -> str:
    system = (
        "You are a SQL debugging expert. The user ran a query that produced an "
        "error. Given the schema, the failing SQL, and the error message, "
        "return ONLY the corrected SQL query in a ```sql code block."
    )
    user_prompt = f"Schema:\n{schema_prompt}\n\nFailing SQL:\n{sql}\n\nError:\n{error_message}"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]
    raw = chat_completion(messages, temperature=0.1)
    return _extract_sql(raw)


def format_sql(sql: str) -> str:
    """Deterministic formatting via sqlparse - no LLM call needed."""
    return sqlparse.format(sql, reindent=True, keyword_case="upper")


def sql_to_english(sql: str) -> str:
    """Alias of explain_sql kept for naming symmetry with the spec."""
    return explain_sql(sql)
