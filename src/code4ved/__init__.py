"""Code4Ved Automation Package.

A comprehensive Life Cycle Management automation toolkit.
"""

__version__ = "0.1.0"
__author__ = "Code4Ved Team"
__email__ = "team@Code4Ved.com"

from .core import Code4VedManager
from .exceptions import Code4VedError, Code4VedConfigError, Code4VedValidationError

__all__ = [
    "Code4VedManager",
    "Code4VedError",
    "Code4VedConfigError",
    "Code4VedValidationError",
]