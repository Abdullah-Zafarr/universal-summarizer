"""
exceptions.py — Custom exception hierarchy for the Omega-Summarizer.
Provides specific error types for different failure scenarios,
enabling more granular error handling throughout the application.
"""


class OmegaSummarizerError(Exception):
    """Base exception for all Omega-Summarizer errors."""

    def __init__(self, message: str, user_message: str | None = None):
        super().__init__(message)
        self.user_message = user_message or message

    def to_display(self) -> str:
        """Format the error for user-facing display."""
        return f"❌ {self.user_message}"


# ═════════════════════════════════════════════════════════
#  API & AUTHENTICATION ERRORS
# ═════════════════════════════════════════════════════════
class APIKeyMissingError(OmegaSummarizerError):
    """Raised when a required API key is not configured."""

    def __init__(self, service_name: str):
        super().__init__(
            message=f"API key for {service_name} is missing or invalid.",
            user_message=(
                f"**{service_name} API key** is not set. "
                f"Please add it to your `.env` file."
            ),
        )
        self.service_name = service_name


class APICallError(OmegaSummarizerError):
    """Raised when an external API call fails."""

    def __init__(self, service_name: str, original_error: Exception):
        super().__init__(
            message=f"{service_name} API call failed: {str(original_error)}",
            user_message=f"**{service_name}** request failed: {str(original_error)}",
        )
        self.service_name = service_name
        self.original_error = original_error


class RateLimitError(APICallError):
    """Raised when an API rate limit is hit."""

    def __init__(self, service_name: str, retry_after: int | None = None):
        message = f"{service_name} rate limit exceeded."
        if retry_after:
            message += f" Retry after {retry_after} seconds."
        super(APICallError, self).__init__(
            message=message,
            user_message=message,
        )
        self.retry_after = retry_after


# ═════════════════════════════════════════════════════════
#  CONTENT EXTRACTION ERRORS
# ═════════════════════════════════════════════════════════
class ContentExtractionError(OmegaSummarizerError):
    """Raised when content cannot be extracted from a source."""

    def __init__(self, source: str, reason: str):
        super().__init__(
            message=f"Failed to extract content from {source}: {reason}",
            user_message=(
                f"Could not extract content from **{source}**. {reason}"
            ),
        )
        self.source = source
        self.reason = reason


class ScrapingError(ContentExtractionError):
    """Raised when web scraping fails."""

    def __init__(self, url: str, reason: str = "The page might be protected or empty."):
        super().__init__(source=url, reason=reason)


class TranscriptError(ContentExtractionError):
    """Raised when YouTube transcript extraction fails."""

    def __init__(self, video_id: str, reason: str = "No captions available."):
        super().__init__(
            source=f"YouTube video ({video_id})",
            reason=reason,
        )
        self.video_id = video_id


# ═════════════════════════════════════════════════════════
#  AUDIO PROCESSING ERRORS
# ═════════════════════════════════════════════════════════
class AudioProcessingError(OmegaSummarizerError):
    """Raised when audio transcription fails."""

    def __init__(self, reason: str, suggestions: list[str] | None = None):
        suggestion_text = ""
        if suggestions:
            suggestion_text = "\nSuggestions:\n" + "\n".join(
                f"• {s}" for s in suggestions
            )
        super().__init__(
            message=f"Audio processing failed: {reason}",
            user_message=f"Audio transcription failed: {reason}{suggestion_text}",
        )


class EmptyTranscriptionError(AudioProcessingError):
    """Raised when Whisper returns an empty transcription."""

    def __init__(self):
        super().__init__(
            reason="Whisper returned an empty transcription.",
            suggestions=[
                "The audio may be silent or corrupted.",
                "Try re-recording with a clearer voice.",
                "Ensure the microphone is working properly.",
            ],
        )


# ═════════════════════════════════════════════════════════
#  VALIDATION ERRORS
# ═════════════════════════════════════════════════════════
class InvalidInputError(OmegaSummarizerError):
    """Raised when user input is invalid."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid input: {reason}",
            user_message=reason,
        )


class InvalidURLError(InvalidInputError):
    """Raised when a URL is malformed or unsupported."""

    def __init__(self, url: str):
        super().__init__(
            reason=f"The URL `{url}` is not valid. Please provide a full URL starting with http:// or https://.",
        )


class UnsupportedFileFormatError(InvalidInputError):
    """Raised when an uploaded file has an unsupported format."""

    def __init__(self, format: str, supported: list[str]):
        super().__init__(
            reason=f"`.{format}` files are not supported. Supported formats: {', '.join(supported)}.",
        )


class FileTooLargeError(InvalidInputError):
    """Raised when an uploaded file exceeds the size limit."""

    def __init__(self, size_mb: float, max_mb: int):
        super().__init__(
            reason=f"File is too large ({size_mb:.1f} MB). Maximum allowed: {max_mb} MB.",
        )


# ═════════════════════════════════════════════════════════
#  SUMMARIZATION ERRORS
# ═════════════════════════════════════════════════════════
class SummarizationError(OmegaSummarizerError):
    """Raised when the summarization step fails."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Summarization failed: {reason}",
            user_message=f"Summarization failed: {reason}",
        )


class AgentLoopError(OmegaSummarizerError):
    """Raised when the agent loop exceeds max iterations."""

    def __init__(self, max_iterations: int):
        super().__init__(
            message=f"Agent loop exceeded {max_iterations} iterations.",
            user_message="The agent hit its safety limit. Please try again with a different input.",
        )
