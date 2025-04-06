.. _changelog:


Changelog
=========

This document lists changes between released versions of
``pwned-passwords-django``.

Version numbering
-----------------

``pwned-passwords-django`` uses "DjangoVer", a version number system based on
the corresponding supported Django versions. The format of a
``pwned-passwords-django`` version number is ``A.B.C``, where ``A.B`` is the
version number of the latest Django feature release supported by that version
of ``pwned-passwords-django``, and ``C`` is an incrementing value for releases
of ``pwned-passwords-django`` paired to that Django feature release.

The policy of ``pwned-passwords-django`` is to support the Django feature
release indicated in the version number, along with any other lower-numbered
Django feature releases receiving support from the Django project at the time
of release.

For example, consider a hypothetical ``pwned-passwords-django`` version
5.0.2. This indicates that the most recent supported Django feature release is
5.0, and that it is the third release of ``pwned-passwords-django`` to support
Django 5.0 (after 5.0.0 and 5.0.1). Since the Django project at the time was
supporting Django 5.0 and 4.2, that version of ``pwned-passwords-django`` would
also support Django 5.0 and 4.2.


API stability and deprecations
------------------------------

The API stability/deprecation policy for ``pwned-passwords-django`` is as follows:

* The supported stable public API is the set of symbols which are documented in
  this documentation. For classes, the supported stable public API is the set
  of methods and attributes of those classes whose names do not begin with one
  or more underscore (``_``) characters and which are documented in this
  documentation.

* When a public API is to be removed, or undergo a backwards-incompatible
  change, it will emit a deprecation warning which serves as notice of the
  intended removal or change. This warning will be emitted for at least two
  releases, after which the removal or change may occur without further
  warning. This is different from Django's own deprecation policy, which avoids
  completing a removal/change in "LTS"-designated releases. Since
  ``pwned-passwords-django`` does not have "LTS" releases, it does not need
  that exception.

* Security fixes, and fixes for high-severity bugs (such as those which might
  cause unrecoverable crash or data loss), are not required to emit deprecation
  warnings, and may -- if needed -- impose backwards-incompatible change in any
  release. If this occurs, this changelog document will contain a note
  explaining why the usual deprecation process could not be followed for that
  case.

* This policy is in effect as of the adoption of "DjangoVer" versioning, with
  version 5.0.0 of ``pwned-passwords-django``.


Releases under DjangoVer
------------------------

Version 5.2
~~~~~~~~~~~

Released April 2025

* Supported Django versions are now 4.2, 5.1, and 5.2. Support for Django 5.0 has been
  dropped.


Version 5.1.3
~~~~~~~~~~~~~

Released March 2025

* Ensured multi-value POST payloads are correctly checked by the middleware. This is
  likely an edge case since even when multiple submissions of a password are desired
  they are typically differently-named fields in the payload (i.e., a "password" and
  "confirm password" field in a signup or password change form), but for completeness'
  sake they should still be handled correctly.


Version 5.1.2
~~~~~~~~~~~~~

Released March 2025

* Fixed a bug where the fallback to Django's common-password validator `would
  pass the wrong value to the fallback validator
  <https://github.com/ubernostrum/pwned-passwords-django/pull/43>`_.


Version 5.1.1
~~~~~~~~~~~~~

Released November 2024

* Supported Python versions are now 3.9, 3.10, 3.11, 3.12, and 3.13.


Version 5.1.0
~~~~~~~~~~~~~

Released August 2024

* Supported Django versions are now 4.2, 5.0, and 5.1.


Version 5.0.0
~~~~~~~~~~~~~

Released May 2024

* Adopted "DjangoVer" versioning.

* Supported Django versions are now 4.2 and 5.0.

* Expanded/reorganized documentation.


Releases not under DjangoVer
----------------------------

Version 2.1
~~~~~~~~~~~

Released February 2024

