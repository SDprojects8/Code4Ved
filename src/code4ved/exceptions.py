"""Custom exceptions for Code4Ved Automation."""


class Code4VedError(Exception):
    """Base exception for Code4Ved Automation."""

    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code


class Code4VedConfigError(Code4VedError):
    """Raised when there's a configuration error."""
    pass


class Code4VedValidationError(Code4VedError):
    """Raised when validation fails."""
    pass


class Code4VedConnectionError(Code4VedError):
    """Raised when connection to external service fails."""
    pass


class Code4VedTimeoutError(Code4VedError):
    """Raised when an operation times out."""
    pass


class Code4VedAuthenticationError(Code4VedError):
    """Raised when authentication fails."""
    pass


class Code4VedAuthorizationError(Code4VedError):
    """Raised when authorization fails."""
    pass


class Code4VedResourceNotFoundError(Code4VedError):
    """Raised when a requested resource is not found."""
    pass


class Code4VedResourceExistsError(Code4VedError):
    """Raised when trying to create a resource that already exists."""
    pass