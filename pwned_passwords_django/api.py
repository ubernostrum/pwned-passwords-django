import hashlib
import logging
import sys

import requests


__version__ = '1.2'

API_ENDPOINT = 'https://api.pwnedpasswords.com/range/{}'
REQUEST_TIMEOUT = 0.6  # 600ms
USER_AGENT = 'Python/{} | pwned-passwords-django/{}'.format(
    '{}.{}'.format(*sys.version_info[:2]),
    __version__
)

log = logging.getLogger(__name__)


def pwned_password(password):
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
                    timeout=REQUEST_TIMEOUT,
            ).text.splitlines()
            if line.startswith(suffix)
        ]
    except (requests.RequestException, ValueError) as e:
        # Gracefully handle timeouts and HTTP error response codes.
        log.warning(
            'Skipping pwnedpasswords check as an error occurred: %r', e
        )
        return None

    if results:
        return results[0]
