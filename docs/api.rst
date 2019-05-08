.. module:: pwned_passwords_django.api

.. _api:

Using the Pwned Passwords API directly
======================================

If the validator and middleware do not cover your needs, you can also
directly check a password against Pwned Passwords.

.. function:: pwned_password(password)

   Given a password, checks it against the Pwned Passwords database
   and returns a count of the number of times that password occurs in
   the database.

   The password to check **must** be a Unicode string (the type
   :class:`str` on Python 3, :class:`unicode` on Python 2). Passing a
   bytes object (:class:`bytes` on Python 3, :class:`str` on Python 2)
   will raise :exc:`TypeError`.

   .. warning:: **API failures**

      pwned-passwords-django needs to communicate with the Pwned
      Passwords API in order to check passwords. If Pwned Passwords is
      down or timing out (the default connection timeout is 1 second),
      this function will not re-try the check or fall back to an
      alternate mechanism; it will return :data:`None`. Whenever this
      happens, a message of level :data:`logging.WARNING` will appear
      in your logs, indicating what type of failure was encountered in
      talking to the Pwned Passwords API.

   :param password: The password to check.
   :type password: Unicode string
   :rtype: :class:`int` or :data:`None`
