import mock

from django.test import TestCase


class PwnedPasswordsTests(TestCase):
    """
    Base test-case class defining some common code.

    """
    sample_password = 'swordfish'
    sample_password_prefix = '4F571'
    sample_password_suffix = '81DCAADE980555F2CE6755CA425F00658BE'

    def _get_mock(self, response_text=None):
        if response_text is None:
            response_text = '{}:3'.format(self.sample_password_suffix)
        requests_get_mock = mock.MagicMock()
        requests_get_mock.return_value.text = response_text
        return requests_get_mock
