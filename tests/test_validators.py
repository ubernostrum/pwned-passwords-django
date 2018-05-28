import mock
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import override_settings

from pwned_passwords_django import api
from pwned_passwords_django.validators import PwnedPasswordsValidator

from .base import PwnedPasswordsTests


class PwnedPasswordsValidatorsTests(PwnedPasswordsTests):
    """
    Test the Pwned Passwords validator.

    """
    def test_compromised(self):
        """
        Compromised passwords raise ValidationError.

        """
        for count in range(1, 10):
            request_mock = self._get_mock(
                response_text='{}:{}'.format(
                    self.sample_password_suffix,
                    count
                )
            )
            with mock.patch('requests.get', request_mock):
                with self.assertRaisesMessage(
                        ValidationError,
                        PwnedPasswordsValidator.PWNED_MESSAGE
                ):
                    validate_password(self.sample_password)
                request_mock.assert_called_with(
                    url=api.API_ENDPOINT.format(
                        self.sample_password_prefix
                    ),
                    headers=self.user_agent,
                    timeout=api.REQUEST_TIMEOUT,
                )

    def test_not_compromised(self):
        """
        Non-compromised passwords don't raise ValidationError.

        """
        request_mock = self._get_mock(
            response_text='{}:5'.format(
                self.sample_password_suffix.replace('A', '3')
            )
        )
        with mock.patch('requests.get', request_mock):
            validate_password(self.sample_password)
            request_mock.assert_called_with(
                url=api.API_ENDPOINT.format(
                    self.sample_password_prefix
                ),
                headers=self.user_agent,
                timeout=api.REQUEST_TIMEOUT,
            )

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME': 'pwned_passwords_django.validators.PwnedPasswordsValidator',
        'OPTIONS': {'timeout': 4},
    }])
    def test_timeout_option(self):
        """
        timeout option is passed down to requests.

        """
        request_mock = self._get_mock(
            response_text='{}:5'.format(
                self.sample_password_suffix.replace('A', '3')
            )
        )
        with mock.patch('requests.get', request_mock):
            validate_password(self.sample_password)
            request_mock.assert_called_with(
                url=api.API_ENDPOINT.format(
                    self.sample_password_prefix
                ),
                headers=self.user_agent,
                timeout=4,
            )
