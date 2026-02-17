"""
app.py — Omega-Summarizer: Main Streamlit entry point.
"""

import os
import sys
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# ── Ensure local imports work ────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from omega_summarizer.css import CUSTOM_CSS
from omega_summarizer.utils import load_history, save_history, add_log
from omega_summarizer.agent import run_agent
from omega_summarizer.ui import render_header, render_feature_cards, render_sidebar, render_execution_log, render_results

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# ═════════════════════════════════════════════════════════
#  PAGE CONFIG & SESSION STATE
# ═════════════════════════════════════════════════════════
st.set_page_config(page_title="Omega Summarizer", page_icon="⚡", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "execution_log" not in st.session_state: st.session_state.execution_log = []
if "summary_result" not in st.session_state: st.session_state.summary_result = None
if "processing" not in st.session_state: st.session_state.processing = False
if "summary_history" not in st.session_state: st.session_state.summary_history = load_history()

# ═════════════════════════════════════════════════════════
#  UI RENDERING
# ═════════════════════════════════════════════════════════
models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama3-70b-8192"]
orchestrator_model = render_sidebar(models)

render_header()
render_feature_cards()

# ── Input Area ──
st.markdown('<p class="section-label">Enter Source</p>', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])

with col1:
    url_input = st.text_input("Enter URL", placeholder="YouTube or Article URL", label_visibility="collapsed")
with col2:
    summarize_btn = st.button("Summarize", use_container_width=True)

st.markdown('<p class="input-divider">— or —</p>', unsafe_allow_html=True)
acol1, acol2 = st.columns(2)
with acol1:
    uploaded_file = st.file_uploader("Upload MP3 / WAV", type=["mp3", "wav"], help="Max 25 MB")
with acol2:
    recorded_audio = st.audio_input("Record Voice")

# ═════════════════════════════════════════════════════════
#  INPUT PROCESSING
# ═════════════════════════════════════════════════════════
def process_input():
    st.session_state.execution_log = []
    st.session_state.summary_result = None

    audio_source = uploaded_file or recorded_audio
    if audio_source is not None:
        source_name = "Uploaded File" if uploaded_file else "Voice Recording"
        add_log("system", f"Audio detected: {source_name}", "working")
        
        ext = ".wav" if recorded_audio else os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(audio_source.getbuffer())
            tmp_path = tmp.name
        
        user_msg = f"Please summarize this audio input from {source_name} located at: {tmp_path}"
        result = run_agent(user_msg, orchestrator_model)
        
        if not (result.startswith("❌") or result.startswith("⚠️")):
            display_name = uploaded_file.name if uploaded_file else f"Recording_{datetime.now().strftime('%H%M')}"
            st.session_state.summary_history.append({"title": f"🎤 {display_name}", "summary": result})
            save_history(st.session_state.summary_history)
        
        try: os.unlink(tmp_path)
        except OSError: pass

        st.session_state.summary_result = result
        return

    if url_input and url_input.strip():
        add_log("system", f"URL detected: {url_input.strip()}", "working")
        result = run_agent(f"Please summarize: {url_input.strip()}", orchestrator_model)
        st.session_state.summary_result = result
        
        if not (result.startswith("❌") or result.startswith("⚠️")):
            url_display = url_input.strip().split("//")[-1][:30]
            st.session_state.summary_history.append({"title": f"🔗 {url_display}", "summary": result})
            save_history(st.session_state.summary_history)
        return

    st.session_state.summary_result = "⚠️ Please enter a URL or provide audio to get started."

if summarize_btn:
    with st.spinner("Processing…"):
        process_input()

render_execution_log()
render_results()
