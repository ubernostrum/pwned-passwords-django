import mock

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .. import api
from ..validators import PwnedPasswordsValidator

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
                    api.API_ENDPOINT.format(
                        self.sample_password_prefix
                    )
                )

    def test_not_compromised(self):
        """
        Non-compromised passwords don't raise ValidationError.

        """
        request_mock = self._get_mock(
            response_text='{}:5'.format(
                self.sample_password_suffix.replace('a', '3')
            )
        )
        with mock.patch('requests.get', request_mock):
            validate_password(self.sample_password)
            request_mock.assert_called_with(
                api.API_ENDPOINT.format(
                    self.sample_password_prefix
                )
            )
