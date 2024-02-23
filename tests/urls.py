"""
URL mapping used during testing.

"""

# SPDX-License-Identifier: BSD-3-Clause

from django.http import HttpResponse
from django.urls import path


def view(request):
    """
    A minimal view for use in testing.

    """
    # pylint: disable=unused-argument
    return HttpResponse("Content.")


async def async_view(request):
    """
    A minimal async view for use in testing.

    """
    # pylint: disable=unused-argument
    return HttpResponse("Content.")


def breach_count(request, field):
    """
    A view which asserts that it received a compromised password, in the given
    ``field``.

    """
    assert hasattr(request, "pwned_passwords")
    assert request.pwned_passwords
    assert field in request.pwned_passwords
    return HttpResponse("Content.")


async def async_breach_count(request, field):
    """
    An async view which asserts that it received a compromised password, in the
    given ``field``.

    """
    assert hasattr(request, "pwned_passwords")
    assert request.pwned_passwords
    assert field in request.pwned_passwords
    return HttpResponse("Content.")


def clean(request):
    """
    A view which asserts that it did not receive a compromised
    password.

    """
    assert hasattr(request, "pwned_passwords")
    assert request.pwned_passwords == []
    return HttpResponse("Content.")


async def async_clean(request):
    """
    An async view which asserts that it did not receive a compromised
    password.

    """
    assert hasattr(request, "pwned_passwords")
    assert request.pwned_passwords == []
    return HttpResponse("Content.")


urlpatterns = [
    path(
        "pwned-passwords-django/tests/middleware",
        view,
        name="pwned-middleware",
    ),
    path(
        "pwned-passwords-django/tests/async/middleware",
        async_view,
        name="pwned-middleware-async",
    ),
    path(
        "pwned-passwords-django/tests/<str:field>/",
        breach_count,
        name="pwned-breach",
    ),
    path(
        "pwned-passwords-django/tests/async/<str:field>/",
        async_breach_count,
        name="pwned-breach-async",
    ),
    path(
        "pwned-passwords-django/tests/clean",
        view,
        name="pwned-clean",
    ),
    path(
        "pwned-passwords-django/tests/async/clean",
        async_view,
        name="pwned-clean",
    ),
]
