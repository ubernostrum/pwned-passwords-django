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
        with self.assertRaises(TypeError):
            api.pwned_password(self.sample_password.encode("utf-8"))

    def test_compromised(self):
        """
        Compromised passwords are detected correctly.

        """
        for count in range(1, 10):
            request_mock = self._get_mock(
                response_text="{}:{}".format(self.sample_password_suffix, count)
            )
            with mock.patch("requests.get", request_mock):
                result = api.pwned_password(self.sample_password)
                request_mock.assert_called_with(
                    url=api.API_ENDPOINT.format(self.sample_password_prefix),
                    headers=self.user_agent,
                    timeout=api.REQUEST_TIMEOUT,
                )
                self.assertEqual(count, result)

    def test_not_compromised(self):
        """
        Non-compromised passwords are detected correctly.

        """
        request_mock = self._get_mock(
            response_text="{}:5".format(self.sample_password_suffix.replace("A", "3"))
        )
        with mock.patch("requests.get", request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=api.API_ENDPOINT.format(self.sample_password_prefix),
                headers=self.user_agent,
                timeout=api.REQUEST_TIMEOUT,
            )
            self.assertEqual(0, result)

        # The real API doesn't return a result with a zero count, but
        # test it just in case.
        request_mock = self._get_mock(
            response_text="{}:0".format(self.sample_password_suffix)
        )
        with mock.patch("requests.get", request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=api.API_ENDPOINT.format(self.sample_password_prefix),
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
                url=api.API_ENDPOINT.format(self.sample_password_prefix),
                headers=self.user_agent,
                timeout=api.REQUEST_TIMEOUT,
            )
            self.assertEqual(0, result)

    @override_settings(PWNED_PASSWORDS_API_TIMEOUT=0.5)
    def test_timeout_override(self):
        """
        The custom request timeout setting is honored.

        """
        request_mock = self._get_mock()
        with mock.patch("requests.get", request_mock):
            api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=api.API_ENDPOINT.format(self.sample_password_prefix),
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
