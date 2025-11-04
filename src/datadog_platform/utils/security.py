"""
Security utilities for the DataDog platform.

Provides credential sanitization, secure logging, and data protection
utilities to prevent accidental exposure of sensitive information.
"""

import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse, urlunparse

# Sensitive field names that should be redacted in logs
SENSITIVE_FIELDS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "secret_key",
    "private_key",
    "auth",
    "authorization",
    "credential",
    "credentials",
    "session_token",
    "sasl_password",
    "account_key",
    "sas_token",
    "connection_string",
}


def redact_sensitive_data(data: Any, redaction_text: str = "***REDACTED***") -> Any:
    """
    Recursively redact sensitive data in dictionaries, lists, and strings.

    Args:
        data: Data structure to redact
        redaction_text: Text to use for redacted values

    Returns:
        Redacted copy of the data
    """
    if isinstance(data, dict):
        return {
            key: (
                redaction_text
                if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS)
                else redact_sensitive_data(value, redaction_text)
            )
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [redact_sensitive_data(item, redaction_text) for item in data]
    elif isinstance(data, str):
        # Redact potential credentials in URLs
        return sanitize_url(data, redaction_text)
    else:
        return data


def sanitize_url(url: str, redaction_text: str = "***REDACTED***") -> str:
    """
    Remove credentials from URLs for safe logging.

    Args:
        url: URL string that may contain credentials
        redaction_text: Text to replace credentials with

    Returns:
        Sanitized URL string
    """
    if not url or "://" not in url:
        return url

    try:
        parsed = urlparse(url)

        # Redact username and password in netloc
        if parsed.username or parsed.password:
            # Replace credentials in netloc
            netloc = parsed.hostname or ""
            if parsed.port:
                netloc = f"{netloc}:{parsed.port}"

            # Reconstruct URL without credentials
            sanitized = parsed._replace(netloc=netloc)
            return urlunparse(sanitized)

        return url
    except Exception:
        # If parsing fails, return as-is (better than crashing)
        return url


def sanitize_exception_message(exception: Exception, redaction_text: str = "***REDACTED***") -> str:
    """
    Sanitize exception message to remove potential sensitive data.

    Args:
        exception: Exception to sanitize
        redaction_text: Text to replace sensitive data with

    Returns:
        Sanitized exception message
    """
    message = str(exception)

    # Remove URLs with credentials
    url_pattern = r"(\w+://)[^:]+:[^@]+@"
    message = re.sub(url_pattern, r"\1" + redaction_text + "@", message)

    # Remove potential tokens and keys (sequences of alphanumeric chars >= 24 chars)
    token_pattern = r"\b[A-Za-z0-9_-]{24,}\b"
    message = re.sub(token_pattern, redaction_text, message)

    return message


def create_audit_log_entry(
    action: str,
    resource_type: str,
    resource_name: str,
    actor: Optional[str] = None,
    outcome: str = "success",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a structured audit log entry.

    Args:
        action: Action performed (e.g., "register", "unregister", "health_check")
        resource_type: Type of resource (e.g., "connector", "pipeline")
        resource_name: Name of the resource
        actor: Who performed the action (optional)
        outcome: Outcome of the action (success, failure, error)
        metadata: Additional metadata (will be sanitized)

    Returns:
        Structured audit log entry as dictionary
    """
    entry = {
        "event_type": "audit",
        "action": action,
        "resource_type": resource_type,
        "resource_name": resource_name,
        "outcome": outcome,
        "actor": actor or "system",
    }

    if metadata:
        # Sanitize metadata before adding
        entry["metadata"] = redact_sensitive_data(metadata)

    return entry


def mask_credentials(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a display-safe copy of a configuration with masked credentials.

    Args:
        config: Configuration dictionary

    Returns:
        Copy of config with sensitive values masked
    """
    return redact_sensitive_data(config.copy())


class SecureString:
    """
    A string wrapper that prevents accidental exposure in logs.

    When converted to string for logging, returns redacted value.
    """

    def __init__(self, value: str, redaction_text: str = "***REDACTED***"):
        """
        Initialize secure string.

        Args:
            value: The sensitive value
            redaction_text: Text to show when converted to string
        """
        self._value = value
        self._redaction_text = redaction_text

    def get_value(self) -> str:
        """Get the actual value (use with caution)."""
        return self._value

    def __str__(self) -> str:
        """Return redacted version for logging."""
        return self._redaction_text

    def __repr__(self) -> str:
        """Return redacted version for debugging."""
        return f"SecureString({self._redaction_text})"
