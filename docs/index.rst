pwned-passwords-django |release|
==================================

pwned-passwords-django provides helpers for working with the `Pwned
Passwords database of Have I Been Pwned
<https://haveibeenpwned.com/Passwords>`_ in `Django
<https://www.djangoproject.com/>`_ powered sites. Pwned Passwords is
an extremely large database of passwords known to have been
compromised through data breaches, and is useful as a tool for
rejecting common or weak passwords.

There are three main components to this application:

* :ref:`A password validator <validator>` which checks the Pwned
  Passwords database.

* :ref:`A middleware <middleware>` which automatically checks certain
  request payloads against the Pwned Passwords database.

* :ref:`Code providing direct access <api>` to the Pwned Passwords
  database.

All three use a secure, anonymized API which never transmits the
password or its hash to any third party. To learn more, see :ref:`the
FAQ <faq>`.


Documentation contents
----------------------

.. toctree::
   :maxdepth: 1

   install
   validator
   middleware
   api
   exceptions
   settings
   faq
   changelog


.. seealso::

  * `About Have I Been Pwned <https://haveibeenpwned.com/About>`_
  * `The Pwned Passwords range-search API
    <https://haveibeenpwned.com/API/v3#SearchingPwnedPasswordsByRange>`_
