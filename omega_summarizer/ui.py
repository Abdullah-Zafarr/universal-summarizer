"""
ui.py — Streamlit UI components and layout.
"""

import streamlit as st
from datetime import datetime
from .utils import save_history

def render_header():
    st.markdown(
        '<div class="omega-header">'
        '<h1>Omega Summarizer<span class="accent-dot">.</span></h1>'
        "<p>Paste a URL or upload audio — get an instant, structured summary.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

def render_feature_cards():
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

def render_sidebar(orchestrator_model_list):
    import os
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
            orchestrator_model_list,
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
        
        return orchestrator_model

def render_execution_log():
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

def render_results():
    if st.session_state.summary_result:
        result = st.session_state.summary_result

        if result.startswith("❌") or result.startswith("⚠️"):
            st.warning(result)
        else:
            st.markdown('<p class="section-label">Result</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-card">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("")

            st.download_button(
                label="Download Summary (.md)",
                data=result,
                file_name=f"omega_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
            )
