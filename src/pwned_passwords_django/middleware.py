import re

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from .api import pwned_password


class PwnedPasswordsMiddleware(MiddlewareMixin):
    """
    Middleware which checks all POST submissions containing likely
    passwords against the Pwned Passwords database.

    """
    def __init__(self, get_response):
        super(PwnedPasswordsMiddleware, self).__init__(get_response)
        self.password_re = re.compile(
            getattr(
                settings,
                'PWNED_PASSWORDS_REGEX',
                r'PASS'
            ), re.IGNORECASE
        )

    def process_request(self, request):
        request.pwned_passwords = {}
        if request.method != 'POST':
            return
        for key in request.POST.keys():
            if self.password_re.search(key):
                count = pwned_password(request.POST[key])
                if count:
                    request.pwned_passwords[key] = count
