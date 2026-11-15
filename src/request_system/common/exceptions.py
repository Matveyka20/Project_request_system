"""Standardized exception hierarchy for the Request System."""


class ApplicationError(Exception):
    """Base exception for application-level errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(message)

    def to_dict(self) -> dict[str, str]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
        }


class ValidationError(ApplicationError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        details: dict[str, str] | None = None,
        error_code: str = "VALIDATION_ERROR",
    ) -> None:
        self.details = details or {}
        super().__init__(message, error_code)

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.details:
            result["details"] = self.details
        return result


class NotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""

    def __init__(
        self, resource_type: str, resource_id: str | int,
        error_code: str = "NOT_FOUND",
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with ID {resource_id} not found."
        super().__init__(message, error_code)


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed.",
        error_code: str = "AUTHENTICATION_ERROR",
    ) -> None:
        super().__init__(message, error_code)


class AuthorizationError(ApplicationError):
    """Raised when user lacks required permissions."""

    def __init__(
        self,
        message: str = "Insufficient permissions.",
        error_code: str = "AUTHORIZATION_ERROR",
    ) -> None:
        super().__init__(message, error_code)


class ConflictError(ApplicationError):
    """Raised when operation conflicts with current state."""

    def __init__(
        self,
        message: str,
        error_code: str = "CONFLICT",
    ) -> None:
        super().__init__(message, error_code)


class OperationNotAllowedError(ApplicationError):
    """Raised when operation cannot be performed in current state."""

    def __init__(
        self,
        operation: str,
        current_state: str,
        error_code: str = "OPERATION_NOT_ALLOWED",
    ) -> None:
        message = f"Cannot {operation} in state: {current_state}"
        super().__init__(message, error_code)
        self.operation = operation
        self.current_state = current_state
