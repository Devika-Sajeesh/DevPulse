"""
Input validation and sanitization utilities for DevPulse.

Provides comprehensive validation for URLs, configurations,
and user inputs with security best practices.
"""

import re
from typing import Optional, Any
from urllib.parse import urlparse
from backend.utils.exceptions import ValidationError


def validate_github_url(url: str, allow_private: bool = False) -> str:
    """
    Validate and sanitize GitHub repository URL.
    
    Args:
        url: GitHub repository URL
        allow_private: Whether to allow private repository URLs
    
    Returns:
        Sanitized URL
    
    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("Repository URL is required", field="repo_url")
    
    url = url.strip()
    
    # Remove trailing slashes and .git extension
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(
            f"Invalid URL format: {str(e)}",
            field="repo_url"
        )
    
    # Validate scheme
    if parsed.scheme not in ['http', 'https', '']:
        raise ValidationError(
            "URL must use HTTP or HTTPS protocol",
            field="repo_url",
            details={"provided_scheme": parsed.scheme}
        )
    
    # Validate domain
    if parsed.netloc and parsed.netloc not in ['github.com', 'www.github.com']:
        raise ValidationError(
            "Only GitHub repositories are supported",
            field="repo_url",
            details={"provided_domain": parsed.netloc}
        )
    
    # Extract owner and repo from path
    path_parts = [p for p in parsed.path.split('/') if p]
    
    if len(path_parts) < 2:
        raise ValidationError(
            "URL must include owner and repository name (e.g., github.com/owner/repo)",
            field="repo_url"
        )
    
    owner, repo = path_parts[0], path_parts[1]
    
    # Validate owner and repo names (GitHub naming rules)
    github_name_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-_]*[a-zA-Z0-9])?$'
    
    if not re.match(github_name_pattern, owner):
        raise ValidationError(
            f"Invalid repository owner name: {owner}",
            field="repo_url",
            details={"owner": owner}
        )
    
    if not re.match(github_name_pattern, repo):
        raise ValidationError(
            f"Invalid repository name: {repo}",
            field="repo_url",
            details={"repo": repo}
        )
    
    # Construct clean URL
    clean_url = f"https://github.com/{owner}/{repo}"
    
    return clean_url


def validate_api_key(api_key: Optional[str], service_name: str) -> None:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        service_name: Name of the service (for error messages)
    
    Raises:
        ValidationError: If API key is invalid
    """
    if not api_key:
        raise ValidationError(
            f"{service_name} API key is not configured",
            field="api_key",
            details={"service": service_name}
        )
    
    if not isinstance(api_key, str):
        raise ValidationError(
            f"Invalid {service_name} API key format",
            field="api_key"
        )
    
    # Basic length check (most API keys are at least 20 chars)
    if len(api_key.strip()) < 20:
        raise ValidationError(
            f"{service_name} API key appears to be invalid (too short)",
            field="api_key",
            details={"service": service_name}
        )


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing potentially dangerous characters.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    
    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(value, str):
        raise ValidationError("Input must be a string")
    
    # Truncate to max length
    value = value[:max_length]
    
    # Remove null bytes and control characters
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    return value.strip()


def validate_report_id(report_id: Any) -> int:
    """
    Validate report ID.
    
    Args:
        report_id: Report ID to validate
    
    Returns:
        Validated integer report ID
    
    Raises:
        ValidationError: If report ID is invalid
    """
    try:
        report_id = int(report_id)
    except (ValueError, TypeError):
        raise ValidationError(
            "Report ID must be an integer",
            field="report_id"
        )
    
    if report_id < 1:
        raise ValidationError(
            "Report ID must be a positive integer",
            field="report_id",
            details={"provided_id": report_id}
        )
    
    return report_id


def validate_pagination_params(limit: Optional[int] = None, offset: Optional[int] = None) -> tuple[int, int]:
    """
    Validate pagination parameters.
    
    Args:
        limit: Number of items to return
        offset: Number of items to skip
    
    Returns:
        Tuple of (validated_limit, validated_offset)
    
    Raises:
        ValidationError: If parameters are invalid
    """
    # Default values
    default_limit = 20
    max_limit = 100
    
    # Validate limit
    if limit is None:
        limit = default_limit
    else:
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            raise ValidationError(
                "Limit must be an integer",
                field="limit"
            )
        
        if limit < 1:
            raise ValidationError(
                "Limit must be at least 1",
                field="limit"
            )
        
        if limit > max_limit:
            raise ValidationError(
                f"Limit cannot exceed {max_limit}",
                field="limit",
                details={"max_limit": max_limit}
            )
    
    # Validate offset
    if offset is None:
        offset = 0
    else:
        try:
            offset = int(offset)
        except (ValueError, TypeError):
            raise ValidationError(
                "Offset must be an integer",
                field="offset"
            )
        
        if offset < 0:
            raise ValidationError(
                "Offset must be non-negative",
                field="offset"
            )
    
    return limit, offset
