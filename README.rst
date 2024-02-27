.. -*-restructuredtext-*-

.. image:: https://github.com/ubernostrum/pwned-passwords-django/workflows/CI/badge.svg
   :alt: CI status image
   :target: https://github.com/ubernostrum/pwned-passwords-django/actions?query=workflow%3ACI

``pwned-passwords-django`` provides helpers for working with the
`Pwned Passwords database from Have I Been Pwned
<https://haveibeenpwned.com/Passwords>`_ in `Django
<https://www.djangoproject.com/>`_ powered sites. Pwned Passwords is
an extremely large database of passwords known to have been
compromised through data breaches, and is useful as a tool for
rejecting common or weak passwords.

There are three main components to this application:

* `A password validator
  <https://pwned-passwords-django.readthedocs.io/en/latest/validator.html>`_
  which integrates with `Django's password-validation tools
  <https://docs.djangoproject.com/en/5.0/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_
  and checks the Pwned Passwords database.

* `A Django middleware
  <https://pwned-passwords-django.readthedocs.io/en/latest/middleware.html>`_
  (supporting both sync and async requests) which automatically checks
  certain request payloads against the Pwned Passwords database.

* `An API client
  <https://pwned-passwords-django.readthedocs.io/en/latest/api.html>`_
  providing direct access (both sync and async) to the Pwned Passwords
  database.

All three use a secure, anonymized API which `never transmits any
password or its full hash to any third party
<https://pwned-passwords-django.readthedocs.io/en/latest/faq.html#api-safety>`_.


Usage
-----

The recommended configuration is to enable both the validator and the
automatic password-checking middleware. To do this, make the following
changes to your Django settings.

First, add the validator to your AUTH_PASSWORD_VALIDATORS list:

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       # ... other password validators ...
       {
           "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
       },
   ]

Then, add the middleware to your MIDDLEWARE list:

.. code-block:: python

   MIDDLEWARE = [
       # .. other middlewares ...
       "pwned_passwords_django.middleware.pwned_passwords_middleware",
   ]

For more details, consult `the full documentation
<https://pwned-passwords-django.readthedocs.io/>`_.
