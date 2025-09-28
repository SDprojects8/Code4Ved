"""Helper utility functions."""

import uuid
from datetime import datetime
from typing import Optional


def generate_id(prefix: Optional[str] = None) -> str:
    """Generate a unique identifier.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique identifier string
    """
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}-{unique_id}" if prefix else unique_id


def format_datetime(dt: datetime, include_time: bool = True) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime to format
        include_time: Whether to include time component

    Returns:
        Formatted datetime string
    """
    if include_time:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return dt.strftime("%Y-%m-%d")