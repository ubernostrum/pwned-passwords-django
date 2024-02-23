"""
A Django middleware which checks all incoming POST requests for
potentially-compromised passwords using the Pwned Passwords API.

"""

# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import logging
import re
import typing

from django import http
from django.conf import settings
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.utils.decorators import sync_and_async_middleware
from django.views.decorators.debug import sensitive_variables

from . import api, exceptions

logger = logging.getLogger(__name__)

_fallback_validator = CommonPasswordValidator()


def _fallback(password: str) -> bool:
    """
    Fallback password check in case of Pwned Passwords errors, using Django's
    built-in CommonPasswordValidator.

    """
    try:
        _fallback_validator.validate(password)
        return False
    except ValidationError:
        return True


@sensitive_variables()
async def _scan_payload_async(request: http.HttpRequest) -> typing.List[str]:
    """
    Asynchronous helper function which performs the scan of the request's payload.

    """
    settings_dict = getattr(settings, "PWNED_PASSWORDS", {})
    search_re = re.compile(settings_dict.get("PASSWORD_REGEX", r"PASS"), re.IGNORECASE)

    keys_to_search = [key for key in request.POST.keys() if search_re.search(key)]
    if not keys_to_search:
        return []
    try:
        return [
            key
            for key in keys_to_search
            if await api.check_password_async(request.POST[key])
        ]
    except exceptions.PwnedPasswordsError:
        logger.error(
            "Falling back to Django CommonPasswordValidator due "
            "to error contacting Pwned Passwords."
        )
        return [key for key in keys_to_search if _fallback(request.POST[key])]


@sensitive_variables()
def _scan_payload_sync(request: http.HttpRequest) -> typing.List[str]:
    """
    Helper function which performs the scan of the request's payload.

    """
    settings_dict = getattr(settings, "PWNED_PASSWORDS", {})
    search_re = re.compile(settings_dict.get("PASSWORD_REGEX", r"PASS"), re.IGNORECASE)

    keys_to_search = [key for key in request.POST.keys() if search_re.search(key)]
    if not keys_to_search:
        return []
    try:
        return [key for key in keys_to_search if api.check_password(request.POST[key])]
    except exceptions.PwnedPasswordsError:
        logger.error(
            "Falling back to Django CommonPasswordValidator due "
            "to error contacting Pwned Passwords."
        )
        return [key for key in keys_to_search if _fallback(key)]


@sync_and_async_middleware
def pwned_passwords_middleware(get_response: typing.Callable) -> typing.Callable:
    """
    Factory function returning a middleware -- sync or async as necessary -- which
    checks ``POST`` submissions that potentially contain passwords against the Pwned
    Passwords database.

    To enable the middleware, add
    ``"pwned_passwords_django.middleware.pwned_passwords_middleware"`` to your
    :setting:`MIDDLEWARE` setting. This will add a new attribute -- ``pwned_passwords``
    -- to each :class:`~django.http.HttpRequest` object. The ``request.pwned_passwords``
    attribute will be a :class:`list` of :class:`str`.

    .. warning:: **Middleware order**

       The order of middleware classes in the Django :setting:`MIDDLEWARE` setting can
       be sensitive. In particular, any middlewares which affect file upload handlers
       *must* be listed above middlewares which inspect
       :attr:`~django.http.HttpRequest.POST`. Since this middleware has to inspect
       :attr:`~django.http.HttpRequest.POST` for likely passwords, it must be listed
       after any middlewares which might change upload handlers. If you're unsure what
       this means, just put this middleware at the bottom of your :setting:`MIDDLEWARE`
       list.

    The ``request.pwned_passwords`` list will be *empty* if any of the following is
    true:

    * The request method is not ``POST``.

    * The request method is ``POST``, but the payload does not appear to contain a
      password.

    * The request method is ``POST``, and the payload appears to contain one or more
      passwords, but none were listed as compromised in Pwned Passwords.

    If the request method is ``POST``, and the payload appears to contain one or more
    passwords, and at least one of those is listed in Pwned Passwords, then
    ``request.pwned_passwords`` will be a list of keys from ``request.POST`` that
    contained compromised passwords.

    For example, if ``request.POST`` contains a key named ``password_field``, and
    ``request.POST["password_field"]`` is a password that appears in the Pwned Passwords
    database, ``request.pwned_passwords`` will be ``["password_field"]``.

    .. warning:: **API failures**

       pwned-passwords-django needs to communicate with the Pwned Passwords API in order
       to check passwords. If Pwned Passwords is down or timing out (the default
       connection timeout is 1 second), or if any other error occurs when checking the
       password, this middleware will fall back to using Django's
       :class:`~django.contrib.auth.password_validation.CommonPasswordValidator`, which
       uses a smaller, locally-stored list of common passwords. Whenever this happens, a
       message of level :data:`logging.ERROR` will appear in your logs, indicating what
       type of failure was encountered in talking to the Pwned Passwords API.

       See :ref:`the error-handling documentation <error-handling>` for details.

    Here's an example of how you might use `Django's message framework
    <https://docs.djangoproject.com/en/stable/ref/contrib/messages/>`_ to indicate to a
    user that they've just submitted a password that appears to be compromised:

    .. code-block:: python

       from django.contrib import messages


       def some_view(request):
           if request.method == "POST" and request.pwned_passwords:
               messages.warning(
                   request,
                   "You just entered a password which appears to be compromised!"
               )

    pwned-passwords-django uses a regular expression to guess which items in
    :attr:`~django.http.HttpRequest.POST` are likely to be passwords. By default, it
    matches on any key in :attr:`~django.http.HttpRequest.POST` containing ``"PASS"``
    (case-insensitive), which catches input names like ``"password"``, ``"passphrase"``,
    and so on. If you use something significantly different than this for a password
    input name, specify it -- as a string, *not* as a compiled regex object! -- in the
    setting ``settings.PWNED_PASSWORDS["PASSWORD_REGEX"]`` to tell the middleware what
    to look for. See :ref:`the settings documentation <settings>` for details.

    """
    # We need to know whether or not the request we're handling is async: if it is, we
    # should return an async middleware that uses an async HTTP client to talk to Pwned
    # Passwords. We determine that by checking whether the get_response() callable is a
    # coroutine -- if so, we're on the async path.
    if asyncio.iscoroutinefunction(get_response):

        async def middleware(request: http.HttpRequest) -> http.HttpResponse:
            """
            Asynchronous middleware function which checks all POST submissions
            containing likely passwords against the Pwned Passwords database.

            """
            request.pwned_passwords = []
            if request.method == "POST":
                # A bug in Django's async test client causes access to request.POST to
                # throw an exception unless preceded by an access to
                # request.body. Future versions of Django will fix this, but for now we
                # do a throwaway access of request.body as a workaround.
                #
                # See https://code.djangoproject.com/ticket/34063 for details.
                request.body  # pylint: disable=pointless-statement
                request.pwned_passwords = await _scan_payload_async(request)
            response = await get_response(request)
            return response

    else:

        def middleware(request: http.HttpRequest) -> http.HttpResponse:
            """
            Synchronous middleware function which checks all POST submissions
            containing likely passwords against the Pwned Passwords database.

            """
            request.pwned_passwords = {}
            if request.method == "POST":
                request.pwned_passwords = _scan_payload_sync(request)
            response = get_response(request)
            return response

    return middleware
