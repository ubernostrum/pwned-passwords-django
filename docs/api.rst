.. module:: pwned_passwords_django.api

.. _api:



Using the Pwned Passwords API directly
======================================

If the validator and middleware do not cover your needs, you can also
directly check a password against Pwned Passwords.

.. function:: pwned_password(password)

   Given a password, checks it against the Pwned Passwords database
   and returns a count of the number of times that password occurs in
   the database, or ``None`` if it is not found.

   The password to check **must** be a Unicode string (the type
   ``str`` on Python 3, ``unicode`` on Python 2). Passing a bytes
   object (``bytes`` on Python 3, ``str`` on Python 2) will raise
   ``TypeError``.

   :param password: The password to check.
   :type password: Unicode string
   :rtype: ``int`` or ``None``
