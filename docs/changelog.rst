.. _changelog:


Changelog
=========

This document lists changes between released versions of
pwned-passwords-django.


1.2 -- released 2018-03-??
--------------------------

New features:
~~~~~~~~~~~~~

* Password-validator error messages are now :ref:`customizable
  <validator-messages>`.

* The request-timeout value for contacting the Pwned Passwords API
  defaults to one second, and is customizable via the setting
  :data:`~django.conf.settings.PWNED_PASSWORDS_API_TIMEOUT`.

* When a request to the Pwned Passwords API times out, or encounters
  an error, it now logs a warning and skips the Pwned Passwords check.

* In the event of a HIBP API failure, the Pwned Passwords validator now falls
  back to Django's ``CommonPasswordValidator``.

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


