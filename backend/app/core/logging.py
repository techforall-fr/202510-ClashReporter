"""Structured logging configuration."""
import logging
import sys
from typing import Any

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask sensitive values for logging."""
    if not value or len(value) <= show_chars:
        return "***"
    return f"{value[:show_chars]}{'*' * (len(value) - show_chars)}"


def log_api_call(logger: logging.Logger, method: str, url: str, **kwargs: Any) -> None:
    """Log API call details safely."""
    safe_kwargs = {k: v for k, v in kwargs.items() if k not in ["authorization", "token"]}
    logger.info(f"API Call: {method} {url}", extra=safe_kwargs)
