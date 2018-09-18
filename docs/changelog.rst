.. _changelog:


Changelog
=========

This document lists changes between released versions of
pwned-passwords-django.


1.3.1 -- released 2018-09-18
----------------------------

Released to include documentation updates which were inadvertently
left out of the 1.3 package.


1.3 -- released 2018-09-18
--------------------------

No new features. No bug fixes. Released only to add explicit markers of
Python 3.7 and Django 2.1 compatibility.


1.2.1 -- released 2018-06-18
----------------------------

Released to correct the date of the 1.2 release listed in this
changelog document. No other changes.


1.2 -- released 2018-06-18
--------------------------

New features:
~~~~~~~~~~~~~

* Password-validator error messages are now :ref:`customizable
  <validator-messages>`.

* The request-timeout value for contacting the Pwned Passwords API
  defaults to one second, and is customizable via the setting
  :data:`~django.conf.settings.PWNED_PASSWORDS_API_TIMEOUT`.

* When a request to the Pwned Passwords API times out, or encounters
  an error, it logs the problem with a message of level
  ``logging.WARNING``. The
  :class:`~pwned_passwords_django.validators.PwnedPasswordsValidator`
  will fall back to `Django's CommonPasswordValidator
  <https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#django.contrib.auth.password_validation.CommonPasswordValidator>`_,
  which has a smaller list of common passwords. The
  :class:`~pwned_passwords_django.middleware.PwnedPasswordsMiddleware`
  does not have a fallback behavior;
  :func:`~pwned_passwords_django.api.pwned_password` will return
  ``None`` to indicate the error case.

Bugs fixed:
~~~~~~~~~~~

N/A

Other changes:
~~~~~~~~~~~~~~

* :func:`~pwned_passwords_django.api.pwned_password` will now raise
  ``TypeError`` if its argument is not a Unicode string (the type
  ``unicode`` on Python 2, ``str`` on Python 3). This is debatably
  backwards-incompatible; ``pwned_password()`` encodes its argument to
  UTF-8 bytes, which will raise ``AttributeError`` if attempted on a
  ``bytes`` object in Python 3. As a result, all supported
  environments other than Python 2.7/Django 1.11 would already raise
  ``AttributeError`` (due to ``bytes`` objects lacking the
  ``encode()`` method) in both 1.0 and 1.1. Enforcing the
  ``TypeError`` on all supported environments ensures users of
  pwned-passwords-django do not write code that accidentally works in
  one and only one environment, and supplies a more accurate and
  comprehensible exception than the ``AttributeError`` which would
  have been raised in previous versions.

* The default error and help messages of
  :class:`~pwned_passwords_django.validators.PwnedPasswordsValidator`
  now match the messages of Django's
  ``CommonPasswordValidator``. Since ``PwnedPasswordsValidator`` falls
  back to ``CommonPasswordValidator`` when the Pwned Passwords API is
  unresponsive, this provides consistency of messages, and also
  ensures the messages are translated (Django provides translations
  for its built-in messages).


1.1 -- released 2018-03-06
----------------------------

New features:
~~~~~~~~~~~~~

N/A

Bugs fixed:
~~~~~~~~~~~

* Case sensitivity issue. The Pwned Passwords API always uses
  uppercase hexadecimal digits for password hashes;
  pwned-passwords-django was using lowercase. Fixed by switching
  pwned-passwords-django to use uppercase.

Other changes
~~~~~~~~~~~~~

N/A


1.0 -- released 2018-03-06
--------------------------

Initial public release.


