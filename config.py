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
# Theme colors
# "light" is the default "Notebook Desk" theme: a soft, bright, student-facing
# e-learning palette (periwinkle-white paper, ink-navy text, pencil-indigo +
# highlighter-coral accents). "dark" is kept as an optional study-at-night mode.
# ---------------------------------------------------------------------------
THEME = {
    "light": {
        "bg": "#F5F7FF",
        "bg_secondary": "#FFFFFF",
        "card": "#FFFFFF",
        "card_border": "#E3E8FB",
        "text": "#1E2A55",
        "text_muted": "#6B7A99",
        "accent": "#5B5FEF",
        "accent2": "#FF7A59",
        "success": "#21C17C",
        "warning": "#FFB020",
        "danger": "#FF5470",
        "gradient": "linear-gradient(135deg, #5B5FEF 0%, #8B7BFF 55%, #FF7A59 100%)",
    },
    "dark": {
        "bg": "#0F1330",
        "bg_secondary": "#171B42",
        "card": "rgba(255,255,255,0.05)",
        "card_border": "rgba(139,123,255,0.18)",
        "text": "#E7E9FF",
        "text_muted": "#9AA3D6",
        "accent": "#8B7BFF",
        "accent2": "#FF9270",
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#FB7185",
        "gradient": "linear-gradient(135deg, #8B7BFF 0%, #6D6FEF 55%, #FF9270 100%)",
    },
}

FONT_DISPLAY = "'Baloo 2', 'Trebuchet MS', sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', sans-serif"
GOOGLE_FONTS_IMPORT_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Baloo+2:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap"
)

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
