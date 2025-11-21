"""
Custom exception hierarchy for DevPulse.

Provides structured error handling with proper error codes,
user-friendly messages, and detailed context.
"""

from typing import Any, Dict, Optional


class DevPulseError(Exception):
    """Base exception for all DevPulse errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        """
        Initialize DevPulse error.
        
        Args:
            message: User-friendly error message
            error_code: Machine-readable error code
            details: Additional error context
            status_code: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "message": self.message,
                "code": self.error_code,
                "details": self.details
            }
        }


class ValidationError(DevPulseError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if field:
            details['field'] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=400
        )


class RepositoryError(DevPulseError):
    """Raised when repository operations fail."""
    
    def __init__(self, message: str, repo_url: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if repo_url:
            details['repo_url'] = repo_url
        super().__init__(
            message=message,
            error_code="REPOSITORY_ERROR",
            details=details,
            status_code=400
        )


class AnalysisError(DevPulseError):
    """Raised when code analysis fails."""
    
    def __init__(self, message: str, tool: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if tool:
            details['tool'] = tool
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details=details,
            status_code=500
        )


class AIServiceError(DevPulseError):
    """Raised when AI service calls fail."""
    
    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if service:
            details['service'] = service
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            details=details,
            status_code=503
        )


class DatabaseError(DevPulseError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if operation:
            details['operation'] = operation
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            status_code=500
        )


class ConfigurationError(DevPulseError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if config_key:
            details['config_key'] = config_key
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            status_code=500
        )


class RateLimitError(DevPulseError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        details = kwargs.pop('details', {})
        if retry_after:
            details['retry_after_seconds'] = retry_after
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            status_code=429
        )


class TimeoutError(DevPulseError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        details = kwargs.pop('details', {})
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            details=details,
            status_code=504
        )
