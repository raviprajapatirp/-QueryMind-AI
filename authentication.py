"""
authentication.py
Lightweight username/password authentication backed by a local SQLite table.
Passwords are never stored in plaintext (PBKDF2-HMAC-SHA256, per-user salt).

NOTE: This is suitable for a portfolio/demo deployment. For real production
use with sensitive data, swap this out for a managed auth provider
(Auth0, Supabase Auth, Firebase Auth, etc.) and enforce HTTPS + rate limiting.
"""

import sqlite3
import re
import secrets
import streamlit as st

from config import USERS_DB_PATH
from utils import hash_password, verify_password


def _get_conn():
    conn = sqlite3.connect(USERS_DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            salt TEXT NOT NULL,
            pwd_hash TEXT NOT NULL,
            security_answer_hash TEXT,
            reset_token TEXT
        )
        """
    )
    conn.commit()
    return conn


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def signup(username: str, email: str, password: str, security_answer: str = ""):
    if not username or not password:
        return False, "Username and password are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if email and not EMAIL_RE.match(email):
        return False, "Please enter a valid email address."

    conn = _get_conn()
    cur = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        return False, "That username is already taken."

    salt_hex, pwd_hash = hash_password(password)
    ans_hash = None
    if security_answer:
        _, ans_hash = hash_password(security_answer.lower().strip())

    conn.execute(
        "INSERT INTO users (username, email, salt, pwd_hash, security_answer_hash) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, email, salt_hex, pwd_hash, ans_hash),
    )
    conn.commit()
    return True, "Account created! You can now log in."


def login(username: str, password: str):
    conn = _get_conn()
    cur = conn.execute(
        "SELECT salt, pwd_hash FROM users WHERE username = ?", (username,)
    )
    row = cur.fetchone()
    if not row:
        return False, "No account found with that username."
    salt_hex, pwd_hash = row
    if verify_password(password, salt_hex, pwd_hash):
        return True, "Login successful."
    return False, "Incorrect password."


def reset_password(username: str, security_answer: str, new_password: str):
    conn = _get_conn()
    cur = conn.execute(
        "SELECT security_answer_hash FROM users WHERE username = ?", (username,)
    )
    row = cur.fetchone()
    if not row or not row[0]:
        return False, "No recovery info on file for that account."
    salt_hex, _ = ("", "")  # placeholder to keep structure explicit
    ans_hash_stored = row[0]
    # verify security answer using stored salt scheme (re-derive with same salt)
    conn2 = _get_conn()
    salt_row = conn2.execute(
        "SELECT salt FROM users WHERE username=?", (username,)
    ).fetchone()
    if not salt_row:
        return False, "Account not found."
    if not verify_password(security_answer.lower().strip(), salt_row[0], ans_hash_stored):
        return False, "Security answer did not match."

    new_salt_hex, new_hash = hash_password(new_password)
    conn.execute(
        "UPDATE users SET salt=?, pwd_hash=? WHERE username=?",
        (new_salt_hex, new_hash, username),
    )
    conn.commit()
    return True, "Password updated. Please log in."


def logout():
    for key in ["authenticated", "username", "df", "engine", "schema", "chat_history"]:
        if key in st.session_state:
            st.session_state[key] = False if key == "authenticated" else None
    st.session_state["chat_history"] = []


def auth_gate():
    """Render login/signup UI. Returns True once authenticated."""
    from utils import page_header

    if st.session_state.get("authenticated"):
        return True

    page_header("🧠 QueryMind AI", "Chat with your data. Instantly.")
    tab_login, tab_signup, tab_forgot = st.tabs(["Log In", "Sign Up", "Forgot Password"])

    with tab_login:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)
            if submitted:
                ok, msg = login(u, p)
                if ok:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = u
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_signup:
        with st.form("signup_form"):
            u = st.text_input("Choose a username")
            e = st.text_input("Email (optional)")
            p = st.text_input("Choose a password", type="password")
            sec = st.text_input("Security answer (for password recovery): What's your favorite dataset?", "")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                ok, msg = signup(u, e, p, sec)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    with tab_forgot:
        with st.form("forgot_form"):
            u = st.text_input("Username", key="forgot_u")
            sec = st.text_input("Security answer", key="forgot_sec")
            new_p = st.text_input("New password", type="password", key="forgot_np")
            submitted = st.form_submit_button("Reset Password", use_container_width=True)
            if submitted:
                ok, msg = reset_password(u, sec, new_p)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.info("Demo tip: create any username/password to explore the app — data stays local to this session.")
    return False
