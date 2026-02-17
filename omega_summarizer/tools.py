"""
tools.py — Agentic tools for the Omega-Summarizer.
Each function handles one content type: web articles, YouTube videos, or audio files.
"""

import os
import re
import tempfile
from dotenv import load_dotenv

load_dotenv()

# ── SDK imports ──────────────────────────────────────────
import google.generativeai as genai
from firecrawl import FirecrawlApp
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import trafilatura

from prompts import SUMMARIZE_PROMPT

# ── Configure APIs ───────────────────────────────────────
def get_gemini_model():
    key = os.getenv("GOOGLE_API_KEY")
    if not key or key.startswith("your_"):
        return None
    try:
        genai.configure(api_key=key)
        # Attempt to find the best available model for the user's key
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority order: Flash 1.5 -> Flash Latest -> Pro 1.5 -> Pro 1.0
        priorities = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-1.0-pro"]
        
        for p in priorities:
            # Check for exact match or suffix match (e.g., 'models/gemini-1.5-flash')
            for m in available_models:
                if m.endswith(p):
                    return genai.GenerativeModel(m)
        
        # Fallback to the first available model if any
        if available_models:
            return genai.GenerativeModel(available_models[0])
            
    except Exception as e:
        # If listing fails, fall back to a hardcoded guess
        return genai.GenerativeModel("gemini-1.5-flash")
    
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

# Initialize lazily or with checks
gemini_model = get_gemini_model()
firecrawl = get_firecrawl_app()
groq_client = get_groq_client()


# ═════════════════════════════════════════════════════════
#  HELPER — Gemini summarization
# ═════════════════════════════════════════════════════════
def summarize_with_gemini(text: str, source_type: str = "content") -> str:
    """Send extracted text to Gemini and return a structured summary."""
    if not gemini_model:
        return "❌ **GOOGLE_API_KEY** is missing or invalid. Summarization cannot proceed."
    
    prompt = SUMMARIZE_PROMPT.format(source_type=source_type, content=text)
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini summarization failed: {str(e)}"


# ═════════════════════════════════════════════════════════
#  TOOL 1 — Article Scraper
# ═════════════════════════════════════════════════════════
def scrape_article(url: str) -> str:
    """
    Uses Firecrawl to scrape a web article URL. 
    Falls back to Trafilatura if Firecrawl is unavailable or fails.
    """
    content = None
    method = "Firecrawl"

    # Attempt 1: Firecrawl
    if firecrawl:
        try:
            result = firecrawl.scrape_url(url, params={"formats": ["markdown"]})
            if result and result.get("markdown"):
                content = result["markdown"]
        except Exception:
            pass

    # Attempt 2: Trafilatura (Fallback)
    if not content:
        method = "Trafilatura"
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded)
        except Exception as e:
            return f"❌ Article scraping failed with both Firecrawl and Trafilatura: {str(e)}."

    if not content:
        return f"❌ Could not extract content from {url}. The page might be protected or have no readable text."

    # Truncate if extremely long
    if len(content) > 200_000:
        content = content[:200_000] + "\n\n[... content truncated ...]"
    
    summary = summarize_with_gemini(content, source_type=f"web article (extracted via {method})")
    return summary


# ═════════════════════════════════════════════════════════
#  TOOL 2 — YouTube Transcript Extractor
# ═════════════════════════════════════════════════════════
def extract_video_id(url: str) -> str | None:
    """Extract the video ID from various YouTube URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
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

    # Attempt 1: Standard transcript API
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript_list])
        
        if full_text.strip():
            summary = summarize_with_gemini(full_text, source_type="YouTube video transcript")
            return summary
    except Exception:
        pass  # Fall through to Gemini fallback

    # Attempt 2: Gemini native URL analysis (multimodal)
    try:
        if not gemini_model:
            return "❌ **GOOGLE_API_KEY** is missing. Cannot perform AI analysis of the video."
            
        prompt = (
            f"Analyze this YouTube video: {url}\n\n"
            "Provide a comprehensive summary of the video's content, key topics discussed, "
            "main arguments, and any important data or conclusions presented."
        )
        response = gemini_model.generate_content(prompt)
        raw_analysis = response.text

        summary = summarize_with_gemini(raw_analysis, source_type="YouTube video (AI-analyzed)")
        return summary
    except Exception as e:
        return (
            f"❌ Could not retrieve transcript or analyze video: {str(e)}.\n"
            "Suggestions:\n"
            "• Check that the video is public and has captions enabled.\n"
            "• Try pasting the URL again.\n"
            "• For private videos, consider uploading the audio file instead."
        )


# ═════════════════════════════════════════════════════════
#  TOOL 3 — Audio Transcriber (Groq Whisper)
# ═════════════════════════════════════════════════════════
def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an uploaded audio file (MP3/WAV) via Groq's Whisper API,
    then sends the transcript to Gemini for summarization.
    """
    if not groq_client:
        return "❌ **GROQ_API_KEY** is missing or invalid. Audio transcription cannot proceed."

    try:
        with open(file_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(os.path.basename(file_path), audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="text",
            )

        transcript_text = str(transcription)
        if not transcript_text.strip():
            return "❌ Whisper returned an empty transcription. The audio may be silent or corrupted."

        summary = summarize_with_gemini(transcript_text, source_type="audio recording")
        return summary
    except Exception as e:
        return (
            f"❌ Audio transcription failed: {str(e)}.\n"
            "Suggestions:\n"
            "• Ensure the file is a valid MP3 or WAV.\n"
            "• Check that the file is under 25 MB.\n"
            "• Verify your GROQ_API_KEY is set correctly."
        )


# ═════════════════════════════════════════════════════════
#  TOOL 4 — Output Formatter
# ═════════════════════════════════════════════════════════
def format_output(summary: str) -> str:
    """
    Validates and cleans the summary format.
    If Gemini already produced the correct format, returns as-is.
    Otherwise, wraps raw text into the standard template.
    """
    # Check if the summary already has our expected sections
    has_quick_take = "Quick Take" in summary or "🎯" in summary
    has_insights = "Key Insights" in summary or "💡" in summary
    has_actions = "Action Steps" in summary or "🚀" in summary

    if has_quick_take and has_insights and has_actions:
        return summary  # Already formatted correctly

    # Fallback: wrap raw text into template
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
