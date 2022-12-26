.. _install:


Installation
============

pwned-passwords-django |release| supports Django 3.2, 4.0, and 4.1 on Python
3.7 (Django 3.2 only), 3.8, 3.9, 3.10, and 3.11 (Django 4.1 only). Note that
Django 3.2's support for Python 3.10 was added in Django 3.2.9, so you may
experience issues with Python 3.10 and earlier Django 3.2 versions.

.. warning:: Django 3.2 and Python versions

   Django 3.2 was released before Python 3.10 had come out, and although it now
   supports Python 3.10, it did not officially do so until the Django 3.2.9
   release. You may encounter problems if you try to use Django 3.2.8 or
   earlier with Python 3.10.

   Also, although Django 3.2 continues to officially support Python 3.6,
   pwned-passwords-django |release| does not, because the Python core team's
   support window for Python 3.6 ended in December 2021.

To install pwned-passwords-django, run::

    pip install pwned-passwords-django

This will use ``pip``, the standard Python package-installation tool. If you
are using a supported version of Python, your installation of Python should
have come with ``pip`` bundled, but instructions are available `how to obtain
and manually install or upgrade pip
<https://pip.pypa.io/en/latest/installation/>`_.

If you don't already have a supported version of Django installed, using
``pip`` to install pwned-passwords-django will also install the latest
supported version of Django.


Configuration and use
=====================

You may need to modify certain Django settings, depending on how you'd like to
use pwned-passwords-django. See the following documentation for notes on
additional configuration:

* Using :ref:`the password validator <validator>`

* Using :ref:`the automatic password-checking middleware <middleware>`

* Using :ref:`the Pwned Passwords API directly <api>`
