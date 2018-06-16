.. module:: pwned_passwords_django.validators

.. _validator:


Using the password validator
============================

.. class:: PwnedPasswordsValidator

   Django's auth system (located in ``django.contrib.auth``) includes
   `a configurable password-validation framework
   <https://docs.djangoproject.com/en/1.11/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_
   with several built-in validators; pwned-passwords-django provides
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
     built-in auth views.

   * Whenever a new user is created via Django's built-in
     ``UserCreationForm``.

   * Whenever the ``createsuperuser`` or ``changepassword`` management
     commands are used.

   * Whenever an instance of the built-in ``User`` model is saved after
     the instance's ``set_password()`` method has been called.

   Keep in mind that validation is **not** run when code sets or
   changes a user's password in other ways. If you manipulate user
   passwords through means other than the high-level APIs listed
   above, you'll need to manually check passwords.

   .. warning:: **API failures**

      pwned-passwords-django needs to communicate with the Pwned
      Passwords API in order to check passwords. If Pwned Passwords is
      down or timing out (the default connection timeout is 1 second),
      this validator will fall back to using `Django's
      CommonPasswordValidator
      <https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#django.contrib.auth.password_validation.CommonPasswordValidator>`_,
      which uses a smaller, locally-stored list of common
      passwords. Whenever this happens, a message of level
      ``logging.WARNING`` will appear in your logs, indicating what
      type of failure was encountered in talking to the Pwned
      Passwords API.


.. _validator-messages:

Customizing the validator's messages
====================================

To change the error or help messages shown to the user, you can set
them in the ``OPTIONS`` dictionary like so:

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       {
           'NAME': 'pwned_passwords_django.validators.PwnedPasswordsValidator',
           'OPTIONS': {
               'error_message': 'That password was pwned',
               'help_message': 'Your password can\'t be a commonly used password.',
           }
       },
   ]

The number of times the password has appeared in a breach can also be
included in the error message, including a plural form:

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       {
           'NAME': 'pwned_passwords_django.validators.PwnedPasswordsValidator',
           'OPTIONS': {
               'error_message': (
                  'Pwned %(amount)d time',
                  'Pwned %(amount)d times',
               )
           }
       },
   ]
