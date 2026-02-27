"""
tools.py — Agentic tools for the Omega-Summarizer.
Each function handles one content type: web articles, YouTube videos, or audio files.

Features:
- Exponential backoff retry for transient API failures
- Custom exception handling for granular error reporting
- Content-type-specific prompt selection via build_summarize_prompt()
- Audio file validation before processing
"""

import os
import re
import time
import tempfile
from dotenv import load_dotenv

load_dotenv()

# ── SDK imports ──────────────────────────────────────────
import google.generativeai as genai
from firecrawl import FirecrawlApp
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import trafilatura

from prompts import SUMMARIZE_PROMPT, build_summarize_prompt
from constants import (
    GEMINI_MODEL_PRIORITIES,
    GEMINI_FALLBACK_MODEL,
    MAX_ARTICLE_LENGTH,
    WHISPER_MODEL,
    WHISPER_RESPONSE_FORMAT,
    YOUTUBE_VIDEO_ID_PATTERNS,
)
from utils import validate_audio_file, truncate_text
from exceptions import (
    APIKeyMissingError,
    APICallError,
    ContentExtractionError,
    ScrapingError,
    TranscriptError,
    AudioProcessingError,
    EmptyTranscriptionError,
    SummarizationError,
)


# ═════════════════════════════════════════════════════════
#  RETRY DECORATOR — Exponential backoff for API calls
# ═════════════════════════════════════════════════════════
def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry a function call with exponential backoff.
    
    Args:
        func: Callable to retry.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds (doubles each retry).
    
    Returns:
        The result of the function call.
    
    Raises:
        The last exception if all retries fail.
    """
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    raise last_exception


# ═════════════════════════════════════════════════════════
#  API CLIENT INITIALIZATION
# ═════════════════════════════════════════════════════════
def get_gemini_model():
    key = os.getenv("GOOGLE_API_KEY")
    if not key or key.startswith("your_"):
        return None
    try:
        genai.configure(api_key=key)
        available_models = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
        
        for p in GEMINI_MODEL_PRIORITIES:
            for m in available_models:
                if m.endswith(p):
                    return genai.GenerativeModel(m)
        
        if available_models:
            return genai.GenerativeModel(available_models[0])
            
    except Exception:
        return genai.GenerativeModel(GEMINI_FALLBACK_MODEL)
    
    return None

def get_firecrawl_app():
    key = os.getenv("FIRE_CRAWL_KEY")
    if not key or key.startswith("your_"):
        return None
    try:
        return FirecrawlApp(api_key=key)
    except Exception:
        return None

def get_groq_client():
    key = os.getenv("GROQ_API_KEY")
    if not key or key.startswith("your_"):
        return None
    return Groq(api_key=key)


# Initialize lazily
gemini_model = get_gemini_model()
firecrawl = get_firecrawl_app()
groq_client = get_groq_client()


# ═════════════════════════════════════════════════════════
#  HELPER — Gemini summarization with retry
# ═════════════════════════════════════════════════════════
def summarize_with_gemini(text: str, source_type: str = "content", extraction_method: str | None = None) -> str:
    """Send extracted text to Gemini and return a structured summary with retry support."""
    if not gemini_model:
        return APIKeyMissingError("GOOGLE_API_KEY").to_display()
    
    # Use the smart prompt builder for content-specific prompts
    prompt = build_summarize_prompt(
        content=text,
        source_type=source_type,
        extraction_method=extraction_method,
    )
    
    try:
        response = retry_with_backoff(
            lambda: gemini_model.generate_content(prompt),
            max_retries=2,
            base_delay=1.0,
        )
        return response.text
    except Exception as e:
        return SummarizationError(str(e)).to_display()


# ═════════════════════════════════════════════════════════
#  TOOL 1 — Article Scraper (with retry)
# ═════════════════════════════════════════════════════════
def scrape_article(url: str) -> str:
    """
    Uses Firecrawl to scrape a web article URL. 
    Falls back to Trafilatura if Firecrawl is unavailable or fails.
    Includes retry logic for transient network failures.
    """
    content = None
    method = "Firecrawl"

    # Attempt 1: Firecrawl with retry
    if firecrawl:
        try:
            result = retry_with_backoff(
                lambda: firecrawl.scrape_url(url, params={"formats": ["markdown"]}),
                max_retries=2,
                base_delay=1.5,
            )
            if result and result.get("markdown"):
                content = result["markdown"]
        except Exception:
            pass  # Fall through to Trafilatura

    # Attempt 2: Trafilatura (Fallback) with retry
    if not content:
        method = "Trafilatura"
        try:
            downloaded = retry_with_backoff(
                lambda: trafilatura.fetch_url(url),
                max_retries=2,
                base_delay=1.0,
            )
            if downloaded:
                content = trafilatura.extract(downloaded)
        except Exception as e:
            return ScrapingError(url, f"Both Firecrawl and Trafilatura failed: {str(e)}").to_display()

    if not content:
        return ContentExtractionError(
            url, "The page might be protected or have no readable text."
        ).to_display()

    # Truncate if extremely long
    content = truncate_text(content, MAX_ARTICLE_LENGTH)
    
    summary = summarize_with_gemini(
        content,
        source_type=f"web article",
        extraction_method=method,
    )
    return summary


# ═════════════════════════════════════════════════════════
#  TOOL 2 — YouTube Transcript Extractor
# ═════════════════════════════════════════════════════════
def extract_video_id(url: str) -> str | None:
    """Extract the video ID from various YouTube URL formats."""
    for pattern in YOUTUBE_VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_transcript(url: str) -> str:
    """
    Extracts transcript via youtube-transcript-api.
    Falls back to Gemini native URL analysis if no transcript is found.
    """
    video_id = extract_video_id(url)
    if not video_id:
        return "❌ Could not extract a valid video ID from the URL. Please provide a full YouTube link."

    # Attempt 1: Standard transcript API with retry
    try:
        transcript_list = retry_with_backoff(
            lambda: YouTubeTranscriptApi.get_transcript(video_id),
            max_retries=2,
            base_delay=1.0,
        )
        full_text = " ".join([entry["text"] for entry in transcript_list])
        
        if full_text.strip():
            summary = summarize_with_gemini(full_text, source_type="YouTube video transcript")
            return summary
    except Exception:
        pass  # Fall through to Gemini fallback

    # Attempt 2: Gemini native URL analysis (multimodal)
    try:
        if not gemini_model:
            return APIKeyMissingError("GOOGLE_API_KEY").to_display()
            
        prompt = (
            f"Analyze this YouTube video: {url}\n\n"
            "Provide a comprehensive summary of the video's content, key topics discussed, "
            "main arguments, and any important data or conclusions presented."
        )
        response = retry_with_backoff(
            lambda: gemini_model.generate_content(prompt),
            max_retries=2,
            base_delay=1.5,
        )
        raw_analysis = response.text

        summary = summarize_with_gemini(raw_analysis, source_type="YouTube video (AI-analyzed)")
        return summary
    except Exception as e:
        return TranscriptError(
            video_id,
            f"Could not retrieve transcript or analyze video: {str(e)}. "
            "Check that the video is public and has captions enabled."
        ).to_display()


# ═════════════════════════════════════════════════════════
#  TOOL 3 — Audio Transcriber (Groq Whisper) with validation
# ═════════════════════════════════════════════════════════
def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an uploaded audio file (MP3/WAV) via Groq's Whisper API,
    then sends the transcript to Gemini for summarization.
    Validates the audio file before processing.
    """
    if not groq_client:
        return APIKeyMissingError("GROQ_API_KEY").to_display()

    # Validate audio file before sending to API
    is_valid, error_msg = validate_audio_file(file_path)
    if not is_valid:
        return f"❌ {error_msg}"

    try:
        with open(file_path, "rb") as audio_file:
            transcription = retry_with_backoff(
                lambda: groq_client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), audio_file.read()),
                    model=WHISPER_MODEL,
                    response_format=WHISPER_RESPONSE_FORMAT,
                ),
                max_retries=2,
                base_delay=1.5,
            )

        transcript_text = str(transcription)
        if not transcript_text.strip():
            return EmptyTranscriptionError().to_display()

        summary = summarize_with_gemini(transcript_text, source_type="audio recording")
        return summary
    except Exception as e:
        return AudioProcessingError(
            reason=str(e),
            suggestions=[
                "Ensure the file is a valid MP3 or WAV.",
                "Check that the file is under 25 MB.",
                "Verify your GROQ_API_KEY is set correctly.",
            ],
        ).to_display()


