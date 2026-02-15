"""Custom exceptions for JIRA operations."""


class JiraError(Exception):
    """Base exception for JIRA operations.

    All JIRA-specific exceptions inherit from this class.
    """

    def __init__(self, message: str) -> None:
        """Initialize with error message.

        Args:
            message: Human-readable error description
        """
        self.message = message
        super().__init__(self.message)


class JiraApiError(JiraError):
    """JIRA API error with HTTP status code.

    Raised when JIRA REST API returns an error response.
    Includes status code for specific error handling.

    Attributes:
        status_code: HTTP status code (e.g., 404, 403, 500)
        message: Human-readable error description
    """

    def __init__(self, status_code: int, message: str) -> None:
        """Initialize with status code and message.

        Args:
            status_code: HTTP status code
            message: Human-readable error description
        """
        self.status_code = status_code
        super().__init__(message)


class JiraAuthError(JiraError):
    """Authentication or authorization failed.

    Raised when:
    - OAuth token is invalid or expired
    - User lacks permission for requested operation
    - HTTP 401 or 403 responses
    """

    pass


class JiraNotFoundError(JiraError):
    """Requested resource not found.

    Raised when:
    - Epic or story key doesn't exist
    - User doesn't have permission to view resource
    - HTTP 404 response
    """

    pass


class JiraRateLimitError(JiraError):
    """Rate limit exceeded.

    Raised when:
    - Server-side rate limit hit (HTTP 429)
    - Too many requests in short timespan

    Note: Client-side rate limiting should prevent this in normal operation.
    """

    pass
