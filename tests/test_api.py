"""
Tests for direct interaction with the Pwned Passwords API.

"""

from unittest import mock

import requests
from django.test import override_settings

from pwned_passwords_django import api

from .base import PwnedPasswordsTests


class PwnedPasswordsAPITests(PwnedPasswordsTests):
    """
    Test interaction with the Pwned Passwords API.

    """

    def test_unicode_requirement(self):
        """
        Calling the API requires a str object, not bytes.

        """
        with self.assertRaises(TypeError):
            api.pwned_password(self.sample_password.encode("utf-8"))

    def test_compromised(self):
        """
        Compromised passwords are detected correctly.

        """
        for count in range(1, 10):
            request_mock = self._get_mock(
                response_text=f"{self.sample_password_suffix}:{count}"
            )
            with mock.patch("requests.get", request_mock):
                result = api.pwned_password(self.sample_password)
                request_mock.assert_called_with(
                    url=f"{api.API_ENDPOINT}{self.sample_password_prefix}",
                    headers=self.user_agent,
                    timeout=api.REQUEST_TIMEOUT,
                )
                self.assertEqual(count, result)

    def test_not_compromised(self):
        """
        Non-compromised passwords are detected correctly.

        """
        suffix = self.sample_password_suffix.replace("A", "3")
        request_mock = self._get_mock(response_text=f"{suffix}:5")
        with mock.patch("requests.get", request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=f"{api.API_ENDPOINT}{self.sample_password_prefix}",
                headers=self.user_agent,
                timeout=api.REQUEST_TIMEOUT,
            )
            self.assertEqual(0, result)

        # The real API doesn't return a result with a zero count, but
        # test it just in case.
        request_mock = self._get_mock(response_text=f"{self.sample_password_suffix}:0")
        with mock.patch("requests.get", request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=f"{api.API_ENDPOINT}{self.sample_password_prefix}",
                headers=self.user_agent,
                timeout=api.REQUEST_TIMEOUT,
            )
            self.assertEqual(0, result)

    def test_empty_response(self):
        """
        An empty API response is handled correctly.

        """
        request_mock = self._get_mock(response_text="")
        with mock.patch("requests.get", request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=f"{api.API_ENDPOINT}{self.sample_password_prefix}",
                headers=self.user_agent,
                timeout=api.REQUEST_TIMEOUT,
            )
            self.assertEqual(0, result)

    def test_comma_response(self):
        """
        An API response where the count includes commas is handled correctly.

        Bug reports indicate the Pwned Passwords API has occasionally done this.

        """
        request_mock = self._get_mock(
            response_text=f"{self.sample_password_suffix}:1,234,567"
        )
        with mock.patch("requests.get", request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(1234567, result)

    @override_settings(PWNED_PASSWORDS_API_TIMEOUT=0.5)
    def test_timeout_override(self):
        """
        The custom request timeout setting is honored.

        """
        request_mock = self._get_mock()
        with mock.patch("requests.get", request_mock):
            api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=f"{api.API_ENDPOINT}{self.sample_password_prefix}",
                headers=self.user_agent,
                timeout=0.5,
            )

    def test_timeout(self):
        """
        Connection timeouts to the API are handled gracefully.

        """
        request_mock = self._get_exception_mock(requests.ConnectTimeout())
        with mock.patch("requests.get", request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(None, result)

    def test_http_error(self):
        """
        Non-200 HTTP responses from the API are handled gracefully.

        """
        request_mock = self._get_exception_mock(requests.HTTPError())
        with mock.patch.object(requests.Response, "raise_for_status", request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(None, result)
