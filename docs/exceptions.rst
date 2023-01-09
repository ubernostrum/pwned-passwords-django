.. module:: pwned_passwords_django.exceptions

.. _exceptions:

Exception classes and error handling
====================================

Because pwned-passwords-django communicates with a remote API, it can encounter
problems, such as connection failures, connection timeouts, failures of the
Pwned Passwords API, and so on.

Exceptions raised in communicating with Pwned Passwords will be caught and
translated into instances of:

.. exception:: PwnedPasswordsError

   A wrapper for all exceptions raised in communicating with Pwned Passwords.

   Has the following attributes:

   .. attribute:: message

      A message (:class:`str`) describing the error.

   .. attribute:: code

      A short code indicating the type of error.

   .. attribute:: params

      A :class:`dict` of additional information about the situation -- such as
      the returned status code, or the timeout threshold, or attributes of the
      attempted request -- for debugging purposes.

The :attr:`~PwnedPasswordsError.code` attribute uses the following enum:

.. class:: ErrorCode

   .. attribute:: API_TIMEOUT

      An HTTP request to the Pwned Passwords API timed out.

   .. attribute:: HTTP_ERROR

      An HTTP request to the Pwned Passwords API returned an error (4XX or 5XX)
      status code.

   .. attribute:: REQUEST_ERROR

      Another type of error occurred in performing the request to the Pwned
      Passwords API.

   .. attribute:: UNKNOWN_ERROR

      An unanticipated or unknown type of error occurred, possibly in code in
      pwned-passwords-django. This can happen if, for example, the Pwned
      Passwords API begins returning responses in a different format than
      expected and so parsing of the response fails.


.. _error-handling:

How errors are handled
----------------------

When the :class:`~pwned_passwords_django.api.PwnedPasswords` client class
encounters a situation that requires raising a :exc:`PwnedPasswordsError`, it
will emit a log message of log level :data:`logging.ERROR` prior to raising the
exception. It will also raise the exception "from" the parent exception it
encountered, such as an ``httpx.TimeoutException`` or
``httpx.HttpStatusError``. If you are working directly with an instance of
:class:`~pwned_passwords_django.api.PwnedPasswords` or a customized subclass of
it, your code is responsible for catching and handling any
:exc:`PwnedPasswordsError` it raises.

When other parts of pwned-passwords-django encounter a
:exc:`PwnedPasswordsError` raised from the client, they will behave as follows:

* :ref:`The password validator <validator>` will catch the exception, log a
  message of log level :data:`logging.ERROR` and fall back to using Django's
  :class:`~django.contrib.auth.password_validation.CommonPasswordValidator`,
  which has a smaller (approximately 20k passwords) but locally-stored list of
  common passwords.

* :ref:`The middleware <middleware>` will catch the exception, log a message of
  log level :data:`logging.ERROR`, and fall back to Django's
  :class:`~django.contrib.auth.password_validation.CommonPasswordValidator`.

* The :func:`~pwned_passwords_django.api.check_password` and
  :func:`~pwned_passwords_django.api.check_password_async` functions will *not*
  catch exceptions for you; your code is responsible for catching and handling
  exceptions raised from them.


.. _filter-sensitive:

Filtering sensitive information
-------------------------------

Because pwned-passwords-django works with values that are (or, in the case of
the middleware, are likely to be) passwords or password-like credentials, care
must be taken to avoid accidentally exposing those values in their raw
form. This can easily happen by accident, for example, if an exception occurs
while trying to check a password, since the password will usually be a local
variable of the stack frame where the exception was raised, and thus is
available from inspecting the traceback. Or a password might accidentally find
its way into the message of an exception.

Django provides `some tools to filter sensitive information from error reports
<https://docs.djangoproject.com/en/stable/howto/error-reporting/#filtering-sensitive-information>`_,
and it is strongly recommended that if you write code which interacts with
pwned-passwords-django directly -- for example, via :ref:`the API <api>` -- you
take care to use those tools.

Internally, pwned-passwords-django takes the following measures:

* The ``validate()`` method of :ref:`the validator <validator>` is decorated
  with :func:`~django.views.decorators.debug.sensitive_variables` which will
  filter all of its local variables from Django's default logging and error
  reporting.

* The internal helper functions of :ref:`the middleware <middleware>` which
  actually scan the request payload for likely passwords are decorated with
  :func:`~django.views.decorators.debug.sensitive_variables`.

* The :func:`~pwned_passwords_django.api.check_password` and
  :func:`~pwned_passwords_django.api.check_password_async` functions pass
  through to methods of the same name on an instance of
  :class:`~pwned_passwords_django.api.PwnedPasswords`, which are decorated with
  :func:`~django.views.decorators.debug.sensitive_variables`.

* The error handling in :class:`~pwned_passwords_django.api.PwnedPasswords`,
  when it encounters an unknown/expected exception type, performs minimal
  logging of the exception's details. Only the class name of the caught
  exception will be logged, not its associated message or other arguments.

This approach can make debugging errors more difficult, but such difficulty is
generally preferable to accidental exposure of passwords via error-reporting
tools.
