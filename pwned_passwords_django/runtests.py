"""
A standalone test runner script, configuring the minimum settings
required for django-pwned-passwords' tests to execute.

Re-use at your own risk: many Django applications will require full
settings and/or templates in order to execute their tests, while
django-pwned-passwords does not.

"""

import os
import sys


# Make sure the app is (at least temporarily) on the import path.
APP_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, APP_DIR)


# Technically, django-pwned-passwords does not require any of these
# settings; it doesn't even need to be in INSTALLED_APPS in order to
# work.
#
# However, Django itself requires DATABASES and ROOT_URLCONF to be
# set, Django's system-check framework will raise warnings if no value
# is provided for MIDDLEWARE_CLASSES, and the Django test runner needs
# your app to be in INSTALLED_APPS in order to work.
SETTINGS_DICT = {
    'INSTALLED_APPS': ('pwned_passwords_django',),
    'ROOT_URLCONF': 'pwned_passwords_django.tests.urls',
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(APP_DIR, 'db.sqlite3'),
        },
    },
    'MIDDLEWARE': (
        'pwned_passwords_django.middleware.PwnedPasswordsMiddleware',
    ),
    'AUTH_PASSWORD_VALIDATORS': [
        {
            'NAME': 'pwned_passwords_django.validators.PwnedPasswordsValidator',
        },
    ],
}


def run_tests():
    # Making Django run this way is a two-step process. First, call
    # settings.configure() to give Django settings to work with:
    from django.conf import settings
    settings.configure(**SETTINGS_DICT)

    # Then, call django.setup() to initialize the application cache
    # and other bits:
    import django
    if hasattr(django, 'setup'):
        django.setup()

    # Now we instantiate a test runner...
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    # And then we run tests and return the results.
    test_runner = TestRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['pwned_passwords_django.tests'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests()
