import hashlib

import requests


API_ENDPOINT = 'https://api.pwnedpasswords.com/range/{}'


def pwned_password(password):
    """
    Checks a password against the Pwned Passwords database.

    """
    password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
    prefix, suffix = password_hash[:5], password_hash[5:]
    results = {
        l[0]: int(l[1]) for l in
        (line.split(':') for line in
         requests.get(API_ENDPOINT.format(prefix)).text.splitlines())
    }
    return results.get(suffix)
