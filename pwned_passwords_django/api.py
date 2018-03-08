import hashlib

import requests


API_ENDPOINT = 'https://api.pwnedpasswords.com/range/{}'


def pwned_password(password):
    """
    Checks a password against the Pwned Passwords database.

    """
    password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = password_hash[:5], password_hash[5:]
    results = [
        int(line.split(':')[1]) for line in
        requests.get(API_ENDPOINT.format(prefix)).text.splitlines()
        if line.startswith(suffix)
    ]
    if results:
        return results[0]