# ═════════════════════════════════════════════════════════
#  TOOL 4 — Output Formatter
# ═════════════════════════════════════════════════════════
def format_output(summary: str) -> str:
    """
    Validates and cleans the summary format.
    If Gemini already produced the correct format, returns as-is.
    Otherwise, wraps raw text into the standard template.
    """
    has_quick_take = "Quick Take" in summary or "🎯" in summary
    has_insights = "Key Insights" in summary or "💡" in summary
    has_actions = "Action Steps" in summary or "🚀" in summary

    if has_quick_take and has_insights and has_actions:
        return summary

    return (
        "## 🎯 Quick Take\n"
        f"{summary[:200].strip()}\n\n"
        "## 💡 Key Insights\n"
        "- **Summary**: The content has been processed but could not be structured automatically.\n"
        "- **Note**: The raw summary is provided above.\n\n"
        "## 🚀 Action Steps\n"
        "- **Review**: Read the summary above for key takeaways.\n"
        "- **Deep Dive**: Visit the original source for full context.\n"
        "- **Apply**: Identify one actionable insight to implement today.\n"
    )


# ═════════════════════════════════════════════════════════
#  DISPATCHER — Maps tool names to functions
# ═════════════════════════════════════════════════════════
TOOL_DISPATCH = {
    "article_tool": lambda args: scrape_article(args["url"]),
    "youtube_tool": lambda args: get_youtube_transcript(args["url"]),
    "audio_tool":   lambda args: transcribe_audio(args["file_path"]),
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool by name with the given arguments."""
    if tool_name not in TOOL_DISPATCH:
        return f"❌ Unknown tool: {tool_name}"
    return TOOL_DISPATCH[tool_name](arguments)

