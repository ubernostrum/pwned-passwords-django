.. _install:

Installation
============

pwned-passwords-django |release| supports Django 1.11 and Django 2.0,
on Python versions supported by those versions of Django:

* Django 1.11 supports Python 2.7, 3.4, 3.5, and 3.6.

* Django 2.0 supports Python 3.4, 3.5, and 3.6.

To install pwned-passwords-django, run::

    pip install pwned-passwords-django

This will use ``pip``, the standard Python package-installation
tool. If you are using a supported version of Python, your
installation of Python came with ``pip`` bundled, but if it is
missing, instructions are available for `how to obtain and install it
<https://pip.pypa.io/en/latest/installing.html>`_.

If you don't already have a supported version of Django installed,
using ``pip`` to install pwned-passwords-django will also install the
latest supported version of Django.


Configuration and use
=====================

You may need to modify certain Django settings, depending on how you'd
like to use ``pwned-passwords-django``. See the following
documentation for notes on additional configuration:

* Using :ref:`the password validator <validator>`

* Using :ref:`the automatic password-checking middleware <middleware>`

* Using :ref:`the Pwned Passwords API directly <api>`

