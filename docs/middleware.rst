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
   `'pwned_passwords_django.middleware.PwnedPasswordsMiddleware'` to
   your :data:`~django.conf.settings.MIDDLEWARE` setting. This will
   add a new attribute -- `pwned_passwords` -- to each
   :class:`~django.http.HttpRequest` object. The
   `request.pwned_passwords` attribute will be a dictionary.

   .. warning:: **Middleware order**
   
      The order of middleware classes in the Django
      :data:`~django.conf.settings.MIDDLEWARE` setting can be
      sensitive. In particular, any middlewares which affect file
      upload handlers *must* be listed above middlewares which inspect
      :attr:`~django.http.HttpRequest.POST`. Since this middleware has
      to inspect :attr:`~django.http.HttpRequest.POST` for likely
      passwords, it must be listed after any middlewares which might
      change upload handlers. If you're unsure what this means, just
      put this middleware at the bottom of your
      :data:`~django.conf.settings.MIDDLEWARE` list.

   The `request.pwned_passwords` dictionary will be *empty* if any
   of the following is true:

   * The request method is not `POST`.

   * The request method is `POST`, but the payload does not appear
     to contain a password.

   * The request method is `POST`, and the payload appears to
     contain a password, but the password is not listed as compromised
     in Pwned Passwords.

   If the request method is `POST`, and the payload appears to contain
   a password, and the password is listed in Pwned Passwords, then
   `request.pwned_passwords` will contain a key corresponding to the
   key in :attr:`~django.http.HttpRequest.POST` which appeared to
   contain a password, and the value associated with that key will be
   the number of times that password appears in the Pwned Passwords
   database.

   For example, if :attr:`~django.http.HttpRequest.POST` contains a
   key named `password`, and the value associated with it appears 42
   times in the Pwned Passwords database, `request.pwned_passwords`
   will be `{'password': 42}`.

   .. warning:: **API failures**

      pwned-passwords-django needs to communicate with the Pwned
      Passwords API in order to check passwords. If Pwned Passwords is
      down or timing out (the default connection timeout is 1 second),
      this middleware will not re-try the check or fall back to an
      alternate mechanism; it will leave `request.pwned_passwords`
      empty. Whenever this happens, a message of level
      :data:`logging.WARNING` will appear in your logs, indicating what
      type of failure was encountered in talking to the Pwned
      Passwords API.
      
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
   items in :attr:`~django.http.HttpRequest.POST` are likely to be
   passwords. By default, it matches on any key in
   :attr:`~django.http.HttpRequest.POST` containing `'PASS'`
   (case-insensitive), which catches input names like `'password'`,
   `'passphrase'`, and so on. If you use something significantly
   different than this for a password input name, specify it -- as a
   raw string, *not* as a compiled regex object! -- in the setting
   :data:`~django.conf.settings.PWNED_PASSWORDS_REGEX` to tell the
   middleware what to look for.


