#!/usr/bin/env python3
"""
Centralized logging for Claude Code hooks.

All hooks should import and use this module for consistent logging.
Provides:
- Daily log files (hooks-YYYY-MM-DD.log)
- Automatic cleanup of logs older than 7 days
- Structured JSON logging for easy parsing
- Timing utilities for performance tracking
- Minimal stderr output for verbose mode visibility

Usage:
    from hook_logger import setup_logger, log_hook_execution
    import time

    logger = setup_logger("my-hook")
    start = time.time()

    try:
        # ... hook logic ...
        log_hook_execution(logger, "PostToolUse", tool="Edit",
                          duration=time.time()-start, status="success")
    except Exception as e:
        log_hook_execution(logger, "PostToolUse", tool="Edit",
                          duration=time.time()-start, status="error",
                          details={"error": str(e)})
        raise

Log location: .claude/hooks/logs/hooks-YYYY-MM-DD.log
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Log file configuration
LOG_DIR = Path(__file__).parent / "logs"
LOG_RETENTION_DAYS = 7  # Keep logs for 7 days

# Track initialized loggers to prevent duplicate handlers
# Key: (hook_name, date_str) to detect date changes
_initialized_loggers: dict[str, str] = {}


def _get_log_file_for_today() -> Path:
    """Get the log file path for today's date."""
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"hooks-{today}.log"


def _cleanup_old_logs():
    """Remove log files older than LOG_RETENTION_DAYS."""
    if not LOG_DIR.exists():
        return

    cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)

    for log_file in LOG_DIR.glob("hooks-*.log"):
        # Extract date from filename (hooks-YYYY-MM-DD.log)
        try:
            date_str = log_file.stem.replace("hooks-", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                log_file.unlink()
        except (ValueError, OSError):
            # Skip files that don't match pattern or can't be deleted
            pass


def setup_logger(hook_name: str) -> logging.Logger:
    """
    Set up a logger for a specific hook.

    Creates a new log file for each day (hooks-YYYY-MM-DD.log).
    Automatically cleans up logs older than LOG_RETENTION_DAYS.

    Args:
        hook_name: Name of the hook (used as logger name)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(hook_name)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = _get_log_file_for_today()

    # Check if we already initialized this logger for today
    if hook_name in _initialized_loggers and _initialized_loggers[hook_name] == today:
        return logger

    # If date changed, remove old file handlers
    if hook_name in _initialized_loggers:
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)

    # Create logs directory if needed
    LOG_DIR.mkdir(exist_ok=True)

    # Clean up old logs (only on first logger setup per session)
    if not _initialized_loggers:
        _cleanup_old_logs()

    # File handler - daily log file
    try:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # Format: timestamp | hook_name | level | message
        fmt = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as e:
        # If we can't create the file handler, log to stderr
        sys.stderr.write(f"[hook_logger] Could not create log file: {e}\n")

    # Stderr handler - only warnings and above for visibility in verbose mode
    # Only add if not already present
    has_stderr_handler = any(
        isinstance(h, logging.StreamHandler) and h.stream == sys.stderr
        for h in logger.handlers
    )
    if not has_stderr_handler:
        sh = logging.StreamHandler(sys.stderr)
        sh.setLevel(logging.WARNING)
        sh.setFormatter(logging.Formatter('%(name)s | %(levelname)s | %(message)s'))
        logger.addHandler(sh)

    _initialized_loggers[hook_name] = today
    return logger


def log_hook_execution(
    logger: logging.Logger,
    event_type: str,
    tool: Optional[str] = None,
    duration: Optional[float] = None,
    status: str = "success",
    details: Optional[dict] = None
):
    """
    Log a hook execution with structured data.

    Args:
        logger: Logger instance from setup_logger()
        event_type: Hook event type (SessionStart, PreToolUse, PostToolUse, etc.)
        tool: Tool name if applicable (Write, Edit, etc.)
        duration: Execution duration in seconds
        status: "success", "warning", or "error"
        details: Additional context (file paths, error messages, etc.)
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "tool": tool,
        "duration_ms": round(duration * 1000) if duration is not None else None,
        "status": status
    }

    if details:
        entry["details"] = details

    # Serialize to JSON for structured logging
    message = json.dumps(entry, ensure_ascii=False)

    if status == "error":
        logger.error(message)
    elif status == "warning":
        logger.warning(message)
    else:
        logger.info(message)


def log_debug(logger: logging.Logger, message: str, **kwargs):
    """Log a debug message with optional context."""
    if kwargs:
        message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
    logger.debug(message)


def log_info(logger: logging.Logger, message: str, **kwargs):
    """Log an info message with optional context."""
    if kwargs:
        message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
    logger.info(message)


def log_warning(logger: logging.Logger, message: str, **kwargs):
    """Log a warning message with optional context."""
    if kwargs:
        message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
    logger.warning(message)


def log_error(logger: logging.Logger, message: str, **kwargs):
    """Log an error message with optional context."""
    if kwargs:
        message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
    logger.error(message)


# Convenience function for simple use cases
def quick_log(hook_name: str, message: str, level: str = "info"):
    """
    Quick one-liner logging without full setup.

    Use for simple debug/info messages. For structured execution logging,
    use setup_logger() + log_hook_execution().
    """
    logger = setup_logger(hook_name)
    getattr(logger, level, logger.info)(message)
