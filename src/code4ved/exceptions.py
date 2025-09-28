"""Custom exceptions for LCM Automation."""


class LCMError(Exception):
    """Base exception for LCM Automation."""

    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code


class LCMConfigError(LCMError):
    """Raised when there's a configuration error."""
    pass


class LCMValidationError(LCMError):
    """Raised when validation fails."""
    pass


class LCMConnectionError(LCMError):
    """Raised when connection to external service fails."""
    pass


class LCMTimeoutError(LCMError):
    """Raised when an operation times out."""
    pass


class LCMAuthenticationError(LCMError):
    """Raised when authentication fails."""
    pass


class LCMAuthorizationError(LCMError):
    """Raised when authorization fails."""
    pass


class LCMResourceNotFoundError(LCMError):
    """Raised when a requested resource is not found."""
    pass


class LCMResourceExistsError(LCMError):
    """Raised when trying to create a resource that already exists."""
    pass