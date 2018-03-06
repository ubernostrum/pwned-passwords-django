from django.conf.urls import url
from django.http import HttpResponse


def view(request):
    """
    A minimal view for use in testing.

    """
    return HttpResponse('Content.')


def assert_compromised_view(request, field, count):
    """
    A view which asserts that it received a compromised password.

    """
    assert hasattr(request, 'pwned_passwords')
    assert request.pwned_passwords
    assert field in request.pwned_passwords
    assert request.pwned_passwords[field] == int(count)
    return HttpResponse('Content.')


def assert_not_compromised_view(request):
    assert hasattr(request, 'pwned_passwords')
    assert not request.pwned_passwords
    assert request.pwned_passwords == {}
    return HttpResponse('Content.')


urlpatterns = [
    url(r'^pwned-passwords-middleware$',
        view,
        name='test-pwned-passwords-clean'),
    url(r'^pwned-passwords-clean$',
        view,
        name='test-pwned-passwords-middleware'),
    url(r'^pwned-passwords-count/(?P<field>\w+)/(?P<count>\d+)$',
        assert_compromised_view,
        name='test-pwned-passwords-count'),
]
