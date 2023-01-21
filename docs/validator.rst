.. module:: pwned_passwords_django.validators

.. _validator:


Using the password validator
============================

.. class:: PwnedPasswordsValidator

   Django's auth system (located in ``django.contrib.auth``) includes `a
   configurable password-validation framework
   <https://docs.djangoproject.com/en/stable/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_
   with several built-in validators, and pwned-passwords-django provides an
   additional validator which checks the Pwned Passwords database. To enable
   it, set your :setting:`AUTH_PASSWORD_VALIDATORS` setting to include the new
   validator, like so:

   .. code-block:: python

      AUTH_PASSWORD_VALIDATORS = [
          # ... other password validators ...
          {
              "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
          },
      ]

   This will cause most high-level password-setting operations to check the
   Pwned Passwords database, and reject any password found there.

   .. warning:: **API failures**

      pwned-passwords-django needs to communicate with the Pwned Passwords API
      in order to check passwords. If Pwned Passwords is down or timing out
      (the default connection timeout is 1 second), or if any other error
      occurs when checking the password, this validator will fall back to using
      Django's
      :class:`~django.contrib.auth.password_validation.CommonPasswordValidator`,
      which uses a smaller, locally-stored list of common passwords. Whenever
      this happens, a message of level :data:`logging.ERROR` will appear in
      your logs, indicating what type of failure was encountered in talking to
      the Pwned Passwords API.

      See :ref:`the error-handling documentation <exceptions>` for details.

   This validator implements the following standard Django password-validator
   method. It will be called automatically by Django at appropriate times, and
   you should not ever need to call it yourself unless you are performing
   low-level/manual password changes (not recommended):

   .. automethod:: validate


.. _validator-limitations:

Limitations
-----------

As mentioned above, Django automatically runs password validators on certain
high-level operations. These operations are:

* Whenever a user changes or resets their password with Django's built-in auth
  views and forms.

* Whenever a new user is created via Django's built-in
  :class:`~django.contrib.auth.forms.UserCreationForm`.

* Whenever the ``createsuperuser`` or ``changepassword`` management commands
  are used.

Password validators are **not** run automatically when a user's password is set
or updated via other mechanisms, and in those cases the validator cannot
provide automatic protection against a user choosing a breached password.

Thus the best approach is always to use the built-in Django auth components,
and avoid setting/updating passwords via other mechanisms. But if you *must*
work manually with passwords, it is recommended that you do the following:

1. Prior to manually setting or changing a password, call
   :func:`django.contrib.auth.password_validation.validate_password` on the
   proposed new password. This will manually run all password validators
   configured in your :setting:`AUTH_PASSWORD_VALIDATORS` setting. You must be
   prepared to catch :exc:`~django.core.exceptions.ValidationError` when doing
   so.

2. Then use the :meth:`~django.contrib.auth.models.User.set_password()` method
   of the user model to set the password *after* successfully validating it.

It is also strongly recommended that you enable :ref:`the middleware provided
by pwned-passwords-django <middleware>`, which provides a way to check every
incoming HTTP ``POST`` payload for potentially-compromised passwords.


.. _validator-messages:

Customizing the validator
-------------------------

To change the error or help messages shown to the user, you can pass
``OPTIONS`` when adding the validator to your settings:

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       # ... other password validators ...
       {
           "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
           "OPTIONS": {
               "error_message": "That password was pwned",
               "help_message": "Your password can't be a commonly used password.",
           }
       },
   ]

The number of times the password has appeared in a breach can also be included
in the error message, including a plural form:

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       # ... other password validators ...
       {
           "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
           "OPTIONS": {
               "error_message": (
                  "Pwned %(amount)d time",
                  "Pwned %(amount)d times",
               )
           }
       },
   ]
