import hashlib
import logging

import requests


API_ENDPOINT = 'https://api.pwnedpasswords.com/range/{}'
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
                timeout=0.6,
            ).text.splitlines()
            if line.startswith(suffix)
        ]
    except (requests.RequestException, ValueError):
        # Gracefully handle timeouts and HTTP error response codes.
        log.exception('Error checking pwnedpasswords')
        return None

    if results:
        return results[0]
