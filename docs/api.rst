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

   :param password: The password to check.
   :type password: ``str``
   :rtype: ``int`` or ``None``
