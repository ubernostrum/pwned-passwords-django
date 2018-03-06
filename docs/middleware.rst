.. module:: pwned_passwords_django.middleware

.. _middleware:


Using the middleware
====================

.. class:: PwnedPasswordsMiddleware

   To help catch situations where a potentially-compromised password
   is used in ways Django's password validators won't catch,
   pwned-passwords-django also provides a middleware which monitors
   every incoming HTTP request for payloads which appear to contain
   passwords, and checks them against Pwned Passwords.

   To enable the middleware, add
   ``pwned_passwords_django.middleware.PwnedPasswordsMiddleware`` to
   your ``MIDDLEWARE`` setting. This will add a new attribute --
   ``pwned_passwords`` -- to each ``HttpRequest`` object. The
   ``request.pwned_passwords`` attribute will be a dictionary.

   .. warning:: **Middleware order**
   
      The order of middleware classes in the Django ``MIDDLEWARE``
      setting can be sensitive. In particular, any middlewares which
      affect file upload handlers *must* be listed above middlewares
      which inspect ``request.POST``. Since this middleware has to
      inspect ``request.POST`` for likely passwords, it must be listed
      after any middlewares which might change upload handlers. If
      you're unsure what this means, just put this middleware at the
      bottom of your ``MIDDLEWARE`` list.

   The ``request.pwned_passwords`` dictionary will be *empty* if any
   of the following is true:

   * The request method is not ``POST``

   * The request method is ``POST``, but the payload does not appear
     to contain a password

   * The request method is ``POST``, and the payload appears to
     contain a password, but the password is not listed as compromised
     in Pwned Passwords

   If the request method is ``POST``, and the payload appears to
   contain a password, and the password is listed in Pwned Passwords,
   then ``request.pwned_passwords`` will contain a key corresponding
   to the key in ``request.POST`` which appeared to contain a
   password, and the value associated with that key will be the number
   of times that password appears in the Pwned Passwords database.

   Here's an example of how you might use `Django's message framework
   <https://docs.djangoproject.com/en/2.0/ref/contrib/messages/>`_ to
   indicate to a user that they've just submitted a password that
   appears to be compromised:

   .. code-block:: python

      from django.contrib import messages


      def some_view(request):
          if request.method == 'POST' and request.pwned_passwords:
              messages.warning(
                  request,
                  'You just entered a password which appears to be compromised!'
              )

   pwned-passwords-django uses a regular expression to guess which
   items in ``request.POST`` are likely to be passwords. By default,
   it matches on any key in ``request.POST`` containing ``'PASS'``
   (case-insensitive), which catches input names like ``'password'``,
   ``'passphrase'``, and so on. If you use something significantly
   different than this for a password input name, specify it -- as a
   raw string, *not* as a compiled regex object! -- in the setting
   ``PWNED_PASSWORDS_REGEX`` to tell the middleware what to look for.


