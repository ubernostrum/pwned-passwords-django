"""
Direct access to the Pwned Passwords API for checking whether a
password is compromised.

"""

import hashlib
import logging
import sys

import requests
from django.conf import settings

from . import __version__

log = logging.getLogger(__name__)

API_ENDPOINT = "https://api.pwnedpasswords.com/range/"
REQUEST_TIMEOUT = 1.0  # 1 second
USER_AGENT = (
    f"pwned-passwords-django/{__version__} "
    f"(Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} "
    f"| requests/{requests.__version__})"
)


def _get_pwned(prefix):
    """
    Fetches a dict of all hash suffixes from Pwned Passwords for a
    given SHA-1 prefix.

    """
    try:
        response = requests.get(
            url=f"{API_ENDPOINT}{prefix}",
            headers={"User-Agent": USER_AGENT},
            timeout=getattr(settings, "PWNED_PASSWORDS_API_TIMEOUT", REQUEST_TIMEOUT),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        # Gracefully handle timeouts and HTTP error response codes.
        log.warning("Skipped Pwned Passwords check due to error: %r", exc)
        return None

    results = {}
    for line in response.text.splitlines():
        line_suffix, _, times = line.partition(":")
        results[line_suffix] = int(times.replace(",", ""))

    return results


def pwned_password(password):
    """
    Checks a password against the Pwned Passwords database.

    """
    if not isinstance(password, str):
        raise TypeError("Password values to check must be Unicode strings.")
    password_hash = (
        hashlib.new("sha1", password.encode("utf-8"), usedforsecurity=False)
        .hexdigest()
        .upper()
    )
    prefix, suffix = password_hash[:5], password_hash[5:]
    results = _get_pwned(prefix)
    if results is None:
        # Gracefully handle timeouts and HTTP error response codes.
        return None
    return results.get(suffix, 0)
