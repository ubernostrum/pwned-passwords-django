"""
Exception classes used in pwned-passwords-django.

"""

import enum


class ErrorCode(str, enum.Enum):
    """
    Enum of possible error code values for :exc:`PwnedPasswordsError`.

    """

    API_TIMEOUT = "api_timeout"
    HTTP_ERROR = "http_error"
    REQUEST_ERROR = "request_error"
    UNKNOWN_ERROR = "unknown_error"


class PwnedPasswordsError(Exception):
    """
    Wrapper for all exceptions raised in communicating with Pwned Passwords.

    """

    def __init__(self, message: str, code: ErrorCode, params: dict) -> None:
        super().__init__(message, code, params)
        self.message = message
        self.code = code
        self.params = params
