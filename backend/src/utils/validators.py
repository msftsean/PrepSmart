"""Validation utilities for PrepSmart."""

import re
from typing import Optional


def validate_zip_code(zip_code: str) -> bool:
    """
    Validate US ZIP code format.

    Args:
        zip_code: ZIP code string to validate

    Returns:
        True if valid 5-digit ZIP code
    """
    return bool(re.match(r"^\d{5}$", zip_code))


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input string.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    # Remove leading/trailing whitespace
    text = text.strip()

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text
