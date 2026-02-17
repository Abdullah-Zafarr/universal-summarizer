"""
app.py — Omega-Summarizer: Main Streamlit entry point and Agent loop.
A production-ready Universal Summarizer powered by Groq + Gemini.
"""

import os
import sys
import json
import time
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ── Ensure local imports work ────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompts import SYSTEM_PROMPT, TOOL_DEFINITIONS
from tools import execute_tool

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# ═════════════════════════════════════════════════════════
#  PAGE CONFIG & PREMIUM CSS
# ═════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Omega Summarizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    /* ── Cyber-Dark Theme Variables ── */
    :root {
        --bg-primary: #05070A;
        --bg-secondary: #0C1117;
        --bg-card: #12181F;
        --bg-sidebar: #05070A;
        --text-primary: #FFFFFF;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        --accent: #00E5FF;
        --accent-hover: #00B8CC;
        --accent-glow: rgba(0, 229, 255, 0.15);
        --border: rgba(255, 255, 255, 0.08);
        --border-strong: rgba(255, 255, 255, 0.15);
        --font-body: 'Inter', sans-serif;
        --font-mono: 'Space Mono', monospace;
        --radius-md: 8px;
    }

    /* ── Global Styles ─────────────────────── */
    .stApp {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
    }

    /* Force visibility for all text */
    .stMarkdown, p, span, li, label, div {
        color: var(--text-primary) !important;
    }

    /* ── Sidebar ───────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #05070A !important;
        border-right: 1px solid var(--border-strong) !important;
        padding-top: 1rem !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--accent) !important;
        font-family: var(--font-mono) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        font-size: 0.9rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar Separators */
    [data-testid="stSidebar"] hr {
        margin: 1.5rem 0 !important;
        border: none !important;
        border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Sidebar Section Labels */
    .section-label {
        color: var(--accent) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
        opacity: 0.7;
    }

    /* Sidebar Spacing Optimization - Breathable */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 1.25rem !important;
    }
    
    /* Sidebar History Cards - Premium Spacing */
    .stSidebar [data-testid="stButton"] button {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: var(--text-secondary) !important;
        text-align: left !important;
        padding: 0.8rem 1.2rem !important;
        margin-bottom: 0.6rem !important;
        transition: all 0.2s ease !important;
        font-size: 0.85rem !important;
        justify-content: flex-start !important;
        width: 100% !important;
    }
    .stSidebar [data-testid="stButton"] button:hover {
        background-color: rgba(0, 229, 255, 0.08) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: translateX(4px);
    }

    /* API Key Badges in Sidebar */
    .status-badge {
        background-color: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-mono) !important;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        width: 100%;
    }
    .badge-ok { border-color: #00E5FF44 !important; color: #00E5FF !important; }
    .badge-missing { border-color: #FF4B4B44 !important; color: #FF4B4B !important; }


    /* ── Header ────────────────────────────── */
    .omega-header {
        text-align: center;
        padding: 3rem 0 2rem;
    }
    .omega-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        letter-spacing: -0.04em;
    }
    .omega-header h1 span {
        color: var(--accent) !important;
    }
    .omega-header p {
        color: var(--text-secondary) !important;
        font-size: 1.1rem;
    }

    /* ── Input Fields ───────────────────────── */
    .stTextInput input {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-strong) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-md) !important;
    }
    .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }

    /* ── Buttons ────────────────────────────── */
    .stButton > button {
        background-color: var(--accent) !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: var(--radius-md) !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: var(--accent-hover) !important;
        box-shadow: 0 0 15px var(--accent-glow) !important;
    }

    /* ── Component Fixes (No more Black Boxes) ── */
    [data-testid="stFileUploader"] {
        background-color: var(--bg-card) !important;
        border: 1px dashed var(--border-strong) !important;
        border-radius: var(--radius-md) !important;
    }
    [data-testid="stFileUploader"] * {
        color: var(--text-primary) !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: var(--accent) !important;
        color: #000000 !important;
    }

    [data-testid="stAudioInput"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-md) !important;
    }
    /* Force all audio input sub-elements to inherit theme */
    [data-testid="stAudioInput"] * {
        background-color: transparent !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stAudioInput"] svg, [data-testid="stAudioInput"] path {
        fill: var(--accent) !important;
    }

    /* ── Selectbox ──────────────────────────── */
    .stSelectbox div[data-baseweb="select"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-strong) !important;
        color: var(--text-primary) !important;
    }

    /* ── Summary Card ───────────────────────── */
    .summary-card {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-left: 4px solid var(--accent) !important;
        padding: 2rem;
        border-radius: 4px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    /* ── Status Badges ─────────────────────── */
    .status-badge {
        background-color: rgba(255,255,255,0.03) !important;
        border: 1px solid var(--border) !important;
        color: var(--accent) !important;
        font-family: var(--font-mono) !important;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .badge-ok { border-color: var(--accent) !important; }
    .badge-missing { color: #FF4B4B !important; border-color: #FF4B4B !important; }

    /* Show Streamlit Header (Three-line menu) */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        visibility: visible !important;
    }
    
    /* Ensure the menu button is visible */
    header[data-testid="stHeader"] button {
        color: var(--accent) !important;
    }

    /* Feature Cards */
    .feature-container {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin: 2rem 0 3rem;
        flex-wrap: wrap;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border);
        padding: 1.5rem;
        border-radius: 12px;
        width: 280px;
        text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: var(--accent);
        background: rgba(0, 229, 255, 0.05);
    }
    .feature-icon {
        font-size: 2rem;
        color: var(--accent);
        margin-bottom: 1rem;
        display: block;
    }
    .feature-title {
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: var(--text-primary);
        font-size: 1.1rem;
    }
    .feature-desc {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    /* Hide Unnecessary Streamlit Elements */
    #MainMenu, footer { visibility: hidden; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════
#  SESSION STATE
# ═════════════════════════════════════════════════════════
# ── Persistent History Helpers ──
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary_history.json")

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

if "execution_log" not in st.session_state:
    st.session_state.execution_log = []
if "summary_result" not in st.session_state:
    st.session_state.summary_result = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "summary_history" not in st.session_state:
    st.session_state.summary_history = load_history()


def add_log(tool: str, message: str, status: str = "working"):
    """Append a log entry with timestamp."""
    st.session_state.execution_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "tool": tool,
        "message": message,
        "status": status,  # working | success | error
    })


