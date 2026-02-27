"""
config.py — Centralized configuration manager for the Omega-Summarizer.
Handles environment variable loading, validation, and provides a single
source of truth for all runtime configuration.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

from constants import (
    DEFAULT_ORCHESTRATOR_MODEL,
    AVAILABLE_ORCHESTRATOR_MODELS,
    MAX_AGENT_ITERATIONS,
    MAX_GROQ_TOKENS,
    MAX_ARTICLE_LENGTH,
    MAX_AUDIO_FILE_SIZE_MB,
    WHISPER_MODEL,
    APP_VERSION,
)


@dataclass
class APIKeys:
    """Container for all API keys with validation."""

    google_api_key: str = ""
    groq_api_key: str = ""
    firecrawl_api_key: str = ""

    @property
    def has_google(self) -> bool:
        return bool(self.google_api_key) and not self.google_api_key.startswith("your_")

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("your_")

    @property
    def has_firecrawl(self) -> bool:
        return bool(self.firecrawl_api_key) and not self.firecrawl_api_key.startswith("your_")

    def get_status(self) -> dict[str, bool]:
        """Return a dictionary of API key availability."""
        return {
            "Google Gemini": self.has_google,
            "Groq Cloud": self.has_groq,
            "Firecrawl": self.has_firecrawl,
        }

    def get_missing_keys(self) -> list[str]:
        """Return list of missing API keys."""
        missing = []
        if not self.has_google:
            missing.append("GOOGLE_API_KEY")
        if not self.has_groq:
            missing.append("GROQ_API_KEY")
        if not self.has_firecrawl:
            missing.append("FIRE_CRAWL_KEY")
        return missing


@dataclass
class ModelConfig:
    """Configuration for AI models used in the pipeline."""

    orchestrator_model: str = DEFAULT_ORCHESTRATOR_MODEL
    whisper_model: str = WHISPER_MODEL
    max_tokens: int = MAX_GROQ_TOKENS
    max_agent_iterations: int = MAX_AGENT_ITERATIONS

    @property
    def available_models(self) -> list[str]:
        return AVAILABLE_ORCHESTRATOR_MODELS


@dataclass
class ProcessingConfig:
    """Configuration for content processing limits."""

    max_article_length: int = MAX_ARTICLE_LENGTH
    max_audio_file_size_mb: int = MAX_AUDIO_FILE_SIZE_MB


@dataclass
class AppConfig:
    """
    Master configuration object for the Omega-Summarizer.
    Aggregates all sub-configurations into a single access point.
    """

    api_keys: APIKeys = field(default_factory=APIKeys)
    models: ModelConfig = field(default_factory=ModelConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    version: str = APP_VERSION
    debug: bool = False

    @classmethod
    def from_env(cls, env_path: str | None = None) -> "AppConfig":
        """
        Load configuration from environment variables.
        Optionally specify a custom .env file path.
        """
        if env_path:
            load_dotenv(env_path)
        else:
            # Try to load from project root
            project_root = os.path.dirname(os.path.abspath(__file__))
            load_dotenv(os.path.join(project_root, ".env"))

        api_keys = APIKeys(
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            firecrawl_api_key=os.getenv("FIRE_CRAWL_KEY", ""),
        )

        debug = os.getenv("OMEGA_DEBUG", "false").lower() in ("true", "1", "yes")

        return cls(
            api_keys=api_keys,
            debug=debug,
        )

    def validate(self) -> list[str]:
        """
        Validate the configuration and return a list of warnings.
        Returns an empty list if everything is properly configured.
        """
        warnings = []

        if not self.api_keys.has_google:
            warnings.append("GOOGLE_API_KEY is not configured — summarization will not work.")

        if not self.api_keys.has_groq:
            warnings.append("GROQ_API_KEY is not configured — orchestration and audio transcription will not work.")

        if not self.api_keys.has_firecrawl:
            warnings.append("FIRE_CRAWL_KEY is not configured — will fall back to Trafilatura for web scraping.")

        if self.models.orchestrator_model not in AVAILABLE_ORCHESTRATOR_MODELS:
            warnings.append(
                f"Unknown orchestrator model: {self.models.orchestrator_model}. "
                f"Available: {', '.join(AVAILABLE_ORCHESTRATOR_MODELS)}"
            )

        return warnings

    def __repr__(self) -> str:
        missing = self.api_keys.get_missing_keys()
        status = "OK" if not missing else f"Missing: {', '.join(missing)}"
        return (
            f"AppConfig(version={self.version}, "
            f"model={self.models.orchestrator_model}, "
            f"api_status={status})"
        )
