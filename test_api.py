"""
test_api.py — Comprehensive test suite for the Omega-Summarizer.
Validates API connectivity, URL parsing, text utilities, and tool execution.

Usage:
    python test_api.py           # Run all tests
    python test_api.py --quick   # Run only offline tests (no API calls)
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    is_valid_url,
    is_youtube_url,
    extract_video_id,
    truncate_text,
    truncate_display_title,
    validate_audio_file,
    is_error_response,
    format_file_size,
    sanitize_filename,
)
from constants import (
    APP_NAME,
    APP_VERSION,
    MAX_ARTICLE_LENGTH,
    SUPPORTED_AUDIO_FORMATS,
)
from config import AppConfig


class TestRunner:
    """Lightweight test runner with colored output and timing."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = None

    def assert_true(self, condition: bool, test_name: str):
        """Assert that a condition is True."""
        if condition:
            self.passed += 1
            print(f"  ✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(test_name)
            print(f"  ❌ {test_name}")

    def assert_equal(self, actual, expected, test_name: str):
        """Assert that two values are equal."""
        if actual == expected:
            self.passed += 1
            print(f"  ✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name} (got: {actual!r}, expected: {expected!r})")
            print(f"  ❌ {test_name} — got {actual!r}, expected {expected!r}")

    def assert_not_none(self, value, test_name: str):
        """Assert that a value is not None."""
        self.assert_true(value is not None, test_name)

    def section(self, title: str):
        """Print a section header."""
        print(f"\n{'─' * 50}")
        print(f"  {title}")
        print(f"{'─' * 50}")

    def run(self):
        """Execute all test functions and print a summary."""
        self.start_time = time.time()
        
        print(f"\n⚡ {APP_NAME} Test Suite v{APP_VERSION}")
        print(f"   Started at {datetime.now().strftime('%H:%M:%S')}")

        # Offline tests (no API calls)
        self.test_url_validation()
        self.test_youtube_url_detection()
        self.test_video_id_extraction()
        self.test_text_processing()
        self.test_file_validation()
        self.test_response_helpers()
        self.test_config_loading()

        # Online tests (require API keys)
        if "--quick" not in sys.argv:
            self.test_api_connectivity()
        else:
            print("\n  ⏭️  Skipping API tests (--quick mode)")

        self.print_summary()

    # ── URL Validation Tests ──
    def test_url_validation(self):
        self.section("URL Validation")
        self.assert_true(is_valid_url("https://example.com"), "Valid HTTPS URL")
        self.assert_true(is_valid_url("http://example.com/path?q=1"), "Valid HTTP URL with query")
        self.assert_true(not is_valid_url("not-a-url"), "Rejects plain text")
        self.assert_true(not is_valid_url(""), "Rejects empty string")
        self.assert_true(not is_valid_url("ftp://files.example.com"), "Rejects FTP scheme")
        self.assert_true(is_valid_url("https://sub.domain.example.co.uk/path"), "Accepts complex domain")

    # ── YouTube URL Detection Tests ──
    def test_youtube_url_detection(self):
        self.section("YouTube URL Detection")
        self.assert_true(is_youtube_url("https://www.youtube.com/watch?v=abc123def45"), "Standard YouTube URL")
        self.assert_true(is_youtube_url("https://youtu.be/abc123def45"), "Short YouTube URL")
        self.assert_true(is_youtube_url("https://m.youtube.com/watch?v=abc123def45"), "Mobile YouTube URL")
        self.assert_true(not is_youtube_url("https://example.com"), "Rejects non-YouTube URL")
        self.assert_true(not is_youtube_url("https://notyoutube.com/watch"), "Rejects lookalike URL")

    # ── Video ID Extraction Tests ──
    def test_video_id_extraction(self):
        self.section("Video ID Extraction")
        self.assert_equal(extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ", "Extract from standard URL")
        self.assert_equal(extract_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ", "Extract from short URL")
        self.assert_equal(extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ"), "dQw4w9WgXcQ", "Extract from embed URL")
        self.assert_equal(extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ"), "dQw4w9WgXcQ", "Extract from shorts URL")
        self.assert_equal(extract_video_id("https://example.com/not-a-video"), None, "Returns None for non-YouTube")

    # ── Text Processing Tests ──
    def test_text_processing(self):
        self.section("Text Processing")
        
        # truncate_text
        long_text = "A" * 1000
        truncated = truncate_text(long_text, 500)
        self.assert_true(len(truncated) <= 600, "truncate_text respects max length")
        self.assert_true(truncate_text("short", 500) == "short", "truncate_text preserves short text")

        # truncate_display_title
        self.assert_equal(truncate_display_title("Short Title"), "Short Title", "Short title unchanged")
        self.assert_true(truncate_display_title("A Very Long Title That Should Be Truncated").endswith("..."), "Long title has ellipsis")

        # format_file_size
        self.assert_equal(format_file_size(500), "500 B", "Format bytes")
        self.assert_equal(format_file_size(1536), "1.5 KB", "Format kilobytes")
        self.assert_equal(format_file_size(2 * 1024 * 1024), "2.0 MB", "Format megabytes")

        # sanitize_filename
        self.assert_equal(sanitize_filename("hello:world?test"), "hello_world_test", "Sanitize special chars")
        self.assert_equal(sanitize_filename("normal_file"), "normal_file", "Leave clean names")

    # ── File Validation Tests ──
    def test_file_validation(self):
        self.section("File Validation")
        is_valid, msg = validate_audio_file("nonexistent_file.mp3")
        self.assert_true(not is_valid, "Rejects nonexistent file")
        self.assert_true("does not exist" in msg, "Error mentions missing file")

    # ── Response Helper Tests ──
    def test_response_helpers(self):
        self.section("Response Helpers")
        self.assert_true(is_error_response("❌ Something failed"), "Detects error prefix")
        self.assert_true(is_error_response("⚠️ Warning message"), "Detects warning prefix")
        self.assert_true(not is_error_response("All good!"), "Passes normal text")

    # ── Configuration Tests ──
    def test_config_loading(self):
        self.section("Configuration Loading")
        config = AppConfig.from_env()
        self.assert_not_none(config, "AppConfig loads successfully")
        self.assert_not_none(config.version, "Version is set")
        self.assert_true(len(config.models.available_models) > 0, "Available models list is not empty")
        self.assert_equal(config.models.orchestrator_model, "llama-3.3-70b-versatile", "Default model is set")

    # ── API Connectivity Tests ──
    def test_api_connectivity(self):
        self.section("API Connectivity")
        load_dotenv()

        keys = {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "FIRE_CRAWL_KEY": os.getenv("FIRE_CRAWL_KEY"),
        }

        for name, val in keys.items():
            is_set = val is not None and val.strip() != "" and not val.startswith("your_")
            self.assert_true(is_set, f"{name} is configured")

    # ── Summary ──
    def print_summary(self):
        elapsed = time.time() - self.start_time
        total = self.passed + self.failed
        
        print(f"\n{'═' * 50}")
        print(f"  Results: {self.passed}/{total} passed")
        if self.failed:
            print(f"  Failed tests:")
            for err in self.errors:
                print(f"    • {err}")
        print(f"  Time: {elapsed:.2f}s")
        print(f"{'═' * 50}\n")

        sys.exit(0 if self.failed == 0 else 1)


if __name__ == "__main__":
    runner = TestRunner()
    runner.run()

