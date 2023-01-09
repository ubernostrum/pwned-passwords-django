"""
Direct access to the Pwned Passwords API for checking whether a
password is compromised.

"""
import hashlib
import logging
import sys
import typing

import httpx
from django.conf import settings
from django.views.decorators.debug import sensitive_variables

from . import __version__, exceptions

logger = logging.getLogger(__name__)

DEFAULT_REQUEST_TIMEOUT: float = 1.0  # 1 second


class PwnedPasswords:
    """
    A client for interacting with the Pwned Passwords API.

    There are two useful public methods here: ``check_password()`` and
    ``check_password_async()``, which are identical to and called by
    :func:`~pwned_passwords_django.api.check_password` and
    :func:`~pwned_passwords_django.api.check_password_async` functions exposed at the
    module level.

    Constructor arguments are all optional; use them only if you want to pass in your
    own custom sync or async HTTP clients (which must be API-compatible with the
    corresponding sync and async client objects in `the HTTPX library
    <https://www.python-httpx.org>`_). Otherwise, default client objects from ``httpx``
    will be used.

    .. warning:: **Error handling and custom HTTP clients**

       This class will catch exceptions raised during the HTTP request/response cycle
       with Pwned Passwords, and wrap them in
       :exc:`~pwned_passwords_django.exceptions.PwnedPasswordsError`. When using the
       default ``httpx`` client, this class is able to distinguish several different
       types of errors -- timeouts, responses with error status codes, and so on -- and
       include that information in both log messages and in the ``PwnedPasswordsError``
       instance.

       When using a client other than ``httpx``, this class is not able to provide the
       same level of fine-grained error processing; the original exception from the HTTP
       client library will still be wrapped, and will still be accessible to
       programmatic inspection, but it will be your responsibility to perform that
       inspection. If you want to use a non-default HTTP client library and also
       preserve the finer-grained error processing in this class, you will need to
       subclass and override its :meth:`check_password` and/or
       :meth:`check_password_async` methods to add your own error-handling blocks which
       catch/inspect the exceptions raised by your preferred client library.

    :param client: A synchronous HTTP client object. Defaults to an ``httpx.Client``.
    :param async_client: An asynchronous HTTP client object. Defaults to an
       ``httpx.AsyncClient``.

    """

    api_endpoint: str = "https://api.pwnedpasswords.com/range/"

    user_agent: str = (
        f"pwned-passwords-django/{__version__} "
        f"(Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} "
        f"| httpx/{httpx.__version__})"
    )

    # pylint: disable=redefined-outer-name
    def __init__(
        self,
        client: typing.Optional[httpx.Client] = None,
        async_client: typing.Optional[httpx.AsyncClient] = None,
    ):
        settings_dict = getattr(settings, "PWNED_PASSWORDS", {})
        self.request_timeout = httpx.Timeout(
            settings_dict.get("API_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
        )
        self.add_padding = settings_dict.get("ADD_PADDING", True)
        self.client = client or httpx.Client()
        self.async_client = async_client or httpx.AsyncClient()

    def _prepare_password(self, password: str) -> typing.Tuple[str, str]:
        """
        Given a password, compute and return a tuple of the hash prefix and suffix
        used by the Pwned Passwords API.

        """
        password_hash = (
            hashlib.new("sha1", password.encode("utf-8"), usedforsecurity=False)
            .hexdigest()
            .upper()
        )
        return password_hash[:5], password_hash[5:]

    def _get_hits(self, response_text: str, suffix: str) -> int:
        """
        Given a resposne from Pwned Passwords and a password hash suffix, return the
        count of hits for that suffix in the response.

        """
        hits = {}
        for line in response_text.splitlines():
            line_suffix, _, count = line.partition(":")
            # Pwned Passwords has sometimes been known to return values with commas in
            # them, like "1,234" instead of "1234". So to be safe, we remove them before
            # trying to parse as int.
            hits[line_suffix] = int(count.replace(",", ""))
        return hits.get(suffix, 0)

    def _request(self, prefix: str) -> httpx.Response:
        """
        Given a hash prefix, perform a request to Pwned Passwords and return the
        response.

        """
        headers = {"User-Agent": self.user_agent}
        if self.add_padding:
            headers["Add-Padding"] = "true"
        response = self.client.get(
            url=f"{self.api_endpoint}{prefix}",
            headers=headers,
            timeout=self.request_timeout,
        )
        response.raise_for_status()
        return response

    async def _request_async(self, prefix: str) -> httpx.Response:
        """
        Given a hash prefix, perform an asynchronous request to Pwned Passwords and
        return the response.

        """
        headers = {"User-Agent": self.user_agent}
        if self.add_padding:
            headers["Add-Padding"] = "true"
        response = await self.async_client.get(
            url=f"{self.api_endpoint}{prefix}",
            headers=headers,
            timeout=self.request_timeout,
        )
        response.raise_for_status()
        return response

    @sensitive_variables()
    def check_password(self, password: str) -> int:
        """
        Check a password against the Pwned Passwords API and return the count of
        times it appears in breaches in the Pwned Passwords database.

        :param password: The password to check.

        :raises TypeError: When the given password value is not a string.

        :raises exceptions.PwnedPasswordsError: When the Pwned Passwords API times out,
           returns an HTTP 4XX or 5XX status code, or when any other error occurs in
           contacting the Pwned Passwords API or checking the password.

        """
        if not isinstance(password, str):
            raise TypeError("Password to check must be a string.")
        try:
            prefix, suffix = self._prepare_password(password)
            response = self._request(prefix)
            return self._get_hits(response.text, suffix)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Pwned Passwords API replied with HTTP error status code "
                f"{exc.response.status_code}."
            )
            raise exceptions.PwnedPasswordsError(
                message="Pwned Passwords API replied with HTTP error status code.",
                code=exceptions.ErrorCode.HTTP_ERROR,
                params={"status_code": exc.response.status_code},
            ) from exc
        except httpx.TimeoutException as exc:
            logger.error("Pwned Passwords API timed out.")
            raise exceptions.PwnedPasswordsError(
                message="Pwned Passwords API timed out.",
                code=exceptions.ErrorCode.API_TIMEOUT,
                params={"timeout_threshold": self.request_timeout},
            ) from exc
        except httpx.RequestError as exc:
            logger.error(
                f"Error making request to Pwned Passwords: {exc.__class__.__name__}"
            )
            raise exceptions.PwnedPasswordsError(
                message="Error making request to Pwned Passwords.",
                code=exceptions.ErrorCode.REQUEST_ERROR,
                params={
                    "add_padding": self.add_padding,
                    "api_endpoint": self.api_endpoint,
                    "exception_class": exc.__class__.__name__,
                    "prefix": prefix,
                    "timeout": self.request_timeout,
                },
            ) from exc
        except Exception as exc:
            logger.error(
                f"Error attempting to check password: {exc.__class__.__name__}"
            )
            raise exceptions.PwnedPasswordsError(
                message="Error attepting to check password.",
                code=exceptions.ErrorCode.UNKNOWN_ERROR,
                params={
                    "exception_class": exc.__class__.__name__,
                },
            ) from exc

    @sensitive_variables()
    async def check_password_async(self, password: str) -> int:
        """
        Check a password against the Pwned Passwords API and return the count of
        times it appears in breaches in the Pwned Passwords database.

        This is an asynchronous version of :meth:`check_password`, and will use an
        asynchronous HTTP client to make the request to Pwned Passwords.

        :raises TypeError: When the given password value is not a string.

        :raises exceptions.PwnedPasswordsError: When the Pwned Passwords API times out,
           returns an HTTP 4XX or 5XX status code, or when any other error occurs in
           contacting the Pwned Passwords API or checking the password.

        """
        if not isinstance(password, str):
            raise TypeError("Password to check must be a string.")
        try:
            prefix, suffix = self._prepare_password(password)
            response = await self._request_async(prefix)
            return self._get_hits(response.text, suffix)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Pwned Passwords API replied with HTTP error status code "
                f"{exc.response.status_code}."
            )
            raise exceptions.PwnedPasswordsError(
                message="Pwned Passwords API replied with HTTP error status code.",
                code=exceptions.ErrorCode.HTTP_ERROR,
                params={"status_code": exc.response.status_code},
            ) from exc
        except httpx.TimeoutException as exc:
            logger.error("Pwned Passwords API timed out.")
            raise exceptions.PwnedPasswordsError(
                message="Pwned Passwords API timed out.",
                code=exceptions.ErrorCode.API_TIMEOUT,
                params={"timeout_threshold": self.request_timeout},
            ) from exc
        except httpx.RequestError as exc:
            logger.error(
                f"Error making request to Pwned Passwords: {exc.__class__.__name__}"
            )
            raise exceptions.PwnedPasswordsError(
                message="Error making request to Pwned Passwords.",
                code=exceptions.ErrorCode.REQUEST_ERROR,
                params={
                    "add_padding": self.add_padding,
                    "api_endpoint": self.api_endpoint,
                    "exception_class": exc.__class__.__name__,
                    "prefix": prefix,
                    "timeout": self.request_timeout,
                },
            ) from exc
        except Exception as exc:
            logger.error(
                f"Error attempting to check password: {exc.__class__.__name__}"
            )
            raise exceptions.PwnedPasswordsError(
                message="Error attepting to check password.",
                code=exceptions.ErrorCode.UNKNOWN_ERROR,
                params={
                    "exception_class": exc.__class__.__name__,
                },
            ) from exc


client = PwnedPasswords()
check_password = client.check_password
check_password_async = client.check_password_async
