"""
css.py — Premium Cyber-Dark styles for Omega Summarizer.
"""

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