* Supported Django versions are now 3.2, 4.2, and 5.0; supported Python
  versions are 3.8, 3.9, 3.10, 3.11, and 3.12.

* Source code formatting was updated to Black 2024 style.

* Some internal test code was rewritten to use HTTPX ``MockTransport`` objects.


Version 2.0
~~~~~~~~~~~

Released March 2023

* Major version bump. Much of the codebase has been rewritten and improved.

The following changes in 2.0 are backwards-incompatible with 1.x releases:

Configuration changes
+++++++++++++++++++++

In 1.x, ``pwned-passwords-django`` was configured by two top-level Django
settings: ``PWNED_PASSWORDS_API_TIMEOUT`` and ``PWNED_PASSWORDS_REGEX``. As of
2.0, configuration uses one top-level Django setting, ``PWNED_PASSWORDS``,
which is a :class:`dict` containing any of :ref:`several optional keys
<settings>` to configure behavior.

Here is an example of old 1.x configuration:

.. code-block:: python

   PWNED_PASSWORDS_API_TIMEOUT = 1.5 # one and a half seconds

   PWNED_PASSWORDS_REGEX = r"TOKEN"

And here is the corresponding configuration for 2.0:

.. code-block:: python

   PWNED_PASSWORDS = {
       "API_TIMEOUT": 1.5, # one and a half seconds
       "PASSWORD_REGEX": r"TOKEN",
   }


Validator changes
+++++++++++++++++

In 1.x, when the password validator encountered an error communicating with
Pwned Passwords, it would fall back to Django's
:class:`~django.contrib.auth.password_validation.CommonPasswordValidator` after
logging a message of log level :data:`logging.WARNING`. In 2.0, it continues to
fall back to ``CommonPasswordValidator``, but the log message is now of log
level :data:`logging.ERROR`.


Middleware changes
++++++++++++++++++

In 1.x, the middleware was a class --
``pwned_passwords_django.middleware.PwnedPasswordsMiddleware`` -- while in 2.0
it is a factory function,
:func:`pwned_passwords_django.middleware.pwned_passwords_middleware`. If you
were using the middleware, you will need to update your :setting:`MIDDLEWARE`
setting.

The middleware in 2.0 supports both synchronous and asynchronous usage, and
will automatically select the correct sync or async code path on a per-request
basis, including use of a sync or async HTTP client to make requests to Pwned
Passwords.

In 1.x, the middleware set the ``request.pwned_passwords`` attribute to a
:class:`dict`, where the keys were keys from
:attr:`~django.http.HttpRequest.POST` that contained compromised passwords, and
the values were the corresponding breach counts for those passwords. In 2.0,
``request.pwned_passwords`` is a :class:`list` of :class:`str`, whose elements
are the keys from :attr:`~django.http.HttpRequest.POST` that contained
compromised passwords. This means that it is no longer possible to get the
breach count for a password from the middleware.

However, the format of ``request.pwned_passwords`` in 1.x meant that the
middleware could not have a consistent fallback in case of errors communicating
with Pwned Passwords; as a result of the change to a :class:`list` in 2.0, the
middleware is now able to fall back to Django's
:class:`~django.contrib.auth.password_validation.CommonPasswordValidator` when
an error occurs in a request to Pwned Passwords, which is a safer failure mode
than was previously possible. This also brings makes the behavior of the
middleware consistent with the validator; see :ref:`the new error-handling
documentation <exceptions>` for details.

Also, as with the validator, the log message recorded when an error occurs
communicating with Pwned Passwords has been changed from log level
:data:`logging.WARNING` to :data:`logging.ERROR`.


Direct API changes
++++++++++++++++++

In 1.x, direct access to the Pwned Passwords API was available through the
function ``pwned_passwords_django.api.pwned_password``, which took a password
and returned either the count of times it had been breached, or :data:`None` in
the event of an error.

