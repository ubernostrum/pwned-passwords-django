.. _faq:

Frequently asked questions
==========================

The following notes answer some common questions, and may be useful to
you when using pwned-passwords-django.


What versions of Django and Python are supported?
-------------------------------------------------

Django 1.11 and 2.0 are supported, on any version of Python supported
by those Django versions. This includes Python 2.7 (only on Django
1.11), Python 3.4, Python 3.5, and Python 3.6.


Should I use the validator, the middleware, or the API directly?
----------------------------------------------------------------

It's probably best to enable both the validator and the
middleware. :ref:`The validator <validator>` by itself can catch many
attempts to set a user's password to a known-compromised value, but
cannot catch cases where a user already has a compromised password and
is continuing to use it. :ref:`The middleware <middleware>` can catch
that case, provided you're checking the ``request.pwned_passwords``
attribute in your view code.

Using :ref:`the direct API <api>` should only be necessary in rare
cases where neither the validator nor the middleware is
sufficient.


I'm getting timeouts from the Pwned Passwords API. What can I do?
-----------------------------------------------------------------

By default, pwned-passwords-django makes requests to the Pwned
Passwords API with a timeout of one second. You can change this by
specifying the Django setting
:data:`~django.conf.settings.PWNED_PASSWORDS_API_TIMEOUT` and setting
it to a float indicating your preferred timeout; for example, to have
a timeout of one and a half seconds, you'd set:

..code-block:: python

  PWNED_PASSWORDS_API_TIMEOUT = 1.5


How can this be secure? It's sending passwords to some random site!
-------------------------------------------------------------------

It's *not* actually sending passwords to any other site, and that's
the magic.

You can read about this in `the post announcing the launch of version
2 of Pwned Passwords
<https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/>`_,
but the summary of how it works is:

1. pwned-passwords-django hashes the password, and sends only the first
   five digits of the hexadecimal digest of the hash to Pwned Passwords.

2. Pwned Passwords responds with a list of hash suffixes (all the
   digits of the hash *except* the first five) for every entry in its
   database matching the submitted five-digit prefix.

3. pwned-passwords-django checks that list to see if the remainder of
   the password hash is present, and if so treats the password as
   compromised.

This means that neither the password, nor the full hash of the
password, is ever sent to any third-party site or service by
pwned-passwords-django.

.. warning:: **You can still accidentally disclose passwords!**

   pwned-passwords-django uses an API that never discloses the
   password or its hash, but that doesn't mean the rest of your code
   or third-party libraries won't.

   You should take care to use `Django's tools for filtering sensitive
   information from tracebacks and error reports
   <https://docs.djangoproject.com/en/2.0/howto/error-reporting/#filtering-sensitive-information>`_
   to ensure that your logging and monitoring systems don't
   accidentally log passwords. You should also be extremely
   conservative about allowing third-party JavaScript to run on your
   site, and periodically audit all JavaScript you use; remember that
   JavaScript can access anything your users enter on your site, and
   potentially do malicious things with that information.


How am I allowed to use this code?
----------------------------------

The pwned-passwords-django module is distributed under a `three-clause
BSD license <http://opensource.org/licenses/BSD-3-Clause>`_. This is
an open-source license which grants you broad freedom to use,
redistribute, modify and distribute modified versions of
pwned-passwords-django. For details, see the file ``LICENSE`` in the
source distribution of pwned-passwords-django.

.. _three-clause BSD license: http://opensource.org/licenses/BSD-3-Clause


I found a bug or want to make an improvement!
---------------------------------------------

The canonical development repository for pwned-passwords-django is
online at
<https://github.com/ubernostrum/pwned-passwords-django>. Issues and
pull requests can both be filed there.
