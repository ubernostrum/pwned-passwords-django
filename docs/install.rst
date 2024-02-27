.. _install:


Installation guide
==================

``pwned-passwords-django`` |release| supports Django 3.2, 4.2, and 5.0, and Python
3.8 through 3.12. See `Django's Python support matrix
<https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django>`_
for details of which Python versions are compatible with each version of
Django.

Installing ``pwned-passwords-django``
-------------------------------------

To install ``pwned-passwords-django``, run the following command from a command
prompt/terminal:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install pwned-passwords-django

.. tab:: Windows

   .. code-block:: shell

      py -m pip install pwned-passwords-django

This will use ``pip``, the standard Python package-installation tool. If you
are using a supported version of Python, your installation of Python should
have come with ``pip`` bundled. If ``pip`` does not appear to be present, you
can try running the following from a command prompt/terminal:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m ensurepip --upgrade

.. tab:: Windows

   .. code-block:: shell

      py -m ensurepip --upgrade

Instructions are also available for `how to obtain and manually install or
upgrade pip <https://pip.pypa.io/en/latest/installation/>`_.

If you don't already have a supported version of Django installed, using
``pip`` to install ``pwned-passwords-django`` will also install the latest
supported version of Django.


Installing from a source checkout
---------------------------------

If you want to work on ``pwned-passwords-django``, you can obtain a source
checkout.

The development repository for ``pwned-passwords-django`` is at
<https://github.com/ubernostrum/pwned-passwords-django>. If you have `git
<http://git-scm.com/>`_ installed, you can obtain a copy of the repository by
typing::

    git clone https://github.com/ubernostrum/pwned-passwords-django.git

From there, you can use git commands to check out the specific revision you
want, and perform an "editable" install (allowing you to change code as you
work on it) by typing:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install -e .

.. tab:: Windows

   .. code-block:: shell

      py -m pip install -e .
