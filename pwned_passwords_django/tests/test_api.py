import mock
import requests

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
                    url=api.API_ENDPOINT.format(
                        self.sample_password_prefix
                    ),
                    timeout=0.6,
                )
                self.assertEqual(count, result)

    def test_not_compromised(self):
        """
        Non-compromised passwords are detected correctly.

        """
        request_mock = self._get_mock(
            response_text='{}:5'.format(
                self.sample_password_suffix.replace('A', '3')
            )
        )
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            request_mock.assert_called_with(
                url=api.API_ENDPOINT.format(
                    self.sample_password_prefix
                ),
                timeout=0.6,
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
                url=api.API_ENDPOINT.format(
                    self.sample_password_prefix
                ),
                timeout=0.6,
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
                url=api.API_ENDPOINT.format(
                    self.sample_password_prefix
                ),
                timeout=0.6,
            )
            self.assertEqual(None, result)

    def test_bad_text(self):
        """
        Handle non-numeric count gracefully

        """
        request_mock = self._get_mock(
            response_text='{}:xxx'.format(
                self.sample_password_suffix
            )
        )
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(None, result)

    def test_bad_response_no_colon(self):
        """
        Handle malformed response with no colon gracefully

        """
        request_mock = self._get_mock(
            response_text=self.sample_password_suffix
        )
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(None, result)

    def test_bad_response_many_colons(self):
        """
        Handle malformed response with too many colons gracefully

        """
        request_mock = self._get_mock(
            response_text='{}:123:xxx'.format(
                self.sample_password_suffix
            )
        )
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(None, result)

    def test_timeout(self):
        """
        Connection timeout response is handled gracefully

        """
        request_mock = mock.MagicMock(side_effect=requests.ConnectTimeout())
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(None, result)

    def test_http_error(self):
        """
        A non-200 HTTP response is handled gracefully

        """
        request_mock = mock.MagicMock(side_effect=requests.HTTPError())
        with mock.patch('requests.get', request_mock):
            result = api.pwned_password(self.sample_password)
            self.assertEqual(None, result)
