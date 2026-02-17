"""
prompts.py — System instructions and tool definitions for the Omega-Summarizer agent.
"""

# ─────────────────────────────────────────────
# SYSTEM PROMPT  (Groq Orchestrator personality)
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are **Omega-Summarizer**, a hyper-efficient AI agent.

### Rules
1. Determine the content type from the user's input:
   • YouTube URL (contains youtube.com or youtu.be) → call `youtube_tool`.
   • Any other URL → call `article_tool`.
   • Uploaded audio file → call `audio_tool`.
2. Call exactly ONE tool. Do NOT call any other tool after that.
3. After receiving the tool result, return it DIRECTLY as your final answer. Do not modify, re-summarize, or reformat the tool result. Just output it verbatim.
4. If a tool returns an error (starts with ❌), relay the error message to the user as-is.
5. NEVER call the same tool twice. NEVER call multiple tools.
"""

# ─────────────────────────────────────────────
# SUMMARIZATION PROMPT  (sent to Gemini)
# ─────────────────────────────────────────────
SUMMARIZE_PROMPT = """You are a world-class content analyst. You will receive raw text extracted from a {source_type}.

Your task is to produce a structured summary with EXACTLY these three sections:

## 🎯 Quick Take
One single sentence that captures the core message.

## 💡 Key Insights
Exactly 5 bullet points. Each bullet should be a concise, self-contained insight.

## 🚀 Action Steps
Exactly 3 concrete, actionable next-steps a reader can take based on this content.

Rules:
- Be specific, not generic.  Use facts and data from the source.
- Write in clear, direct language.  No filler or hedging.
- Each bullet must start with a bold keyword.

Here is the content to summarize:

---
{content}
---
"""

# ─────────────────────────────────────────────
# GROQ TOOL DEFINITIONS  (function-calling JSON)
# ─────────────────────────────────────────────
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "article_tool",
            "description": "Scrape and summarize a web article from a URL. Use this for any non-YouTube URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL of the web article to scrape and summarize."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "youtube_tool",
            "description": "Extract transcript from a YouTube video and summarize it. Use this when the URL contains youtube.com or youtu.be.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full YouTube video URL."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "audio_tool",
            "description": "Transcribe and summarize an uploaded audio file (MP3 or WAV). Use this when the user uploads an audio file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The local file path to the uploaded audio file."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
]

