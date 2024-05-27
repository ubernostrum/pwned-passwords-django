.. _usage:


Usage guide
===========

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

This will cause user creation (provided it's done via Django's built-in
:class:`~django.contrib.auth.forms.UserCreationForm` or a subclass, or via
Django's ``createsuperuser`` management command) and password changes (via the
built-in Django password-change views/forms, and the ``changepassword``
management comment) to check the Pwned Passwords database, and reject any
password found there.

Then, add :ref:`the middleware <middleware>` to your :setting:`MIDDLEWARE`
list:

.. code-block:: python

   MIDDLEWARE = [
       # .. other middlewares ...
       "pwned_passwords_django.middleware.pwned_passwords_middleware",
   ]

This will add the attribute ``pwned_passwords`` to every Django
:class:`~django.http.HttpRequest` object. The value of this attribute will be a
:class:`list` of :class:`str`, where each item in the list is the name of a
field in ``request.POST`` believed to contain a compromised password. If the
request method was not ``POST``, did not appear to contain any passwords, or no
compromised passwords were detected, the ``request.pwned_passwords`` list will
be empty.


Identifying passwords in request payloads
-----------------------------------------

By default, the middleware checks any field in ``request.POST`` whose name is a
case-insensitive match for the regex ``r"PASS"``. This will catch many common
password field names, such as ``"password"``, ``"passphrase"``, and so on. But
if your site uses something significantly different, you will need to configure
``pwned-passwords-django`` to check for it. You can do this by specifying the
Django setting ``PWNED_PASSWORDS`` as a dictionary, and placing a regex -- as a
string, not as a compiled regex object -- in the key ``"PASSWORD_REGEX"`` of
that dictionary. For example, if your site uses a field named ``"token"``
for its passwords, you could specify this in your Django settings:

.. code-block:: python

   PWNED_PASSWORDS = {
       "PASSWORD_REGEX": r"token",
   }

See :ref:`the settings documentation <settings>` for full details.
