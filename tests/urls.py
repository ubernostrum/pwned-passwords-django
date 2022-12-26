"""
URL mapping used during testing.

"""
from django.http import HttpResponse
from django.urls import re_path


def view(request):
    """
    A minimal view for use in testing.

    """
    return HttpResponse("Content.")


def assert_compromised_view(request, field, count):
    """
    A view which asserts that it received a compromised password.

    """
    assert hasattr(request, "pwned_passwords")
    assert request.pwned_passwords
    assert field in request.pwned_passwords
    assert request.pwned_passwords[field] == int(count)
    return HttpResponse("Content.")


def assert_not_compromised_view(request):
    """
    A view which asserts that it did not receive a compromised
    password.

    """
    assert hasattr(request, "pwned_passwords")
    assert not request.pwned_passwords
    assert request.pwned_passwords == {}
    return HttpResponse("Content.")


urlpatterns = [
    re_path(
        r"^pwned-passwords-middleware$",
        assert_not_compromised_view,
        name="test-pwned-passwords-clean",
    ),
    re_path(r"^pwned-passwords-clean$", view, name="test-pwned-passwords-middleware"),
    re_path(
        r"^pwned-passwords-count/(?P<field>\w+)/(?P<count>\d+)$",
        assert_compromised_view,
        name="test-pwned-passwords-count",
    ),
]
