"""
Tests for security utilities.
"""

import pytest
from datadog_platform.utils.security import (
    redact_sensitive_data,
    sanitize_url,
    sanitize_exception_message,
    create_audit_log_entry,
    mask_credentials,
    SecureString,
)


class TestRedactSensitiveData:
    """Tests for redact_sensitive_data function."""

    def test_redact_password_in_dict(self):
        """Test that password fields are redacted in dictionaries."""
        data = {"username": "admin", "password": "secret123", "host": "localhost"}
        result = redact_sensitive_data(data)
        
        assert result["username"] == "admin"
        assert result["password"] == "***REDACTED***"
        assert result["host"] == "localhost"

    def test_redact_nested_dict(self):
        """Test redaction in nested dictionaries."""
        data = {
            "db_config": {
                "host": "localhost",
                "password": "secret",
                "port": 5432,
            },
            "api_key": "abc123",
        }
        result = redact_sensitive_data(data)
        
        assert result["db_config"]["host"] == "localhost"
        assert result["db_config"]["password"] == "***REDACTED***"
        assert result["api_key"] == "***REDACTED***"

    def test_redact_list_of_dicts(self):
        """Test redaction in lists of dictionaries."""
        data = [
            {"name": "user1", "token": "token1"},
            {"name": "user2", "secret_key": "secret2"},
        ]
        result = redact_sensitive_data(data)
        
        assert result[0]["name"] == "user1"
        assert result[0]["token"] == "***REDACTED***"
        assert result[1]["secret_key"] == "***REDACTED***"

    def test_custom_redaction_text(self):
        """Test custom redaction text."""
        data = {"password": "secret"}
        result = redact_sensitive_data(data, redaction_text="[HIDDEN]")
        
        assert result["password"] == "[HIDDEN]"

    def test_case_insensitive_matching(self):
        """Test that field matching is case insensitive."""
        data = {"PASSWORD": "secret", "Secret_Key": "key123", "ApiKey": "xyz"}
        result = redact_sensitive_data(data)
        
        assert result["PASSWORD"] == "***REDACTED***"
        assert result["Secret_Key"] == "***REDACTED***"
        assert result["ApiKey"] == "***REDACTED***"


class TestSanitizeUrl:
    """Tests for sanitize_url function."""

    def test_sanitize_url_with_credentials(self):
        """Test URL sanitization removes credentials."""
        url = "mongodb://user:pass@localhost:27017/mydb"
        result = sanitize_url(url)
        
        assert "user" not in result
        assert "pass" not in result
        assert "localhost:27017" in result

    def test_sanitize_url_without_credentials(self):
        """Test URL without credentials remains unchanged."""
        url = "mongodb://localhost:27017/mydb"
        result = sanitize_url(url)
        
        assert result == url

    def test_sanitize_http_url_with_credentials(self):
        """Test HTTP URL with credentials."""
        url = "https://admin:secret@api.example.com/v1/data"
        result = sanitize_url(url)
        
        assert "admin" not in result
        assert "secret" not in result
        assert "api.example.com" in result

    def test_sanitize_non_url_string(self):
        """Test non-URL strings are returned as-is."""
        text = "This is not a URL"
        result = sanitize_url(text)
        
        assert result == text

    def test_sanitize_empty_string(self):
        """Test empty string handling."""
        result = sanitize_url("")
        assert result == ""


class TestSanitizeExceptionMessage:
    """Tests for sanitize_exception_message function."""

    def test_sanitize_exception_with_url(self):
        """Test exception message with embedded URL is sanitized."""
        exc = ValueError("Connection failed to mongodb://user:pass@localhost:27017")
        result = sanitize_exception_message(exc)
        
        assert "user" not in result
        assert "pass" not in result

    def test_sanitize_exception_with_token(self):
        """Test exception message with token-like strings."""
        exc = RuntimeError("Auth failed with token: AbCdEf1234567890123456789012")
        result = sanitize_exception_message(exc)
        
        # Long token should be redacted
        assert "AbCdEf1234567890123456789012" not in result
        assert "***REDACTED***" in result

    def test_sanitize_exception_plain_message(self):
        """Test plain exception message without sensitive data."""
        exc = ValueError("Invalid configuration")
        result = sanitize_exception_message(exc)
        
        assert result == "Invalid configuration"


class TestCreateAuditLogEntry:
    """Tests for create_audit_log_entry function."""

    def test_create_basic_audit_entry(self):
        """Test basic audit log entry creation."""
        entry = create_audit_log_entry(
            action="register",
            resource_type="connector",
            resource_name="my-connector",
        )
        
        assert entry["event_type"] == "audit"
        assert entry["action"] == "register"
        assert entry["resource_type"] == "connector"
        assert entry["resource_name"] == "my-connector"
        assert entry["outcome"] == "success"
        assert entry["actor"] == "system"

    def test_create_audit_entry_with_actor(self):
        """Test audit entry with specific actor."""
        entry = create_audit_log_entry(
            action="delete",
            resource_type="pipeline",
            resource_name="my-pipeline",
            actor="admin_user",
        )
        
        assert entry["actor"] == "admin_user"

    def test_create_audit_entry_with_metadata(self):
        """Test audit entry with metadata."""
        entry = create_audit_log_entry(
            action="update",
            resource_type="connector",
            resource_name="my-connector",
            metadata={"connector_type": "mongodb", "password": "secret"},
        )
        
        assert "metadata" in entry
        assert entry["metadata"]["connector_type"] == "mongodb"
        # Password should be redacted in metadata
        assert entry["metadata"]["password"] == "***REDACTED***"

    def test_create_audit_entry_failure(self):
        """Test audit entry for failure outcome."""
        entry = create_audit_log_entry(
            action="connect",
            resource_type="connector",
            resource_name="failing-connector",
            outcome="failure",
        )
        
        assert entry["outcome"] == "failure"


class TestMaskCredentials:
    """Tests for mask_credentials function."""

    def test_mask_credentials_dict(self):
        """Test masking credentials in configuration dict."""
        config = {
            "host": "localhost",
            "port": 5432,
            "username": "admin",
            "password": "secret",
            "ssl": True,
        }
        
        masked = mask_credentials(config)
        
        assert masked["host"] == "localhost"
        assert masked["port"] == 5432
        assert masked["username"] == "admin"
        assert masked["password"] == "***REDACTED***"
        assert masked["ssl"] is True
        
        # Original should not be modified
        assert config["password"] == "secret"


class TestSecureString:
    """Tests for SecureString class."""

    def test_secure_string_creation(self):
        """Test SecureString creation and value retrieval."""
        secure = SecureString("my-secret-value")
        
        assert secure.get_value() == "my-secret-value"

    def test_secure_string_str_redacted(self):
        """Test SecureString __str__ returns redacted value."""
        secure = SecureString("my-secret-value")
        
        assert str(secure) == "***REDACTED***"
        assert "my-secret-value" not in str(secure)

    def test_secure_string_repr_redacted(self):
        """Test SecureString __repr__ returns redacted value."""
        secure = SecureString("my-secret-value")
        
        assert "my-secret-value" not in repr(secure)
        assert "***REDACTED***" in repr(secure)

    def test_secure_string_custom_redaction(self):
        """Test SecureString with custom redaction text."""
        secure = SecureString("my-secret", redaction_text="[HIDDEN]")
        
        assert str(secure) == "[HIDDEN]"
        assert secure.get_value() == "my-secret"
