"""
Tests for direct interaction with the Pwned Passwords API.

"""

from unittest import mock

import httpx
from django.test import override_settings, tag

from pwned_passwords_django import api, exceptions

from . import base


# pylint: disable=too-many-public-methods
class PwnedPasswordsAPITests(base.PwnedPasswordsTests):
    """
    Test interaction with the Pwned Passwords API.

    """

    def test_unicode_requirement(self):
        """
        Calling the API requires a ``str`` object, not ``bytes``.

        """
        with self.assertRaises(TypeError):
            api.client.check_password(self.sample_password.encode("utf-8"))

    async def test_unicode_requirement_async(self):
        """
        Calling the async API requires a ``str`` object, not ``bytes``.

        """
        with self.assertRaises(TypeError):
            await api.client.check_password_async(self.sample_password.encode("utf-8"))

    def test_compromised(self):
        """
        Compromised passwords are detected correctly.

        """
        for count in range(1, 10):
            api_client = api.PwnedPasswords(client=self.http_client(count=count))
            result = api_client.check_password(self.sample_password)
            assert count == result

    async def test_compromised_async(self):
        """
        Compromised passwords are detected correctly in the async code path.

        """
        for count in range(1, 10):
            api_client = api.PwnedPasswords(
                async_client=self.http_client(count=count, is_async=True)
            )
            result = await api_client.check_password_async(self.sample_password)
            assert count == result

    def test_not_compromised(self):
        """
        Non-compromised passwords are detected correctly.

        """
        for suffix in (
            self.sample_password_suffix,
            self.sample_password_suffix.replace("A", "3"),
        ):
            api_client = api.PwnedPasswords(
                client=self.http_client(suffix=suffix, count=0)
            )
            result = api_client.check_password(self.sample_password)
            assert 0 == result

    async def test_not_compromised_async(self):
        """
        Non-compromised passwords are detected correctly in the async code path.

        """
        for suffix in (
            self.sample_password_suffix,
            self.sample_password_suffix.replace("A", "3"),
        ):
            api_client = api.PwnedPasswords(
                async_client=self.http_client(suffix=suffix, count=0, is_async=True)
            )
            result = await api_client.check_password_async(self.sample_password)
            assert 0 == result

    def test_empty_response(self):
        """
        An empty API response is handled correctly.

        """
        api_client = api.PwnedPasswords(
            client=self.custom_response_client(response_text="")
        )
        result = api_client.check_password(self.sample_password)
        assert 0 == result

    async def test_empty_response_async(self):
        """
        An empty API response is handled correctly in the async code path.

        """
        api_client = api.PwnedPasswords(
            async_client=self.custom_response_client(response_text="", is_async=True)
        )
        result = await api_client.check_password_async(self.sample_password)
        assert 0 == result

    def test_comma_response(self):
        """
        An API response where the count includes commas is handled correctly.

        Bug reports indicate the Pwned Passwords API has occasionally done this.

        """
        api_client = api.PwnedPasswords(
            client=self.custom_response_client(
                response_text=f"{self.sample_password_suffix}:1,234,567"
            )
        )
        result = api_client.check_password(self.sample_password)
        self.assertEqual(1234567, result)

    async def test_comma_response_async(self):
        """
        An API response where the count includes commas is handled correctly.

        Bug reports indicate the Pwned Passwords API has occasionally done this.

        """
        api_client = api.PwnedPasswords(
            async_client=self.custom_response_client(
                response_text=f"{self.sample_password_suffix}:1,234,567", is_async=True
            )
        )
        result = await api_client.check_password_async(self.sample_password)
        self.assertEqual(1234567, result)

    @override_settings(PWNED_PASSWORDS={"API_TIMEOUT": 0.5})
    def test_timeout_override(self):
        """
        The custom request timeout setting is honored.

        """
        client = self.http_client()
        api_client = api.PwnedPasswords(client=client)
        api_client.check_password(self.sample_password)
        client.get.assert_called_with(
            url=mock.ANY, headers=mock.ANY, timeout=httpx.Timeout(0.5)
        )

    @override_settings(PWNED_PASSWORDS={"API_TIMEOUT": 0.5})
    async def test_timeout_override_async(self):
        """
        The custom request timeout setting is honored in the async code path.

        """
        client = self.http_client(is_async=True)
        api_client = api.PwnedPasswords(async_client=client)
        await api_client.check_password_async(self.sample_password)
        client.get.assert_called_with(
            url=mock.ANY, headers=mock.ANY, timeout=httpx.Timeout(0.5)
        )

    def test_timeout(self):
        """
        Connection timeouts to the API are translated into a PwnedPasswordsError.

        """
        api_client = api.PwnedPasswords(
            client=self.exception_client(
                exception_class=httpx.ConnectTimeout, message="Timed out"
            )
        )
        try:
            api_client.check_password(self.sample_password)
        except exceptions.PwnedPasswordsError as exc:
            assert exc.code == exceptions.ErrorCode.API_TIMEOUT
        else:
            raise AssertionError()

    async def test_timeout_async(self):
        """
        Connection timeouts to the API are translated into a PwnedPasswordsError in
        the async code path.

        """
        api_client = api.PwnedPasswords(
            async_client=self.exception_client(
                exception_class=httpx.ConnectTimeout, message="Timed out", is_async=True
            )
        )
        try:
            await api_client.check_password_async(self.sample_password)
        except exceptions.PwnedPasswordsError as exc:
            assert exc.code == exceptions.ErrorCode.API_TIMEOUT
        else:
            raise AssertionError()

    def test_http_error(self):
        """
        HTTP error responses from the API are translated into a PwnedPasswordsError.

        """
        for error_status in [
            code for code in httpx.codes if httpx.codes.is_error(code)
        ]:
            api_client = api.PwnedPasswords(
                client=self.http_client(status_code=error_status)
            )
            try:
                api_client.check_password(self.sample_password)
            except exceptions.PwnedPasswordsError as exc:
                assert exc.code == exceptions.ErrorCode.HTTP_ERROR
                assert exc.params["status_code"] == error_status
            else:
                raise AssertionError()

    async def test_http_error_async(self):
        """
        HTTP error responses from the API are translated into a PwnedPasswordsError
        in the async code path.

        """
        for error_status in [
            code for code in httpx.codes if httpx.codes.is_error(code)
        ]:
            api_client = api.PwnedPasswords(
                async_client=self.http_client(status_code=error_status, is_async=True)
            )
            try:
                await api_client.check_password_async(self.sample_password)
            except exceptions.PwnedPasswordsError as exc:
                assert exc.code == exceptions.ErrorCode.HTTP_ERROR
                assert exc.params["status_code"] == error_status
            else:
                raise AssertionError()

    def test_request_error(self):
        """
        Other request-related (neither timeout, nor HTTP 4XX/5XX) errors from
        attempting to contact Pwned Passwords are translated into a PwnedPasswordsError.

        """
        api_client = api.PwnedPasswords(
            client=self.exception_client(
                exception_class=httpx.RequestError, message="Unspecified error"
            )
        )
        try:
            api_client.check_password(self.sample_password)
        except exceptions.PwnedPasswordsError as exc:
            assert exc.code == exceptions.ErrorCode.REQUEST_ERROR
        else:
            raise AssertionError()

    async def test_request_error_async(self):
        """
        Other request-related (neither timeout, nor HTTP 4XX/5XX) errors from
        attempting to contact Pwned Passwords are translated into a PwnedPasswordsError
        in the async code path.

        """
        api_client = api.PwnedPasswords(
            async_client=self.exception_client(
                exception_class=httpx.RequestError,
                message="Unspecified error",
                is_async=True,
            )
        )
        try:
            await api_client.check_password_async(self.sample_password)
        except exceptions.PwnedPasswordsError as exc:
            assert exc.code == exceptions.ErrorCode.REQUEST_ERROR
        else:
            raise AssertionError()

    def test_other_error(self):
        """
        Other non-request-related errors during password checking are translated
        into a PwnedPasswordsError.

        """
        api_client = api.PwnedPasswords(
            client=self.exception_client(
                exception_class=ValueError, message="Unspecified error"
            )
        )
        try:
            api_client.check_password(self.sample_password)
        except exceptions.PwnedPasswordsError as exc:
            assert exc.code == exceptions.ErrorCode.UNKNOWN_ERROR
        else:
            raise AssertionError()

    async def test_other_error_async(self):
        """
        Other non-request-related errors during password checking are translated
        into a PwnedPasswordsError in the async code path.

        """
        api_client = api.PwnedPasswords(
            async_client=self.exception_client(
                exception_class=ValueError, message="Unspecified error", is_async=True
            )
        )
        try:
            await api_client.check_password_async(self.sample_password)
        except exceptions.PwnedPasswordsError as exc:
            assert exc.code == exceptions.ErrorCode.UNKNOWN_ERROR
        else:
            raise AssertionError()

    def test_add_padding_default(self):
        """
        By default, the ``Add-Padding`` header is enabled on requests to Pwned
        Passwords.

        """
        client = self.http_client()
        api_client = api.PwnedPasswords(client=client)
        api_client.check_password(self.sample_password)
        client.get.assert_called_with(
            url=mock.ANY,
            headers={"User-Agent": mock.ANY, "Add-Padding": "true"},
            timeout=mock.ANY,
        )

    async def test_add_padding_default_async(self):
        """
        By default, the ``Add-Padding`` header is enabled on async requests to Pwned
        Passwords.

        """
        client = self.http_client(is_async=True)
        api_client = api.PwnedPasswords(async_client=client)
        await api_client.check_password_async(self.sample_password)
        client.get.assert_called_with(
            url=mock.ANY,
            headers={"User-Agent": mock.ANY, "Add-Padding": "true"},
            timeout=mock.ANY,
        )

    @override_settings(PWNED_PASSWORDS={"ADD_PADDING": False})
    def test_add_padding_override(self):
        """
        When the key ``ADD_PADDING`` is ``False`` in the app's settings dict, the
        ``Add-Padding`` header is not enabled on requests to Pwned Passwords.

        """
        client = self.http_client()
        api_client = api.PwnedPasswords(client=client)
        api_client.check_password(self.sample_password)
        client.get.assert_called_with(
            url=mock.ANY, headers={"User-Agent": mock.ANY}, timeout=mock.ANY
        )

    @override_settings(PWNED_PASSWORDS={"ADD_PADDING": False})
    async def test_add_padding_override_async(self):
        """
        When the key ``ADD_PADDING`` is ``False`` in the app's settings dict, the
        ``Add-Padding`` header is not enabled on async requests to Pwned Passwords.

        """
        client = self.http_client(is_async=True)
        api_client = api.PwnedPasswords(async_client=client)
        await api_client.check_password_async(self.sample_password)
        client.get.assert_called_with(
            url=mock.ANY, headers={"User-Agent": mock.ANY}, timeout=mock.ANY
        )

    @tag("end-to-end")
    def test_end_to_end(self):
        """
        A request to the real Pwned Passwords API succeeds and is parsed correctly.

        """
        result = api.check_password("password")
        assert result > 0

    @tag("end-to-end")
    async def test_end_to_end_async(self):
        """
        An async request to the real Pwned Passwords API succeeds and is parsed correctly.

        """
        result = await api.check_password_async("password")
        assert result > 0
