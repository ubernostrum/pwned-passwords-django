.. _install:


Installation
============

pwned-passwords-django |release| supports Django 3.2 and 4.0 on Python
3.7 (Django 3.2 only), 3.8, 3.9, and 3.10. Note that Django 3.2's
support for Python 3.10 was added in Django 3.2.9, so you may
experience issues with Python 3.10 and earlier Django 3.2 versions.

To install pwned-passwords-django, run::

    pip install pwned-passwords-django

This will use `pip`, the standard Python package-installation
tool. If you are using a supported version of Python, your
installation of Python should have come with `pip` bundled. To make
sure you have the latest version of `pip`, run::

    python -m ensurepip --upgrade

If this fails, instructions are available for `how to obtain and
manually install pip
<https://pip.pypa.io/en/latest/installing.html>`_.

If you don't already have a supported version of Django installed,
using `pip` to install pwned-passwords-django will also install the
latest supported version of Django.


Configuration and use
=====================

You may need to modify certain Django settings, depending on how you'd
like to use `pwned-passwords-django`. See the following
documentation for notes on additional configuration:

* Using :ref:`the password validator <validator>`

* Using :ref:`the automatic password-checking middleware <middleware>`

* Using :ref:`the Pwned Passwords API directly <api>`

