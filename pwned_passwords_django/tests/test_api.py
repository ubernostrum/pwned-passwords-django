import mock

from .. import api

from .base import PwnedPasswordsTests


class PwnedPasswordsAPITests(PwnedPasswordsTests):
    """
    Test interaction with the Pwned Passwords API.

    """
    def test_compromised(self):
        """
        Compromised passwords are detected correctly.

        """
        for count in range(1, 10):
            request_mock = self._get_mock(
                response_text='{}:{}'.format(
                    self.sample_password_suffix,
                    count
                )
            )
            with mock.patch('requests.get', request_mock):
                result = api.pwned_password(self.sample_password)
                request_mock.assert_called_with(
                    api.API_ENDPOINT.format(
                        self.sample_password_prefix
                    )
                )
                self.assertEqual(count, result)

    def test_not_compromised(self):
        """
        Non-compromised passwords are detected correctly.

        """
        request_mock = self._get_mock(
            response_text='{}:5'.format(
                self.sample_password_suffix.replace('a', '3')
            )
        )
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                api.API_ENDPOINT.format(
                    self.sample_password_prefix
                )
            )
            self.assertEqual(None, result)

        # The real API doesn't return a result with a zero count, but
        # test it just in case.
        request_mock = self._get_mock(
            response_text='{}:0'.format(
                self.sample_password_suffix
            )
        )
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                api.API_ENDPOINT.format(
                    self.sample_password_prefix
                )
            )
            self.assertEqual(0, result)

    def test_empty_response(self):
        """
        An empty API response is handled correctly.

        """
        request_mock = self._get_mock(
            response_text=''
        )
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                api.API_ENDPOINT.format(
                    self.sample_password_prefix
                )
            )
            self.assertEqual(None, result)
