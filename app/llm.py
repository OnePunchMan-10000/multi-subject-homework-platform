import requests
import streamlit as st
from app.subjects import SUBJECTS


def get_api_response(question, subject):
    """Get response from OpenRouter API"""
    if 'OPENROUTER_API_KEY' not in st.secrets:
        st.error("⚠️ API key not configured. Please add OPENROUTER_API_KEY to Streamlit secrets.")
        return None
    
    api_key = st.secrets['OPENROUTER_API_KEY']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Choose model (Physics gets a stronger one) and prepare request body
    primary_model = "openai/gpt-4o-mini"
    if subject in ("Physics", "Chemistry"):
        primary_model = "openai/gpt-4o"

    fallback_model = "openai/gpt-4o-mini"  # previously working model

    def _make_body(model_name: str):
        return {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SUBJECTS[subject]['prompt']},
                {"role": "user", "content": question}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
    
    try:
        # First try with the primary model
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=_make_body(primary_model),
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']

        # If primary fails, silently try a safe fallback (no noisy UI messages)
        response_fb = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=_make_body(fallback_model),
            timeout=30
        )

        if response_fb.status_code == 200:
            return response_fb.json()['choices'][0]['message']['content']

        # If fallback also fails, show a minimal, user-friendly message only
        st.error("The service is temporarily unavailable. Please try again in a moment.")
        return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None


