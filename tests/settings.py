"""
Minimal Django settings file for test runs.

"""
from django.utils.crypto import get_random_string

INSTALLED_APPS = ["pwned_passwords_django"]
ROOT_URLCONF = "tests.urls"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
MIDDLEWARE = [
    "pwned_passwords_django.middleware.pwned_passwords_middleware",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator"}
]
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "loggers": {
        "pwned_passwords_django.api": {"handlers": ["null"], "propagate": False}
    },
}
SECRET_KEY = (get_random_string(12),)
