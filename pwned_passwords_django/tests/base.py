import mock

from django.test import TestCase


class PwnedPasswordsTests(TestCase):
    """
    Base test-case class defining some common code.

    """
    sample_password = 'swordfish'
    sample_password_prefix = '4f571'
    sample_password_suffix = '81dcaade980555f2ce6755ca425f00658be'

    def _get_mock(self, response_text=None):
        if response_text is None:
            response_text = '{}:3'.format(self.sample_password_suffix)
        requests_get_mock = mock.MagicMock()
        requests_get_mock.return_value.text = response_text
        return requests_get_mock
