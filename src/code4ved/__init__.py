"""LCM Automation Package.

A comprehensive Life Cycle Management automation toolkit.
"""

__version__ = "0.1.0"
__author__ = "LCM Team"
__email__ = "team@lcm.com"

from .core import LCMManager
from .exceptions import LCMError, LCMConfigError, LCMValidationError

__all__ = [
    "LCMManager",
    "LCMError",
    "LCMConfigError",
    "LCMValidationError",
]