"""
Unit tests for validators module.

Tests input validation and sanitization functions.
"""

import pytest
from backend.utils.validators import (
    validate_github_url,
    validate_api_key,
    sanitize_string,
    validate_report_id,
    validate_pagination_params
)
from backend.utils.exceptions import ValidationError


class TestGitHubURLValidation:
    """Tests for GitHub URL validation."""
    
    def test_valid_https_url(self):
        """Test valid HTTPS GitHub URL."""
        url = "https://github.com/owner/repo"
        result = validate_github_url(url)
        assert result == url
    
    def test_valid_http_url(self):
        """Test valid HTTP GitHub URL."""
        url = "http://github.com/owner/repo"
        result = validate_github_url(url)
        assert result == "https://github.com/owner/repo"
    
    def test_url_with_trailing_slash(self):
        """Test URL with trailing slash is normalized."""
        url = "https://github.com/owner/repo/"
        result = validate_github_url(url)
        assert result == "https://github.com/owner/repo"
    
    def test_url_with_git_extension(self):
        """Test URL with .git extension is normalized."""
        url = "https://github.com/owner/repo.git"
        result = validate_github_url(url)
        assert result == "https://github.com/owner/repo"
    
    def test_url_with_www(self):
        """Test URL with www subdomain."""
        url = "https://www.github.com/owner/repo"
        result = validate_github_url(url)
        assert result == "https://github.com/owner/repo"
    
    def test_empty_url(self):
        """Test empty URL raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("")
        assert "required" in str(exc_info.value).lower()
    
    def test_non_github_domain(self):
        """Test non-GitHub domain raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://gitlab.com/owner/repo")
        assert "github" in str(exc_info.value).lower()
    
    def test_missing_repo_name(self):
        """Test URL missing repository name."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/owner")
        assert "owner and repository" in str(exc_info.value).lower()
    
    def test_invalid_owner_name(self):
        """Test invalid owner name characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/invalid@owner/repo")
        assert "owner" in str(exc_info.value).lower()
    
    def test_invalid_repo_name(self):
        """Test invalid repository name characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/owner/invalid@repo")
        assert "repository" in str(exc_info.value).lower()


class TestAPIKeyValidation:
    """Tests for API key validation."""
    
    def test_valid_api_key(self):
        """Test valid API key."""
        api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        validate_api_key(api_key, "TestService")
        # Should not raise
    
    def test_empty_api_key(self):
        """Test empty API key raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_api_key("", "TestService")
        assert "not configured" in str(exc_info.value).lower()
    
    def test_none_api_key(self):
        """Test None API key raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_api_key(None, "TestService")
        assert "not configured" in str(exc_info.value).lower()
    
    def test_short_api_key(self):
        """Test API key that is too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_api_key("short", "TestService")
        assert "too short" in str(exc_info.value).lower()


class TestStringSanitization:
    """Tests for string sanitization."""
    
    def test_normal_string(self):
        """Test normal string passes through."""
        text = "Hello, World!"
        result = sanitize_string(text)
        assert result == text
    
    def test_string_with_newlines(self):
        """Test string with newlines is preserved."""
        text = "Line 1\nLine 2\nLine 3"
        result = sanitize_string(text)
        assert result == text
    
    def test_string_truncation(self):
        """Test long string is truncated."""
        text = "a" * 2000
        result = sanitize_string(text, max_length=100)
        assert len(result) == 100
    
    def test_string_with_null_bytes(self):
        """Test null bytes are removed."""
        text = "Hello\x00World"
        result = sanitize_string(text)
        assert "\x00" not in result
    
    def test_string_with_control_chars(self):
        """Test control characters are removed."""
        text = "Hello\x01\x02World"
        result = sanitize_string(text)
        # Control chars should be removed
        assert len(result) < len(text)


class TestReportIDValidation:
    """Tests for report ID validation."""
    
    def test_valid_integer(self):
        """Test valid integer ID."""
        result = validate_report_id(123)
        assert result == 123
    
    def test_valid_string_integer(self):
        """Test valid string that can be converted to integer."""
        result = validate_report_id("456")
        assert result == 456
    
    def test_zero_id(self):
        """Test zero ID raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_report_id(0)
        assert "positive" in str(exc_info.value).lower()
    
    def test_negative_id(self):
        """Test negative ID raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_report_id(-1)
        assert "positive" in str(exc_info.value).lower()
    
    def test_non_integer_string(self):
        """Test non-integer string raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_report_id("abc")
        assert "integer" in str(exc_info.value).lower()


class TestPaginationValidation:
    """Tests for pagination parameter validation."""
    
    def test_default_values(self):
        """Test default pagination values."""
        limit, offset = validate_pagination_params()
        assert limit == 20
        assert offset == 0
    
    def test_valid_params(self):
        """Test valid pagination parameters."""
        limit, offset = validate_pagination_params(10, 5)
        assert limit == 10
        assert offset == 5
    
    def test_max_limit_exceeded(self):
        """Test limit exceeding maximum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination_params(limit=200)
        assert "cannot exceed" in str(exc_info.value).lower()
    
    def test_negative_limit(self):
        """Test negative limit raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination_params(limit=-1)
        assert "at least 1" in str(exc_info.value).lower()
    
    def test_negative_offset(self):
        """Test negative offset raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination_params(offset=-1)
        assert "non-negative" in str(exc_info.value).lower()
