"""
utils.py — Helper functions for history and logging.
"""

import os
import json
import streamlit as st
from datetime import datetime

# Persistent History Helpers
HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "summary_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception:
        pass

def add_log(tool: str, message: str, status: str = "working"):
    """Append a log entry with timestamp to session state."""
    if "execution_log" not in st.session_state:
        st.session_state.execution_log = []
        
    st.session_state.execution_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "tool": tool,
        "message": message,
        "status": status,  # working | success | error
    })
