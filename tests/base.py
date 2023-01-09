"""
Base test-case class for pwned-passwords-django.

"""
import typing
from unittest import mock

try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock

import httpx
from django.test import TestCase

from pwned_passwords_django import api, exceptions


class PwnedPasswordsTests(TestCase):
    """
    Base test-case class defining common attributes and methods.

    """

    sample_password = "swordfish"  # nosec: B105
    sample_password_prefix = "4F571"  # nosec: B105
    sample_password_suffix = "81DCAADE980555F2CE6755CA425F00658BE"  # nosec: B105

    def api_mocks(
        self, count: int = 10
    ) -> typing.Tuple[
        typing.Callable[[str], int], typing.Callable[[str], typing.Awaitable[int]]
    ]:
        """
        Return test mocks for ``pwned_passwords_django.api.check_password()`` and
        ``pwned_passwords_django.api.check_password_async()`` which will return
        ``count`` when called.

        """
        return mock.Mock(return_value=count), AsyncMock(return_value=count)

    def api_error_mocks(
        self,
        message: str = "Error",
        code: exceptions.ErrorCode = exceptions.ErrorCode.UNKNOWN_ERROR,
        params: typing.Optional[dict] = None,
    ) -> typing.Tuple[
        typing.Callable[[str], int], typing.Callable[[str], typing.Awaitable[int]]
    ]:
        """
        Return test mocks for ``pwned_passwords_django.api.check_password()`` and
        ``pwned_passwords_django.api.check_password_async()`` which will raise a
        PwnedPasswordsError when called. Pass ``message``, ``code``, or ``params`` to
        control the attributes of the exception.

        """
        params = params or {}
        sync_mock = mock.Mock(
            side_effect=exceptions.PwnedPasswordsError(
                message=message, code=code, params=params
            )
        )
        async_mock = AsyncMock(
            side_effect=exceptions.PwnedPasswordsError(
                message=message, code=code, params=params
            )
        )
        return sync_mock, async_mock

    def http_client(
        self,
        suffix: typing.Optional[str] = None,
        count: int = 10,
        status_code: int = 200,
        is_async: bool = False,
    ) -> mock.Mock:
        """
        Return an HTTP client for use in testing.

        The client's ``get()`` method will return an httpx.Response in Pwned Passwords'
        format, with the given hash suffix and breach count.

        Pass ``status_code`` to have the ``get()`` response return that HTTP status
        code.

        Pass ``is_async=True`` to return an async client; otherwise, the client will be
        synchronous.

        """
        if suffix is None:
            suffix = self.sample_password_suffix
        response = httpx.Response(
            request=httpx.Request(
                "GET",
                f"{api.PwnedPasswords.api_endpoint}/{self.sample_password_prefix}",
            ),
            status_code=status_code,
            content=f"{suffix}:{count}",
        )
        mock_class = mock.Mock if not is_async else AsyncMock
        spec_class = httpx.Client if not is_async else httpx.AsyncClient
        return mock_class(spec_set=spec_class, get=mock_class(return_value=response))

    def custom_response_client(
        self, response_text: str, is_async: bool = False
    ) -> mock.Mock:
        """
        Return an HTTP client that produces a fixed response, for use in testing.

        The client's ``get()`` method will always return a response with a status of 200
        and response body of ``response_text``.

        Pass ``is_async=True`` to return an async client; otherwise, the client will be
        synchronous.

        """
        response = httpx.Response(
            request=httpx.Request(
                "GET",
                f"{api.PwnedPasswords.api_endpoint}/{self.sample_password_prefix}",
            ),
            status_code=200,
            content=response_text,
        )
        mock_class = mock.Mock if not is_async else AsyncMock
        spec_class = httpx.Client if not is_async else httpx.AsyncClient
        return mock_class(spec_set=spec_class, get=mock_class(return_value=response))

    def exception_client(
        self,
        exception_class: Exception,
        message: typing.Optional[str] = None,
        is_async: bool = False,
    ) -> mock.Mock:
        """
        Return an HTTP client that always errors, for use in testing.

        The client's ``get()`` method will raise the given ``exception_class``,
        optionally with the given ``message``.

        Pass ``is_async=True`` to return an async client; otherwise, the client will be
        synchronous.

        """
        if message is None:
            error = exception_class()
        else:
            error = exception_class(message)
        mock_class = mock.Mock if not is_async else AsyncMock
        spec_class = httpx.Client if not is_async else httpx.AsyncClient
        return mock_class(spec_set=spec_class, get=mock_class(side_effect=error))
