"""
utils.py
Shared helper functions used across the app: session-state bootstrapping,
CSS injection for the premium glassmorphism theme, secure password hashing,
generic error handling decorator, and small formatting helpers.
"""

import hashlib
import hmac
import os
import functools
import traceback
import streamlit as st
import pandas as pd

from config import THEME, APP_SECRET_KEY


# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "authenticated": False,
        "username": None,
        "theme": "dark",
        "sidebar_collapsed": False,
        "active_page": "Home",
        "df": None,                # currently active pandas DataFrame
        "df_name": None,           # label for the active dataset/table
        "engine": None,            # SQLAlchemy engine for DB connections
        "schema": None,            # detected schema dict
        "chat_history": [],        # list of {role, content}
        "query_history": [],       # list of executed queries
        "saved_queries": [],       # list of favorited queries
        "selected_model_label": None,
        "last_sql": "",
        "last_result": None,
        "connections": [],         # recent DB connections (metadata only)
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256) - no plaintext ever stored
# ---------------------------------------------------------------------------
def hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200_000
    )
    return salt.hex(), pwd_hash.hex()


def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    _, computed = hash_password(password, salt)
    return hmac.compare_digest(computed, hash_hex)


# ---------------------------------------------------------------------------
# Error handling decorator - keeps the UI alive on unexpected exceptions
# ---------------------------------------------------------------------------
def safe_run(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            st.error(f"⚠️ Something went wrong in `{fn.__name__}`: {e}")
            with st.expander("Technical details"):
                st.code(traceback.format_exc())
            return None
    return wrapper


# ---------------------------------------------------------------------------
# CSS injection - glassmorphism / gradient premium dark-first theme
# ---------------------------------------------------------------------------
def inject_css():
    t = THEME[st.session_state.get("theme", "dark")]
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {t['bg']};
            color: {t['text']};
        }}
        section[data-testid="stSidebar"] {{
            background: {t['bg_secondary']};
            border-right: 1px solid {t['card_border']};
        }}
        .qm-card {{
            background: {t['card']};
            border: 1px solid {t['card_border']};
            border-radius: 16px;
            padding: 1.1rem 1.3rem;
            backdrop-filter: blur(10px);
            margin-bottom: 0.9rem;
        }}
        .qm-kpi-value {{
            font-size: 1.8rem;
            font-weight: 700;
            background: {t['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .qm-kpi-label {{
            color: {t['text_muted']};
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .qm-header {{
            font-size: 2rem;
            font-weight: 800;
            background: {t['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }}
        .qm-subtle {{
            color: {t['text_muted']};
            font-size: 0.95rem;
        }}
        .qm-badge {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            background: {t['card']};
            border: 1px solid {t['card_border']};
        }}
        div.stButton > button {{
            border-radius: 10px;
            border: 1px solid {t['card_border']};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, help_text: str = ""):
    st.markdown(
        f"""
        <div class="qm-card">
            <div class="qm-kpi-label">{label}</div>
            <div class="qm-kpi-value">{value}</div>
            <div class="qm-subtle">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="qm-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="qm-subtle">{subtitle}</div>', unsafe_allow_html=True)
    st.write("")


# ---------------------------------------------------------------------------
# Misc formatting helpers
# ---------------------------------------------------------------------------
def human_number(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    for unit in ["", "K", "M", "B", "T"]:
        if abs(n) < 1000:
            return f"{n:,.2f}{unit}" if unit else f"{n:,.0f}"
        n /= 1000
    return f"{n:,.2f}P"


def dataframe_from_upload(uploaded_file) -> pd.DataFrame:
    """Load a CSV or Excel upload into a DataFrame."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload CSV or Excel.")
