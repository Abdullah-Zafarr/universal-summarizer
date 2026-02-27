"""
utils.py — Utility functions for the Omega-Summarizer.
Provides input validation, text processing, and helper functions
used across the application.
"""

import re
import os
from urllib.parse import urlparse
from constants import (
    SUPPORTED_AUDIO_FORMATS,
    MAX_AUDIO_FILE_SIZE_MB,
    MAX_ARTICLE_LENGTH,
    YOUTUBE_VIDEO_ID_PATTERNS,
    URL_DISPLAY_MAX_LENGTH,
    SIDEBAR_TITLE_MAX_LENGTH,
)


# ═════════════════════════════════════════════════════════
#  URL VALIDATION & CLASSIFICATION
# ═════════════════════════════════════════════════════════
def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL with proper scheme and netloc."""
    try:
        parsed = urlparse(url.strip())
        return all([parsed.scheme in ("http", "https"), parsed.netloc])
    except Exception:
        return False


def is_youtube_url(url: str) -> bool:
    """Determine if a URL points to a YouTube video."""
    youtube_domains = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    ]
    try:
        parsed = urlparse(url.strip())
        return any(parsed.netloc.lower() == domain for domain in youtube_domains)
    except Exception:
        return False


def extract_video_id(url: str) -> str | None:
    """Extract a YouTube video ID from various URL formats."""
    for pattern in YOUTUBE_VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


# ═════════════════════════════════════════════════════════
#  TEXT PROCESSING
# ═════════════════════════════════════════════════════════
def truncate_text(text: str, max_length: int, suffix: str = "\n\n[... content truncated ...]") -> str:
    """Truncate text to a maximum length, appending a suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def truncate_display_title(title: str, max_length: int = SIDEBAR_TITLE_MAX_LENGTH) -> str:
    """Truncate a title for sidebar display with ellipsis."""
    if len(title) <= max_length:
        return title
    return title[:max_length] + "..."


def extract_domain_from_url(url: str, max_length: int = URL_DISPLAY_MAX_LENGTH) -> str:
    """Extract a short display name from a URL for history labels."""
    try:
        display = url.strip().split("//")[-1]
        return display[:max_length] if len(display) > max_length else display
    except Exception:
        return "Unknown Source"


# ═════════════════════════════════════════════════════════
#  FILE VALIDATION
# ═════════════════════════════════════════════════════════
def validate_audio_file(file_path: str) -> tuple[bool, str]:
    """
    Validate an audio file before processing.
    Returns (is_valid, error_message).
    """
    if not os.path.exists(file_path):
        return False, "File does not exist."

    # Check file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lstrip(".").lower()
    if ext not in SUPPORTED_AUDIO_FORMATS:
        return False, f"Unsupported format: .{ext}. Supported: {', '.join(SUPPORTED_AUDIO_FORMATS)}"

    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_AUDIO_FILE_SIZE_MB:
        return False, f"File too large ({file_size_mb:.1f} MB). Maximum: {MAX_AUDIO_FILE_SIZE_MB} MB."

    # Check file is not empty
    if os.path.getsize(file_path) == 0:
        return False, "File is empty (0 bytes)."

    return True, ""


# ═════════════════════════════════════════════════════════
#  RESPONSE HELPERS
# ═════════════════════════════════════════════════════════
def is_error_response(text: str) -> bool:
    """Check if a response string represents an error."""
    return text.startswith("❌") or text.startswith("⚠️")


def format_file_size(size_bytes: int) -> str:
    """Format byte size into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def sanitize_filename(name: str) -> str:
    """Remove characters that are unsafe for filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()