# ═════════════════════════════════════════════════════════
#  SIDEBAR
# ═════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div style="text-align: center; padding: 1.5rem 0 0.5rem;">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: var(--accent); margin-bottom: 0; font-size: 1.8rem; letter-spacing: 0.2em;">OMEGA</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 0.7rem; opacity: 0.5; letter-spacing: 0.3em; margin-top: 2px;">SYSTEM STATUS</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")

    # ── API Key status ──
    st.markdown('<p class="section-label">Connected APIs</p>', unsafe_allow_html=True)
    
    keys = {
        "Google Gemini": os.getenv("GOOGLE_API_KEY"),
        "Groq Cloud": os.getenv("GROQ_API_KEY"),
        "Firecrawl": os.getenv("FIRE_CRAWL_KEY"),
    }
    
    for name, val in keys.items():
        is_set = val is not None and val.strip() != "" and not val.startswith("your_")
        badge_cls = "badge-ok" if is_set else "badge-missing"
        icon = "✓" if is_set else "✕"
        
        st.markdown(
            f'<div class="status-badge {badge_cls}">'
            f'  <span>{name}</span>'
            f'  <span style="flex: 1; text-align: right; font-weight: bold;">{icon}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    
    st.markdown("---")

    # ── Model selection ──
    st.markdown('<p class="section-label">Model Configuration</p>', unsafe_allow_html=True)
    
    orchestrator_model = st.selectbox(
        "Orchestrator Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama3-70b-8192"],
        index=0,
        help="The primary model that decides how to process your request."
    )
    
    st.markdown('<p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 5px;">'
                'Summarization Engine: <b>Gemini 1.5 Flash</b></p>', unsafe_allow_html=True)

    st.markdown("---")

    # ── History ──
    if st.session_state.summary_history:
        st.markdown('<p class="section-label">Recent Summaries</p>', unsafe_allow_html=True)
        for i, hist in enumerate(reversed(st.session_state.summary_history)):
            title = hist.get('title', f"Summary {i}")
            # Truncate title for sidebar
            disp_title = (title[:25] + '...') if len(title) > 25 else title
            if st.button(f"📄 {disp_title}", key=f"hist_{i}", use_container_width=True):
                st.session_state.summary_result = hist['summary']
        
        st.markdown("")
        if st.button("Clear History", use_container_width=True):
            st.session_state.summary_history = []
            save_history([])
            st.rerun()

    st.markdown("---")

    # ── Platform Stats ──
    st.markdown('<div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; border: 1px solid var(--border);">'
                '<p style="margin:0; font-size: 0.7rem; color: var(--text-muted);">PLATFORM VERSION</p>'
                '<p style="margin:0; font-weight: bold; color: var(--accent);">v2.4.0-CORE</p>'
                '</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
#  HEADER
# ═════════════════════════════════════════════════════════
st.markdown(
    '<div class="omega-header">'
    '<h1>Omega Summarizer<span class="accent-dot">.</span></h1>'
    "<p>Paste a URL or upload audio — get an instant, structured summary.</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Feature Highlight Cards ──
st.markdown(
    '<div class="feature-container">'
    '  <div class="feature-card">'
    '    <span class="feature-icon">📺</span>'
    '    <div class="feature-title">YouTube Intelligence</div>'
    '    <div class="feature-desc">Automatic transcript extraction and deep analysis of any video content.</div>'
    '  </div>'
    '  <div class="feature-card">'
    '    <span class="feature-icon">📰</span>'
    '    <div class="feature-title">Web Insight</div>'
    '    <div class="feature-desc">Scrape and distill long-form articles, blogs, and documentation in seconds.</div>'
    '  </div>'
    '  <div class="feature-card">'
    '    <span class="feature-icon">🎙️</span>'
    '    <div class="feature-title">Audio Processing</div>'
    '    <div class="feature-desc">Powered by Groq Whisper for near-instant transcription of voice and files.</div>'
    '  </div>'
    '</div>',
    unsafe_allow_html=True,
)

# ═════════════════════════════════════════════════════════
#  INPUT AREA
# ═════════════════════════════════════════════════════════
# ── URL Input ──
st.markdown('<p class="section-label">Enter Source</p>', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])

with col1:
    url_input = st.text_input(
        "Enter a YouTube or article URL",
        placeholder="https://youtube.com/watch?v=... or https://blog.example.com/article",
        label_visibility="collapsed",
    )

with col2:
    summarize_btn = st.button("Summarize", use_container_width=True)

st.markdown('<p class="input-divider">— or —</p>', unsafe_allow_html=True)

# ── Audio Inputs ──
acol1, acol2 = st.columns(2)

with acol1:
    uploaded_file = st.file_uploader(
        "Upload MP3 / WAV",
        type=["mp3", "wav"],
        help="Max 25 MB",
    )

with acol2:
    recorded_audio = st.audio_input("Record Voice")


# ═════════════════════════════════════════════════════════
#  GROQ AGENT LOOP
# ═════════════════════════════════════════════════════════
def run_agent(user_input: str, model: str):
    """
    Orchestrates the agentic flow:
    1. Sends user input to Groq with tool definitions.
    2. Groq decides which tool to call.
    3. Tool executes — the FULL result is stored for the user.
    4. A SHORT confirmation is sent back to Groq.
    5. Groq produces a brief final response (or we use the tool result directly).
    """
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or groq_key.startswith("your_"):
        return "❌ **GROQ_API_KEY** is not set. Please add it to your `.env` file."

    client = Groq(api_key=groq_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    add_log("agent", "Starting Groq orchestration…", "working")
    
    # Store the full tool result here — this is what the user sees
    last_tool_result = None
    max_iterations = 3  # Reduced — should only need 1-2 iterations

    for iteration in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                max_tokens=4096,
            )
        except Exception as e:
            error_msg = str(e)
            add_log("agent", f"Groq API error: {error_msg}", "error")
            # If Groq fails but we already got a good tool result, use that
            if last_tool_result and not last_tool_result.startswith("❌"):
                add_log("agent", "Using cached tool result ✓", "success")
                return last_tool_result
            return f"❌ Groq API call failed: {error_msg}"

        choice = response.choices[0]

        # ── If Groq wants to call a tool ──
        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                add_log(tool_name, f"Executing with args: {tool_args}", "working")

                # Execute the tool — this returns the FULL formatted summary
                tool_result = execute_tool(tool_name, tool_args)
                last_tool_result = tool_result  # Save the full result

                add_log(tool_name, "Completed ✓", "success")

                # Send only a SHORT confirmation back to Groq
                # This prevents context overflow and malformed tool calls
                if tool_result.startswith("❌"):
                    truncated = tool_result[:500]
                else:
                    truncated = "[Tool completed successfully. The summary has been generated and will be displayed to the user. Just confirm completion in your response.]"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": truncated,
                })

        # ── If Groq returns a final response ──
        elif choice.finish_reason == "stop":
            add_log("agent", "Final response ready ✓", "success")
            # If we have a full tool result, prefer that over Groq's text
            if last_tool_result and not last_tool_result.startswith("❌"):
                return last_tool_result
            # Otherwise use Groq's response (e.g. for error explanations)
            return choice.message.content or last_tool_result or "❌ No response generated."

        else:
            add_log("agent", f"Unexpected finish_reason: {choice.finish_reason}", "error")
            if last_tool_result and not last_tool_result.startswith("❌"):
                return last_tool_result
            return choice.message.content or "❌ Unexpected response from the orchestrator."

    # If we hit max iterations but have a good tool result, use it
    if last_tool_result and not last_tool_result.startswith("❌"):
        add_log("agent", "Returning cached tool result ✓", "success")
        return last_tool_result

    add_log("agent", "Max iterations reached", "error")
    return "❌ Agent loop hit the safety limit. Please try again."



