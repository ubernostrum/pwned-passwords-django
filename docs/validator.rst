.. module:: pwned_passwords_django.validators

.. _validator:


Using the password validator
============================

.. class:: PwnedPasswordsValidator

   Django's auth system (located in ``django.contrib.auth``) includes
   `a configurable password-validation framework
   <https://docs.djangoproject.com/en/1.11/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_
   with several built-in validators. pwned-passwords-django provides
   an additional validator which checks the Pwned Passwords
   database. To enable it, set your ``AUTH_PASSWORD_VALIDATORS``
   setting to include
   ``pwned_passwords_django.validators.PwnedPasswordsValidator``, like
   so:

   .. code-block:: python

      AUTH_PASSWORD_VALIDATORS = [
          {
              'NAME': 'pwned_passwords_django.validators.PwnedPasswordsValidator',
          },
      ]

   This will cause most high-level password-setting operations to
   check the Pwned Passwords database, and reject any password found
   there. Specifically, password validators are applied:

   * Whenever a user changes or resets their password with Django's
     built-in auth views

   * Whenever a new user is created via Django's built-in
     ``UserCreationForm``

   * Whenever the ``createsuperuser`` or ``changepassword`` management
     commands are used

   * Whenever an instance of the built-in ``User`` model is saved after
     the instance's ``set_password()`` method has been called.

   Keep in mind that validation is **not** run when code sets or
   changes a user's password in other ways. If you manipulate user
   passwords through means other than the high-level APIs listed
   above, you'll need to manually check passwords.


Configuration options
=====================

You can change several options on the validator via the ``OPTIONS`` key on the validation entry in the
``AUTH_PASSWORD_VALIDATORS`` setting.


   .. code-block:: python

      AUTH_PASSWORD_VALIDATORS = [
          {
              'NAME': 'pwned_passwords_django.validators.PwnedPasswordsValidator',
              'OPTIONS': {
                  'timeout': 0.6,
              },
          },
      ]

* ``timeout`` changes the request timeout to the API, in seconds. Defaults to 0.6 seconds.
