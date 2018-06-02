.. _settings:
.. module:: django.conf.settings


Custom settings
===============

Two optional custom Django settings can be used to customize the
behavior of pwned-passwords-django.


.. data:: PWNED_PASSWORDS_API_TIMEOUT

   A ``float`` indicating, in seconds, how long to wait for a response
   from the Pwned Passwords API before giving up.

   Defaults to ``1.0`` (1 second) if not set.


.. data:: PWNED_PASSWORDS_REGEX

   A ``str`` containing a regular expression to use when
   :class:`~pwned_passwords_django.middleware.PwnedPasswordsMiddleware`
   is scanning HTTP ``POST`` payloads for possible passwords. Will be
   checked case-insensitively.

   Defaults to ``r'PASS'`` (thus matching "password", "passphrase",
   etc.) if not set.

