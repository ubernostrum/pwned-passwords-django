"""
A Django middleware which checks all incoming POST requests for
potentially-compromised passwords using the Pwned Passwords API.

"""

import re
from typing import Callable

from django import http
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from .api import pwned_password


class PwnedPasswordsMiddleware(MiddlewareMixin):
    """
    Middleware which checks all POST submissions containing likely
    passwords against the Pwned Passwords database.

    """

    def __init__(self, get_response: Callable[[http.HttpRequest], http.HttpResponse]):
        super().__init__(get_response)
        self.password_re = re.compile(
            getattr(settings, "PWNED_PASSWORDS_REGEX", r"PASS"), re.IGNORECASE
        )

    def process_request(self, request: http.HttpRequest) -> None:
        request.pwned_passwords = {}
        if request.method != "POST":
            return
        for key in request.POST.keys():
            if self.password_re.search(key):
                count = pwned_password(request.POST[key])
                if count:
                    request.pwned_passwords[key] = count
