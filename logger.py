"""
logger.py — Structured logging for the Omega-Summarizer.
Provides both console logging and in-app execution log tracking
with configurable log levels and formatted output.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Literal

from constants import APP_NAME


# ═════════════════════════════════════════════════════════
#  CONSOLE LOGGER SETUP
# ═════════════════════════════════════════════════════════
def setup_logger(
    name: str = APP_NAME,
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_dir: str | None = None,
) -> logging.Logger:
    """
    Create and configure a logger with formatted console output.
    Optionally writes to a rotating log file.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers on re-import
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler with colored-style formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    console_format = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_to_file:
        log_directory = log_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "logs"
        )
        os.makedirs(log_directory, exist_ok=True)

        log_filename = os.path.join(
            log_directory,
            f"omega_{datetime.now().strftime('%Y%m%d')}.log",
        )

        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        file_format = logging.Formatter(
            fmt="%(asctime)s │ %(levelname)-8s │ %(name)s.%(funcName)s:%(lineno)d │ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


# ═════════════════════════════════════════════════════════
#  IN-APP EXECUTION LOG (for Streamlit UI)
# ═════════════════════════════════════════════════════════
LogStatus = Literal["working", "success", "error"]


class ExecutionLog:
    """
    Tracks tool executions for display in the Streamlit UI.
    Each entry includes a timestamp, tool name, message, and status.
    """

    def __init__(self):
        self._entries: list[dict] = []

    def add(self, tool: str, message: str, status: LogStatus = "working") -> None:
        """Append a new log entry."""
        self._entries.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "tool": tool,
            "message": message,
            "status": status,
        })

    def clear(self) -> None:
        """Clear all log entries."""
        self._entries.clear()

    @property
    def entries(self) -> list[dict]:
        """Return a copy of all log entries."""
        return list(self._entries)

    @property
    def is_empty(self) -> bool:
        """Check if the log has any entries."""
        return len(self._entries) == 0

    @property
    def last_entry(self) -> dict | None:
        """Get the most recent log entry."""
        return self._entries[-1] if self._entries else None

    @property
    def has_errors(self) -> bool:
        """Check if any log entry has an error status."""
        return any(e["status"] == "error" for e in self._entries)

    def to_html(self) -> str:
        """Render the execution log as styled HTML for Streamlit."""
        if self.is_empty:
            return ""

        html = '<div class="log-container">'
        for entry in self._entries:
            status_cls = f"log-{entry['status']}"
            status_icon = {
                "working": "⏳",
                "success": "✅",
                "error": "❌",
            }.get(entry["status"], "•")

            html += (
                f'<div class="log-entry">'
                f'  <span class="log-time">{entry["time"]}</span>'
                f'  <span class="log-tool">{entry["tool"]}</span>'
                f'  <span class="log-msg {status_cls}">{status_icon} {entry["message"]}</span>'
                f'</div>'
            )
        html += '</div>'
        return html

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"ExecutionLog(entries={len(self._entries)})"


# ═════════════════════════════════════════════════════════
#  MODULE-LEVEL LOGGER INSTANCE
# ═════════════════════════════════════════════════════════
# Use this throughout the application:
#   from logger import log
#   log.info("Something happened")
log = setup_logger()
