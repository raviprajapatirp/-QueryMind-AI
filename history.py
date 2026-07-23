"""
history.py
Tracks executed query history and user-saved/favorited queries. Persisted
per-user to a local SQLite table so history survives across sessions
(not just st.session_state, which resets on reload).
"""

import sqlite3
from datetime import datetime
import pandas as pd

from config import APP_STATE_DB_PATH


def _get_conn():
    conn = sqlite3.connect(APP_STATE_DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question TEXT,
            sql TEXT,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            label TEXT,
            sql TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    return conn


def log_query(username: str, question: str, sql: str):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO query_history (username, question, sql, created_at) VALUES (?, ?, ?, ?)",
        (username, question, sql, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()


def get_history(username: str, limit: int = 100) -> pd.DataFrame:
    conn = _get_conn()
    return pd.read_sql(
        "SELECT question, sql, created_at FROM query_history WHERE username=? "
        "ORDER BY id DESC LIMIT ?",
        conn, params=(username, limit),
    )


def save_query(username: str, label: str, sql: str):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO saved_queries (username, label, sql, created_at) VALUES (?, ?, ?, ?)",
        (username, label, sql, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()


def get_saved_queries(username: str) -> pd.DataFrame:
    conn = _get_conn()
    return pd.read_sql(
        "SELECT id, label, sql, created_at FROM saved_queries WHERE username=? ORDER BY id DESC",
        conn, params=(username,),
    )


def delete_saved_query(query_id: int):
    conn = _get_conn()
    conn.execute("DELETE FROM saved_queries WHERE id=?", (query_id,))
    conn.commit()