In 2.0, this has been replaced by two functions: the synchronous
:func:`~pwned_passwords_django.api.check_password`, and the asynchronous
:func:`~pwned_passwords_django.api.check_password_async`. Both of these
functions take a password and return a count of times it has been breached;
rather than returning :data:`None` or some other sentinel value, they raise
exceptions in the event of errors communicating with Pwned Passwords. Your code
which calls these functions is responsible for catching and handling exceptions
raised from them; see :ref:`the new error-handling documentation <exceptions>`
for details.

A new :class:`~pwned_passwords_django.api.PwnedPasswords` API client class is
also provided; the above-mentioned functions are aliases to methods of a
default instance of this client class. See :ref:`the direct API access
documentation <api>` for details of how it may be used and customized.


Error handling changes
++++++++++++++++++++++

In 1.x, errors were caught and handled in a variety of different ways by
different parts of ``pwned-passwords-django``. In 2.0, error handling is much
more unified:

* All external exceptions raised when communicating with Pwned Passwords are
  caught and wrapped in
  :exc:`~pwned_passwords_django.exceptions.PwnedPasswordsError`, meaning that
  code which works with ``pwned-passwords-django`` should only need to catch
  and be able to understand that one exception class.

* All exception paths also consistently log messages of log level
  :data:`logging.ERROR`.

* As noted above, the validator and middleware error handling has been made
  consistent: both will fall back to Django's ``CommonPasswordValidator`` in
  the event of errors communicating with Pwned Passwords.

Additionally, as a side effect of better/more unified error handling, code
paths in ``pwned-passwords-django`` that handle passwords or likely passwords
now have had Django's
:func:`~django.views.decorators.debug.sensitive_variables` decorator applied to
help prevent accidental appearance of raw password values in error reports, and
the explicit error-handling code in ``pwned-passwords-django`` deliberately
minimizes the amount of information reported for unknown/unanticipated
exceptions, to further reduce the risk of this issue.

See :ref:`the error-handling documentation <error-handling>` for details.


Dependency changes
++++++++++++++++++

In 1.x, the underlying HTTP client library for communicating with Pwned
Passwords was `requests <https://requests.readthedocs.io/en/latest/>`_. In 2.0,
it is `HTTPX <https://www.python-httpx.org>`_, which is broadly API-compatible
but provides several additional features (such as async support). The new
:class:`~pwned_passwords_django.api.PwnedPasswords` API client class can use an
instance of any object API-compatible with ``httpx.Client`` as its synchronous
client, and any object API-compatible with ``httpx.AsyncClient`` as its
asynchronous client. This means that, for example, a ``requests.Session`` could
still be passed in to a custom
:class:`~pwned_passwords_django.api.PwnedPasswords` instance and used as the
synchronous HTTP client, if desired (though see the note in the documentation
of :class:`~pwned_passwords_django.api.PwnedPasswords` regarding error handling
with alternate HTTP clients).

In 1.x, the test suite and continuous integration of ``pwned-passwords-django``
were orchestrated using the ``tox`` automation tool. In 2.0, they are
orchestrated using `nox <https://nox.thea.codes/en/stable/>`_ instead.


Version 1.6.1
~~~~~~~~~~~~~

Released December 2022

* Bugfix release: the Pwned Passwords API was reported to sometimes return the
  count as a value with a comma in it, which requires additional handling. No
  other changes; a release for official compatibility with Python 3.11 and
  Django 4.1 will occur later.


Version 1.6
~~~~~~~~~~~

Released May 2022

* Django 4.0 is now supported. Python 3.6, Django 2.2, and Django 3.1 are no
  longer supported, as they have reached the end of their upstream support
  cycles.


Version 1.5
~~~~~~~~~~~

Released June 2021

* Django 3.2 is now supported; Django 3.0 and Python 3.5 are no longer
  supported, as they have both reached the end of their upstream support
  cycles.


Version 1.4
~~~~~~~~~~~