# ═════════════════════════════════════════════════════════
#  MAIN EXECUTION FLOW
# ═════════════════════════════════════════════════════════
def process_input():
    """Determine input type and run the agent."""
    st.session_state.execution_log = []
    st.session_state.summary_result = None

    # ── Handle Audio (Uploaded or Recorded) ──
    audio_source = uploaded_file or recorded_audio
    if audio_source is not None:
        source_name = "Uploaded File" if uploaded_file else "Voice Recording"
        add_log("system", f"Audio detected: {source_name}", "working")
        
        # Save to temp file
        ext = ".wav" if recorded_audio else os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(audio_source.getbuffer())
            tmp_path = tmp.name
        
        user_msg = f"Please summarize this audio input from {source_name} located at: {tmp_path}"
        result = run_agent(user_msg, orchestrator_model)
        
        # Add to history
        if not (result.startswith("❌") or result.startswith("⚠️")):
            display_name = uploaded_file.name if uploaded_file else f"Recording_{datetime.now().strftime('%H%M')}"
            st.session_state.summary_history.append({"title": f"🎤 {display_name}", "summary": result})
            save_history(st.session_state.summary_history)
        
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        st.session_state.summary_result = result
        return

    # ── URL input ──
    if url_input and url_input.strip():
        add_log("system", f"URL detected: {url_input.strip()}", "working")
        user_msg = f"Please summarize this content: {url_input.strip()}"
        result = run_agent(user_msg, orchestrator_model)
        st.session_state.summary_result = result
        
        # Add to history
        if not (result.startswith("❌") or result.startswith("⚠️")):
            url_display = url_input.strip().split("//")[-1][:30]
            st.session_state.summary_history.append({"title": f"🔗 {url_display}", "summary": result})
            save_history(st.session_state.summary_history)
        return

    st.session_state.summary_result = "⚠️ Please enter a URL or provide audio to get started."


