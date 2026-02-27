"""
constants.py — Centralized constants for the Omega-Summarizer system.
Eliminates magic numbers/strings scattered throughout the codebase.
"""

# ═════════════════════════════════════════════════════════
#  APPLICATION METADATA
# ═════════════════════════════════════════════════════════
APP_NAME = "Omega Summarizer"
APP_VERSION = "2.5.0"
APP_ICON = "⚡"
APP_DESCRIPTION = "Paste a URL or upload audio — get an instant, structured summary."

# ═════════════════════════════════════════════════════════
#  AGENT CONFIGURATION
# ═════════════════════════════════════════════════════════
MAX_AGENT_ITERATIONS = 3
MAX_GROQ_TOKENS = 4096
DEFAULT_ORCHESTRATOR_MODEL = "llama-3.3-70b-versatile"
AVAILABLE_ORCHESTRATOR_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "llama3-70b-8192",
]

# ═════════════════════════════════════════════════════════
#  CONTENT PROCESSING LIMITS
# ═════════════════════════════════════════════════════════
MAX_ARTICLE_LENGTH = 200_000          # Characters before truncation
MAX_AUDIO_FILE_SIZE_MB = 25           # Groq Whisper's limit
MAX_SUMMARY_HISTORY_ITEMS = 50        # Max items in sidebar history
SIDEBAR_TITLE_MAX_LENGTH = 25         # Truncate history titles
URL_DISPLAY_MAX_LENGTH = 30           # Truncate URLs in history

# ═════════════════════════════════════════════════════════
#  WHISPER CONFIGURATION
# ═════════════════════════════════════════════════════════
WHISPER_MODEL = "whisper-large-v3-turbo"
WHISPER_RESPONSE_FORMAT = "text"
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav"]

# ═════════════════════════════════════════════════════════
#  GEMINI MODEL PRIORITY ORDER
# ═════════════════════════════════════════════════════════
GEMINI_MODEL_PRIORITIES = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-1.0-pro",
]
GEMINI_FALLBACK_MODEL = "gemini-1.5-flash"

# ═════════════════════════════════════════════════════════
#  ERROR PREFIXES (for checking error states)
# ═════════════════════════════════════════════════════════
ERROR_PREFIX = "❌"
WARNING_PREFIX = "⚠️"

# ═════════════════════════════════════════════════════════
#  FILE PATHS
# ═════════════════════════════════════════════════════════
HISTORY_FILENAME = "summary_history.json"

# ═════════════════════════════════════════════════════════
#  YOUTUBE URL PATTERNS
# ═════════════════════════════════════════════════════════
YOUTUBE_VIDEO_ID_PATTERNS = [
    r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
    r'(?:embed/)([a-zA-Z0-9_-]{11})',
    r'(?:shorts/)([a-zA-Z0-9_-]{11})',
]
YOUTUBE_VIDEO_ID_LENGTH = 11
