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

from config import THEME, APP_SECRET_KEY, FONT_DISPLAY, FONT_BODY, GOOGLE_FONTS_IMPORT_URL


# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "authenticated": False,
        "username": None,
        "theme": "light",
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
    t = THEME[st.session_state.get("theme", "light")]
    # Subtle "notebook paper" ruled-line texture behind the main canvas — restrained,
    # just enough to feel like a study desk rather than a generic dashboard.
    paper_lines = (
        f"repeating-linear-gradient(0deg, transparent, transparent 35px, "
        f"{t['card_border']}55 36px)" if st.session_state.get("theme", "light") == "light"
        else "none"
    )
    st.markdown(
        f"""
        <style>
        @import url('{GOOGLE_FONTS_IMPORT_URL}');

        html, body, .stApp, [class*="css"] {{
            font-family: {FONT_BODY};
        }}

        .stApp {{
            background: {t['bg']} {paper_lines};
            background-attachment: fixed;
            color: {t['text']};
        }}
        section[data-testid="stSidebar"] {{
            background: {t['bg_secondary']};
            border-right: 2px solid {t['card_border']};
        }}
        section[data-testid="stSidebar"] * {{
            font-family: {FONT_BODY};
        }}

        /* Lesson-chip sidebar nav: rounded pill, colored left bar on hover/focus */
        section[data-testid="stSidebar"] div.stButton > button {{
            text-align: left;
            border-radius: 12px;
            border: 1px solid transparent;
            border-left: 4px solid transparent;
            background: transparent;
            color: {t['text']};
            font-weight: 600;
            padding: 0.55rem 0.9rem;
            transition: all 0.15s ease;
        }}
        section[data-testid="stSidebar"] div.stButton > button:hover {{
            background: {t['card_border']}55;
            border-left: 4px solid {t['accent2']};
            color: {t['accent']};
        }}

        .qm-card {{
            background: {t['card']};
            border: 1px solid {t['card_border']};
            border-left: 4px solid {t['accent']};
            border-radius: 16px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 4px 14px rgba(91,95,239,0.08);
            margin-bottom: 0.9rem;
        }}
        .qm-kpi-value {{
            font-family: {FONT_DISPLAY};
            font-size: 1.9rem;
            font-weight: 700;
            background: {t['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .qm-kpi-label {{
            color: {t['text_muted']};
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .qm-header {{
            font-family: {FONT_DISPLAY};
            font-size: 2.2rem;
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
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: {t['accent2']}22;
            color: {t['accent2']};
            border: 1px solid {t['accent2']}55;
        }}

        /* Default (non-sidebar) buttons: friendly rounded pill with accent fill */
        div.stButton > button {{
            border-radius: 999px;
            border: 1px solid {t['card_border']};
            font-weight: 600;
        }}
        div.stButton > button[kind="primary"] {{
            background: {t['gradient']};
            border: none;
            color: white;
        }}

        h1, h2, h3, h4 {{
            font-family: {FONT_DISPLAY};
            color: {t['text']};
        }}

        div[data-testid="stMetricValue"] {{
            font-family: {FONT_DISPLAY};
            color: {t['accent']};
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
