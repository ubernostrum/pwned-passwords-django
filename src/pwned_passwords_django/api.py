import hashlib
import logging
import sys

import requests
from django.conf import settings
from django.core.cache import caches
from django.utils.six import text_type

from . import __version__


log = logging.getLogger(__name__)

API_ENDPOINT = 'https://api.pwnedpasswords.com/range/{}'
REQUEST_TIMEOUT = 1.0  # 1 second
DEFAULT_CACHE_TIMEOUT = 60 * 60  # 1 hour
USER_AGENT = 'pwned-passwords-django/{} (Python/{} | requests/{})'.format(
    __version__,
    '{}.{}.{}'.format(*sys.version_info[:3]),
    requests.__version__
)


def hash_password(password):
    """
    Get the SHA-1 k-anonymity prefix and suffix of a password.

    """
    if not isinstance(password, text_type):
        raise TypeError('Password values to check must be Unicode strings.')
    password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = password_hash[:5], password_hash[5:]
    return prefix, suffix


def get_pwned_list(prefix):
    """
    Get the list of all pwned password hashes for a given SHA-1 prefix.

    """
    try:
        response = requests.get(
            url=API_ENDPOINT.format(prefix),
            headers={'User-Agent': USER_AGENT},
            timeout=getattr(
                settings,
                'PWNED_PASSWORDS_API_TIMEOUT',
                REQUEST_TIMEOUT
            ),
        )
        response.raise_for_status()
    except requests.RequestException as e:
        # Gracefully handle timeouts and HTTP error response codes.
        log.warning(
            'Skipped Pwned Passwords check due to error: %r', e
        )
        return None
    result = {}
    for line in response.text.splitlines():
        try:
            suffix, _, times = line.partition(':')
            result[suffix] = int(times)
        except ValueError as e:
            log.warning('Invalid value in Pwned Passwords API: %r', e)
            pass
    return result


def pwned_password(password):
    """
    Checks a password against the Pwned Passwords database.

    """
    prefix, suffix = hash_password(password)
    cache_name = getattr(settings, 'PWNED_PASSWORDS_CACHE_NAME', 'default')
    cache_key = 'pwned:{}'.format(prefix)
    use_cache = getattr(settings, 'PWNED_PASSWORDS_CACHE', True)

    if use_cache:
        results = caches[cache_name].get(cache_key)
    else:
        results = None

    if results is None:
        results = get_pwned_list(prefix)
        if use_cache:
            caches[cache_name].set(
                cache_key,
                results,
                timeout=getattr(
                    settings,
                    'PWNED_PASSWORDS_CACHE_TIMEOUT',
                    DEFAULT_CACHE_TIMEOUT
                )
            )

    if results is not None:
        return results.get(suffix)
