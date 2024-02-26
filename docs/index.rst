``pwned-passwords-django`` |release|
====================================

``pwned-passwords-django`` provides helpers for working with the `Pwned
Passwords database of Have I Been Pwned
<https://haveibeenpwned.com/Passwords>`_ in `Django
<https://www.djangoproject.com/>`_ powered sites. Pwned Passwords is an
extremely large database of passwords known to have been compromised through
data breaches, and is useful as a tool for rejecting common or weak passwords.

There are three main components to this application:

* :ref:`A password validator <validator>` which integrates with `Django's
  password-validation tools
  <https://docs.djangoproject.com/en/5.0/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_
  and checks the Pwned Passwords database.

* :ref:`A Django middleware <middleware>` (supporting both sync and async
  requests) which automatically checks certain request payloads against the
  Pwned Passwords database.

* :ref:`An API client <api>` providing direct access (both sync and async) to
  the Pwned Passwords database.

All three use a secure, anonymized API which never transmits any password or
its full hash to any third party. To learn more, see :ref:`the FAQ <faq>`.


Usage
-----

The recommended configuration is to enable both :ref:`the password validator
<validator>` and :ref:`the automatic password-checking middleware
<middleware>`. To do this, make the following changes to your Django settings.

First, add :ref:`the validator <validator>` to your
:setting:`AUTH_PASSWORD_VALIDATORS` list:

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       # ... other password validators ...
       {
           "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
       },
   ]

Then, add :ref:`the middleware <middleware>` to your :setting:`MIDDLEWARE`
list:

.. code-block:: python

   MIDDLEWARE = [
       # .. other middlewares ...
       "pwned_passwords_django.middleware.pwned_passwords_middleware",
   ]


Documentation contents
----------------------

.. toctree::
   :maxdepth: 1

   install
   validator
   middleware
   api
   exceptions
   settings
   faq
   changelog


.. seealso::

  * `About Have I Been Pwned <https://haveibeenpwned.com/About>`_
  * `The Pwned Passwords range-search API
    <https://haveibeenpwned.com/API/v3#SearchingPwnedPasswordsByRange>`_