Released January 2020

* The :class:`~pwned_passwords_django.validators.PwnedPasswordsValidator` is
  now serializable. This is unlikely to be useful, however, as the validator is
  not intended to be attached to a model.

* The supported versions of Django are now 2.2 and 3.0. This means Python 2
  support is dropped; if you still need to use ``pwned-passwords-django`` on
  Python 2 with Django 1.11, stay with the 1.3 release series of
  ``pwned-passwords-django``.


Version 1.3.2
~~~~~~~~~~~~~

Released May 2019

* Released to add explicit markers of Django 2.2 compatibility.


Version 1.3.1
~~~~~~~~~~~~~

Released September 2018

* Released to include documentation updates which were inadvertently left out
  of the 1.3 package.


Version 1.3
~~~~~~~~~~~

Released September 2018

* Released to add explicit markers of Python 3.7 and Django 2.1 compatibility.


Version 1.2.1
~~~~~~~~~~~~~

Released June 2018

* Released to correct the date of the 1.2 release listed in this changelog
  document.


Version 1.2
~~~~~~~~~~~

Released June 2018

* Password-validator error messages are now :ref:`customizable
  <validator-messages>`.

* The request-timeout value for contacting the Pwned Passwords API defaults to
  one second, and is customizable via the setting
  :data:`~django.conf.settings.PWNED_PASSWORDS_API_TIMEOUT`.

* When a request to the Pwned Passwords API times out, or encounters an error,
  it logs the problem with a message of level :data:`logging.WARNING`. The
  :class:`~pwned_passwords_django.validators.PwnedPasswordsValidator` will fall
  back to
  :class:`~django.contrib.auth.password_validation.CommonPasswordValidator`,
  which has a smaller list of common passwords. The
  :class:`~pwned_passwords_django.middleware.PwnedPasswordsMiddleware` does not
  have a fallback behavior; :func:`~pwned_passwords_django.api.pwned_password`
  will return :data:`None` to indicate the error case.

* :func:`~pwned_passwords_django.api.pwned_password` will now raise
  :exc:`TypeError` if its argument is not a Unicode string (the type
  :class:`unicode` on Python 2, :class:`str` on Python 3). This is debatably
  backwards-incompatible; :func:`~pwned_passwords_django.api.pwned_password`
  encodes its argument to UTF-8 bytes, which will raise :exc:`AttributeError`
  if attempted on a :class:`bytes` object in Python 3. As a result, all
  supported environments other than Python 2.7/Django 1.11 would already raise
  :exc:`AttributeError` (due to :class:`bytes` objects lacking the
  :meth:`~str.encode` method) in both 1.0 and 1.1. Enforcing the
  :exc:`TypeError` on all supported environments ensures users of
  ``pwned-passwords-django`` do not write code that accidentally works in one
  and only one environment, and supplies a more accurate and comprehensible
  exception than the :exc:`AttributeError` which would have been raised in
  previous versions.

* The default error and help messages of
  :class:`~pwned_passwords_django.validators.PwnedPasswordsValidator` now match
  the messages of Django's
  :class:`~django.contrib.auth.password_validation.CommonPasswordValidator`. Since
  :class:`~pwned_passwords_django.validators.PwnedPasswordsValidator` falls
  back to
  :class:`~django.contrib.auth.password_validation.CommonPasswordValidator`
  when the Pwned Passwords API is unresponsive, this provides consistency of
  messages, and also ensures the messages are translated (Django provides
  translations for its built-in messages).


Version 1.1
~~~~~~~~~~~

Released March 2018

* Fixed case sensitivity issue. The Pwned Passwords API always uses uppercase
  hexadecimal digits for password hashes; ``pwned-passwords-django`` was using
  lowercase. Fixed by switching ``pwned-passwords-django`` to use uppercase.


Version 1.0
~~~~~~~~~~~

Released March 2018

* Initial public release.
