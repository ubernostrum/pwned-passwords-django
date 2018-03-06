import mock

from django.test import override_settings
from django.urls import reverse

from ..api import API_ENDPOINT

from .base import PwnedPasswordsTests


@override_settings(PWNED_PASSWORDS_REGEX=r'PASS')
class PwnedPasswordsMiddlewareTests(PwnedPasswordsTests):
    """
    Test PwnedPasswordsMiddleware.

    """
    test_pwned_url = 'test-pwned-passwords-count'
    test_non_pwned_url = reverse('test-pwned-passwords-clean')
    test_url = reverse('test-pwned-passwords-middleware')

    def test_password_detection(self):
        """
        The middleware correctly only checks values matching the
        likely-password-input regex.

        """
        for payload in (
                {'password': self.sample_password},
                {'passphrase': self.sample_password},
                {'passcode': self.sample_password},
                {'password1': self.sample_password},
                {'password2': self.sample_password},
                {'input_password': self.sample_password},
        ):
            request_mock = self._get_mock()
            with mock.patch('requests.get', request_mock):
                self.client.post(self.test_url, data=payload)
                request_mock.assert_called_with(
                    API_ENDPOINT.format(
                        self.sample_password_prefix
                    )
                )

        for payload in (
                {'authtoken': self.sample_password},
                {'login_code': self.sample_password},
                {'token': self.sample_password},
                {'authcode': self.sample_password},
        ):
            request_mock = self._get_mock()
            with mock.patch('requests.get', request_mock):
                self.client.post(self.test_url, data=payload)
                request_mock.assert_not_called()

    def test_post_only(self):
        """
        The middleware only checks on POST.

        """
        request_mock = self._get_mock()
        with mock.patch('requests.get', request_mock):
            self.client.get(
                self.test_non_pwned_url,
                data={'password': self.sample_password}
            )
            request_mock.assert_not_called()

    def test_compromised(self):
        """
        Compromised passwords are detected, with their count.

        """
        for field, count in (
                ('password', 3),
                ('passphrase', 5),
                ('password2', 4),
        ):
            request_mock = self._get_mock(
                response_text='{}:{}'.format(
                    self.sample_password_suffix, count
                )
            )
            with mock.patch('requests.get', request_mock):
                self.client.post(
                    reverse(
                        self.test_pwned_url,
                        kwargs={'field': field, 'count': count}
                    ),
                    data={field: self.sample_password}
                )

    def test_non_compromised(self):
        """
        Non-compromised passwords do not set a count.

        """
        request_mock = self._get_mock(
            response_text='{}:5'.format(
                self.sample_password_suffix.replace('a', '3'),
            )
        )
        with mock.patch('requests.get', request_mock):
            self.client.post(
                self.test_non_pwned_url,
                data={'password': self.sample_password}
            )

    @override_settings(PWNED_PASSWORDS_REGEX=r'TOKEN')
    def test_custom_regex(self):
        """
        Setting a custom password-input regex works.

        """
        for payload in (
                {'token': self.sample_password},
                {'authtoken': self.sample_password},
                {'apitoken': self.sample_password},
        ):
            request_mock = self._get_mock()
            with mock.patch('requests.get', request_mock):
                self.client.post(self.test_url, data=payload)
                request_mock.assert_called_with(
                    API_ENDPOINT.format(
                        self.sample_password_prefix
                    )
                )

        for payload in (
                {'login_code': self.sample_password},
                {'authcode': self.sample_password},
                {'password': self.sample_password},
        ):
            request_mock = self._get_mock()
            with mock.patch('requests.get', request_mock):
                self.client.post(self.test_url, data=payload)
                request_mock.assert_not_called()
