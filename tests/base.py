"""
Base test-case class for pwned-passwords-django.

"""

from unittest import mock

from django.test import TestCase

from pwned_passwords_django import api


class PwnedPasswordsTests(TestCase):
    """
    Base test-case class defining some common code.

    """

    sample_password = "swordfish"  # nosec: B105
    sample_password_prefix = "4F571"  # nosec: B105
    sample_password_suffix = "81DCAADE980555F2CE6755CA425F00658BE"  # nosec: B105
    user_agent = {"User-Agent": api.USER_AGENT}

    def _get_mock(self, response_text=None):
        """
        Return a mock of requests.get() for use in testing.

        """
        if response_text is None:
            response_text = "{}:3".format(self.sample_password_suffix)
        requests_get_mock = mock.MagicMock()
        requests_get_mock.return_value.text = response_text
        return requests_get_mock

    def _get_exception_mock(self, exception):
        """
        Return a mock which will raise an exception, to test API failures.

        """
        return mock.MagicMock(side_effect=exception)
