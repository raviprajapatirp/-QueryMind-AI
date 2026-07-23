"""
config.py
Central configuration for QueryMind AI: page setup, theming, constants, and
environment variable loading. Every other module imports from here so that
colors, model names, and paths stay consistent across the app.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_NAME = "QueryMind AI"
APP_TAGLINE = "Chat with your data. Instantly."
APP_ICON = "🧠"
VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Environment / secrets
# ---------------------------------------------------------------------------
def get_secret(key: str, default: str = "") -> str:
    """Read a secret from st.secrets first (Streamlit Cloud), then env vars."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
APP_SECRET_KEY = get_secret("APP_SECRET_KEY", "dev-secret-change-me")

# ---------------------------------------------------------------------------
# Groq models available for selection in the UI
# ---------------------------------------------------------------------------
AVAILABLE_MODELS = {
    "Llama 3.3 70B (Versatile)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 2 9B": "gemma2-9b-it",
}
DEFAULT_MODEL_LABEL = "Llama 3.3 70B (Versatile)"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "sample_data")
USERS_DB_PATH = os.path.join(BASE_DIR, "users.db")
APP_STATE_DB_PATH = os.path.join(BASE_DIR, "app_state.db")

# ---------------------------------------------------------------------------
# Theme colors (dark, glassmorphism-inspired premium palette)
# ---------------------------------------------------------------------------
THEME = {
    "dark": {
        "bg": "#0B0F19",
        "bg_secondary": "#111827",
        "card": "rgba(255,255,255,0.04)",
        "card_border": "rgba(255,255,255,0.08)",
        "text": "#E5E7EB",
        "text_muted": "#9CA3AF",
        "accent": "#7C3AED",
        "accent2": "#22D3EE",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "gradient": "linear-gradient(135deg, #7C3AED 0%, #22D3EE 100%)",
    },
    "light": {
        "bg": "#F7F8FC",
        "bg_secondary": "#FFFFFF",
        "card": "rgba(17,24,39,0.03)",
        "card_border": "rgba(17,24,39,0.08)",
        "text": "#111827",
        "text_muted": "#6B7280",
        "accent": "#7C3AED",
        "accent2": "#0891B2",
        "success": "#059669",
        "warning": "#D97706",
        "danger": "#DC2626",
        "gradient": "linear-gradient(135deg, #7C3AED 0%, #0891B2 100%)",
    },
}

NAV_PAGES = [
    ("🏠", "Home"),
    ("📂", "Upload Data"),
    ("🔗", "Database Connection"),
    ("💬", "AI Chat"),
    ("📝", "SQL Generator"),
    ("▶", "SQL Executor"),
    ("📊", "Dashboard"),
    ("📈", "Charts"),
    ("🧹", "Data Cleaning"),
    ("📉", "Data Analysis"),
    ("🧠", "AI Insights"),
    ("📜", "Query History"),
    ("⭐", "Saved Queries"),
    ("📄", "Reports"),
    ("⚙", "Settings"),
    ("👤", "Profile"),
]


def configure_page():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