if summarize_btn:
    with st.spinner("Processing…"):
        process_input()


# ═════════════════════════════════════════════════════════
#  EXECUTION LOG
# ═════════════════════════════════════════════════════════
if st.session_state.execution_log:
    with st.expander("Execution Log", expanded=False):
        log_html = '<div class="log-container">'
        for entry in st.session_state.execution_log:
            status_cls = f"log-{entry['status']}"
            log_html += (
                f'<div class="log-entry">'
                f'  <span class="log-time">{entry["time"]}</span>'
                f'  <span class="log-tool">{entry["tool"]}</span>'
                f'  <span class="log-msg {status_cls}">{entry["message"]}</span>'
                f"</div>"
            )
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
#  RESULTS DISPLAY
# ═════════════════════════════════════════════════════════
if st.session_state.summary_result:
    result = st.session_state.summary_result

    if result.startswith("❌") or result.startswith("⚠️"):
        st.warning(result)
    else:
        st.markdown('<p class="section-label">Result</p>', unsafe_allow_html=True)
        # Render markdown inside the styled card
        st.markdown(f'<div class="summary-card">', unsafe_allow_html=True)
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("")  # whitespace

        # ── Download button ──
        st.download_button(
            label="Download Summary (.md)",
            data=result,
            file_name=f"omega_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
        )
