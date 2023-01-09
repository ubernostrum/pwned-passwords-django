.. module:: pwned_passwords_django.middleware

.. _middleware:


Using the middleware
====================

To help with situations where a potentially-compromised password is used
:ref:`in ways Django's password validators won't catch
<validator-limitations>`, pwned-passwords-django also provides a middleware
which monitors every incoming HTTP request for ``POST`` payloads which appear
to contain passwords, and checks them against Pwned Passwords.


.. autofunction:: pwned_passwords_middleware
