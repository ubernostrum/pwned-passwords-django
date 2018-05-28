import hashlib
import logging
import sys

import requests

from . import __version__


log = logging.getLogger(__name__)

API_ENDPOINT = 'https://api.pwnedpasswords.com/range/{}'
REQUEST_TIMEOUT = 0.6  # 600ms
USER_AGENT = 'pwned-passwords-django/{} (Python/{} | requests/{})'.format(
    __version__,
    '{}.{}.{}'.format(*sys.version_info[:3]),
    requests.__version__
)


def pwned_password(password, timeout=REQUEST_TIMEOUT):
    """
    Checks a password against the Pwned Passwords database.

    """
    password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = password_hash[:5], password_hash[5:]
    try:
        results = [
            int(line.partition(':')[2])
            for line in requests.get(
                    url=API_ENDPOINT.format(prefix),
                    headers={'User-Agent': USER_AGENT},
                    timeout=timeout,
            ).text.splitlines()
            if line.startswith(suffix)
        ]
    except (requests.RequestException, ValueError) as e:
        # Gracefully handle timeouts and HTTP error response codes.
        log.warning(
            'Skipped Pwned Passwords check due to error: %r', e
        )
        return None

    if results:
        return results[0]
