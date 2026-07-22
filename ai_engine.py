"""
ai_engine.py
Thin wrapper around the Groq chat-completion API used for:
  - conversational chat about the data
  - automatic business insight generation
Centralizing the client here means sql_generator.py, dashboard.py, and
app.py all share one consistent way of calling the LLM.
"""

import streamlit as st
from groq import Groq

from config import GROQ_API_KEY, AVAILABLE_MODELS, DEFAULT_MODEL_LABEL


@st.cache_resource(show_spinner=False)
def get_client():
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


def current_model_id() -> str:
    label = st.session_state.get("selected_model_label") or DEFAULT_MODEL_LABEL
    return AVAILABLE_MODELS.get(label, AVAILABLE_MODELS[DEFAULT_MODEL_LABEL])


def chat_completion(messages: list, temperature: float = 0.2, max_tokens: int = 1500) -> str:
    """
    messages: list of {"role": "system"|"user"|"assistant", "content": str}
    Returns the assistant's text response. Raises a friendly error if the
    API key is missing so the UI can surface setup instructions.
    """
    client = get_client()
    if client is None:
        raise RuntimeError(
            "No Groq API key configured. Add GROQ_API_KEY to your .env file "
            "or Streamlit secrets to enable AI features."
        )
    response = client.chat.completions.create(
        model=current_model_id(),
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def generate_insights(df_summary: str) -> str:
    """Ask the model for a structured business-insights readout of a dataset."""
    system = (
        "You are a senior data analyst. Given a statistical summary of a "
        "dataset, produce concise, concrete business insights: top/bottom "
        "performers, trends, outliers, data-quality issues, and 3-5 actionable "
        "recommendations. Use short bullet points grouped under bold headers. "
        "Never invent numbers that are not implied by the summary."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Dataset summary:\n{df_summary}\n\nGenerate insights."},
    ]
    return chat_completion(messages, temperature=0.3)
