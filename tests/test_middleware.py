"""
Tests for pwned-passwords-django's middleware.

"""

from unittest import mock

from django.test import override_settings
from django.urls import reverse
from django.utils.crypto import get_random_string

from .base import PwnedPasswordsTests


class PwnedPasswordsMiddlewareTests(PwnedPasswordsTests):
    """
    Test the Pwned Passwords middleware.

    """

    test_clean = "pwned-clean"
    test_clean_async = "pwned-clean-async"
    test_breach = "pwned-breach"
    test_breach_async = "pwned-breach-async"
    test_middleware = "pwned-middleware"
    test_middleware_async = "pwned-middleware-async"

    def test_password_detection(self):
        """
        The middleware correctly only checks values matching the
        likely-password-input regex.

        """
        sync_mock, async_mock = self.api_mocks()

        with mock.patch(
            "pwned_passwords_django.api.check_password", sync_mock
        ), mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            for payload in (
                {"password": self.sample_password},
                {"passphrase": self.sample_password},
                {"passcode": self.sample_password},
                {"password1": self.sample_password},
                {"password2": self.sample_password},
                {"input_password": self.sample_password},
            ):
                self.client.post(self.test_middleware, data=payload)
                sync_mock.assert_called_with(self.sample_password)
                async_mock.assert_not_called()
                sync_mock.reset_mock()

            for payload in (
                {"authtoken": self.sample_password},
                {"login_code": self.sample_password},
                {"token": self.sample_password},
                {"authcode": self.sample_password},
            ):
                self.client.post(self.test_middleware, data=payload)
                sync_mock.assert_not_called()
                async_mock.assert_not_called()

    async def test_password_detection_async(self):
        """
        The async middleware correctly only checks values matching the
        likely-password-input regex.

        """
        sync_mock, async_mock = self.api_mocks()

        with mock.patch(
            "pwned_passwords_django.api.check_password", sync_mock
        ), mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            for payload in (
                {"password": self.sample_password},
                {"passphrase": self.sample_password},
                {"passcode": self.sample_password},
                {"password1": self.sample_password},
                {"password2": self.sample_password},
                {"input_password": self.sample_password},
            ):
                await self.async_client.post(self.test_middleware_async, data=payload)
                async_mock.assert_called_with(self.sample_password)
                sync_mock.assert_not_called()
                async_mock.reset_mock()

            for payload in (
                {"authtoken": self.sample_password},
                {"login_code": self.sample_password},
                {"token": self.sample_password},
                {"authcode": self.sample_password},
            ):
                await self.async_client.post(self.test_middleware_async, data=payload)
                async_mock.assert_not_called()
                sync_mock.assert_not_called()

    def test_post_only(self):
        """
        The middleware only checks on POST.

        """
        sync_mock, async_mock = self.api_mocks()

        with mock.patch(
            "pwned_passwords_django.api.check_password", sync_mock
        ), mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            self.client.get(self.test_clean, data={"password": self.sample_password})
            sync_mock.assert_not_called()
            async_mock.assert_not_called()

    async def test_post_only_async(self):
        """
        The async middleware only checks on POST.

        """
        sync_mock, async_mock = self.api_mocks()

        with mock.patch(
            "pwned_passwords_django.api.check_password", sync_mock
        ), mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            await self.async_client.get(
                self.test_clean_async, data={"password": self.sample_password}
            )
            sync_mock.assert_not_called()
            async_mock.assert_not_called()

    def test_compromised(self):
        """
        Compromised passwords are detected in the middleware.

        """
        for field in ("password", "passphrase", "password2"):
            sync_mock, _ = self.api_mocks()
            with mock.patch("pwned_passwords_django.api.check_password", sync_mock):
                self.client.post(
                    reverse(self.test_breach, kwargs={"field": field}),
                    data={field: self.sample_password},
                )

    async def test_compromised_async(self):
        """
        Compromised passwords are detected in the async middleware.

        """
        for field in ("password", "passphrase", "password2"):
            _, async_mock = self.api_mocks()
            with mock.patch(
                "pwned_passwords_django.api.check_password_async", async_mock
            ):
                await self.async_client.post(
                    reverse(self.test_breach_async, kwargs={"field": field}),
                    data={field: self.sample_password},
                )

    def test_non_compromised(self):
        """
        Non-compromised passwords do not set a count in the middleware.

        """
        sync_mock, _ = self.api_mocks(count=0)
        with mock.patch("pwned_passwords_django.api.check_password", sync_mock):
            self.client.post(self.test_clean, data={"password": self.sample_password})

    async def test_non_compromised_async(self):
        """
        Non-compromised passwords do not set a count in the async middleware.

        """
        _, async_mock = self.api_mocks(count=0)
        with mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            await self.async_client.post(
                self.test_clean_async, data={"password": self.sample_password}
            )

    @override_settings(PWNED_PASSWORDS={"PASSWORD_REGEX": r"TOKEN"})
    def test_custom_regex(self):
        """
        The middleware will check a custom password regex, if set.

        """
        sync_mock, async_mock = self.api_mocks()

        with mock.patch(
            "pwned_passwords_django.api.check_password", sync_mock
        ), mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            for payload in (
                {"token": self.sample_password},
                {"authtoken": self.sample_password},
                {"apitoken": self.sample_password},
            ):
                self.client.post(self.test_middleware, data=payload)
                sync_mock.assert_called_with(self.sample_password)
                async_mock.assert_not_called()
                sync_mock.reset_mock()

            for payload in (
                {"login_code": self.sample_password},
                {"authcode": self.sample_password},
                {"password": self.sample_password},
            ):
                self.client.post(self.test_middleware, data=payload)
                sync_mock.assert_not_called()
                async_mock.assert_not_called()

    @override_settings(PWNED_PASSWORDS={"PASSWORD_REGEX": r"TOKEN"})
    async def test_custom_regex_async(self):
        """
        The async middleware will check a custom password regex, if set.

        """
        sync_mock, async_mock = self.api_mocks()

        with mock.patch(
            "pwned_passwords_django.api.check_password", sync_mock
        ), mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            for payload in (
                {"token": self.sample_password},
                {"authtoken": self.sample_password},
                {"apitoken": self.sample_password},
            ):
                await self.async_client.post(self.test_middleware_async, data=payload)
                async_mock.assert_called_with(self.sample_password)
                sync_mock.assert_not_called()
                async_mock.reset_mock()

            for payload in (
                {"login_code": self.sample_password},
                {"authcode": self.sample_password},
                {"password": self.sample_password},
            ):
                await self.async_client.post(self.test_middleware_async, data=payload)
                async_mock.assert_not_called()
                sync_mock.assert_not_called()

    def test_error_handler(self):
        """
        The middleware will catch a PwnedPasswordsError and set
        ``request.pwned_passwords`` based on CommonPasswordValidator.

        """
        sync_mock, _ = self.api_error_mocks()
        with mock.patch("pwned_passwords_django.api.check_password", sync_mock):
            self.client.post(
                self.test_clean, data={"password": get_random_string(length=20)}
            )

    async def test_error_handler_async(self):
        """
        The async middleware will catch a PwnedPasswordsError and set
        ``request.pwned_passwords`` to an empty dictionary.

        """
        async_mock, _ = self.api_error_mocks()
        with mock.patch("pwned_passwords_django.api.check_password_async", async_mock):
            await self.async_client.post(
                self.test_clean_async, data={"password": get_random_string(length=20)}
            )
